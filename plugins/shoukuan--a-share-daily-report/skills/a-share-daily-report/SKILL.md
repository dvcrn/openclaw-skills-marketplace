---
name: a-share-daily-report
description: "生成专业级 A股早报/晚报，包含大盘指数行情、市场情绪、K线走势图、 行业/概念板块排行、个股涨跌榜、主题新闻追踪、综合分析， 输出 Markdown + PNG 图表 + PDF。数据源为东方财富公开 API。 Use when asked to create daily A-share reports, market analysis, 或当用户提到 A股/大盘/股市/行情/晚报/早报."
---

# A股早晚报 - 专业行情报告

## Overview

生成包含 **9 大板块** 的 A 股专业日报：

1. **主要指数行情** — 上证/深证/创业板/科创50/北证50/上证50/沪深300/中证500/创业板50
2. **市场情绪** — 涨跌家数、涨停跌停、涨跌比温度计、饼图+柱状图
3. **指数 K 线走势** — 近 30 个交易日蜡烛图 + MA5/MA10/MA20 + 成交量
4. **行业板块表现** — 涨幅/跌幅 Top 10 + 横向对比柱状图
5. **热门概念 Top 10** — 概念板块涨跌排名
6. **个股涨跌排行** — 涨/跌幅各 Top 10
7. **主题追踪** — 新能源、半导体、AI/人工智能、机器人、有色金属、医药生物
8. **今日要闻** — 东方财富首页热点新闻
9. **综合分析** — 趋势、量能、风格分化、市场宽度、技术面(RSI)、板块轮动、后市展望

## Quick Start

```bash
# 晚报（默认），输出到桌面
python3 scripts/generate_report.py \
  --mode evening \
  --date 2026-03-05 \
  --outdir "/Users/yibiao/Desktop/openclaw_doc/财经日报"

# 早报
python3 scripts/generate_report.py --mode morning

# 不生成图表（纯文本环境）
python3 scripts/generate_report.py --no-charts
```

### 产出文件
- `A股晚报-YYYYMMDD.md` — 完整 Markdown 报告
- `A股晚报-YYYYMMDD.pdf` — PDF 版本
- `index_kline.png` — 指数 K 线走势图
- `sector_ranking.png` — 行业板块涨跌排行图
- `market_breadth.png` — 市场情绪全景图

## Dependencies

- **Python 3.10+**（标准库：urllib, json, re, argparse, pathlib, datetime）
- **matplotlib**（可选，用于生成图表；通过 `--no-charts` 跳过）

```bash
pip install matplotlib
```

## Data Sources

所有数据均来自 **东方财富公开 Push API**（无需认证）：

| 数据 | API |
| :--- | :--- |
| 指数行情 | `push2.eastmoney.com/api/qt/ulist.np/get` |
| 行业/概念板块 | `push2.eastmoney.com/api/qt/clist/get` |
| 个股排行 | `push2.eastmoney.com/api/qt/clist/get` |
| 市场宽度 | `push2.eastmoney.com/api/qt/clist/get` (全A股) |
| K 线数据 | `push2his.eastmoney.com/api/qt/stock/kline/get` |
| 新闻 | `finance.eastmoney.com` (HTML 抓取) |

## Workflow

### 1) 生成报告
```
scripts/generate_report.py --mode evening --outdir <dir>
```

### 2) 写入飞书文档
- 早报：`feishu_doc.write` 覆盖写入
- 晚报：`feishu_doc.append` 追加到同一文档

### 3) 发送 PDF + 图表
- `message` 发送 PDF 和 PNG 图表附件

## Notes

- 网络请求全部包含 try/except，单个 API 失败不影响整体报告
- 图表使用系统中文字体（PingFang SC / Songti SC / Heiti TC 等）
- K 线图包含蜡烛图 + 均线 + 成交量，支持多指数对比
- 市场宽度统计包含 涨跌比、涨停/跌停、大涨(>5%)/大跌(>5%) 等指标
- 综合分析包含 RSI(14) 技术指标计算
