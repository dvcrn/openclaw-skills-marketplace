#!/usr/bin/env python3
"""
Mapulse — 对话查询引擎 (组件3)
自然语言问答韩国股市

支持查询:
  "삼성 오늘 어때?" / "삼성今天怎么样?"
  "왜 빠졌어?" / "为什么跌了?"
  "외국인 뭐 사?" / "外资在买什么?"
  "코스피 전망" / "KOSPI怎么看?"
  "내 포트폴리오" / "我的组合分析"
  "비교 삼성 SK" / "对比三星和SK"

用法:
  python3 chat_query.py "삼성 오늘 어때?"
  python3 chat_query.py "KOSPI 왜 빠졌어?"
  python3 chat_query.py demo
"""

import sys
import os
import re
import json
import time
import datetime

sys.path.insert(0, os.path.dirname(__file__))

from fetch_briefing import (
    find_trading_date, get_stock, fetch_all,
    STOCK_NAMES, INDEX_ETFS, DEFAULT_WATCHLIST, fmt_arrow
)


# ─── 종목 매칭 ───

# 한글이름 → 티커 역매핑
NAME_TO_TICKER = {v: k for k, v in STOCK_NAMES.items()}
# 별명/약칭
ALIASES = {
    "삼성": "005930", "삼전": "005930", "samsung": "005930",
    "하이닉스": "000660", "sk하이닉스": "000660", "skhynix": "000660",
    "네이버": "035420", "naver": "035420",
    "카카오": "035720", "kakao": "035720",
    "lg에너지": "373220", "엘지에너지": "373220",
    "셀트리온": "068270",
    "lg화학": "051910", "엘지화학": "051910",
    "삼성sdi": "006400", "sdi": "006400",
    "현대차": "005380", "현대자동차": "005380", "hyundai": "005380",
    "기아": "000270", "kia": "000270",
    "sk이노": "096770", "sk이노베이션": "096770",
    "두산에너": "034020", "두산에너빌리티": "034020",
    "포스코인터": "003670", "포스코": "003670",
    "한전": "015760", "한국전력": "015760",
    "엔씨": "036570", "엔씨소프트": "036570", "ncsoft": "036570",
    "하이브": "352820", "hybe": "352820",
    "코스피": "KOSPI", "kospi": "KOSPI",
    "코스닥": "KOSDAQ", "kosdaq": "KOSDAQ",
}


def resolve_ticker(text):
    """텍스트에서 종목 코드 추출"""
    t = text.lower().strip()

    # 직접 티커
    if re.match(r'^\d{6}$', t):
        return t

    # 별명
    for alias, ticker in ALIASES.items():
        if alias in t:
            return ticker

    # 정식 이름
    for name, ticker in NAME_TO_TICKER.items():
        if name.lower() in t:
            return ticker

    return None


def resolve_multiple_tickers(text):
    """텍스트에서 여러 종목 추출"""
    tickers = []
    t = text.lower()
    for alias, ticker in ALIASES.items():
        if alias in t and ticker not in tickers and ticker not in ("KOSPI", "KOSDAQ"):
            tickers.append(ticker)
    return tickers


# ─── 의도 분류 ───

class Intent:
    STOCK_PRICE = "stock_price"       # 개별 종목 조회
    WHY_DROP = "why_drop"             # 왜 빠졌어
    WHY_RISE = "why_rise"             # 왜 올랐어
    MARKET_OVERVIEW = "market_overview"  # 시장 전체
    FOREIGN_FLOW = "foreign_flow"     # 외국인 동향
    COMPARE = "compare"               # 종목 비교
    SECTOR = "sector"                 # 섹터 분석
    OUTLOOK = "outlook"               # 전망
    UNKNOWN = "unknown"


def classify_intent(text):
    """의도 분류"""
    t = text.lower()

    if any(w in t for w in ["왜 빠", "왜 떨어", "왜 하락", "为什么跌", "why drop", "why down", "why fall"]):
        return Intent.WHY_DROP
    if any(w in t for w in ["왜 올", "왜 상승", "为什么涨", "why up", "why rise"]):
        return Intent.WHY_RISE
    if any(w in t for w in ["비교", "对比", "compare", "vs"]):
        return Intent.COMPARE
    if any(w in t for w in ["외국인", "外资", "foreign"]):
        return Intent.FOREIGN_FLOW
    if any(w in t for w in ["전망", "outlook", "怎么看", "내일", "tomorrow"]):
        return Intent.OUTLOOK
    if any(w in t for w in ["섹터", "sector", "板块", "업종"]):
        return Intent.SECTOR
    if any(w in t for w in ["시장", "코스피", "코스닥", "kospi", "kosdaq", "市场", "시황"]):
        return Intent.MARKET_OVERVIEW

    # 默认: 如果提到了股票名 → 个股查询
    ticker = resolve_ticker(t)
    if ticker and ticker not in ("KOSPI", "KOSDAQ"):
        return Intent.STOCK_PRICE

    return Intent.UNKNOWN


