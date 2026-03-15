#!/usr/bin/env python3
"""
ClawSaver Session Analyzer
Queries your OpenRouter management key to show context overhead and
estimate savings from batching over the last N days.

Usage:
  export OPENROUTER_MANAGEMENT_KEY=sk-or-v1-...
  python3 analyze.py
  python3 analyze.py --days 7
  python3 analyze.py --days 30
"""

import os
import sys
import json
import argparse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

def fetch_activity(key):
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/activity",
        headers={"Authorization": f"Bearer {key}"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())

def analyze(days=7, batch_rate=0.25, batch_ratio=3):
    key = os.environ.get("OPENROUTER_MANAGEMENT_KEY")
    if not key:
        print("Error: OPENROUTER_MANAGEMENT_KEY not set.")
        print("  export OPENROUTER_MANAGEMENT_KEY=sk-or-v1-...")
        sys.exit(1)

    print(f"Fetching OpenRouter activity...")
    data = fetch_activity(key)
    rows = data.get("data", [])

    if not rows:
        print("No activity data found.")
        return

    # Filter to last N days
    now = datetime.now(timezone.utc)
    cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
    from datetime import timedelta
    cutoff -= timedelta(days=days - 1)
    cutoff_str = cutoff.strftime("%Y-%m-%d")

    active = [r for r in rows if r.get("date", "")[:10] >= cutoff_str]

    if not active:
        print(f"No activity in the last {days} days.")
        return

    by_date = defaultdict(lambda: {"requests": 0, "prompt": 0, "completion": 0, "cost": 0.0})
    for r in active:
        d = r["date"][:10]
        by_date[d]["requests"]   += r.get("requests", 0)
        by_date[d]["prompt"]     += r.get("prompt_tokens", 0)
        by_date[d]["completion"] += r.get("completion_tokens", 0)
        by_date[d]["cost"]       += r.get("usage", 0.0)

    total_req    = sum(v["requests"]   for v in by_date.values())
    total_prompt = sum(v["prompt"]     for v in by_date.values())
    total_out    = sum(v["completion"] for v in by_date.values())
    total_cost   = sum(v["cost"]       for v in by_date.values())

    if total_req == 0:
        print("No requests found in range.")
        return

    avg_ctx    = total_prompt // total_req
    ratio      = total_prompt / total_out if total_out else 0

    # Savings estimate
    # batch_rate  = fraction of requests that could be batched
    # batch_ratio = average requests collapsed into 1
    saved_req     = int(total_req * batch_rate * (1 - 1/batch_ratio))
    saved_prompt  = saved_req * avg_ctx
    saved_cost    = (saved_prompt / total_prompt) * total_cost if total_prompt else 0
    saved_pct     = (saved_req / total_req * 100) if total_req else 0

    # Display
    w = 52
    print()
    print("╭" + "─" * w + "╮")
    print(f"│{'  💸 ClawSaver — Session Analysis':^{w}}│")
    print("├" + "─" * w + "┤")
    print(f"│  Period        {f'Last {days} days':>{w-18}}  │")
    print(f"│  Requests      {total_req:>{w-18},}  │")
    print(f"│  Prompt tokens {total_prompt/1e6:>{w-18}.1f}M  │")
    print(f"│  Output tokens {total_out/1e6:>{w-18}.2f}M  │")
    print(f"│  Cost          ${total_cost:>{w-19}.2f}  │")
    print("├" + "─" * w + "┤")
    print(f"│  Avg context/request   {avg_ctx:>{w-26},} tok  │")
    print(f"│  Input/output ratio    {ratio:>{w-26}.0f}x  │")
    print("├" + "─" * w + "┤")
    print(f"│{'  Batching estimate ({:.0f}% of reqs, {}→1)'.format(batch_rate*100, batch_ratio):^{w}}│")
    print(f"│  Requests avoided  {saved_req:>{w-22},}  │")
    print(f"│  Tokens saved      {saved_prompt/1e6:>{w-22}.1f}M  │")
    print(f"│  Cost saved        ${saved_cost:>{w-23}.2f}  │")
    print(f"│  Request reduction {saved_pct:>{w-22}.0f}%  │")
    print("├" + "─" * w + "┤")
    print(f"│  * Estimate: {batch_rate*100:.0f}% of requests batchable at {batch_ratio}→1  │")
    print(f"│    Adjust --batch-rate and --batch-ratio to tune.  │")
    print("╰" + "─" * w + "╯")
    print()

    print("Daily breakdown:")
    print(f"  {'Date':<12} {'Reqs':>6} {'Avg ctx':>10} {'Cost':>8}")
    print(f"  {'─'*12} {'─'*6} {'─'*10} {'─'*8}")
    for date in sorted(by_date.keys()):
        v = by_date[date]
        avg = v["prompt"] // v["requests"] if v["requests"] else 0
        print(f"  {date:<12} {v['requests']:>6,} {avg:>9,}t  ${v['cost']:>6.2f}")
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ClawSaver session analyzer")
    parser.add_argument("--days",        type=int,   default=7,    help="Days to analyze (default: 7)")
    parser.add_argument("--batch-rate",  type=float, default=0.25, help="Fraction of requests you estimate are batchable (default: 0.25)")
    parser.add_argument("--batch-ratio", type=int,   default=3,    help="Avg requests collapsed per batch (default: 3)")
    args = parser.parse_args()
    analyze(days=args.days, batch_rate=args.batch_rate, batch_ratio=args.batch_ratio)
