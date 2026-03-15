#!/usr/bin/env python3
"""
ClawSavings Wallet — track gift cards, coupons, and vouchers.

Usage:
  wallet.py --list                     # All active cards
  wallet.py --list --all               # Including used/expired
  wallet.py --add                      # Interactive add
  wallet.py --use <id> [--amount N]    # Mark used / deduct balance
  wallet.py --balance <id>             # Show card details
  wallet.py --expired                  # List expired / fully used
  wallet.py --summary                  # Total value by merchant/type
"""

import argparse
import json
import os
import sys
import uuid
from datetime import date, datetime

WALLET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wallet.json")

# ── Schema ────────────────────────────────────────────────────────────────────

CARD_TYPES   = ["gift_card", "coupon", "voucher"]
SOURCES      = ["bought", "received", "wonder", "htzone_pro2", "htzone_club",
                "carrefour_club", "work_benefit", "other"]
STATUSES     = ["active", "partial", "used", "expired"]

def empty_card():
    return {
        "id":            str(uuid.uuid4())[:8],
        "type":          "gift_card",     # gift_card | coupon | voucher
        "merchant":      "",              # Hebrew store name
        "merchant_en":   "",              # English store name
        "face_value":    None,            # original card value (₪)
        "balance":       None,            # remaining balance (₪); null = unknown
        "code":          None,            # card/coupon code
        "pin":           None,            # optional PIN
        "expiry":        None,            # "YYYY-MM-DD" or null
        "source":        "bought",        # how we got it
        "source_card":   None,            # which discount card was used to buy it
        "price_paid":    None,            # what we paid (null if gifted)
        "effective_pct": None,            # discount % vs face value
        "status":        "active",        # active | partial | used | expired
        "notes":         "",
        "added":         str(date.today()),
        "last_used":     None,
    }

# ── File I/O ──────────────────────────────────────────────────────────────────

def load_wallet():
    if not os.path.exists(WALLET_PATH):
        return {"version": "1.0", "last_updated": str(date.today()), "cards": []}
    with open(WALLET_PATH) as f:
        return json.load(f)

def save_wallet(w):
    w["last_updated"] = str(date.today())
    with open(WALLET_PATH, "w") as f:
        json.dump(w, f, ensure_ascii=False, indent=2)

# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt_ils(v):
    return f"₪{v:,.0f}" if v is not None else "—"

def is_expired(card):
    if card.get("expiry"):
        return date.fromisoformat(card["expiry"]) < date.today()
    return False

def effective_status(card):
    if card["status"] in ("used", "expired"):
        return card["status"]
    if is_expired(card):
        return "expired"
    return card["status"]

def compute_pct(face, paid):
    if face and paid and face > 0:
        return round((face - paid) / face * 100, 1)
    return None

def find_card(wallet, id_prefix):
    matches = [c for c in wallet["cards"] if c["id"].startswith(id_prefix)]
    if not matches:
        print(f"❌ No card found with id starting with '{id_prefix}'")
        sys.exit(1)
    if len(matches) > 1:
        print(f"❌ Ambiguous id '{id_prefix}' — matches: {[c['id'] for c in matches]}")
        sys.exit(1)
    return matches[0]

# ── Display ───────────────────────────────────────────────────────────────────

STATUS_EMOJI = {"active": "🟢", "partial": "🟡", "used": "⚫", "expired": "🔴"}

