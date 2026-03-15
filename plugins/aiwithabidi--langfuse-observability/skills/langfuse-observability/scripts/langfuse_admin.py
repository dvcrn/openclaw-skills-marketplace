#!/usr/bin/env python3
"""
langfuse_admin.py — CLI for querying the Langfuse dashboard.

Usage:
    python langfuse_admin.py status
    python langfuse_admin.py traces [--limit N] [--name X] [--session X]
    python langfuse_admin.py costs [--days N]
    python langfuse_admin.py sessions [--limit N]
    python langfuse_admin.py scores [--limit N]
    python langfuse_admin.py models
    python langfuse_admin.py export [--limit N] [--format json|csv]
    python langfuse_admin.py health
"""

import sys
import os
import json
import argparse
import time
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError
from base64 import b64encode

PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY", "pk-lf-8a9322b9-5eb1-4e8b-815e-b3428dc69bc4")
SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY", "sk-lf-115cb6b4-7153-4fe6-9255-bf28f8b115de")
HOST = os.environ.get("LANGFUSE_HOST", "http://langfuse-web:3000")
BASE = f"{HOST}/api/public"
AUTH = b64encode(f"{PUBLIC_KEY}:{SECRET_KEY}".encode()).decode()


def _api(path, params=None):
    """Make authenticated GET request to Langfuse API."""
    url = f"{BASE}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if qs:
            url += f"?{qs}"
    req = Request(url, headers={"Authorization": f"Basic {AUTH}"})
    try:
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except URLError as e:
        print(f"API error: {e}", file=sys.stderr)
        return None


def cmd_status(_args):
    """Langfuse health + trace count."""
    start = time.time()
    data = _api("/traces", {"limit": "1"})
    latency = round((time.time() - start) * 1000)

    if data is None:
        print("❌ Langfuse unreachable")
        return

    total = data.get("meta", {}).get("totalItems", "?")
    print(f"✅ Langfuse is UP ({latency}ms)")
    print(f"📊 Total traces: {total}")

    traces = data.get("data", [])
    if traces:
        latest = traces[0]
        print(f"🕐 Latest: {latest.get('name', '?')} @ {latest.get('timestamp', '?')[:19]}")


def cmd_traces(args):
    """List recent traces."""
    params = {"limit": str(args.limit)}
    if args.name:
        params["name"] = args.name
    if args.session:
        params["sessionId"] = args.session

    data = _api("/traces", params)
    if not data:
        return

    for t in data.get("data", []):
        ts = t.get("timestamp", "")[:19]
        name = t.get("name", "?")
        sid = t.get("sessionId", "-")
        tags = ",".join(t.get("tags", []))
        print(f"{ts}  {name:<40} session={sid}  tags=[{tags}]")

    total = data.get("meta", {}).get("totalItems", "?")
    print(f"\n({len(data.get('data', []))} shown / {total} total)")


def cmd_costs(args):
    """Cost breakdown from observations."""
    # Fetch recent generations
    data = _api("/observations", {"limit": "100", "type": "GENERATION"})
    if not data:
        return

    by_model = {}
    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)

    for obs in data.get("data", []):
        ts = obs.get("startTime", "")
        if ts and ts[:10] < cutoff.isoformat()[:10]:
            continue
        model = obs.get("model", "unknown")
        meta = obs.get("metadata", {}) or {}
        cost = meta.get("total_cost", 0) or 0
        if model not in by_model:
            by_model[model] = {"count": 0, "cost": 0.0}
        by_model[model]["count"] += 1
        by_model[model]["cost"] += cost

    print(f"📊 Cost breakdown (last {args.days} days):\n")
    total = 0.0
    for model, info in sorted(by_model.items(), key=lambda x: -x[1]["cost"]):
        print(f"  {model:<35} {info['count']:>4} calls  ${info['cost']:.4f}")
        total += info["cost"]
    print(f"\n  {'TOTAL':<35} {'':>4}        ${total:.4f}")


def cmd_sessions(args):
    """List sessions."""
    data = _api("/sessions", {"limit": str(args.limit)})
    if not data:
        return

    for s in data.get("data", []):
        sid = s.get("id", "?")
        created = s.get("createdAt", "")[:19]
        print(f"  {sid:<30} created={created}")


def cmd_scores(args):
    """View scores."""
    data = _api("/scores", {"limit": str(args.limit)})
    if not data:
        return

    for s in data.get("data", []):
        name = s.get("name", "?")
        value = s.get("value", "?")
        tid = s.get("traceId", "?")[:12]
        print(f"  {name:<20} value={value}  trace={tid}...")


def cmd_models(_args):
    """List configured models."""
    from langfuse_hub import MODEL_COSTS
    print("📋 Configured model pricing (per 1M tokens):\n")
    for model, costs in sorted(MODEL_COSTS.items()):
        print(f"  {model:<35} in=${costs['input']:<6.2f}  out=${costs['output']:.2f}")


def cmd_export(args):
    """Export traces."""
    data = _api("/traces", {"limit": str(args.limit)})
    if not data:
        return

    traces = data.get("data", [])
    if args.format == "csv":
        print("timestamp,name,session_id,tags")
        for t in traces:
            ts = t.get("timestamp", "")[:19]
            name = t.get("name", "").replace(",", ";")
            sid = t.get("sessionId", "")
            tags = ";".join(t.get("tags", []))
            print(f"{ts},{name},{sid},{tags}")
    else:
        print(json.dumps(traces, indent=2))


def cmd_health(_args):
    """Full health check."""
    checks = []

    # API reachability
    start = time.time()
    data = _api("/traces", {"limit": "1"})
    latency = round((time.time() - start) * 1000)
    checks.append(("API", "✅" if data else "❌", f"{latency}ms"))

    # Auth check
    sys.path.insert(0, os.path.dirname(__file__))
    try:
        from langfuse_hub import _get_client
        client = _get_client()
        auth = client.auth_check() if client else False
        checks.append(("Auth", "✅" if auth else "❌", ""))
    except Exception as e:
        checks.append(("Auth", "❌", str(e)))

    # Trace count
    if data:
        total = data.get("meta", {}).get("totalItems", "?")
        checks.append(("Traces", "✅", f"{total} total"))

    print("🏥 Langfuse Health Check\n")
    for name, status, detail in checks:
        print(f"  {status} {name:<15} {detail}")


def main():
    parser = argparse.ArgumentParser(description="Langfuse Admin CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status")

    p_traces = sub.add_parser("traces")
    p_traces.add_argument("--limit", type=int, default=10)
    p_traces.add_argument("--name", default=None)
    p_traces.add_argument("--session", default=None)

    p_costs = sub.add_parser("costs")
    p_costs.add_argument("--days", type=int, default=7)

    p_sessions = sub.add_parser("sessions")
    p_sessions.add_argument("--limit", type=int, default=20)

    p_scores = sub.add_parser("scores")
    p_scores.add_argument("--limit", type=int, default=20)

    sub.add_parser("models")

    p_export = sub.add_parser("export")
    p_export.add_argument("--limit", type=int, default=100)
    p_export.add_argument("--format", choices=["json", "csv"], default="json")

    sub.add_parser("health")

    args = parser.parse_args()
    commands = {
        "status": cmd_status, "traces": cmd_traces, "costs": cmd_costs,
        "sessions": cmd_sessions, "scores": cmd_scores, "models": cmd_models,
        "export": cmd_export, "health": cmd_health,
    }

    fn = commands.get(args.command)
    if fn:
        fn(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