# ─── 응답 생성 ───

def handle_stock_price(ticker, date_str):
    """개별 종목 조회"""
    data = get_stock(ticker, date_str)
    if not data:
        return f"❌ {ticker} 데이터를 가져올 수 없습니다."

    name = STOCK_NAMES.get(ticker, ticker)
    arrow = fmt_arrow(data["change_pct"])

    return (
        f"{arrow} *{name} ({ticker})*\n\n"
        f"📊 종가: ₩{data['close']:,}\n"
        f"📈 변동: {data['change_pct']:+.1f}%\n"
        f"📦 거래량: {data['volume']:,}\n"
        f"📅 {date_str}"
    )


def handle_why_move(ticker, date_str, direction="drop"):
    """왜 올랐어/빠졌어"""
    data = get_stock(ticker, date_str)
    if not data:
        return f"❌ 데이터를 가져올 수 없습니다."

    name = STOCK_NAMES.get(ticker, ticker)
    pct = data["change_pct"]

    # 섹터 분석
    from crash_alert import CRASH_PATTERNS
    sector = "default"
    for sec_name, sec_info in CRASH_PATTERNS.items():
        if ticker in sec_info["tickers"]:
            sector = sec_name
            break

    # 동종 종목 체크
    peers = []
    sec_tickers = CRASH_PATTERNS.get(sector, {}).get("tickers", [])
    for peer in sec_tickers:
        if peer != ticker:
            p = get_stock(peer, date_str)
            if p:
                peers.append(p)

    # 시장 상태
    idx = get_stock(INDEX_ETFS["KOSPI"]["ticker"], date_str)
    market_status = ""
    if idx:
        if idx["change_pct"] < -1:
            market_status = "KOSPI 전체 약세 (시장 전반 리스크오프)"
        elif idx["change_pct"] > 1:
            market_status = "KOSPI 전체 강세 (시장 전반 리스크온)"

    # 구성
    lines = [
        f"🧠 *{name} 분석*\n",
        f"📊 오늘: ₩{data['close']:,} ({pct:+.1f}%)",
        f"📦 거래량: {data['volume']:,}\n",
        f"*분석:*",
    ]

    if abs(pct) < 1:
        lines.append(f"• 소폭 변동 — 특별한 이슈 감지되지 않음")
    elif pct < -3:
        lines.append(f"• {'급락' if pct < -5 else '하락'} 수준 — 주의 필요")
    elif pct > 3:
        lines.append(f"• {'급등' if pct > 5 else '상승'} — 모멘텀 주의")

    if market_status:
        lines.append(f"• {market_status}")

    if peers:
        peer_moves = [f"{STOCK_NAMES.get(p['ticker'], p['ticker'])} {p['change_pct']:+.1f}%"
                      for p in peers]
        same_dir = sum(1 for p in peers if (p["change_pct"] < 0) == (pct < 0))
        if same_dir > 0:
            lines.append(f"• {sector.upper()} 섹터 동반 {'하락' if pct < 0 else '상승'}: {', '.join(peer_moves)}")
        else:
            lines.append(f"• 섹터 내 차별화: {', '.join(peer_moves)}")

    lines.append(f"\n📋 DART 공시는 DART API Key 설정 후 자동 매칭됩니다.")
    lines.append(f"⚠️ 정보 제공 목적이며 투자 조언이 아닙니다.")

    return "\n".join(lines)


def handle_market_overview(date_str):
    """시장 전체 개요"""
    watchlist = [t.strip() for t in DEFAULT_WATCHLIST.split(",")]
    data = fetch_all(date_str, watchlist)

    lines = [f"📊 *한국 증시 현황 — {date_str}*\n"]

    # 지수
    for name, d in data["indices"].items():
        a = fmt_arrow(d["change_pct"])
        lines.append(f"{a} {name}: {d['close']:,} ({d['change_pct']:+.1f}%)")

    # TOP 상승/하락
    lines.append(f"\n*상승 TOP 3:*")
    for d in data["gainers"][:3]:
        lines.append(f"🟢 {d['name']} {d['change_pct']:+.1f}%")

    lines.append(f"\n*하락 TOP 3:*")
    for d in data["losers"][:3]:
        lines.append(f"🔴 {d['name']} {d['change_pct']:+.1f}%")

    return "\n".join(lines)


