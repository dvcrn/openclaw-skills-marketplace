#!/usr/bin/env python3
"""OpenRouter Toolkit — Smart routing, cost tracking, fallback chains, model comparison."""

import argparse
import json
import os
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests library required. Install: pip install requests")
    sys.exit(1)

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
BASE_URL = "https://openrouter.ai/api/v1"
DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "openrouter_costs.db"

# Task-to-model routing profiles
ROUTING_PROFILES = {
    "code": {
        "preferred": ["anthropic/claude-opus-4", "anthropic/claude-sonnet-4", "openai/gpt-4o", "google/gemini-2.0-flash-001"],
        "traits": ["high_context", "code_quality"],
    },
    "reasoning": {
        "preferred": ["anthropic/claude-opus-4", "openai/o1", "deepseek/deepseek-r1", "anthropic/claude-sonnet-4"],
        "traits": ["reasoning", "accuracy"],
    },
    "creative": {
        "preferred": ["anthropic/claude-sonnet-4", "openai/gpt-4o", "anthropic/claude-opus-4", "google/gemini-2.0-flash-001"],
        "traits": ["creative", "fluency"],
    },
    "fast": {
        "preferred": ["anthropic/claude-haiku-4.5", "openai/gpt-4o-mini", "google/gemini-2.0-flash-001", "meta-llama/llama-3.1-8b-instruct"],
        "traits": ["low_latency", "good_enough"],
    },
    "cheap": {
        "preferred": ["google/gemini-2.0-flash-001", "openai/gpt-4o-mini", "anthropic/claude-haiku-4.5", "meta-llama/llama-3.1-8b-instruct"],
        "traits": ["lowest_cost"],
    },
}


def ensure_db():
    """Create SQLite tables if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS api_calls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        model TEXT NOT NULL,
        prompt_tokens INTEGER DEFAULT 0,
        completion_tokens INTEGER DEFAULT 0,
        cost_usd REAL DEFAULT 0.0,
        task_type TEXT DEFAULT '',
        latency_ms INTEGER DEFAULT 0,
        success INTEGER DEFAULT 1,
        note TEXT DEFAULT ''
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS budget (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        monthly_limit REAL DEFAULT 0.0,
        alert_threshold REAL DEFAULT 0.8
    )""")
    conn.commit()
    conn.close()


def log_call(model, prompt_tokens, completion_tokens, cost, task_type="", latency_ms=0, success=True, note=""):
    ensure_db()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO api_calls (timestamp, model, prompt_tokens, completion_tokens, cost_usd, task_type, latency_ms, success, note) VALUES (?,?,?,?,?,?,?,?,?)",
        (datetime.utcnow().isoformat(), model, prompt_tokens, completion_tokens, cost, task_type, latency_ms, int(success), note),
    )
    conn.commit()
    conn.close()


def headers():
    return {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}


def fetch_models():
    """Fetch available models from OpenRouter."""
    resp = requests.get(f"{BASE_URL}/models", headers=headers(), timeout=30)
    resp.raise_for_status()
    return resp.json().get("data", [])


def chat_completion(model, prompt, max_tokens=1024, temperature=0.7):
    """Send a chat completion request, return (response_text, usage_dict, latency_ms)."""
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    start = time.time()
    resp = requests.post(f"{BASE_URL}/chat/completions", headers=headers(), json=payload, timeout=120)
    latency_ms = int((time.time() - start) * 1000)
    resp.raise_for_status()
    data = resp.json()
    text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    usage = data.get("usage", {})
    return text, usage, latency_ms


def estimate_cost(model, usage, models_cache=None):
    """Estimate cost from usage and model pricing."""
    if models_cache is None:
        models_cache = fetch_models()
    info = next((m for m in models_cache if m["id"] == model), None)
    if not info or "pricing" not in info:
        return 0.0
    p = info["pricing"]
    prompt_cost = float(p.get("prompt", "0")) * usage.get("prompt_tokens", 0)
    completion_cost = float(p.get("completion", "0")) * usage.get("completion_tokens", 0)
    return prompt_cost + completion_cost


# ── Commands ──────────────────────────────────────────────────────────────

