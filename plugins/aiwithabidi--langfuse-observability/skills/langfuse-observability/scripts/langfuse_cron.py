#!/usr/bin/env python3
"""
langfuse_cron.py — Daily observability report for Telegram.

Designed to run via cron. Outputs plain text summary of yesterday's activity.

Usage:
    python langfuse_cron.py
"""

import os
import sys
import json
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
    url = f"{BASE}{path}"
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if qs:
            url += f"?{qs}"
    req = Request(url, headers={"Authorization": f"Basic {AUTH}"})
    try:
        with urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except URLError as e:
        return None


def generate_report():
    now = datetime.now(timezone.utc)
    yesterday = (now - timedelta(days=1)).strftime("%Y-%m-%d")

    lines = [f"📡 Langfuse Daily Report — {yesterday}", "=" * 40, ""]

    # Fetch traces (get a big batch and filter by date)
    data = _api("/traces", {"limit": "100"})
    if not data:
        lines.append("❌ Could not reach Langfuse API")
        return "\n".join(lines)

    all_traces = data.get("data", [])
    day_traces = [t for t in all_traces if t.get("timestamp", "")[:10] == yesterday]

    lines.append(f"📊 Traces yesterday: {len(day_traces)}")
    total_all = data.get("meta", {}).get("totalItems", "?")
    lines.append(f"📊 Total all-time: {total_all}")
    lines.append("")

    # Count by name prefix
    by_type = {}
    errors = 0
    for t in day_traces:
        name = t.get("name", "unknown")
        prefix = name.split("-")[0] if "-" in name else name
        by_type[prefix] = by_type.get(prefix, 0) + 1
        if t.get("level") == "ERROR":
            errors += 1

    if by_type:
        lines.append("📋 By type:")
        for typ, count in sorted(by_type.items(), key=lambda x: -x[1]):
            lines.append(f"  • {typ}: {count}")
        lines.append("")

    lines.append(f"⚠️ Errors: {errors}")
    lines.append("")

    # Cost from observations
    obs_data = _api("/observations", {"limit": "100", "type": "GENERATION"})
    if obs_data:
        day_obs = [o for o in obs_data.get("data", []) if o.get("startTime", "")[:10] == yesterday]
        by_model = {}
        total_cost = 0.0
        for o in day_obs:
            model = o.get("model", "unknown")
            cost = (o.get("metadata") or {}).get("total_cost", 0) or 0
            if model not in by_model:
                by_model[model] = {"count": 0, "cost": 0.0}
            by_model[model]["count"] += 1
            by_model[model]["cost"] += cost
            total_cost += cost

        if by_model:
            lines.append("💰 Cost breakdown:")
            for model, info in sorted(by_model.items(), key=lambda x: -x[1]["cost"])[:5]:
                lines.append(f"  • {model}: {info['count']} calls, ${info['cost']:.4f}")
            lines.append(f"  Total: ${total_cost:.4f}")
        else:
            lines.append("💰 No generation costs recorded")
    lines.append("")

    # Sessions
    sessions = set(t.get("sessionId") for t in day_traces if t.get("sessionId"))
    lines.append(f"🔗 Sessions: {len(sessions)}")

    lines.append("")
    lines.append("— AgxntSix Observability 📡")
    return "\n".join(lines)


if __name__ == "__main__":
    print(generate_report())
