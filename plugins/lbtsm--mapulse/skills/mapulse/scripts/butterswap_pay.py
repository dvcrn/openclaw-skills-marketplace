#!/usr/bin/env python3
"""
Mapulse — 60小时免费 + 按次计费 + ButterSwap充值
免费60小时 → 充值最低$5 → $0.06/次
"""

import json
import time
import hashlib
import os
import sys

COST_PER_CALL = 0.06  # USD
FREE_TRIAL_HOURS = 60
FREE_TRIAL_CALLS = 50  # 免费期内最多50次
MIN_TOPUP = 5.0  # 最低充值$5

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
SERVICE_WALLET = os.environ.get("BUTTERSWAP_WALLET", "0xYOUR_WALLET")
API_BASE = "https://bs-router-v3.chainservice.io"


# ─── 数据管理 ───

def _load():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def _save(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _get_user(user_id):
    data = _load()
    if user_id not in data:
        data[user_id] = {
            "trial_start": time.time(),
            "trial_expires": time.time() + FREE_TRIAL_HOURS * 3600,
            "balance": 0.0,
            "total_spent": 0.0,
            "total_calls": 0,
            "free_calls": 0,
            "history": []
        }
        _save(data)
    return data, data[user_id]


# ─── 核心: 扣费判断 ───

def charge(user_id, query_type="query"):
    """
    扣费逻辑:
    1. 60小时内 → 免费
    2. 60小时后 + 余额够 → 扣$0.06
    3. 60小时后 + 余额不够 → 提示充值(最低$5)
    """
    data, user = _get_user(user_id)
    now = time.time()

    # 免费期内 + 未超50次
    if now < user["trial_expires"] and user["free_calls"] < FREE_TRIAL_CALLS:
        remaining_hours = (user["trial_expires"] - now) / 3600
        remaining_calls = FREE_TRIAL_CALLS - user["free_calls"] - 1
        user["free_calls"] += 1
        user["total_calls"] += 1
        data[user_id] = user
        _save(data)
        return {
            "status": "free_trial",
            "charged": 0,
            "balance": user["balance"],
            "trial_remaining_hours": round(remaining_hours, 1),
            "trial_remaining_calls": remaining_calls,
            "free_calls": user["free_calls"]
        }

    # 免费期已过 → 检查余额
    if user["balance"] >= COST_PER_CALL:
        user["balance"] = round(user["balance"] - COST_PER_CALL, 4)
        user["total_spent"] = round(user["total_spent"] + COST_PER_CALL, 4)
        user["total_calls"] += 1
        user["history"].append({
            "type": "charge",
            "query": query_type,
            "amount": -COST_PER_CALL,
            "balance_after": user["balance"],
            "time": now
        })
        data[user_id] = user
        _save(data)
        return {
            "status": "charged",
            "charged": COST_PER_CALL,
            "balance": user["balance"],
            "remaining_calls": int(user["balance"] / COST_PER_CALL)
        }

    # 余额不足
    return {
        "status": "insufficient",
        "charged": 0,
        "balance": user["balance"],
        "needed": round(COST_PER_CALL - user["balance"], 4),
        "min_topup": MIN_TOPUP
    }


def top_up(user_id, amount, tx_hash="manual"):
    """充值 — 最低$5"""
    if amount < MIN_TOPUP:
        return {"error": f"최소 충전 금액: ${MIN_TOPUP} USDC", "min_topup": MIN_TOPUP}

    data, user = _get_user(user_id)
    user["balance"] = round(user["balance"] + amount, 4)
    user["history"].append({
        "type": "topup",
        "amount": amount,
        "tx_hash": tx_hash,
        "balance_after": user["balance"],
        "time": time.time()
    })
    data[user_id] = user
    _save(data)
    return {
        "status": "success",
        "balance": user["balance"],
        "calls_available": int(user["balance"] / COST_PER_CALL)
    }


def get_status(user_id):
    """用户状态"""
    data, user = _get_user(user_id)
    now = time.time()
    in_trial = now < user["trial_expires"]

    lines = []
    if in_trial and user["free_calls"] < FREE_TRIAL_CALLS:
        remaining = (user["trial_expires"] - now) / 3600
        remaining_calls = FREE_TRIAL_CALLS - user["free_calls"]
        lines.append(f"🆓 *무료 체험 중*")
        lines.append(f"⏰ 남은 시간: {remaining:.1f}시간")
        lines.append(f"🎫 남은 무료: {remaining_calls}/{FREE_TRIAL_CALLS}회")
        lines.append(f"📊 사용: {user['free_calls']}회")
    else:
        lines.append(f"💰 *유료 이용 중*")
        lines.append(f"💳 잔액: ${user['balance']:.2f} USDC")
        lines.append(f"📊 남은 조회: {int(user['balance'] / COST_PER_CALL)}회")
        lines.append(f"📊 총 사용: ${user['total_spent']:.2f}")

    lines.append(f"\n📈 총 조회: {user['total_calls']}회")
    lines.append(f"💰 단가: ${COST_PER_CALL}/회")
    return "\n".join(lines)


def generate_topup_link(user_id, amount):
    """ButterSwap 충전"""
    if amount < MIN_TOPUP:
        return {"error": f"최소 충전: ${MIN_TOPUP}"}

    data, user = _get_user(user_id)
    order_id = hashlib.sha256(f"{user_id}:{amount}:{time.time()}".encode()).hexdigest()[:12]

    msg = (
        f"💰 *Mapulse 충전*\n\n"
        f"충전 금액: ${amount:.2f} USDC\n"
        f"현재 잔액: ${user['balance']:.2f}\n"
        f"충전 후 잔액: ${user['balance'] + amount:.2f}\n"
        f"약 {int((user['balance'] + amount) / COST_PER_CALL)}회 조회 가능\n\n"
        f"주문번호: MPL-{order_id}\n"
    )

    buttons = [
        [{"text": "⚡ ButterSwap 크로스체인 결제", "callback": f"topup_{order_id}"}],
        [{"text": "💎 Telegram Wallet (TON)", "callback": f"topup_tg_{order_id}"}],
        [{"text": "🔗 지갑 직접 결제 (USDC)", "callback": f"topup_direct_{order_id}"}],
        [{"text": "❌ 취소", "callback": "topup_cancel"}],
    ]

    return {"text": msg, "buttons": buttons, "order_id": f"MPL-{order_id}"}


def format_trial_expired(user_id):
    """免费期满提示"""
    data, user = _get_user(user_id)
    in_trial = time.time() < user["trial_expires"]
    reason = "50회 무료 사용을 모두 소진" if user["free_calls"] >= FREE_TRIAL_CALLS else "60시간 체험 기간 만료"
    return (
        f"⏰ *무료 체험이 종료되었습니다.*\n\n"
        f"사유: {reason}\n"
        f"{user['free_calls']}회 사용하셨습니다.\n"
        f"계속 이용하려면 충전이 필요합니다.\n\n"
        f"최소 충전: ${MIN_TOPUP} USDC (≈{int(MIN_TOPUP/COST_PER_CALL)}회)\n"
        f"단가: ${COST_PER_CALL}/회\n\n"
        f"→ '충전 5' 입력 시 ButterSwap으로 간편 충전\n"
        f"→ 30+체인, 어떤 토큰이든 결제 가능"
    )


def format_insufficient(user_id):
    """잔액 부족"""
    data, user = _get_user(user_id)
    return (
        f"🔴 *잔액 부족*\n\n"
        f"현재 잔액: ${user['balance']:.2f}\n"
        f"필요 금액: ${COST_PER_CALL}\n\n"
        f"→ '충전 5' 입력 (최소 ${MIN_TOPUP})\n"
        f"→ ButterSwap 30+체인 결제 지원"
    )


# ─── 데모 ───

def demo():
    print()
    print("  ╔══════════════════════════════════════════╗")
    print("  ║  💰 Mapulse 결제 모델                  ║")
    print("  ║  60시간 무료 → 충전(최소$5) → $0.06/회     ║")
    print("  ╚══════════════════════════════════════════╝")

    user = "demo_user"
    # 清空
    data = _load()
    data.pop(user, None)
    _save(data)

    # Phase 1: 免费期
    print(f"\n{'━' * 50}")
    print("  Phase 1: 60시간 무료 체험")
    print(f"{'━' * 50}\n")

    for i in range(5):
        r = charge(user, "stock_query")
        print(f"  [{i+1}] 조회: 🆓 무료 (남은: {r['trial_remaining_calls']}회 / {r['trial_remaining_hours']}시간)")

    print(f"\n{get_status(user)}")

    # Phase 2: 模拟免费期过期
    print(f"\n{'━' * 50}")
    print("  Phase 2: 50회 소진 → 무료 종료")
    print(f"{'━' * 50}\n")

    data, u = _get_user(user)
    u["free_calls"] = 50  # 模拟用完50次
    data[user] = u
    _save(data)

    r = charge(user, "ai_analysis")
    print(f"  AI 분석 요청: {r['status']}")
    print(f"\n{format_trial_expired(user)}")

    # Phase 3: 尝试充$1 → 被拒
    print(f"\n{'━' * 50}")
    print("  Phase 3: 충전 $1 시도 → 최소 $5")
    print(f"{'━' * 50}\n")

    r = top_up(user, 1.0)
    print(f"  충전 $1: ❌ {r.get('error')}")

    # Phase 4: 充值$5
    print(f"\n{'━' * 50}")
    print("  Phase 4: 충전 $5 → ButterSwap")
    print(f"{'━' * 50}\n")

    link = generate_topup_link(user, 5.0)
    print(link["text"])
    for row in link["buttons"]:
        for btn in row:
            print(f"  [{btn['text']}]")

    print(f"\n  ✅ ButterSwap 결제 완료")
    r = top_up(user, 5.0, "0xbutter_demo_tx")
    print(f"  잔액: ${r['balance']:.2f} (≈{r['calls_available']}회)")

    # Phase 5: 付费调用
    print(f"\n{'━' * 50}")
    print("  Phase 5: 유료 조회")
    print(f"{'━' * 50}\n")

    for i, qt in enumerate(["ai_analysis", "stock_query", "dart", "compare", "crash_alert"]):
        r = charge(user, qt)
        print(f"  [{i+1}] {qt}: 💰 ${r['charged']:.2f} → 잔액 ${r['balance']:.2f} ({r['remaining_calls']}회 남음)")

    # Phase 6: 状态
    print(f"\n{'━' * 50}")
    print("  Phase 6: 상태 확인")
    print(f"{'━' * 50}\n")
    print(get_status(user))

    print(f"\n  ╔═══════════════════════════════════╗")
    print(f"  ║  요약                              ║")
    print(f"  ╠═══════════════════════════════════╣")
    print(f"  ║  무료: 60시간 / 50회 (먼저 도달 시) ║")
    print(f"  ║  단가: ${COST_PER_CALL}/회 (Claude×2)  ║")
    print(f"  ║  최소 충전: ${MIN_TOPUP} USDC          ║")
    print(f"  ║  충전: ButterSwap 30+체인          ║")
    print(f"  ╚═══════════════════════════════════╝\n")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "demo":
        demo()
    elif sys.argv[1] == "status":
        uid = sys.argv[2] if len(sys.argv) > 2 else "demo"
        print(get_status(uid))
    elif sys.argv[1] == "topup":
        uid = sys.argv[2] if len(sys.argv) > 2 else "demo"
        amt = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
        link = generate_topup_link(uid, amt)
        print(link["text"])
    else:
        print(__doc__)
