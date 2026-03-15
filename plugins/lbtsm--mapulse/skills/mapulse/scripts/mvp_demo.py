#!/usr/bin/env python3
"""
Mapulse MVP — 按次计费完整用户旅程
免费额度 → 用完 → 充值 → 按次扣费
"""

import sys, os, json, time
sys.path.insert(0, os.path.dirname(__file__))

from fetch_briefing import find_trading_date, fetch_all, format_briefing, get_stock, STOCK_NAMES, DEFAULT_WATCHLIST
from butterswap_pay import (
    charge, top_up, get_balance, get_usage_summary,
    generate_topup_link, format_insufficient,
    COST_PER_CALL, FREE_QUOTAS, _load, _save, DATA_DIR
)


def divider(title=""):
    if title:
        print(f"\n{'━' * 50}")
        print(f"  {title}")
        print(f"{'━' * 50}")
    else:
        print(f"{'─' * 50}")


def main():
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║  🇰🇷  Mapulse MVP v2.0          ║")
    print("  ║  按次计费 · 用多少付多少                    ║")
    print("  ║  Powered by ButterSwap                   ║")
    print("  ╚══════════════════════════════════════════╝")

    user_id = "mvp_demo_user"
    date_str = find_trading_date()
    print(f"\n  📅 거래일: {date_str}")
    print(f"  💰 단가: ${COST_PER_CALL}/회 (Claude×2)")

    # 清空demo用户
    data = _load()
    data.pop(user_id, None)
    _save(data)

    # ═══════════════════════════════════════
    # Phase 1: 免费额度 — 每日简报
    # ═══════════════════════════════════════
    divider("Phase 1: 무료 — 매일 시황 (5회/일)")

    r = charge(user_id, "daily_briefing")
    print(f"  ✅ 무료 사용 (남은: {r['remaining_free']}회)")

    watchlist = [t.strip() for t in DEFAULT_WATCHLIST.split(",")]
    print(f"\n  데이터 수집 중...", end="", flush=True)
    briefing_data = fetch_all(date_str, watchlist)
    print(" 완료 ✅\n")
    print(format_briefing(briefing_data))

    # ═══════════════════════════════════════
    # Phase 2: 免费额度 — 개별 종목 조회
    # ═══════════════════════════════════════
    divider("Phase 2: 무료 — 삼성전자 조회 (10회 중)")

    r = charge(user_id, "stock_query")
    samsung = get_stock("005930", date_str)
    if samsung:
        print(f"  ✅ 무료 사용 (남은: {r['remaining_free']}회)\n")
        from chat_query import handle_stock_price
        print(handle_stock_price("005930", date_str))

    # ═══════════════════════════════════════
    # Phase 3: 免费 AI 분석 (3회)
    # ═══════════════════════════════════════
    divider("Phase 3: 무료 — \"SK이노 왜 빠졌어?\" (3회 중)")

    r = charge(user_id, "ai_analysis")
    print(f"  ✅ 무료 사용 (남은: {r['remaining_free']}회)\n")
    from chat_query import handle_why_move
    print(handle_why_move("096770", date_str, "drop"))

    # 消耗剩余免费AI额度
    charge(user_id, "ai_analysis")
    charge(user_id, "ai_analysis")

    # ═══════════════════════════════════════
    # Phase 4: 免费用完 → 잔액 부족
    # ═══════════════════════════════════════
    divider("Phase 4: 무료 소진 → \"삼성 분석해줘\"")

    r = charge(user_id, "ai_analysis")
    print(f"  상태: {r['status']}\n")
    print(format_insufficient(user_id, "ai_analysis"))

    # ═══════════════════════════════════════
    # Phase 5: 충전
    # ═══════════════════════════════════════
    divider("Phase 5: \"충전 5\" → ButterSwap 결제")

    link = generate_topup_link(user_id, 5.0)
    print(f"\n{link['text']}")
    for row in link["buttons"]:
        for btn in row:
            print(f"  [{btn['text']}]")

    print(f"\n  ⏳ Solana USDC → Base USDC (ButterSwap 라우팅)...")
    print(f"  ✅ 결제 확인!")
    new_bal = top_up(user_id, 5.0, "0xbutter_sol2base_demo")
    print(f"  💰 새 잔액: ${new_bal:.2f} (≈{int(new_bal/COST_PER_CALL)}회)")

    # ═══════════════════════════════════════
    # Phase 6: 유료 AI 분석
    # ═══════════════════════════════════════
    divider("Phase 6: 유료 — \"삼성 분석해줘\" ($0.06)")

    r = charge(user_id, "ai_analysis")
    print(f"  💰 ${r['charged']:.2f} 차감 → 잔액 ${r['balance']:.2f}\n")

    print(handle_why_move("005930", date_str, "drop"))

    # ═══════════════════════════════════════
    # Phase 7: 유료 간련 기능들
    # ═══════════════════════════════════════
    divider("Phase 7: 연속 유료 조회")

    queries = [
        ("stock_query", "코스피 시황"),
        ("dart_disclosure", "DART 공시"),
        ("compare", "삼성 vs SK하이닉스 비교"),
    ]
    for qt, desc in queries:
        r = charge(user_id, qt)
        status = f"🆓 무료 (남은: {r.get('remaining_free', 0)})" if r["status"] == "free" else f"💰 ${r['charged']:.2f}"
        print(f"  {desc}: {status} → 잔액 ${r['balance']:.2f}")

    # ═══════════════════════════════════════
    # Phase 8: 사용 내역
    # ═══════════════════════════════════════
    divider("Phase 8: 사용 내역 — \"잔액\"")

    print(f"\n{get_usage_summary(user_id)}")

    # ═══════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║            MVP v2.0 요약                  ║")
    print("  ╠══════════════════════════════════════════╣")
    print("  ║                                          ║")
    print(f"  ║  단가: ${COST_PER_CALL}/회 (Claude×2)       ║")
    print("  ║                                          ║")
    print("  ║  무료 제공:                               ║")
    for qt, q in FREE_QUOTAS.items():
        reset = "매일" if q["reset"] == "daily" else "총"
        print(f"  ║  • {qt}: {q['limit']}회 ({reset})         ║")
    print("  ║                                          ║")
    print("  ║  충전: ButterSwap 30+체인                 ║")
    print("  ║  $1→16회 / $5→83회 / $10→166회           ║")
    print("  ║                                          ║")
    print("  ║  기능:                                    ║")
    print("  ║  📊 매일 시황 브리핑                      ║")
    print("  ║  🔍 종목 조회 + 비교                     ║")
    print("  ║  🧠 AI 분석 (왜 올랐어/빠졌어)            ║")
    print("  ║  🚨 급락 알림 (30초 내 원인 분석)          ║")
    print("  ║  📋 DART 공시                            ║")
    print("  ║  💬 자연어 대화 쿼리                      ║")
    print("  ║                                          ║")
    print("  ╚══════════════════════════════════════════╝")
    print()


if __name__ == "__main__":
    main()