def cmd_route(args):
    """Smart routing: recommend best model for a task type."""
    task = args.task.lower()
    if task not in ROUTING_PROFILES:
        print(f"Unknown task type: {task}. Options: {', '.join(ROUTING_PROFILES.keys())}")
        return
    profile = ROUTING_PROFILES[task]
    models = fetch_models()
    model_map = {m["id"]: m for m in models}

    print(f"🔀 Smart Route for task: {task}")
    print(f"   Traits: {', '.join(profile['traits'])}")
    print(f"   Recommended models (in priority order):\n")
    for i, mid in enumerate(profile["preferred"], 1):
        m = model_map.get(mid)
        if m:
            p = m.get("pricing", {})
            prompt_price = float(p.get("prompt", "0")) * 1_000_000
            comp_price = float(p.get("completion", "0")) * 1_000_000
            ctx = m.get("context_length", "?")
            print(f"   {i}. {mid}")
            print(f"      Context: {ctx:,} | ${prompt_price:.2f}/1M in | ${comp_price:.2f}/1M out")
        else:
            print(f"   {i}. {mid} (not currently available)")
    print()


def cmd_compare(args):
    """Compare models on the same prompt."""
    model_ids = [m.strip() for m in args.models.split(",")]
    models_cache = fetch_models()
    print(f"📊 Comparing {len(model_ids)} models on prompt: \"{args.prompt[:80]}...\"\n")

    results = []
    for mid in model_ids:
        try:
            text, usage, latency = chat_completion(mid, args.prompt, max_tokens=args.max_tokens)
            cost = estimate_cost(mid, usage, models_cache)
            log_call(mid, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0), cost, "compare", latency)
            results.append({"model": mid, "text": text, "usage": usage, "latency": latency, "cost": cost, "error": None})
        except Exception as e:
            results.append({"model": mid, "text": "", "usage": {}, "latency": 0, "cost": 0, "error": str(e)})

    for r in results:
        print(f"{'─'*60}")
        print(f"Model: {r['model']}")
        if r["error"]:
            print(f"  ❌ Error: {r['error']}")
        else:
            print(f"  Latency: {r['latency']}ms | Tokens: {r['usage'].get('prompt_tokens',0)}+{r['usage'].get('completion_tokens',0)} | Cost: ${r['cost']:.6f}")
            print(f"  Response:\n{r['text'][:500]}")
        print()


def cmd_fallback(args):
    """Try models in order until one succeeds."""
    chain = [m.strip() for m in args.chain.split(",")]
    models_cache = fetch_models()
    print(f"🔗 Fallback chain: {' → '.join(chain)}\n")

    for mid in chain:
        try:
            print(f"  Trying {mid}...", end=" ", flush=True)
            text, usage, latency = chat_completion(mid, args.prompt, max_tokens=args.max_tokens)
            cost = estimate_cost(mid, usage, models_cache)
            log_call(mid, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0), cost, "fallback", latency)
            print(f"✅ ({latency}ms, ${cost:.6f})")
            print(f"\nResponse:\n{text}")
            return
        except Exception as e:
            log_call(mid, 0, 0, 0, "fallback", 0, success=False, note=str(e))
            print(f"❌ {e}")

    print("\n⚠️ All models in chain failed!")


def cmd_cost(args):
    """Show cost reports."""
    ensure_db()
    conn = sqlite3.connect(str(DB_PATH))
    now = datetime.utcnow()
    if args.period == "daily":
        since = (now - timedelta(days=1)).isoformat()
        label = "Last 24 hours"
    elif args.period == "weekly":
        since = (now - timedelta(days=7)).isoformat()
        label = "Last 7 days"
    else:
        since = (now - timedelta(days=30)).isoformat()
        label = "Last 30 days"

    rows = conn.execute(
        "SELECT model, COUNT(*), SUM(prompt_tokens), SUM(completion_tokens), SUM(cost_usd) FROM api_calls WHERE timestamp >= ? GROUP BY model ORDER BY SUM(cost_usd) DESC",
        (since,),
    ).fetchall()
    conn.close()

    total = sum(r[4] or 0 for r in rows)
    print(f"💰 Cost Report — {label}")
    print(f"{'─'*60}")
    print(f"{'Model':<40} {'Calls':>6} {'Cost':>10}")
    print(f"{'─'*60}")
    for model, calls, pt, ct, cost in rows:
        print(f"{model:<40} {calls:>6} ${cost:>9.4f}")
    print(f"{'─'*60}")
    print(f"{'TOTAL':<40} {sum(r[1] for r in rows):>6} ${total:>9.4f}")