def print_card(c, verbose=False):
    st = effective_status(c)
    emoji = STATUS_EMOJI.get(st, "⚪")
    merchant = c.get("merchant") or c.get("merchant_en") or "?"
    bal = c.get("balance")
    face = c.get("face_value")
    paid = c.get("price_paid")
    pct = c.get("effective_pct")
    expiry = c.get("expiry") or "no expiry"

    balance_str = fmt_ils(bal) if bal is not None else (fmt_ils(face) if face else "unknown")

    if pct:
        savings = f"  💰 bought for {fmt_ils(paid)} ({pct}% off)"
    elif paid:
        savings = f"  paid {fmt_ils(paid)}"
    else:
        savings = ""

    print(f"  {emoji} [{c['id']}] {merchant} — {balance_str} remaining  ({c['type']}){savings}")
    if verbose:
        if c.get("code"):  print(f"       code:   {c['code']}")
        if c.get("pin"):   print(f"       PIN:    {c['pin']}")
        print(f"       expiry: {expiry}")
        if c.get("notes"): print(f"       notes:  {c['notes']}")
        print(f"       source: {c.get('source','?')}  added: {c.get('added','?')}")

# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_list(args):
    wallet = load_wallet()
    cards = wallet["cards"]
    if not args.all:
        cards = [c for c in cards if effective_status(c) not in ("used", "expired")]

    if not cards:
        print("👜 Wallet is empty." if args.all else "👜 No active cards.")
        return

    # Group by merchant
    by_merchant = {}
    for c in cards:
        m = c.get("merchant") or c.get("merchant_en") or "?"
        by_merchant.setdefault(m, []).append(c)

    total_balance = sum(
        c.get("balance") or c.get("face_value") or 0
        for c in cards if effective_status(c) in ("active", "partial")
    )

    print(f"👜 Wallet — {len(cards)} cards  (total value: {fmt_ils(total_balance)})\n")
    for merchant, group in sorted(by_merchant.items()):
        for c in group:
            print_card(c, verbose=args.verbose)


def cmd_balance(args):
    wallet = load_wallet()
    c = find_card(wallet, args.id)
    print_card(c, verbose=True)


def cmd_add(args):
    wallet = load_wallet()
    card = empty_card()

    print("➕ Add new card/coupon to wallet")
    print("   (press Enter to skip optional fields)\n")

    # Type
    print(f"   Type [{'/'.join(CARD_TYPES)}]: ", end="")
    t = input().strip() or "gift_card"
    card["type"] = t if t in CARD_TYPES else "gift_card"

    # Merchant
    print("   Merchant name (Hebrew): ", end="")
    card["merchant"] = input().strip()
    print("   Merchant name (English, optional): ", end="")
    card["merchant_en"] = input().strip()

    # Face value
    print("   Face value (₪): ", end="")
    fv = input().strip()
    if fv:
        card["face_value"] = float(fv)
        card["balance"] = float(fv)  # assume full balance when new

    # Code
    print("   Code (optional): ", end="")
    code = input().strip()
    if code: card["code"] = code

    # PIN
    print("   PIN (optional): ", end="")
    pin = input().strip()
    if pin: card["pin"] = pin

    # Expiry
    print("   Expiry date YYYY-MM-DD (optional): ", end="")
    exp = input().strip()
    if exp: card["expiry"] = exp

    # Source
    print(f"   Source [{'/'.join(SOURCES)}] (default: bought): ", end="")
    src = input().strip() or "bought"
    card["source"] = src if src in SOURCES else "other"

    # What we paid
    print("   Price paid (₪, optional): ", end="")
    paid = input().strip()
    if paid:
        card["price_paid"] = float(paid)
        if card["face_value"]:
            card["effective_pct"] = compute_pct(card["face_value"], card["price_paid"])

    # Source card
    print("   Which discount card used to buy? (e.g. poalim_wonder, htzone_pro2, optional): ", end="")
    sc = input().strip()
    if sc: card["source_card"] = sc

    # Notes
    print("   Notes (optional): ", end="")
    note = input().strip()
    if note: card["notes"] = note

    wallet["cards"].append(card)
    save_wallet(wallet)

    print(f"\n✅ Added [{card['id']}] {card['merchant'] or card['merchant_en']}")
    print_card(card, verbose=True)


