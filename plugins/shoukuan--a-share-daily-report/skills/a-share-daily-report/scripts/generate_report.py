#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股早晚报生成器 (Enhanced Version)
===================================
数据源: 东方财富 (finance.eastmoney.com) 公开 API
输出:   Markdown 报告 + 数据图表 (PNG) + PDF

报告包含:
  1. 主要指数行情表格
  2. 市场情绪分析 (涨跌比、涨停跌停、成交额)
  3. 行业/概念板块涨跌排行
  4. 个股涨幅/跌幅排行
  5. 指数 K 线走势图 (近30个交易日, 含均线)
  6. 板块涨跌幅横向柱状图
  7. 市场情绪饼图
  8. 热点新闻聚合 & 主题追踪
  9. 综合分析与展望
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback
import urllib.request
from pathlib import Path

# ───────────────────── Configuration ──────────────────────────────────────

EASTMONEY_NEWS_URL = "https://finance.eastmoney.com/"

# Eastmoney push API base
API_BASE = "https://push2.eastmoney.com/api/qt"
API_HIS_BASE = "https://push2his.eastmoney.com/api/qt"

# Index secids: "market.code" -> display name
INDEX_SECIDS = {
    "1.000001": "上证指数",
    "0.399001": "深证成指",
    "0.399006": "创业板指",
    "1.000688": "科创50",
    "0.899050": "北证50",
    "1.000016": "上证50",
    "1.000300": "沪深300",
    "1.000905": "中证500",
    "0.399673": "创业板50",
}

# 主题关键词追踪
THEME_KEYWORDS = {
    "新能源": ["新能源", "光伏", "风电", "储能", "电池", "锂电", "充电桩"],
    "半导体": ["半导体", "芯片", "集成电路", "封装", "晶圆", "EDA"],
    "AI/人工智能": ["人工智能", "AI", "大模型", "算力", "GPT", "机器学习", "深度学习"],
    "机器人": ["机器人", "人形", "减速器", "伺服", "机械臂"],
    "有色金属": ["钛", "镁", "金属", "有色", "铜", "铝", "黄金", "稀土"],
    "医药生物": ["医药", "生物", "创新药", "医疗器械", "CXO"],
}

# ───────────────────── Helpers ────────────────────────────────────────────

def _safe_float(v, default=0.0):
    """Safely convert to float."""
    if v is None or v == "-" or v == "":
        return default
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def format_turnover(val):
    """Format turnover to human-readable."""
    v = _safe_float(val)
    if v >= 1e8:
        return f"{v / 1e8:.2f}亿"
    if v >= 1e4:
        return f"{v / 1e4:.2f}万"
    if v > 0:
        return f"{v:.0f}"
    return "N/A"


def format_volume(val):
    """Format volume (手) to human-readable."""
    v = _safe_float(val)
    if v >= 1e4:
        return f"{v / 1e4:.2f}万手"
    if v > 0:
        return f"{v:.0f}手"
    return "N/A"


def color_pct(val):
    """Format change percent with emoji indicator."""
    v = _safe_float(val)
    if v > 0:
        return f"🔴 +{v:.2f}%"
    if v < 0:
        return f"🟢 {v:.2f}%"
    return f"⚪ {v:.2f}%"


def color_pct_plain(val):
    """Format change percent without emoji, with +/- sign."""
    v = _safe_float(val)
    return f"{v:+.2f}%"


# ───────────────────── Data Fetching ──────────────────────────────────────