def cmd_budget(args):
    """Set or check budget."""
    ensure_db()
    conn = sqlite3.connect(str(DB_PATH))
    if args.set is not None:
        conn.execute("INSERT OR REPLACE INTO budget (id, monthly_limit, alert_threshold) VALUES (1, ?, 0.8)", (args.set,))
        conn.commit()
        print(f"✅ Monthly budget set to ${args.set:.2f}")
    if args.check or args.set is None:
        budget_row = conn.execute("SELECT monthly_limit, alert_threshold FROM budget WHERE id=1").fetchone()
        if not budget_row or budget_row[0] == 0:
            print("No budget set. Use --set <amount>")
            conn.close()
            return
        limit, threshold = budget_row
        since = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0).isoformat()
        spent = conn.execute("SELECT COALESCE(SUM(cost_usd),0) FROM api_calls WHERE timestamp >= ?", (since,)).fetchone()[0]
        pct = (spent / limit * 100) if limit > 0 else 0
        status = "🟢" if pct < threshold * 100 else "🟡" if pct < 100 else "🔴"
        print(f"{status} Budget: ${spent:.4f} / ${limit:.2f} ({pct:.1f}%)")
        if pct >= threshold * 100:
            print(f"⚠️ ALERT: Spending at {pct:.1f}% of monthly limit!")
    conn.close()


def cmd_models(args):
    """List, search, or find best models."""
    models = fetch_models()
    if args.search:
        models = [m for m in models if args.search.lower() in m["id"].lower() or args.search.lower() in m.get("name", "").lower()]
    if args.best:
        profile = ROUTING_PROFILES.get(args.best)
        if profile:
            preferred = set(profile["preferred"])
            models = [m for m in models if m["id"] in preferred]

    models.sort(key=lambda m: float(m.get("pricing", {}).get("prompt", "999")))
    top = args.top or 20

    print(f"{'Model':<45} {'Context':>8} {'$/1M in':>9} {'$/1M out':>9}")
    print("─" * 75)
    for m in models[:top]:
        p = m.get("pricing", {})
        pin = float(p.get("prompt", "0")) * 1_000_000
        pout = float(p.get("completion", "0")) * 1_000_000
        ctx = m.get("context_length", 0)
        print(f"{m['id']:<45} {ctx:>8,} ${pin:>8.2f} ${pout:>8.2f}")


def main():
    if not API_KEY:
        print("ERROR: OPENROUTER_API_KEY not set")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="OpenRouter Toolkit")
    sub = parser.add_subparsers(dest="command")

    r = sub.add_parser("route", help="Smart model routing")
    r.add_argument("--task", required=True, choices=ROUTING_PROFILES.keys())

    c = sub.add_parser("compare", help="Compare models")
    c.add_argument("--prompt", required=True)
    c.add_argument("--models", required=True, help="Comma-separated model IDs")
    c.add_argument("--max-tokens", type=int, default=512)

    f = sub.add_parser("fallback", help="Fallback chain")
    f.add_argument("--prompt", required=True)
    f.add_argument("--chain", required=True, help="Comma-separated model IDs")
    f.add_argument("--max-tokens", type=int, default=512)

    co = sub.add_parser("cost", help="Cost report")
    co.add_argument("--period", default="monthly", choices=["daily", "weekly", "monthly"])

    b = sub.add_parser("budget", help="Budget management")
    b.add_argument("--set", type=float, default=None)
    b.add_argument("--check", action="store_true")

    m = sub.add_parser("models", help="List models")
    m.add_argument("--top", type=int, default=20)
    m.add_argument("--search", default=None)
    m.add_argument("--best", default=None, choices=ROUTING_PROFILES.keys())

    args = parser.parse_args()
    cmds = {"route": cmd_route, "compare": cmd_compare, "fallback": cmd_fallback, "cost": cmd_cost, "budget": cmd_budget, "models": cmd_models}
    if args.command in cmds:
        cmds[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
