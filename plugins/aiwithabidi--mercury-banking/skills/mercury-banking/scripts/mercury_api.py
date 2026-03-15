#!/usr/bin/env python3
"""Mercury Banking API integration for OpenClaw agents."""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode

BASE_URL = "https://api.mercury.com/api/v1"


def get_api_key():
    key = os.environ.get("MERCURY_API_KEY")
    if not key:
        print("Error: MERCURY_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(endpoint, params=None):
    url = f"{BASE_URL}{endpoint}"
    if params:
        url += "?" + urlencode({k: v for k, v in params.items() if v is not None})
    req = Request(url, headers={
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; AgxntSix/1.0)",
    })
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"API Error {e.code}: {body}", file=sys.stderr)
        sys.exit(1)


def llm_request(prompt, system="You are a financial analyst."):
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print("Error: OPENROUTER_API_KEY required for AI features", file=sys.stderr)
        sys.exit(1)
    data = json.dumps({
        "model": "anthropic/claude-haiku-4.5",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 2000,
    }).encode()
    req = Request("https://openrouter.ai/api/v1/chat/completions", data=data, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    })
    try:
        with urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            return result["choices"][0]["message"]["content"]
    except HTTPError as e:
        print(f"LLM Error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def cmd_accounts(args):
    data = api_request("/accounts")
    accounts = data.get("accounts", data) if isinstance(data, dict) else data
    if not accounts:
        print("No accounts found.")
        return
    for a in accounts:
        bal = a.get("currentBalance", a.get("availableBalance", "N/A"))
        print(f"  {a.get('name','?')} | ID: {a.get('id','?')} | Balance: ${bal:,.2f}" if isinstance(bal, (int, float)) else f"  {a.get('name','?')} | ID: {a.get('id','?')} | Balance: {bal}")
        print(f"    Type: {a.get('type','?')} | Status: {a.get('status','?')} | Routing: {a.get('routingNumber','?')} | Account#: {a.get('accountNumber','?')}")


def cmd_transactions(args):
    params = {"limit": str(args.limit)}
    if args.start:
        params["start"] = args.start
    if args.end:
        params["end"] = args.end
    if args.status:
        params["status"] = args.status
    if args.search:
        params["search"] = args.search

    data = api_request(f"/account/{args.account_id}/transactions", params)
    txns = data.get("transactions", data) if isinstance(data, dict) else data
    if not txns:
        print("No transactions found.")
        return

    total_in, total_out = 0, 0
    for t in txns:
        amt = t.get("amount", 0)
        direction = "+" if amt > 0 else "-"
        if amt > 0:
            total_in += amt
        else:
            total_out += abs(amt)
        date = t.get("postedAt", t.get("createdAt", "?"))[:10]
        counterparty = t.get("counterpartyName", t.get("bankDescription", "?"))
        status = t.get("status", "?")
        print(f"  {date} | {direction}${abs(amt):,.2f} | {counterparty} | {status}")

    print(f"\n  Total In: ${total_in:,.2f} | Total Out: ${total_out:,.2f} | Net: ${total_in - total_out:,.2f}")


def cmd_cashflow(args):
    days = args.days
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    end = datetime.now().strftime("%Y-%m-%d")
    params = {"start": start, "end": end, "limit": "500"}

    data = api_request(f"/account/{args.account_id}/transactions", params)
    txns = data.get("transactions", data) if isinstance(data, dict) else data
    if not txns:
        print("No transactions in period.")
        return

    inflows = sum(t["amount"] for t in txns if t.get("amount", 0) > 0)
    outflows = sum(abs(t["amount"]) for t in txns if t.get("amount", 0) < 0)
    net = inflows - outflows
    daily_avg_out = outflows / days if days > 0 else 0

    print(f"  Cash Flow Analysis ({start} to {end})")
    print(f"  {'='*50}")
    print(f"  Total Inflows:   ${inflows:,.2f}")
    print(f"  Total Outflows:  ${outflows:,.2f}")
    print(f"  Net Cash Flow:   ${net:,.2f}")
    print(f"  Daily Avg Spend: ${daily_avg_out:,.2f}")
    if daily_avg_out > 0:
        acct = api_request(f"/account/{args.account_id}")
        bal = acct.get("currentBalance", 0)
        runway = bal / daily_avg_out
        print(f"  Current Balance: ${bal:,.2f}")
        print(f"  Runway:          {runway:.0f} days ({runway/30:.1f} months)")


def cmd_categorize(args):
    days = args.days
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    params = {"start": start, "limit": "500"}

    data = api_request(f"/account/{args.account_id}/transactions", params)
    txns = data.get("transactions", data) if isinstance(data, dict) else data
    if not txns:
        print("No transactions to categorize.")
        return

    txn_list = []
    for t in txns:
        txn_list.append({
            "date": (t.get("postedAt") or t.get("createdAt", ""))[:10],
            "amount": t.get("amount", 0),
            "counterparty": t.get("counterpartyName", t.get("bankDescription", "Unknown")),
        })

    prompt = f"""Categorize these transactions into business categories (Payroll, SaaS/Software, Revenue, Marketing, Office, Professional Services, Banking Fees, Other).

Return a JSON object with:
- "categories": dict of category name -> {{"total": number, "count": number, "transactions": [counterparty names]}}
- "summary": one paragraph summary

Transactions:
{json.dumps(txn_list, indent=2)}"""

    result = llm_request(prompt)
    print(result)


def cmd_summary(args):
    period = args.period
    days = 7 if period == "weekly" else 30
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    params = {"start": start, "limit": "500"}

    data = api_request(f"/account/{args.account_id}/transactions", params)
    txns = data.get("transactions", data) if isinstance(data, dict) else data

    acct = api_request(f"/account/{args.account_id}")
    bal = acct.get("currentBalance", 0)

    txn_list = []
    for t in (txns or []):
        txn_list.append({
            "date": (t.get("postedAt") or t.get("createdAt", ""))[:10],
            "amount": t.get("amount", 0),
            "counterparty": t.get("counterpartyName", t.get("bankDescription", "Unknown")),
        })

    prompt = f"""Generate a {period} financial summary report.

Current balance: ${bal:,.2f}
Period: last {days} days (from {start})

Transactions:
{json.dumps(txn_list, indent=2)}

Include:
1. Cash position overview
2. Top 5 expenses
3. Revenue sources
4. Notable trends or concerns
5. Key metrics (burn rate, runway estimate)

Format as a clean, readable report."""

    result = llm_request(prompt)
    print(f"  {period.upper()} FINANCIAL SUMMARY")
    print(f"  {'='*50}")
    print(result)


def main():
    parser = argparse.ArgumentParser(description="Mercury Banking API")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("accounts", help="List accounts and balances")

    p_txn = sub.add_parser("transactions", help="List transactions")
    p_txn.add_argument("account_id")
    p_txn.add_argument("--start", help="Start date YYYY-MM-DD")
    p_txn.add_argument("--end", help="End date YYYY-MM-DD")
    p_txn.add_argument("--search", help="Search term")
    p_txn.add_argument("--status", help="Filter by status")
    p_txn.add_argument("--limit", type=int, default=50)

    p_cf = sub.add_parser("cashflow", help="Cash flow analysis")
    p_cf.add_argument("account_id")
    p_cf.add_argument("--days", type=int, default=30)

    p_cat = sub.add_parser("categorize", help="AI categorize transactions")
    p_cat.add_argument("account_id")
    p_cat.add_argument("--days", type=int, default=30)

    p_sum = sub.add_parser("summary", help="Financial summary")
    p_sum.add_argument("account_id")
    p_sum.add_argument("--period", choices=["weekly", "monthly"], default="weekly")

    args = parser.parse_args()
    {"accounts": cmd_accounts, "transactions": cmd_transactions, "cashflow": cmd_cashflow,
     "categorize": cmd_categorize, "summary": cmd_summary}[args.command](args)


if __name__ == "__main__":
    main()