def handle_compare(tickers, date_str):
    """종목 비교"""
    if len(tickers) < 2:
        return "❌ 비교하려면 2개 이상의 종목이 필요합니다."

    lines = [f"📊 *종목 비교 — {date_str}*\n"]
    for ticker in tickers[:5]:
        data = get_stock(ticker, date_str)
        if data:
            name = STOCK_NAMES.get(ticker, ticker)
            a = fmt_arrow(data["change_pct"])
            lines.append(
                f"{a} {name}: ₩{data['close']:,} ({data['change_pct']:+.1f}%) "
                f"Vol: {data['volume']:,}"
            )
    return "\n".join(lines)


def handle_outlook(date_str):
    """전망"""
    idx = get_stock(INDEX_ETFS["KOSPI"]["ticker"], date_str)
    lines = [f"🔮 *시장 전망 판단 요소*\n"]

    if idx:
        if idx["change_pct"] < -2:
            lines.append(f"📉 KOSPI 2%+ 하락 — 단기 약세 신호")
            lines.append(f"• 추가 하락 시 기술적 지지선 확인 필요")
            lines.append(f"• 외국인 순매도 지속 여부가 핵심")
        elif idx["change_pct"] > 2:
            lines.append(f"📈 KOSPI 2%+ 상승 — 단기 강세 신호")
            lines.append(f"• 거래량 동반 상승인지 확인 필요")
        else:
            lines.append(f"➡️ KOSPI 보합권 — 방향성 탐색 중")

    lines.extend([
        f"\n*주요 변수:*",
        f"• 미국 CPI/금리 결정",
        f"• 국제 유가 동향",
        f"• 외국인 투자 흐름",
        f"• 중국 경기 지표",
        f"\n⚠️ 시장 전망은 참고용이며 투자 판단의 근거가 될 수 없습니다.",
    ])
    return "\n".join(lines)


# ─── 메인 라우터 ───

def process_query(text, date_str=None):
    """자연어 질의 처리"""
    date_str = date_str or find_trading_date()
    intent = classify_intent(text)
    ticker = resolve_ticker(text)

    if intent == Intent.STOCK_PRICE and ticker:
        return handle_stock_price(ticker, date_str)

    elif intent == Intent.WHY_DROP:
        t = ticker or "005930"  # 기본: 삼성
        return handle_why_move(t, date_str, "drop")

    elif intent == Intent.WHY_RISE:
        t = ticker or "005930"
        return handle_why_move(t, date_str, "rise")

    elif intent == Intent.MARKET_OVERVIEW:
        return handle_market_overview(date_str)

    elif intent == Intent.COMPARE:
        tickers = resolve_multiple_tickers(text)
        if len(tickers) >= 2:
            return handle_compare(tickers, date_str)
        return "❌ 비교할 종목을 2개 이상 언급해주세요. 예: 비교 삼성 SK하이닉스"

    elif intent == Intent.OUTLOOK:
        return handle_outlook(date_str)

    elif intent == Intent.FOREIGN_FLOW:
        return ("📊 *외국인 매매 동향*\n\n"
                "현재 외국인 실시간 데이터는 KRX API 접속 제한으로 일시 불가합니다.\n"
                "DART API Key 설정 후 외국인 지분 변동 공시 자동 추적이 가능합니다.")

    else:
        if ticker:
            return handle_stock_price(ticker, date_str)
        return ("❓ 질문을 이해하지 못했습니다.\n\n"
                "*가능한 질의:*\n"
                "• 종목 조회: \"삼성 오늘 어때?\"\n"
                "• 원인 분석: \"삼성 왜 빠졌어?\"\n"
                "• 시장 현황: \"코스피 시황\"\n"
                "• 종목 비교: \"비교 삼성 SK하이닉스\"\n"
                "• 전망: \"코스피 전망\"")


# ─── 데모 ───

def demo():
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║  💬 Mapulse — 대화 쿼리 엔진    ║")
    print("  ║  자연어로 한국 주식 정보 조회               ║")
    print("  ╚══════════════════════════════════════════╝")

    date_str = find_trading_date()
    print(f"\n  📅 거래일: {date_str}")

    queries = [
        "삼성 오늘 어때?",
        "SK이노 왜 빠졌어?",
        "코스피 시황",
        "비교 삼성 하이닉스 LG에너지",
        "코스피 전망",
        "엔씨소프트 왜 올랐어?",
    ]

    for q in queries:
        print(f"\n{'━' * 50}")
        print(f"  💬 \"{q}\"")
        print(f"{'━' * 50}\n")
        result = process_query(q, date_str)
        for line in result.split("\n"):
            print(f"  {line}")

    print(f"\n{'━' * 50}")
    print("  ✅ 대화 쿼리 엔진 데모 완료")
    print(f"{'━' * 50}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "demo":
        demo()
    else:
        query = " ".join(sys.argv[1:])
        print(process_query(query))