def _fetch_json(url, timeout=20):
    """Fetch JSON from Eastmoney API, auto-strips jQuery callback wrapper."""
    req = urllib.request.Request(url, headers={
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.eastmoney.com/",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        text = r.read().decode("utf-8", "ignore")
    # Strip jQuery callback wrapper
    m = re.match(r"^jQuery\w*\((.*)\);?\s*$", text, re.S)
    if m:
        text = m.group(1)
    return json.loads(text)


def _fetch_html(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")


# -- 1) Major index quotes ------------------------------------------------

def fetch_indices():
    """Fetch major index real-time quotes."""
    secids = ",".join(INDEX_SECIDS.keys())
    url = (
        f"{API_BASE}/ulist.np/get?fltt=2&secids={secids}"
        f"&fields=f2,f3,f4,f5,f6,f7,f12,f13,f14,f15,f16,f17,f18"
    )
    data = _fetch_json(url)
    results = []
    if data and data.get("data") and data["data"].get("diff"):
        for item in data["data"]["diff"]:
            results.append({
                "code": item.get("f12", ""),
                "name": item.get("f14", ""),
                "price": item.get("f2", "-"),
                "change_pct": item.get("f3", 0),
                "change_amt": item.get("f4", "-"),
                "volume": item.get("f5", 0),
                "turnover": item.get("f6", 0),
                "amplitude": item.get("f7", "-"),
                "high": item.get("f15", "-"),
                "low": item.get("f16", "-"),
                "open": item.get("f17", "-"),
                "prev_close": item.get("f18", "-"),
            })
    return results


# -- 2) Sector / concept board ranking ------------------------------------

def fetch_sector_ranking(sector_type="industry", direction="up", count=10):
    """
    Fetch sector performance ranking.
    sector_type: 'industry' | 'concept'
    direction:   'up' | 'down'
    """
    fs_type = "t:2" if sector_type == "industry" else "t:3"
    po = 1 if direction == "up" else 0
    url = (
        f"{API_BASE}/clist/get?pn=1&pz={count}&po={po}&np=1&fltt=2&invt=2"
        f"&fid=f3&fs=m:90+{fs_type}+f:!50"
        f"&fields=f2,f3,f4,f12,f14,f104,f105,f128,f140,f141"
    )
    data = _fetch_json(url)
    results = []
    if data and data.get("data") and data["data"].get("diff"):
        for item in data["data"]["diff"]:
            results.append({
                "code": item.get("f12", ""),
                "name": item.get("f14", ""),
                "price": item.get("f2", "-"),
                "change_pct": item.get("f3", 0),
                "change_amt": item.get("f4", 0),
                "up_count": item.get("f104", 0),
                "down_count": item.get("f105", 0),
                "lead_stock": item.get("f140", ""),
                "lead_stock_pct": item.get("f141", 0),
            })
    return results


# -- 3) Individual stock ranking -------------------------------------------

def fetch_stock_ranking(direction="up", count=10):
    """Fetch individual A-share stock ranking by change %."""
    po = 1 if direction == "up" else 0
    url = (
        f"{API_BASE}/clist/get?pn=1&pz={count}&po={po}&np=1&fltt=2&invt=2"
        f"&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23"
        f"&fields=f2,f3,f4,f5,f6,f7,f12,f14,f15,f16,f17,f18"
    )
    data = _fetch_json(url)
    results = []
    if data and data.get("data") and data["data"].get("diff"):
        for item in data["data"]["diff"]:
            results.append({
                "code": item.get("f12", ""),
                "name": item.get("f14", ""),
                "price": item.get("f2", "-"),
                "change_pct": item.get("f3", 0),
                "change_amt": item.get("f4", "-"),
                "volume": item.get("f5", 0),
                "turnover": item.get("f6", 0),
                "amplitude": item.get("f7", "-"),
            })
    return results


# -- 4) Market breadth -----------------------------------------------------

def fetch_market_breadth():
    """Fetch all A-share stocks change % and compute breadth stats."""
    url = (
        f"{API_BASE}/clist/get?pn=1&pz=6000&np=1&fltt=2&invt=2&fid=f3"
        f"&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23"
        f"&fields=f3"
    )
    data = _fetch_json(url)
    stats = {
        "up": 0, "down": 0, "flat": 0,
        "limit_up": 0, "limit_down": 0,
        "big_up": 0, "big_down": 0,
        "total": 0,
    }
    if data and data.get("data") and data["data"].get("diff"):
        for item in data["data"]["diff"]:
            pct = item.get("f3")
            if pct is None or pct == "-":
                continue
            pct = _safe_float(pct)
            stats["total"] += 1
            if pct > 0:
                stats["up"] += 1
            elif pct < 0:
                stats["down"] += 1
            else:
                stats["flat"] += 1
            if pct >= 9.9:
                stats["limit_up"] += 1
            elif pct >= 5.0:
                stats["big_up"] += 1
            if pct <= -9.9:
                stats["limit_down"] += 1
            elif pct <= -5.0:
                stats["big_down"] += 1
    return stats


# -- 5) K-line data --------------------------------------------------------

def fetch_kline(secid, count=30):
    """Fetch daily K-line data for an index / stock."""
    url = (
        f"{API_HIS_BASE}/stock/kline/get?"
        f"secid={secid}&fields1=f1,f2,f3,f4,f5,f6"
        f"&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
        f"&klt=101&fqt=1&end=20500101&lmt={count}"
    )
    data = _fetch_json(url)
    results = []
    if data and data.get("data") and data["data"].get("klines"):
        for line in data["data"]["klines"]:
            parts = line.split(",")
            if len(parts) >= 11:
                results.append({
                    "date": parts[0],
                    "open": float(parts[1]),
                    "close": float(parts[2]),
                    "high": float(parts[3]),
                    "low": float(parts[4]),
                    "volume": float(parts[5]),
                    "turnover": float(parts[6]),
                    "amplitude": float(parts[7]),
                    "change_pct": float(parts[8]),
                    "change_amt": float(parts[9]),
                    "turnover_rate": float(parts[10]),
                })
    return results


# -- 6) News scraping ------------------------------------------------------

def fetch_news_links():
    """Scrape news links from Eastmoney finance homepage."""
    html = _fetch_html(EASTMONEY_NEWS_URL)
    links = re.findall(
        r'<a[^>]+href="(https?://finance\.eastmoney\.com/a/[^\"]+)"[^>]*>(.*?)</a>',
        html,
    )
    items = []
    seen = set()
    for href, text in links:
        text = re.sub(r"<.*?>", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        if text and len(text) > 6 and text not in seen:
            seen.add(text)
            items.append((text, href))
    return items


# ───────────────────── Chart Generation ───────────────────────────────────

_PLT = None  # lazy-loaded


def _setup_matplotlib():
    """Setup matplotlib with Chinese font support. Returns plt or None."""
    global _PLT
    if _PLT is not None:
        return _PLT
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        chinese_fonts = [
            "PingFang HK", "Songti SC", "Heiti TC", "STHeiti",
            "Kaiti SC", "Arial Unicode MS", "SimHei", "WenQuanYi Micro Hei",
        ]
        matplotlib.rcParams["font.sans-serif"] = chinese_fonts
        matplotlib.rcParams["axes.unicode_minus"] = False
        matplotlib.rcParams["figure.dpi"] = 150
        matplotlib.rcParams["savefig.bbox"] = "tight"
        matplotlib.rcParams["savefig.facecolor"] = "white"

        _PLT = plt
        return plt
    except ImportError:
        print("   ⚠️  matplotlib unavailable, skipping charts.")
        return None


def generate_kline_chart(kline_data, outdir):
    """Generate K-line + MA + Volume chart for major indices. Returns filename."""
    plt = _setup_matplotlib()
    if plt is None:
        return None

    indices_to_plot = [(n, d) for n, d in kline_data.items() if d]
    if not indices_to_plot:
        return None

    n_panels = len(indices_to_plot)
    fig, axes = plt.subplots(n_panels, 1, figsize=(15, 4.5 * n_panels), squeeze=False)
    fig.suptitle("A股主要指数近期走势", fontsize=17, fontweight="bold", y=0.995)

    palette = {"上证指数": "#E74C3C", "深证成指": "#3498DB", "创业板指": "#27AE60"}

    for idx, (name, klines) in enumerate(indices_to_plot):
        ax = axes[idx][0]
        dates = [k["date"][-5:] for k in klines]
        closes = [k["close"] for k in klines]
        opens = [k["open"] for k in klines]
        highs = [k["high"] for k in klines]
        lows = [k["low"] for k in klines]
        volumes = [k["turnover"] / 1e8 for k in klines]
        changes = [k["change_pct"] for k in klines]
        x = list(range(len(dates)))

        # Candlestick
        for i in x:
            c = "#E74C3C" if closes[i] >= opens[i] else "#27AE60"
            body_lo = min(opens[i], closes[i])
            body_hi = max(opens[i], closes[i])
            body_h = body_hi - body_lo or (closes[i] * 0.001)
            ax.add_patch(plt.Rectangle(
                (i - 0.35, body_lo), 0.7, body_h,
                facecolor=c, edgecolor=c, linewidth=0.8,
            ))
            ax.plot([i, i], [lows[i], highs[i]], color=c, linewidth=0.7)

        ax.set_xlim(-0.8, len(dates) - 0.2)
        ax.set_ylim(min(lows) * 0.998, max(highs) * 1.002)

        # Moving averages
        def _ma(data, period):
            return [
                sum(data[max(0, i - period + 1): i + 1]) / min(i + 1, period)
                for i in range(len(data))
            ]

        if len(closes) >= 5:
            ax.plot(x, _ma(closes, 5), color="#F39C12", linewidth=1.2,
                    linestyle="--", alpha=0.85, label="MA5")
        if len(closes) >= 10:
            ax.plot(x, _ma(closes, 10), color="#9B59B6", linewidth=1.2,
                    linestyle="-.", alpha=0.85, label="MA10")
        if len(closes) >= 20:
            ax.plot(x, _ma(closes, 20), color="#1ABC9C", linewidth=1.2,
                    linestyle=":", alpha=0.85, label="MA20")

        ax.set_title(f"{name}  收盘 {closes[-1]:.2f}  ({changes[-1]:+.2f}%)",
                     fontsize=13, fontweight="bold")
        ax.set_ylabel("点位", fontsize=10)
        ax.legend(loc="upper left", fontsize=8, framealpha=0.7)
        ax.grid(True, alpha=0.25)
        ax.set_xticks(x)
        ax.set_xticklabels(dates, fontsize=7, rotation=45)
        step = max(1, len(dates) // 10)
        for i, lbl in enumerate(ax.xaxis.get_ticklabels()):
            if i % step != 0:
                lbl.set_visible(False)

        # Volume bars
        ax2 = ax.twinx()
        bar_colors = ["#E74C3C" if c >= 0 else "#27AE60" for c in changes]
        ax2.bar(x, volumes, alpha=0.25, color=bar_colors, width=0.55)
        ax2.set_ylabel("成交额(亿元)", fontsize=8, alpha=0.6)
        ax2.tick_params(axis="y", labelsize=7)
        ax2.set_ylim(0, max(volumes) * 3)

    plt.tight_layout(rect=[0, 0, 1, 0.97])
    fname = "index_kline.png"
    fig.savefig(outdir / fname, dpi=150)
    plt.close(fig)
    return fname


def generate_sector_chart(sectors_up, sectors_down, outdir):
    """Horizontal bar chart of top gaining/losing sectors."""
    plt = _setup_matplotlib()
    if plt is None:
        return None
    if not sectors_up and not sectors_down:
        return None

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("行业板块涨跌排行", fontsize=17, fontweight="bold")

    if sectors_up:
        names = [s["name"] for s in reversed(sectors_up[:10])]
        pcts = [_safe_float(s["change_pct"]) for s in reversed(sectors_up[:10])]
        colors = ["#E74C3C" if p >= 0 else "#27AE60" for p in pcts]
        bars = ax1.barh(names, pcts, color=colors, height=0.55, edgecolor="white")
        ax1.set_title("涨幅 Top 10", fontsize=13, fontweight="bold", color="#C0392B")
        ax1.set_xlabel("涨跌幅 (%)")
        for bar, pct in zip(bars, pcts):
            ax1.text(bar.get_width() + 0.08, bar.get_y() + bar.get_height() / 2,
                     f"{pct:+.2f}%", va="center", fontsize=9, fontweight="bold")
        ax1.grid(True, axis="x", alpha=0.25)
    else:
        ax1.text(0.5, 0.5, "暂无数据", transform=ax1.transAxes, ha="center")

    if sectors_down:
        names = [s["name"] for s in sectors_down[:10]]
        pcts = [_safe_float(s["change_pct"]) for s in sectors_down[:10]]
        colors = ["#E74C3C" if p >= 0 else "#27AE60" for p in pcts]
        bars = ax2.barh(names, pcts, color=colors, height=0.55, edgecolor="white")
        ax2.set_title("跌幅 Top 10", fontsize=13, fontweight="bold", color="#27AE60")
        ax2.set_xlabel("涨跌幅 (%)")
        for bar, pct in zip(bars, pcts):
            offset = bar.get_width() - 0.08 if pct < 0 else bar.get_width() + 0.08
            ha = "right" if pct < 0 else "left"
            ax2.text(offset, bar.get_y() + bar.get_height() / 2,
                     f"{pct:+.2f}%", va="center", fontsize=9, fontweight="bold", ha=ha)
        ax2.grid(True, axis="x", alpha=0.25)
    else:
        ax2.text(0.5, 0.5, "暂无数据", transform=ax2.transAxes, ha="center")

    plt.tight_layout()
    fname = "sector_ranking.png"
    fig.savefig(outdir / fname, dpi=150)
    plt.close(fig)
    return fname


def generate_breadth_chart(stats, outdir):
    """Pie chart + bar chart for market breadth."""
    plt = _setup_matplotlib()
    if plt is None or stats["total"] == 0:
        return None

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.suptitle("市场情绪全景", fontsize=17, fontweight="bold")

    labels = ["上涨", "下跌", "平盘"]
    sizes = [stats["up"], stats["down"], stats["flat"]]
    colors_pie = ["#E74C3C", "#27AE60", "#BDC3C7"]
    explode = (0.04, 0.04, 0)
    wedges, texts, autotexts = ax1.pie(
        sizes, explode=explode, labels=labels, colors=colors_pie,
        autopct="%1.1f%%", startangle=90, textprops={"fontsize": 11},
        pctdistance=0.75,
    )
    for at in autotexts:
        at.set_fontweight("bold")
    ax1.set_title(f"涨跌分布（共 {stats['total']} 只）", fontsize=12)

    categories = ["涨停", "涨>5%", "跌>5%", "跌停"]
    values = [stats["limit_up"], stats["big_up"], stats["big_down"], stats["limit_down"]]
    bar_colors = ["#E74C3C", "#E67E22", "#2ECC71", "#27AE60"]
    bars = ax2.bar(categories, values, color=bar_colors, width=0.55, edgecolor="white")
    ax2.set_title("极端涨跌统计", fontsize=12)
    ax2.set_ylabel("家数")
    for bar, val in zip(bars, values):
        if val > 0:
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
                     str(val), ha="center", va="bottom", fontsize=12, fontweight="bold")
    ax2.grid(True, axis="y", alpha=0.25)

    plt.tight_layout()
    fname = "market_breadth.png"
    fig.savefig(outdir / fname, dpi=150)
    plt.close(fig)
    return fname


# ───────────────────── Market Analysis Engine ─────────────────────────────

def _compute_rsi(closes, period=14):
    """Compute RSI from closing prices list. Returns latest RSI or None."""
    if len(closes) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i - 1]
        gains.append(diff if diff > 0 else 0)
        losses.append(-diff if diff < 0 else 0)
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - 100 / (1 + rs)


def analyze_market(indices, breadth, kline_sh, industry_up, industry_down,
                   concept_up, is_morning):
    """Generate multi-dimensional market analysis commentary."""
    analysis = []

    sh = next((i for i in indices if i["code"] == "000001"), None)
    sz = next((i for i in indices if i["code"] == "399001"), None)
    cy = next((i for i in indices if i["code"] == "399006"), None)

    # 1. 大盘走势
    if sh:
        pct = _safe_float(sh["change_pct"])
        price = sh["price"]
        if pct > 2:
            desc = "大幅上涨，市场做多热情高涨"
        elif pct > 1:
            desc = "强势上涨，多头占据明显优势"
        elif pct > 0.3:
            desc = "温和上涨，市场情绪偏暖"
        elif pct > -0.3:
            desc = "窄幅震荡，多空博弈激烈"
        elif pct > -1:
            desc = "小幅回调，空头略占上风"
        elif pct > -2:
            desc = "明显下跌，市场承压运行"
        else:
            desc = "大幅下跌，恐慌情绪蔓延"
        analysis.append(
            f"**大盘走势**：上证指数报 {price} 点，{desc}（{pct:+.2f}%）。"
        )

    # 2. 量能分析
    if sh and sh.get("turnover") and sh["turnover"] != "-":
        turnover = _safe_float(sh["turnover"])
        if turnover >= 1e12:
            vol_desc = ("两市成交额突破万亿，市场交投极为活跃，"
                        "增量资金入场迹象明显")
        elif turnover >= 8000e8:
            vol_desc = "两市成交额维持高位，资金参与意愿较强"
        elif turnover >= 5000e8:
            vol_desc = "两市成交额处于中等水平，存量博弈为主"
        else:
            vol_desc = ("两市成交量能偏弱，市场观望情绪浓厚，"
                        "增量资金不足")
        analysis.append(
            f"**量能分析**：{vol_desc}（成交额 {format_turnover(turnover)}元）。"
        )

    if kline_sh and len(kline_sh) >= 5:
        recent_vol = [k["turnover"] for k in kline_sh[-5:]]
        prev_vol = ([k["turnover"] for k in kline_sh[-10:-5]]
                    if len(kline_sh) >= 10 else [])
        if prev_vol:
            avg_recent = sum(recent_vol) / len(recent_vol)
            avg_prev = sum(prev_vol) / len(prev_vol)
            ratio = avg_recent / avg_prev if avg_prev else 1
            if ratio > 1.3:
                analysis.append(
                    f"**量价配合**：近5日平均成交额较前5日放大 "
                    f"{(ratio-1)*100:.0f}%，量能放大趋势明显，"
                    "关注是否配合价格突破。"
                )
            elif ratio < 0.7:
                analysis.append(
                    f"**量价配合**：近5日成交额较前5日萎缩 "
                    f"{(1-ratio)*100:.0f}%，市场交投趋于清淡。"
                )

    # 3. 创业板风格
    if cy and sh:
        cy_pct = _safe_float(cy["change_pct"])
        sh_pct = _safe_float(sh["change_pct"])
        diff = cy_pct - sh_pct
        if diff > 0.5:
            analysis.append(
                f"**风格分化**：创业板指（{cy_pct:+.2f}%）明显强于"
                f"主板（{sh_pct:+.2f}%），成长/科技风格占优，"
                "市场风险偏好提升。"
            )
        elif diff < -0.5:
            analysis.append(
                f"**风格分化**：创业板指（{cy_pct:+.2f}%）弱于"
                f"主板（{sh_pct:+.2f}%），资金偏好大盘蓝筹和"
                "防御性品种，避险情绪升温。"
            )

    # 4. 市场广度
    if breadth and breadth["total"] > 0:
        up_ratio = breadth["up"] / breadth["total"] * 100
        if up_ratio > 70:
            bd = "普涨格局，赚钱效应极强，可积极参与"
        elif up_ratio > 55:
            bd = "多数个股上涨，赚钱效应较好"
        elif up_ratio > 45:
            bd = "涨跌参半，结构性行情，需精选个股"
        elif up_ratio > 30:
            bd = "多数个股下跌，亏钱效应明显，宜控制仓位"
        else:
            bd = "普跌格局，市场风险偏好极低，建议观望为主"
        analysis.append(
            f"**市场宽度**：上涨 {breadth['up']} 家 vs "
            f"下跌 {breadth['down']} 家"
            f"（涨跌比 {breadth['up']}:{breadth['down']}），{bd}。"
            f"涨停 {breadth['limit_up']} 家，"
            f"跌停 {breadth['limit_down']} 家。"
        )

    # 5. 技术面 (K线 + 均线 + RSI)
    if kline_sh and len(kline_sh) >= 5:
        closes = [k["close"] for k in kline_sh]
        ma5 = sum(closes[-5:]) / 5
        ma10 = sum(closes[-10:]) / 10 if len(closes) >= 10 else None
        ma20 = sum(closes[-20:]) / 20 if len(closes) >= 20 else None
        current = closes[-1]
        rsi = _compute_rsi(closes, 14)

        tech_parts = []

        # Consecutive trend detection
        up_days = 0
        for i in range(len(closes) - 1, 0, -1):
            if closes[i] >= closes[i - 1]:
                up_days += 1
            else:
                break
        down_days = 0
        for i in range(len(closes) - 1, 0, -1):
            if closes[i] <= closes[i - 1]:
                down_days += 1
            else:
                break

        if up_days >= 5:
            tech_parts.append(
                f"指数连续{up_days}日收阳，短线偏强但注意超买回调风险"
            )
        elif up_days >= 3:
            tech_parts.append(f"指数连续{up_days}日反弹，短期趋势向好")
        elif down_days >= 5:
            tech_parts.append(
                f"指数连续{down_days}日收阴，短线偏弱，关注能否企稳"
            )
        elif down_days >= 3:
            tech_parts.append(f"指数连续{down_days}日调整，注意下方支撑")

        # MA alignment
        if ma20 is not None:
            if ma10 and current > ma5 > ma10 > ma20:
                tech_parts.append("均线多头排列，中短期趋势偏强")
            elif current < ma5 < ma20:
                tech_parts.append("均线空头排列，中短期趋势偏弱")
            elif current > ma20 and current < ma5:
                tech_parts.append(
                    f"价格回踩5日均线（{ma5:.0f}），"
                    f"20日均线（{ma20:.0f}）提供支撑"
                )

        # RSI
        if rsi is not None:
            if rsi > 80:
                tech_parts.append(
                    f"RSI(14)={rsi:.1f}，已进入超买区间，短线回调概率增大"
                )
            elif rsi > 70:
                tech_parts.append(
                    f"RSI(14)={rsi:.1f}，接近超买，注意高位风险"
                )
            elif rsi < 20:
                tech_parts.append(
                    f"RSI(14)={rsi:.1f}，已进入超卖区间，存在技术性反弹需求"
                )
            elif rsi < 30:
                tech_parts.append(
                    f"RSI(14)={rsi:.1f}，接近超卖，可关注底部信号"
                )
            else:
                tech_parts.append(f"RSI(14)={rsi:.1f}，处于中性区间")

        if tech_parts:
            analysis.append("**技术面**：" + "；".join(tech_parts) + "。")

    # 6. 板块轮动
    if industry_up and concept_up:
        top_ind = [s["name"] for s in industry_up[:3]]
        top_con = [s["name"] for s in concept_up[:3]]
        analysis.append(
            f"**板块轮动**：领涨行业为「{'、'.join(top_ind)}」，"
            f"活跃概念为「{'、'.join(top_con)}」。"
        )
        if industry_down:
            bot_ind = [s["name"] for s in industry_down[:3]]
            analysis.append(
                f"调整板块为「{'、'.join(bot_ind)}」，"
                "注意规避短期弱势方向。"
            )

    # 7. 操作建议
    if is_morning:
        analysis.append(
            "**操作参考**：盘前关注外围市场表现和消息面变化，"
            "若高开则关注持续性，低开则关注支撑位能否企稳。"
            "建议控制仓位，聚焦主线板块。"
        )
    else:
        analysis.append(
            "**后市展望**：关注量能变化和板块轮动节奏，"
            "保持仓位弹性，攻守兼备。"
            "如有突发利好/利空，及时调整策略。"
        )

    return analysis


# ───────────────────── Markdown Composition ───────────────────────────────

def md_table(headers, rows, align=None):
    """Generate a Markdown table string."""
    if not rows:
        return "*暂无数据*\n"
    if align is None:
        align = ["left"] * len(headers)
    sep_map = {"right": "---:", "center": ":---:", "left": ":---"}
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join(sep_map.get(a, ":---") for a in align) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines) + "\n"


def compose_report(
    date_str, is_morning, indices, industry_up, industry_down,
    concept_up, stocks_up, stocks_down, breadth, kline_data,
    news, chart_files,
):
    """Compose the full enhanced Markdown report."""
    mode = "早报" if is_morning else "晚报"
    gen_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    md = []

    # Header
    md.append(f"# 📊 A股{mode}｜{date_str}")
    md.append("")
    md.append(f"> **生成时间**：{gen_time}（Asia/Shanghai）  ")
    md.append(f"> **数据源**：东方财富（finance.eastmoney.com）  ")
    md.append(f"> **报告类型**：{'盘前参考' if is_morning else '盘后复盘'}")
    md.append("")
    md.append("---")
    md.append("")

    # == Section 1: 主要指数行情 ==
    md.append("## 📈 一、主要指数行情")
    md.append("")
    if indices:
        headers = ["指数", "最新价", "涨跌幅", "涨跌额", "振幅",
                   "今开", "最高", "最低", "成交额"]
        align = ["left"] + ["right"] * 8
        rows = []
        for idx in indices:
            rows.append([
                f"**{idx['name']}**",
                f"{idx['price']}" if idx["price"] != "-" else "N/A",
                color_pct(idx["change_pct"]),
                f"{idx['change_amt']}" if idx["change_amt"] != "-" else "N/A",
                f"{idx['amplitude']}%" if idx["amplitude"] != "-" else "N/A",
                f"{idx['open']}" if idx["open"] != "-" else "N/A",
                f"{idx['high']}" if idx["high"] != "-" else "N/A",
                f"{idx['low']}" if idx["low"] != "-" else "N/A",
                format_turnover(idx["turnover"]),
            ])
        md.append(md_table(headers, rows, align))
    else:
        md.append("*指数数据获取失败*\n")
    md.append("")

    # == Section 2: 市场情绪 ==
    md.append("## 🌡️ 二、市场情绪")
    md.append("")
    if breadth and breadth["total"] > 0:
        up_ratio = breadth["up"] / breadth["total"] * 100
        bar_len = 20
        up_bars = round(up_ratio / 100 * bar_len)
        down_bars = bar_len - up_bars
        md.append(
            f"**涨跌温度计** {'🟥' * up_bars}{'🟩' * down_bars}"
        )
        md.append("")
        headers = ["指标", "数值", "指标", "数值"]
        align = ["left", "right", "left", "right"]
        rows = [
            ["上涨家数", f"**{breadth['up']}**",
             "下跌家数", f"**{breadth['down']}**"],
            ["平盘家数", f"{breadth['flat']}",
             "涨跌比", f"{breadth['up']}:{breadth['down']}"],
            ["涨停", f"🔴 **{breadth['limit_up']}**",
             "跌停", f"🟢 **{breadth['limit_down']}**"],
            ["涨幅 >5%", f"{breadth['big_up']}",
             "跌幅 >5%", f"{breadth['big_down']}"],
            ["上涨占比", f"**{up_ratio:.1f}%**",
             "总计", f"{breadth['total']}只"],
        ]
        md.append(md_table(headers, rows, align))
    else:
        md.append("*市场涨跌数据获取失败*\n")
    md.append("")

    if chart_files.get("breadth"):
        md.append(f"![市场情绪全景]({chart_files['breadth']})")
        md.append("")

    # == Section 3: 指数走势图 ==
    if chart_files.get("kline"):
        md.append("## 📉 三、指数走势（近30个交易日）")
        md.append("")
        md.append(f"![指数K线走势图]({chart_files['kline']})")
        md.append("")

    # == Section 4: 行业板块排行 ==
    md.append("## 🏭 四、行业板块表现")
    md.append("")
    md.append("### 涨幅 Top 10")
    md.append("")
    if industry_up:
        headers = ["#", "板块", "涨跌幅", "领涨股", "板块涨/跌家数"]
        align = ["center", "left", "right", "left", "center"]
        rows = []
        for i, s in enumerate(industry_up[:10], 1):
            lead = s.get("lead_stock", "")
            lead_pct = _safe_float(s.get("lead_stock_pct", 0))
            lead_str = (f"{lead}（{lead_pct:+.2f}%）"
                        if lead and lead != "-" else "-")
            rows.append([
                f"{i}", f"**{s['name']}**", color_pct(s["change_pct"]),
                lead_str,
                f"{s.get('up_count', '-')}/{s.get('down_count', '-')}",
            ])
        md.append(md_table(headers, rows, align))
    md.append("")
    md.append("### 跌幅 Top 10")
    md.append("")
    if industry_down:
        headers = ["#", "板块", "涨跌幅", "领跌股", "板块涨/跌家数"]
        align = ["center", "left", "right", "left", "center"]
        rows = []
        for i, s in enumerate(industry_down[:10], 1):
            lead = s.get("lead_stock", "")
            lead_pct = _safe_float(s.get("lead_stock_pct", 0))
            lead_str = (f"{lead}（{lead_pct:+.2f}%）"
                        if lead and lead != "-" else "-")
            rows.append([
                f"{i}", f"**{s['name']}**", color_pct(s["change_pct"]),
                lead_str,
                f"{s.get('up_count', '-')}/{s.get('down_count', '-')}",
            ])
        md.append(md_table(headers, rows, align))
    md.append("")

    if chart_files.get("sector"):
        md.append(f"![行业板块涨跌排行]({chart_files['sector']})")
        md.append("")

    # == Section 5: 热门概念板块 ==
    md.append("## 🔥 五、热门概念 Top 10")
    md.append("")
    if concept_up:
        headers = ["#", "概念", "涨跌幅", "领涨股"]
        align = ["center", "left", "right", "left"]
        rows = []
        for i, s in enumerate(concept_up[:10], 1):
            lead = s.get("lead_stock", "")
            lead_pct = _safe_float(s.get("lead_stock_pct", 0))
            lead_str = (f"{lead}（{lead_pct:+.2f}%）"
                        if lead and lead != "-" else "-")
            rows.append([
                f"{i}", f"**{s['name']}**",
                color_pct(s["change_pct"]), lead_str,
            ])
        md.append(md_table(headers, rows, align))
    else:
        md.append("*概念板块数据暂无*\n")
    md.append("")

    # == Section 6: 个股涨跌排行 ==
    md.append("## 🏆 六、个股涨跌排行")
    md.append("")
    md.append("### 🔝 涨幅榜 Top 10")
    md.append("")
    if stocks_up:
        headers = ["#", "代码", "名称", "最新价", "涨跌幅", "成交额", "振幅"]
        align = ["center", "center", "left", "right",
                 "right", "right", "right"]
        rows = []
        for i, s in enumerate(stocks_up[:10], 1):
            rows.append([
                f"{i}", s["code"], f"**{s['name']}**",
                f"{s['price']}", color_pct(s["change_pct"]),
                format_turnover(s["turnover"]),
                f"{s['amplitude']}%" if s["amplitude"] != "-" else "N/A",
            ])
        md.append(md_table(headers, rows, align))
    md.append("")
    md.append("### 🔻 跌幅榜 Top 10")
    md.append("")
    if stocks_down:
        headers = ["#", "代码", "名称", "最新价", "涨跌幅", "成交额", "振幅"]
        align = ["center", "center", "left", "right",
                 "right", "right", "right"]
        rows = []
        for i, s in enumerate(stocks_down[:10], 1):
            rows.append([
                f"{i}", s["code"], f"**{s['name']}**",
                f"{s['price']}", color_pct(s["change_pct"]),
                format_turnover(s["turnover"]),
                f"{s['amplitude']}%" if s["amplitude"] != "-" else "N/A",
            ])
        md.append(md_table(headers, rows, align))
    md.append("")

    # == Section 7: 主题追踪 ==
    md.append("## 🎯 七、主题追踪")
    md.append("")
    if news:
        for theme, keywords in THEME_KEYWORDS.items():
            theme_news = [
                (t, h) for t, h in news
                if any(k in t for k in keywords)
            ]
            md.append(f"### {theme}")
            if theme_news:
                for t, h in theme_news[:4]:
                    md.append(f"- [{t}]({h})")
            else:
                md.append("- 暂无相关新闻")
            md.append("")
    else:
        md.append("*新闻数据获取失败*\n")
        md.append("")

    # == Section 8: 今日要闻 ==
    md.append("## 📰 八、今日要闻")
    md.append("")
    if news:
        for t, h in news[:12]:
            md.append(f"- [{t}]({h})")
    else:
        md.append("- 暂无新闻数据")
    md.append("")

    # == Section 9: 综合分析 ==
    md.append("## 🧠 九、综合分析")
    md.append("")
    kline_sh = kline_data.get("上证指数", [])
    analysis_lines = analyze_market(
        indices, breadth, kline_sh,
        industry_up, industry_down, concept_up, is_morning,
    )
    for line in analysis_lines:
        md.append(line)
        md.append("")

    # Footer
    md.append("---")
    md.append("")
    md.append(
        "> ⚠️ **免责声明**：本报告基于公开数据自动生成，仅供参考，"
        "不构成任何投资建议。投资有风险，入市需谨慎。"
        "数据来源为东方财富，可能存在延迟或偏差。"
    )
    md.append("")
    md.append(f"*— A股{mode} · 自动生成 @ {gen_time} —*")

    return "\n".join(md)


# ───────────────────── PDF (basic fallback) ───────────────────────────────

def make_simple_pdf(text, out_path):
    """Generate a rudimentary PDF. For proper Chinese PDF use nano-pdf."""
    lines = text.splitlines()
    content_lines = ["BT", "/F1 9 Tf", "11 TL", "40 790 Td"]
    for line in lines[:120]:
        clean = re.sub(r"[#*|>]", "", line)
        clean = re.sub(r"!\[.*?\]\(.*?\)", "[图表]", clean)
        clean = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean)
        esc = (clean.replace("\\", "\\\\")
               .replace("(", "\\(").replace(")", "\\)"))
        content_lines.append(f"({esc}) Tj T*")
    content_lines.append("ET")
    content = "\n".join(content_lines).encode("latin-1", "ignore")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842]"
         b" /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"),
        b"<< /Length %d >>\nstream\n" % len(content)
        + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    out = b"%PDF-1.4\n"
    offsets = []
    for i, data in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode("ascii") + data + b"\nendobj\n"
    xref_pos = len(out)
    out += b"xref\n0 %d\n" % (len(objects) + 1)
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode("ascii")
    out += (b"trailer\n<< /Size %d /Root 1 0 R >>\n"
            b"startxref\n%d\n%%%%EOF" % (len(objects) + 1, xref_pos))
    out_path.write_bytes(out)