def cmd_use(args):
    wallet = load_wallet()
    card = find_card(wallet, args.id)
    merchant = card.get("merchant") or card.get("merchant_en") or "?"

    if args.amount:
        # Deduct specific amount
        current = card.get("balance") or card.get("face_value")
        if current is None:
            print(f"⚠️  No balance set for {merchant} — setting balance after use")
            card["balance"] = 0
        else:
            new_bal = current - args.amount
            if new_bal < 0:
                print(f"⚠️  Amount ({fmt_ils(args.amount)}) exceeds balance ({fmt_ils(current)})")
                sys.exit(1)
            card["balance"] = round(new_bal, 2)
            card["status"] = "used" if card["balance"] == 0 else "partial"
            print(f"✅ {merchant}: {fmt_ils(current)} → {fmt_ils(card['balance'])} remaining")
    else:
        # Mark fully used
        card["status"] = "used"
        card["balance"] = 0
        print(f"✅ {merchant} [{card['id']}] marked as fully used")

    card["last_used"] = str(date.today())
    save_wallet(wallet)


def cmd_expired(args):
    wallet = load_wallet()
    expired = [c for c in wallet["cards"] if effective_status(c) in ("used", "expired")]
    if not expired:
        print("✅ No expired or used cards.")
        return
    print(f"🗑  {len(expired)} used/expired cards:\n")
    for c in expired:
        print_card(c, verbose=False)


def cmd_summary(args):
    wallet = load_wallet()
    active = [c for c in wallet["cards"] if effective_status(c) in ("active", "partial")]

    if not active:
        print("👜 No active cards.")
        return

    total = sum(c.get("balance") or c.get("face_value") or 0 for c in active)
    total_paid = sum(c.get("price_paid") or 0 for c in active if c.get("price_paid"))
    total_face = sum(c.get("face_value") or 0 for c in active if c.get("face_value"))
    saved = total_face - total_paid if total_face and total_paid else 0

    print(f"👜 Wallet Summary — {len(active)} active cards")
    print(f"   Total remaining value: {fmt_ils(total)}")
    if saved > 0:
        print(f"   Total saved buying below face: {fmt_ils(saved)}\n")
    else:
        print()

    # By merchant
    by_merchant = {}
    for c in active:
        m = c.get("merchant") or c.get("merchant_en") or "?"
        by_merchant.setdefault(m, []).append(c)

    for merchant, group in sorted(by_merchant.items()):
        val = sum(c.get("balance") or c.get("face_value") or 0 for c in group)
        count = len(group)
        print(f"   {merchant}: {fmt_ils(val)}  ({count} card{'s' if count>1 else ''})")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ClawSavings Wallet")
    sub = parser.add_subparsers(dest="cmd")

    # list
    p_list = sub.add_parser("list", help="List cards")
    p_list.add_argument("--all", action="store_true", help="Include used/expired")
    p_list.add_argument("--verbose", "-v", action="store_true")

    # add
    sub.add_parser("add", help="Add a card interactively")

    # use
    p_use = sub.add_parser("use", help="Mark used or deduct balance")
    p_use.add_argument("id", help="Card ID prefix")
    p_use.add_argument("--amount", type=float, help="Amount to deduct (₪)")

    # balance
    p_bal = sub.add_parser("balance", help="Show card details")
    p_bal.add_argument("id", help="Card ID prefix")

    # expired
    sub.add_parser("expired", help="List used/expired cards")

    # summary
    sub.add_parser("summary", help="Value summary by merchant")

    args = parser.parse_args()

    dispatch = {
        "list":    cmd_list,
        "add":     cmd_add,
        "use":     cmd_use,
        "balance": cmd_balance,
        "expired": cmd_expired,
        "summary": cmd_summary,
    }

    if args.cmd in dispatch:
        dispatch[args.cmd](args)
    else:
        # Default: list active
        args.cmd = "list"
        args.all = False
        args.verbose = False
        cmd_list(args)


if __name__ == "__main__":
    main()