# ───────────────────── Main Entry ─────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="A股早晚报生成器（增强版）",
    )
    ap.add_argument(
        "--mode", choices=["morning", "evening"], required=True,
        help="报告类型: morning=早报, evening=晚报",
    )
    ap.add_argument(
        "--date", default=dt.date.today().strftime("%Y-%m-%d"),
        help="报告日期 YYYY-MM-DD",
    )
    ap.add_argument("--outdir", required=True, help="输出目录")
    ap.add_argument(
        "--no-charts", action="store_true",
        help="跳过图表生成",
    )
    args = ap.parse_args()

    date_str = args.date
    ymd = date_str.replace("-", "")
    is_morning = args.mode == "morning"
    mode_cn = "早报" if is_morning else "晚报"
    base = f"A股{mode_cn}-{ymd}"
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"{'='*60}")
    print(f" 📊 A股{mode_cn}生成器（增强版）")
    print(f" 📅 日期: {date_str}")
    print(f" 📁 输出: {outdir}")
    print(f"{'='*60}")
    print()

    # == Data Fetching ==

    print("📡 [1/7] 获取主要指数行情...")
    try:
        indices = fetch_indices()
        print(f"   ✅ 获取到 {len(indices)} 个指数")
    except Exception as e:
        print(f"   ⚠️  失败: {e}")
        indices = []

    print("📡 [2/7] 获取行业板块排行...")
    try:
        industry_up = fetch_sector_ranking("industry", "up", 10)
        industry_down = fetch_sector_ranking("industry", "down", 10)
        print(f"   ✅ 涨幅{len(industry_up)} / 跌幅{len(industry_down)}")
    except Exception as e:
        print(f"   ⚠️  失败: {e}")
        industry_up, industry_down = [], []

    print("📡 [3/7] 获取概念板块排行...")
    try:
        concept_up = fetch_sector_ranking("concept", "up", 10)
        print(f"   ✅ 概念板块 Top {len(concept_up)}")
    except Exception as e:
        print(f"   ⚠️  失败: {e}")
        concept_up = []

    print("📡 [4/7] 获取个股涨跌排行...")
    try:
        stocks_up = fetch_stock_ranking("up", 10)
        stocks_down = fetch_stock_ranking("down", 10)
        print(f"   ✅ 涨幅{len(stocks_up)} / 跌幅{len(stocks_down)}")
    except Exception as e:
        print(f"   ⚠️  失败: {e}")
        stocks_up, stocks_down = [], []

    print("📡 [5/7] 获取市场涨跌统计...")
    try:
        breadth = fetch_market_breadth()
        print(f"   ✅ 共{breadth['total']}只: "
              f"↑{breadth['up']} ↓{breadth['down']} "
              f"={breadth['flat']} "
              f"涨停{breadth['limit_up']} 跌停{breadth['limit_down']}")
    except Exception as e:
        print(f"   ⚠️  失败: {e}")
        breadth = {
            "up": 0, "down": 0, "flat": 0,
            "limit_up": 0, "limit_down": 0,
            "big_up": 0, "big_down": 0, "total": 0,
        }

    print("📡 [6/7] 获取 K 线数据（近30日）...")
    kline_data = {}
    for secid, name in [
        ("1.000001", "上证指数"),
        ("0.399001", "深证成指"),
        ("0.399006", "创业板指"),
    ]:
        try:
            klines = fetch_kline(secid, 30)
            kline_data[name] = klines
            print(f"   ✅ {name}: {len(klines)} 根K线")
        except Exception as e:
            print(f"   ⚠️  {name} 失败: {e}")
            kline_data[name] = []

    print("📡 [7/7] 获取新闻数据...")
    try:
        news = fetch_news_links()
        print(f"   ✅ 获取 {len(news)} 条新闻")
    except Exception as e:
        print(f"   ⚠️  失败: {e}")
        news = []

    # == Chart Generation ==

    chart_files = {}
    if not args.no_charts:
        print()
        print("📊 生成可视化图表...")
        try:
            fname = generate_kline_chart(kline_data, outdir)
            if fname:
                chart_files["kline"] = fname
                print(f"   ✅ 指数K线走势图: {fname}")
            else:
                print("   ⚠️  无K线数据或 matplotlib 不可用")
        except Exception as e:
            print(f"   ⚠️  K线图失败: {e}")
            traceback.print_exc()

        try:
            fname = generate_sector_chart(industry_up, industry_down, outdir)
            if fname:
                chart_files["sector"] = fname
                print(f"   ✅ 板块排行图: {fname}")
        except Exception as e:
            print(f"   ⚠️  板块图失败: {e}")

        try:
            fname = generate_breadth_chart(breadth, outdir)
            if fname:
                chart_files["breadth"] = fname
                print(f"   ✅ 市场情绪图: {fname}")
        except Exception as e:
            print(f"   ⚠️  情绪图失败: {e}")

    # == Report Composition ==

    print()
    print("📝 生成报告...")
    md_text = compose_report(
        date_str=date_str,
        is_morning=is_morning,
        indices=indices,
        industry_up=industry_up,
        industry_down=industry_down,
        concept_up=concept_up,
        stocks_up=stocks_up,
        stocks_down=stocks_down,
        breadth=breadth,
        kline_data=kline_data,
        news=news,
        chart_files=chart_files,
    )

    md_path = outdir / f"{base}.md"
    md_path.write_text(md_text, encoding="utf-8")
    print(f"   ✅ Markdown: {md_path}")

    pdf_path = outdir / f"{base}.pdf"
    try:
        make_simple_pdf(md_text, pdf_path)
        print(f"   ✅ PDF (basic): {pdf_path}")
    except Exception as e:
        print(f"   ⚠️  PDF 失败: {e}")
        pdf_path = None

    # == Summary ==

    print()
    print(f"{'='*60}")
    print(f" ✅ A股{mode_cn} 生成完毕！")
    print(f"{'='*60}")
    print(f" 📄 Markdown : {md_path}")
    if pdf_path:
        print(f" 📄 PDF      : {pdf_path}")
    for label, fname in chart_files.items():
        print(f" 📊 图表({label:8s}): {outdir / fname}")
    print(f"{'='*60}")
    print()
    print(md_path)
    if pdf_path:
        print(pdf_path)


if __name__ == "__main__":
    main()
