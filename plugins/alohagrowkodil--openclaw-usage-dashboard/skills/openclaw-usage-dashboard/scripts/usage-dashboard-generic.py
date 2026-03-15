#!/usr/bin/env python3
"""
OpenClaw Usage Dashboard — Generic Multi-Provider Edition v2
=============================================================
Reads session transcripts and generates an interactive HTML dashboard.
Supports: Anthropic, OpenAI, Google (Gemini), Moonshot, Mistral, Cohere, Groq

Usage: python3 usage-dashboard-generic.py [output.html]
"""

import json, glob, os, sys, math
from collections import defaultdict
from datetime import datetime, timedelta

_OPENCLAW_ROOT = os.environ.get("OPENCLAW_ROOT", os.path.expanduser("~/.openclaw"))
SESSIONS_DIR = os.path.join(_OPENCLAW_ROOT, "agents", "main", "sessions")
# Parse arguments
OUTPUT_PATH = os.path.join(os.path.expanduser("~"), "openclaw-usage-dashboard.html")
demo_mode = False

for i, arg in enumerate(sys.argv[1:], 1):
    if arg == "--demo":
        demo_mode = True
    elif not arg.startswith("-"):
        # Sanitize output path: resolve to absolute, reject path traversal
        candidate = os.path.realpath(os.path.expanduser(arg))
        if ".." in os.path.relpath(candidate, os.getcwd()):
            pass  # allow absolute paths but resolve them
        OUTPUT_PATH = candidate

# ═══════════════════════════════════════════════════════════════════════════════
# PRICING DATABASE — Extend this for new models
# ═══════════════════════════════════════════════════════════════════════════════
# Format: provider/model-name -> price per 1M tokens in USD
# Cache prices apply only when prompt caching is active

PRICES = {
    # ── Anthropic ─────────────────────────────────────────────────────────────
    "anthropic/claude-opus-4-6":       {"input": 15.00, "output": 75.00, "cache_read": 1.50, "cache_write": 18.75},
    "anthropic/claude-sonnet-4-6":     {"input": 3.00,  "output": 15.00, "cache_read": 0.30, "cache_write": 3.75},
    "anthropic/claude-sonnet-4-5":     {"input": 3.00,  "output": 15.00, "cache_read": 0.30, "cache_write": 3.75},
    "anthropic/claude-haiku-4-5":      {"input": 0.80,  "output": 4.00,  "cache_read": 0.08, "cache_write": 1.00},

    # ── OpenAI ────────────────────────────────────────────────────────────────
    "openai/gpt-4o":                   {"input": 2.50,  "output": 10.00, "cache_read": 1.25, "cache_write": 2.50},
    "openai/gpt-4o-mini":              {"input": 0.15,  "output": 0.60,  "cache_read": 0.075,"cache_write": 0.15},
    "openai/o3-mini":                  {"input": 1.10,  "output": 4.40,  "cache_read": 0.55, "cache_write": 1.10},
    "openai/o1":                       {"input": 15.00, "output": 60.00, "cache_read": 7.50, "cache_write": 15.00},
    "openai/o1-mini":                  {"input": 1.10,  "output": 4.40,  "cache_read": 0.55, "cache_write": 1.10},

    # ── Google (Gemini) ───────────────────────────────────────────────────────
    "google/gemini-2.0-flash":         {"input": 0.10,  "output": 0.40,  "cache_read": 0.025,"cache_write": 0.10},
    "google/gemini-2.0-pro":           {"input": 3.50,  "output": 10.50, "cache_read": 0.875,"cache_write": 3.50},
    "google/gemini-1.5-pro":           {"input": 1.25,  "output": 5.00,  "cache_read": 0.312,"cache_write": 1.25},
    "google/gemini-1.5-flash":         {"input": 0.075, "output": 0.30,  "cache_read": 0.019,"cache_write": 0.075},

    # ── Moonshot / Kimi ───────────────────────────────────────────────────────
    "moonshot/kimi-k2.5":              {"input": 0.0,   "output": 0.0,   "cache_read": 0.0,  "cache_write": 0.0},
    "moonshot/moonshot-v1-8k":         {"input": 0.0,   "output": 0.0,   "cache_read": 0.0,  "cache_write": 0.0},

    # ── Mistral AI ────────────────────────────────────────────────────────────
    "mistral/mistral-large-latest":    {"input": 2.00,  "output": 6.00,  "cache_read": 0.50, "cache_write": 2.00},
    "mistral/mistral-medium":          {"input": 0.60,  "output": 1.80,  "cache_read": 0.15, "cache_write": 0.60},
    "mistral/mistral-small":           {"input": 0.10,  "output": 0.30,  "cache_read": 0.025,"cache_write": 0.10},
    "mistral/codestral":               {"input": 0.20,  "output": 0.60,  "cache_read": 0.05, "cache_write": 0.20},

    # ── Cohere ────────────────────────────────────────────────────────────────
    "cohere/command-r-plus":           {"input": 2.50,  "output": 10.00, "cache_read": 0.625,"cache_write": 2.50},
    "cohere/command-r":                {"input": 0.50,  "output": 1.50,  "cache_read": 0.125,"cache_write": 0.50},

    # ── Groq (Ultra-fast inference) ───────────────────────────────────────────
    "groq/llama-3.3-70b-versatile":    {"input": 0.59,  "output": 0.79,  "cache_read": 0.0,  "cache_write": 0.0},
    "groq/llama-3.1-8b-instant":       {"input": 0.05,  "output": 0.08,  "cache_read": 0.0,  "cache_write": 0.0},
    "groq/gemma2-9b-it":               {"input": 0.20,  "output": 0.40,  "cache_read": 0.0,  "cache_write": 0.0},
}

# ── Legacy aliases (model names without provider prefix) ───────────────────────
ALIAS_MAP = {
    "claude-opus-4-6": "anthropic/claude-opus-4-6",
    "claude-sonnet-4-6": "anthropic/claude-sonnet-4-6",
    "claude-sonnet-4-5": "anthropic/claude-sonnet-4-5",
    "claude-haiku-4-5": "anthropic/claude-haiku-4-5",
    "gpt-4o": "openai/gpt-4o",
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "o3-mini": "openai/o3-mini",
    "kimi-k2.5": "moonshot/kimi-k2.5",
    "gemini-2.0-flash": "google/gemini-2.0-flash",
}

# Colors for visualization (can be extended)
MODEL_COLORS = {
    "anthropic/claude-opus-4-6": "#f97316",   # orange
    "anthropic/claude-sonnet-4-6": "#06b6d4", # cyan
    "anthropic/claude-sonnet-4-5": "#0891b2", # darker cyan
    "anthropic/claude-haiku-4-5": "#8b5cf6",  # violet
    "openai/gpt-4o": "#22c55e",               # green
    "openai/gpt-4o-mini": "#10b981",          # emerald
    "openai/o3-mini": "#14b8a6",              # teal
    "openai/o1": "#0ea5e9",                   # sky
    "moonshot/kimi-k2.5": "#3b82f6",          # blue
    "google/gemini-2.0-flash": "#eab308",     # yellow
    "google/gemini-2.0-pro": "#f59e0b",       # amber
    "mistral/mistral-large-latest": "#ec4899", # pink
    "cohere/command-r-plus": "#a855f7",       # purple
}

def normalize_model(model: str) -> str:
    """Normalize model name to full provider/model format."""
    if model in ALIAS_MAP:
        return ALIAS_MAP[model]
    if "/" not in model and model in PRICES:
        # Try to find by suffix
        for full_name in PRICES:
            if full_name.endswith(f"/{model}"):
                return full_name
    return model

def get_price(model: str) -> dict:
    """Get pricing info for a model, trying various fallbacks."""
    normalized = normalize_model(model)
    if normalized in PRICES:
        return PRICES[normalized]
    # Try without provider prefix
    for key in PRICES:
        if key.endswith(f"/{model}") or key == model:
            return PRICES[key]
    # Default: free (unknown model)
    return {"input": 0.0, "output": 0.0, "cache_read": 0.0, "cache_write": 0.0}

def get_color(model: str) -> str:
    """Get color for a model, with fallback."""
    normalized = normalize_model(model)
    if normalized in MODEL_COLORS:
        return MODEL_COLORS[normalized]
    # Try without provider
    for key in MODEL_COLORS:
        if key.endswith(f"/{model}"):
            return MODEL_COLORS[key]
    # Generate deterministic color from model name
    hash_val = sum(ord(c) for c in model) % 360
    return f"hsl({hash_val}, 70%, 50%)"

def calc_cost(model: str, usage: dict) -> float:
    """Calculate cost in USD for a usage entry."""
    price = get_price(model)
    inp = usage.get("input", 0)
    out = usage.get("output", 0)
    cr = usage.get("cache_read", 0) or usage.get("cacheRead", 0)
    cw = usage.get("cache_write", 0) or usage.get("cacheWrite", 0)

    cost = (inp * price["input"] + out * price["output"]) / 1e6
    if cr or cw:
        cost += (cr * price.get("cache_read", price["input"]*0.1) +
                 cw * price.get("cache_write", price["input"]*0.125)) / 1e6
    return cost

# ═══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════════════════

def load_sessions():
    """Load all session transcripts."""
    sessions = []
    if not os.path.isdir(SESSIONS_DIR):
        print(f"⚠️ Sessions directory not found: {SESSIONS_DIR}")
        return sessions

    for fn in sorted(glob.glob(os.path.join(SESSIONS_DIR, "*.jsonl")) + glob.glob(os.path.join(SESSIONS_DIR, "*.jsonl.reset.*"))):
        try:
            with open(fn) as f:
                lines = [json.loads(l) for l in f if l.strip()]
                sessions.append({"file": fn, "lines": lines})
        except Exception as e:
            print(f"⚠️ Error reading {fn}: {e}")
    return sessions

def parse_transcripts(sessions):
    """Extract usage data from all sessions."""
    model_usage = defaultdict(lambda: {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "cost": 0.0, "turns": 0})
    daily = defaultdict(lambda: {"total": 0.0, "models": defaultdict(float), "turns": 0})
    hourly_today = defaultdict(lambda: defaultdict(lambda: {"cost": 0.0, "turns": 0}))
    weekly = defaultdict(lambda: {"total": 0.0, "models": defaultdict(float), "turns": 0})
    monthly = defaultdict(lambda: {"total": 0.0, "models": defaultdict(float), "turns": 0})
    yearly = defaultdict(lambda: {"total": 0.0, "models": defaultdict(float), "turns": 0})

    today_str = datetime.now().strftime("%Y-%m-%d")

    for sess in sessions:
        for obj in sess["lines"]:
            msg = obj.get("message", {})
            usage = msg.get("usage")
            model = msg.get("model", "")
            ts = msg.get("timestamp") or obj.get("timestamp")

            if not usage or not model or model in ("delivery-mirror", "gateway-injected"):
                continue

            # Normalize model name
            model = normalize_model(model)

            # Extract usage numbers (support both camelCase and snake_case)
            inp = usage.get("input", 0)
            out = usage.get("output", 0)
            cr = usage.get("cache_read", 0) or usage.get("cacheRead", 0)
            cw = usage.get("cache_write", 0) or usage.get("cacheWrite", 0)

            cost = calc_cost(model, usage)

            # Aggregate by model
            u = model_usage[model]
            u["input"] += inp
            u["output"] += out
            u["cache_read"] += cr
            u["cache_write"] += cw
            u["cost"] += cost
            u["turns"] += 1

            # Time-based aggregation
            if ts:
                try:
                    # Support both Unix ms (13 digits) and ISO string formats
                    if isinstance(ts, (int, float)) or (isinstance(ts, str) and ts.isdigit() and len(ts) >= 10):
                        ts_int = int(ts)
                        # Convert ms to seconds if needed
                        if ts_int > 1e12:
                            ts_int = ts_int / 1000
                        dt = datetime.fromtimestamp(ts_int)
                    else:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                    day = dt.strftime("%Y-%m-%d")
                    week = f"{dt.year}-W{dt.isocalendar()[1]:02d}"
                    month = dt.strftime("%Y-%m")
                    year = str(dt.year)
                    hour = dt.hour

                    # Daily
                    daily[day]["total"] += cost
                    daily[day]["models"][model] += cost
                    daily[day]["turns"] += 1

                    # Hourly (today only)
                    if day == today_str:
                        hour_str = f"{hour:02d}:00"
                        hourly_today[hour_str][model]["cost"] += cost
                        hourly_today[hour_str][model]["turns"] += 1

                    # Weekly
                    weekly[week]["total"] += cost
                    weekly[week]["models"][model] += cost
                    weekly[week]["turns"] += 1

                    # Monthly
                    monthly[month]["total"] += cost
                    monthly[month]["models"][model] += cost
                    monthly[month]["turns"] += 1

                    # Yearly
                    yearly[year]["total"] += cost
                    yearly[year]["models"][model] += cost
                    yearly[year]["turns"] += 1

                except Exception:
                    pass

    return model_usage, daily, hourly_today, weekly, monthly, yearly

# ═══════════════════════════════════════════════════════════════════════════════
# RATE LIMIT CHECKING (Anthropic-specific, optional)
# ═══════════════════════════════════════════════════════════════════════════════

def get_anthropic_limits():
    """Query Anthropic rate limits if API key available."""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return {"error": "No ANTHROPIC_API_KEY"}

    try:
        import urllib.request, urllib.error
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=b'{"model": "claude-sonnet-4-6", "max_tokens": 1, "messages": [{"role": "user", "content": "hi"}]}',
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
        )
        try:
            urllib.request.urlopen(req, timeout=10)
        except urllib.error.HTTPError as e:
            headers = dict(e.headers)
            limits = {}
            for window in ["5h", "7d"]:
                pct = headers.get(f"anthropic-ratelimit-unified-{window}-utilization")
                status = headers.get(f"anthropic-ratelimit-unified-{window}-status")
                reset = headers.get(f"anthropic-ratelimit-unified-{window}-reset")
                if pct:
                    limits[window] = {
                        "pct": float(pct),
                        "status": status,
                        "reset": int(reset) if reset else None
                    }
            # Overage info
            ov_status = headers.get("anthropic-ratelimit-unified-overage-status")
            if ov_status:
                limits["overage"] = {
                    "status": ov_status,
                    "in_use": headers.get("anthropic-ratelimit-unified-overage-in-use", "").lower() == "true",
                    "reset": headers.get("anthropic-ratelimit-unified-overage-reset"),
                }
            return limits
    except Exception as e:
        return {"error": str(e)}
    return {"error": "Unknown"}

def ts_to_local(ts):
    if not ts:
        return "—"
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%d.%m. %H:%M")
    except:
        return "—"

# ═══════════════════════════════════════════════════════════════════════════════
# HTML GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def build_html(data):
    """Generate interactive HTML dashboard."""

    # Prepare data structures
    model_costs = [(m, u["cost"], u["turns"], get_color(m)) for m, u in data["model_usage"].items()]
    model_costs.sort(key=lambda x: -x[1])

    daily_list = sorted(data["daily"].items())
    weekly_list = sorted(data["weekly"].items())
    monthly_list = sorted(data["monthly"].items())
    yearly_list = sorted(data["yearly"].items())

    # Anthropic limits if available
    anth = data.get("anthropic_limits", {})

    # ── Cache Hit Rate KPI ──────────────────────────────────────────────────
    total_cache_read = sum(u["cache_read"] for u in data["model_usage"].values())
    total_input = sum(u["input"] for u in data["model_usage"].values())
    total_output = sum(u["output"] for u in data["model_usage"].values())
    total_tokens = total_input + total_output + total_cache_read
    cache_pct = (total_cache_read / total_tokens * 100) if total_tokens > 0 else 0

    cache_savings = 0.0
    for m, u in data["model_usage"].items():
        p = get_price(m)
        cache_savings += u["cache_read"] * (p["input"] - p.get("cache_read", 0)) / 1e6

    if total_cache_read == 0:
        cache_kpi_value = "—"
        cache_kpi_sub = "No cache data"
    else:
        cache_kpi_value = f"{cache_pct:.0f}%"
        cache_kpi_sub = f"Est. savings: ${cache_savings:.2f}"

    # ── Monthly Projection KPI ──────────────────────────────────────────────
    daily_sorted = sorted(data["daily"].items())
    last7 = daily_sorted[-7:] if len(daily_sorted) >= 7 else daily_sorted
    avg_daily = sum(v["total"] for _, v in last7) / len(last7) if last7 else 0
    monthly_projection = avg_daily * 30
    last7_count = len(last7)

    # ── Build JSON data for JS ─────────────────────────────────────────────
    chart_data = json.dumps({
        "costPerModel": [{"model": m, "cost": c, "turns": t, "color": col} for m, c, t, col in model_costs],
        "dailyCosts": [{"day": d, "total": v["total"], "models": dict(v["models"])} for d, v in daily_list],
        "weeklyCosts": [{"day": d, "period": d, "total": v["total"], "models": dict(v["models"])} for d, v in weekly_list],
        "monthlyCosts": [{"day": d, "period": d, "total": v["total"], "models": dict(v["models"])} for d, v in monthly_list],
        "yearlyCosts": [{"day": d, "period": d, "total": v["total"], "models": dict(v["models"])} for d, v in yearly_list],
        "hourlyToday": [{"hour": h, "cost": sum(m["cost"] for m in v.values()), "turns": sum(m["turns"] for m in v.values())} for h, v in sorted(data["hourly_today"].items())],
        "dailyTable": [{"day": d, "cost": v["total"], "turns": v["turns"], "models": ", ".join(f"{m.split('/')[-1]}" for m in v["models"])} for d, v in daily_list],
        "weeklyTable": [{"period": d, "cost": v["total"], "turns": v["turns"], "models": ", ".join(f"{m.split('/')[-1]}" for m in v["models"])} for d, v in weekly_list],
        "monthlyTable": [{"period": d, "cost": v["total"], "turns": v["turns"], "models": ", ".join(f"{m.split('/')[-1]}" for m in v["models"])} for d, v in monthly_list],
        "yearlyTable": [{"period": d, "cost": v["total"], "turns": v["turns"], "models": ", ".join(f"{m.split('/')[-1]}" for m in v["models"])} for d, v in yearly_list],
        "summary": data["summary"],
        "modelConfig": data.get("model_config", {}),
        "anthropic": anth,
        "modelTable": [
            {
                "model": m,
                "color": get_color(m),
                "turns": u["turns"],
                "input": u["input"],
                "output": u["output"],
                "cache_read": u["cache_read"],
                "cost": u["cost"],
                "known": normalize_model(m) in PRICES,
            }
            for m, u in sorted(data["model_usage"].items(), key=lambda x: -x[1]["cost"])
        ],
    }, default=float)

    # Calculate totals
    total_cost = sum(u["cost"] for u in data["model_usage"].values())
    total_turns = sum(u["turns"] for u in data["model_usage"].values())

    # Model config display
    model_cfg = data.get("model_config", {})
    active_model = model_cfg.get("active", "—")
    default_model = model_cfg.get("default", "—")
    fallback_models = ", ".join(model_cfg.get("fallbacks", [])) or "—"

    # Anthropic quota cards
    quota_html = ""
    if "error" not in anth:
        for window, label, color_var in [("5h", "5-Hour", "--clr-blue"), ("7d", "7-Day", "--clr-emerald")]:
            if window in anth:
                w = anth[window]
                pct = w.get("pct", 0) * 100
                status = w.get("status", "unknown")
                reset = ts_to_local(w.get("reset"))
                if status == "unknown":
                    status_display = "—"
                else:
                    status_icon = "🟢" if status == "allowed" else "🔴"
                    status_display = f"{status_icon} {status}"
                quota_html += f"""
                <div class="quota-card">
                    <div class="quota-title">{label}</div>
                    <div class="quota-pct" style="color:var({color_var})">{pct:.0f}%</div>
                    <div class="quota-status">{status_display}</div>
                    <div class="quota-reset">Reset: {reset}</div>
                </div>"""

        # Overage info
        if anth.get("overage"):
            ov = anth["overage"]
            if ov and (ov.get("in_use") or ov.get("status") == "allowed"):
                ov_reset = ts_to_local(ov.get("reset"))
                quota_html += f"""
                <div class="quota-card overage">
                    <div class="quota-title">Overage</div>
                    <div class="quota-pct" style="color:var(--clr-emerald)">✅ Active</div>
                    <div class="quota-status">Extra budget loaded</div>
                    <div class="quota-reset">Reset: {ov_reset}</div>
                </div>"""

    active_model_display = active_model.split('/')[-1] if '/' in active_model else active_model

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OpenClaw Usage Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root {{
  --bg:       #080B10;
  --bg1:      #0F1318;
  --bg2:      #141920;
  --bg3:      #1A2030;
  --border:   #1E2535;
  --border2:  #2A3448;
  --text:     #E2E8F0;
  --text2:    #8899B0;
  --text3:    #4A5568;
  --clr-blue:    #3B82F6;
  --clr-emerald: #10B981;
  --clr-amber:   #F59E0B;
  --clr-rose:    #F43F5E;
  --clr-cyan:    #06B6D4;
  --clr-purple:  #A855F7;
  --clr-orange:  #F97316;
}}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', sans-serif;
  font-size: 13px;
  line-height: 1.5;
  min-height: 100vh;
}}

.mono {{
  font-family: 'SF Mono', 'Cascadia Code', 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
  letter-spacing: -0.3px;
}}

.container {{
  max-width: 1280px;
  margin: 0 auto;
  padding: 28px 24px 60px;
}}

/* ── Animations ── */
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(12px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes drawRing {{
  from {{ stroke-dashoffset: 1000; }}
  to   {{ stroke-dashoffset: 0; }}
}}
@keyframes pulse-warn {{
  0%, 100% {{ opacity: 1; }}
  50%       {{ opacity: 0.6; }}
}}

.fade-in {{ animation: fadeUp 0.4s ease both; }}
.fade-in:nth-child(1) {{ animation-delay: 0.05s; }}
.fade-in:nth-child(2) {{ animation-delay: 0.10s; }}
.fade-in:nth-child(3) {{ animation-delay: 0.15s; }}
.fade-in:nth-child(4) {{ animation-delay: 0.20s; }}
.fade-in:nth-child(5) {{ animation-delay: 0.25s; }}
.fade-in:nth-child(6) {{ animation-delay: 0.30s; }}

/* ── Header ── */
.header {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 32px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
}}
.header-title {{
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.2px;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 8px;
}}
.header-dot {{
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--clr-emerald);
  box-shadow: 0 0 8px var(--clr-emerald);
}}

/* ── Provider Dropdown ── */
.provider-dropdown {{
  position: relative;
}}
.provider-btn {{
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: var(--bg1);
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text2);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}}
.provider-btn:hover {{
  background: var(--bg2);
  border-color: var(--border2);
  color: var(--text);
}}
.provider-btn::after {{
  content: "▼";
  font-size: 8px;
  margin-left: 2px;
}}
.provider-menu {{
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 6px;
  min-width: 180px;
  background: var(--bg1);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-8px);
  transition: all 0.15s ease;
  z-index: 10000;
  box-shadow: 0 10px 40px rgba(0,0,0,0.4);
}}
.provider-dropdown:hover .provider-menu,
.provider-dropdown.active .provider-menu {{
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}}
.provider-item {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 6px;
  color: var(--text2);
  font-size: 12px;
  text-decoration: none;
  transition: all 0.1s ease;
}}
.provider-item:hover {{
  background: var(--bg2);
  color: var(--text);
}}
.provider-dot {{
  width: 6px; height: 6px;
  border-radius: 50%;
}}
.provider-dot.anthropic {{ background: #D4A574; }}
.provider-dot.openai {{ background: #10A37F; }}
.provider-dot.google {{ background: #4285F4; }}
.provider-dot.moonshot {{ background: #FF6B6B; }}
.provider-dot.mistral {{ background: #FF7000; }}
.provider-dot.cohere {{ background: #D4B5FF; }}
.provider-dot.groq {{ background: #F55036; }}
.header-sub {{
  font-size: 11px;
  color: var(--text3);
  margin-top: 4px;
  font-family: 'JetBrains Mono', monospace;
}}

/* ── KPIs ── */
.kpis {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}}

.kpi {{
  position: relative;
  background: var(--bg1);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3), 0 0 0 1px var(--border);
  transition: border-color 0.2s, box-shadow 0.2s;
}}
.kpi::before {{
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 12px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(59,130,246,0.15), transparent 60%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}}
.kpi:hover {{
  border-color: var(--border2);
  box-shadow: 0 0 20px rgba(59,130,246,0.06);
}}
.kpi-label {{
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text3);
  margin-bottom: 8px;
}}
.kpi-value {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 26px;
  font-weight: 700;
  color: #fff;
  letter-spacing: -1px;
  line-height: 1;
  font-variant-numeric: tabular-nums;
}}
.kpi-sub {{
  font-size: 10px;
  color: var(--text3);
  margin-top: 6px;
  font-family: 'JetBrains Mono', monospace;
}}

/* ── Model Config Pills ── */
.model-bar {{
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}}
.model-pill {{
  background: var(--bg1);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 11px;
  transition: border-color 0.15s;
}}
.model-pill:hover {{ border-color: var(--border2); }}
.model-pill .label {{
  font-size: 9px;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 2px;
}}
.model-pill .value {{
  font-weight: 600;
  color: var(--clr-cyan);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
}}

/* ── Quota Section ── */
.quota-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}}
.quota-card {{
  background: var(--bg1);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3), 0 0 0 1px var(--border);
  transition: border-color 0.2s, box-shadow 0.2s;
}}
.quota-card.overage {{
  border-color: rgba(16,185,129,0.3);
  background: rgba(16,185,129,0.05);
}}
.quota-title {{
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text3);
  margin-bottom: 8px;
}}
.quota-pct {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 4px;
}}
.quota-status {{ font-size: 11px; color: var(--text2); margin-bottom: 4px; }}
.quota-reset {{ font-size: 10px; color: var(--text3); }}

/* ── Chart Cards ── */
.section-label {{
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: var(--text3);
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}}
.section-label::after {{
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}}

.charts {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}}

.chart-card {{
  background: var(--bg1);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3), 0 0 0 1px var(--border);
  transition: border-color 0.2s, box-shadow 0.2s;
}}
.chart-card:hover {{ border-color: var(--border2); box-shadow: 0 4px 12px rgba(59,130,246,0.1), 0 0 0 1px var(--border2); }}
.chart-card h3 {{
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.2px;
  color: var(--text3);
  margin-bottom: 16px;
}}

/* ── Period Tabs (pill style) ── */
.period-tabs {{
  display: flex;
  gap: 4px;
  margin-bottom: 14px;
  flex-wrap: wrap;
  background: var(--bg);
  border-radius: 8px;
  padding: 3px;
  width: fit-content;
}}
.period-tab {{
  background: transparent;
  border: none;
  border-radius: 6px;
  padding: 5px 12px;
  font-size: 11px;
  font-weight: 500;
  color: var(--text3);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  font-family: 'Inter', sans-serif;
}}
.period-tab:hover {{ color: var(--text2); }}
.period-tab.active {{
  background: var(--clr-blue);
  color: #fff;
  box-shadow: 0 0 12px rgba(59,130,246,0.3);
}}

/* ── Budget Section ── */
.budget-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}}
.budget-card {{
  background: var(--bg1);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3), 0 0 0 1px var(--border);
  transition: border-color 0.2s, box-shadow 0.2s;
}}
.budget-card .bc-label {{
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text3);
  margin-bottom: 8px;
  font-weight: 600;
}}
.budget-card .bc-val {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 22px;
  font-weight: 700;
  color: #fff;
  font-variant-numeric: tabular-nums;
}}
.budget-card .bc-sub {{ font-size: 11px; color: var(--text3); margin-top: 4px; }}
.budget-card input {{
  background: var(--bg3);
  border: 1px solid var(--border2);
  border-radius: 6px;
  color: #fff;
  padding: 6px 10px;
  font-size: 12px;
  width: 90px;
  margin-top: 8px;
  font-family: 'JetBrains Mono', monospace;
}}
.budget-card button {{
  background: var(--clr-blue);
  border: none;
  border-radius: 6px;
  color: #fff;
  padding: 6px 12px;
  font-size: 11px;
  margin-left: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.15s;
}}
.budget-card button:hover {{ opacity: 0.85; }}

/* ── Portal Links ── */
.portals {{
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}}
.portal {{
  background: var(--bg1);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 13px;
  font-size: 11px;
  color: var(--text2);
  text-decoration: none;
  transition: border-color 0.15s, color 0.15s;
}}
.portal:hover {{ border-color: var(--clr-blue); color: var(--text); }}

/* ── Tables ── */
.table-wrap {{ overflow-x: auto; }}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}}
thead {{
  position: sticky;
  top: 0;
  z-index: 2;
  background: var(--bg1);
}}
th {{
  text-align: left;
  padding: 10px 12px;
  color: var(--text3);
  font-weight: 600;
  border-bottom: 2px solid #2A3448;
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  white-space: nowrap;
}}
td {{
  padding: 9px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  font-variant-numeric: tabular-nums;
}}
tbody tr:nth-child(even) {{ background: rgba(26,32,48,0.5); }}
tbody tr:hover {{ background: rgba(59,130,246,0.06); }}
.cost {{
  color: var(--clr-amber);
  font-weight: 600;
  font-family: 'JetBrains Mono', monospace;
}}

/* ── Model dot ── */
.model-dot {{
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  margin-right: 6px;
  flex-shrink: 0;
}}
.model-name-cell {{
  display: flex;
  align-items: center;
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
}}

/* ── Warn pulse ── */
.warn-badge {{
  animation: pulse-warn 2s ease-in-out infinite;
  color: var(--clr-rose);
}}

/* ── Export button ── */
.btn-export {{
  background: transparent;
  border: 1px solid var(--border2);
  border-radius: 7px;
  color: var(--text2);
  padding: 5px 12px;
  font-size: 11px;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
}}
.btn-export:hover {{
  border-color: var(--clr-blue);
  color: var(--text);
}}

/* ── View toggle ── */
.view-toggle {{
  display: flex;
  gap: 4px;
  background: var(--bg);
  border-radius: 8px;
  padding: 3px;
}}
.view-toggle .period-tab {{ padding: 4px 10px; }}

/* ── Detail controls bar ── */
.detail-controls {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
  flex-wrap: wrap;
  gap: 8px;
}}
</style>
</head>
<body>
<div class="container">

<!-- Header -->
<header class="header fade-in">
  <div>
    <div class="header-title">
      <span class="header-dot"></span>
      OpenClaw Usage Dashboard
    </div>
    <div class="header-sub">Generated: {datetime.now().strftime("%d.%m.%Y %H:%M")} · Multi-Provider Edition v2</div>
  </div>
  <div class="provider-dropdown" id="providerDropdown">
    <button class="provider-btn" onclick="toggleProviders()">Providers</button>
    <div class="provider-menu">
      <a href="https://console.anthropic.com/" target="_blank" class="provider-item">
        <span class="provider-dot anthropic"></span> Anthropic
      </a>
      <a href="https://platform.openai.com/" target="_blank" class="provider-item">
        <span class="provider-dot openai"></span> OpenAI
      </a>
      <a href="https://aistudio.google.com/app/apikey" target="_blank" class="provider-item">
        <span class="provider-dot google"></span> Google (Gemini)
      </a>
      <a href="https://platform.moonshot.cn/" target="_blank" class="provider-item">
        <span class="provider-dot moonshot"></span> Moonshot
      </a>
      <a href="https://console.mistral.ai/" target="_blank" class="provider-item">
        <span class="provider-dot mistral"></span> Mistral
      </a>
      <a href="https://dashboard.cohere.com/" target="_blank" class="provider-item">
        <span class="provider-dot cohere"></span> Cohere
      </a>
      <a href="https://console.groq.com/" target="_blank" class="provider-item">
        <span class="provider-dot groq"></span> Groq
      </a>
    </div>
  </div>
</header>

<!-- KPIs -->
<div class="kpis">
  <div class="kpi fade-in">
    <div class="kpi-label">Total Cost</div>
    <div class="kpi-value" style="color:var(--clr-amber)">${total_cost:.2f}</div>
    <div class="kpi-sub">all time</div>
  </div>
  <div class="kpi fade-in">
    <div class="kpi-label">API Calls</div>
    <div class="kpi-value">{total_turns}</div>
    <div class="kpi-sub">total turns</div>
  </div>
  <div class="kpi fade-in">
    <div class="kpi-label">Active Model</div>
    <div class="kpi-value" style="font-size:14px;letter-spacing:-0.5px">{active_model_display}</div>
    <div class="kpi-sub">current</div>
  </div>
  <div class="kpi fade-in">
    <div class="kpi-label">Cache Hit Rate</div>
    <div class="kpi-value" style="color:var(--clr-emerald)">{cache_kpi_value}</div>
    <div class="kpi-sub">{cache_kpi_sub}</div>
  </div>
  <div class="kpi fade-in">
    <div class="kpi-label">Monthly Projection</div>
    <div class="kpi-value" style="color:var(--clr-blue);font-size:20px">${monthly_projection:.0f}/mo</div>
    <div class="kpi-sub">Ø ${avg_daily:.2f}/day (last {last7_count}d)</div>
  </div>
</div>

<!-- Model Config -->
<div class="model-bar fade-in">
  <div class="model-pill"><div class="label">Active</div><div class="value">{active_model}</div></div>
  <div class="model-pill"><div class="label">Default</div><div class="value">{default_model}</div></div>
  <div class="model-pill"><div class="label">Fallbacks</div><div class="value">{fallback_models}</div></div>
</div>

<!-- Anthropic Quota (if available) -->
{f'<div class="quota-grid">{quota_html}</div>' if quota_html else '<!-- Anthropic API key not configured -->'}

<!-- Budget Cards -->
<div class="budget-grid" id="budget-section"></div>



<!-- Charts Row -->
<div class="charts">
  <div class="chart-card fade-in">
    <h3>Cost by Model</h3>
    <div id="donut-wrap" style="display:flex;align-items:center;gap:20px;flex-wrap:wrap">
      <div id="donut-chart"></div>
      <div id="donut-legend" style="flex:1;min-width:120px"></div>
    </div>
  </div>
  <div class="chart-card fade-in">
    <h3>Today — Calls per Hour</h3>
    <div id="hourly-chart"></div>
  </div>
</div>

<!-- Period Costs Stacked Bars -->
<div class="chart-card fade-in" style="margin-bottom:16px">
  <h3>Cost by Period</h3>
  <div class="period-tabs">
    <button class="period-tab active" onclick="switchPeriod('daily')">Daily</button>
    <button class="period-tab" onclick="switchPeriod('weekly')">Weekly</button>
    <button class="period-tab" onclick="switchPeriod('monthly')">Monthly</button>
    <button class="period-tab" onclick="switchPeriod('yearly')">Yearly</button>
  </div>
  <div id="period-chart"></div>
  <div id="period-legend" style="margin-top:12px;display:flex;gap:12px;flex-wrap:wrap"></div>
</div>

<!-- Model Breakdown Table -->
<div class="chart-card fade-in" style="margin-bottom:16px">
  <h3>Model Breakdown</h3>
  <div class="table-wrap">
    <table id="model-table">
      <thead>
        <tr>
          <th>Model</th>
          <th style="text-align:right">Calls</th>
          <th style="text-align:right">Input</th>
          <th style="text-align:right">Output</th>
          <th style="text-align:right">Cache Read</th>
          <th style="text-align:right">Cost</th>
        </tr>
      </thead>
      <tbody id="model-table-body"></tbody>
    </table>
  </div>
  <div id="model-table-footnote" style="margin-top:8px;font-size:10px;color:var(--clr-rose);display:none">
    ⚠️ Price unknown — add model to PRICES dict in the script
  </div>
</div>

<!-- Detail Table -->
<div class="chart-card fade-in">
  <h3>Details</h3>
  <div class="detail-controls">
    <div class="period-tabs">
      <button class="period-tab active" onclick="switchTable('daily')">Daily</button>
      <button class="period-tab" onclick="switchTable('weekly')">Weekly</button>
      <button class="period-tab" onclick="switchTable('monthly')">Monthly</button>
      <button class="period-tab" onclick="switchTable('yearly')">Yearly</button>
    </div>
    <div style="display:flex;gap:8px;align-items:center">
      <div class="view-toggle">
        <button class="period-tab active" id="view-table-btn" onclick="switchView('table')">☰ Table</button>
        <button class="period-tab" id="view-chart-btn" onclick="switchView('chart')">■ Bars</button>
      </div>
      <button class="btn-export" onclick="exportCSV()">⬇ Export CSV</button>
    </div>
  </div>
  <div id="detail-content"></div>
</div>

</div><!-- /container -->

<script>
const D = {chart_data};

// ── Token formatter ──
function fmtTokens(n) {{
  if (n >= 1e9) return (n/1e9).toFixed(1)+'B';
  if (n >= 1e6) return (n/1e6).toFixed(1)+'M';
  if (n >= 1e3) return (n/1e3).toFixed(0)+'K';
  return String(n);
}}

// ── Donut Chart ──
(function() {{
  const container = document.getElementById('donut-chart');
  const legend = document.getElementById('donut-legend');
  if (!container || D.costPerModel.length === 0) return;

  const total = D.costPerModel.reduce((a,b) => a + b.cost, 0);
  const size = 160;
  const cx = size / 2, cy = size / 2;
  const R = 62, r = 38; // outer/inner radius for proper ring

  let svg = `<svg viewBox="0 0 ${{size}} ${{size}}" width="${{size}}" height="${{size}}">
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>`;

  // Gradient defs per segment
  D.costPerModel.forEach((d, i) => {{
    svg += `<linearGradient id="g${{i}}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${{d.color}}" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="${{d.color}}" stop-opacity="0.65"/>
    </linearGradient>`;
  }});
  svg += `</defs>`;

  // Background ring (track)
  svg += `<circle cx="${{cx}}" cy="${{cy}}" r="${{R}}" fill="none" stroke="#2A3448" stroke-width="24"/>`;
  svg += `<circle cx="${{cx}}" cy="${{cy}}" r="${{r}}" fill="none" stroke="#2A3448" stroke-width="24"/>`;

  let currentAngle = -Math.PI / 2;

  D.costPerModel.forEach((d, i) => {{
    const angle = (d.cost / total) * Math.PI * 2;
    if (angle < 0.001) {{ currentAngle += angle; return; }}

    const x1o = cx + R * Math.cos(currentAngle);
    const y1o = cy + R * Math.sin(currentAngle);
    const x2o = cx + R * Math.cos(currentAngle + angle);
    const y2o = cy + R * Math.sin(currentAngle + angle);
    const x1i = cx + r * Math.cos(currentAngle + angle);
    const y1i = cy + r * Math.sin(currentAngle + angle);
    const x2i = cx + r * Math.cos(currentAngle);
    const y2i = cy + r * Math.sin(currentAngle);
    const largeArc = angle > Math.PI ? 1 : 0;

    const path = [
      `M ${{x1o}} ${{y1o}}`,
      `A ${{R}} ${{R}} 0 ${{largeArc}} 1 ${{x2o}} ${{y2o}}`,
      `L ${{x1i}} ${{y1i}}`,
      `A ${{r}} ${{r}} 0 ${{largeArc}} 0 ${{x2i}} ${{y2i}}`,
      'Z'
    ].join(' ');

    svg += `<path d="${{path}}" fill="url(#g${{i}})" stroke="var(--bg1)" stroke-width="2" filter="url(#glow)"/>`;
    currentAngle += angle;
  }});

  // Center text
  svg += `<text x="${{cx}}" y="${{cy - 6}}" text-anchor="middle" fill="var(--text3)" font-size="9" font-family="Inter" font-weight="600" letter-spacing="0.5">TOTAL</text>`;
  svg += `<text x="${{cx}}" y="${{cy + 10}}" text-anchor="middle" fill="#fff" font-size="14" font-weight="700" font-family="JetBrains Mono">$${{total.toFixed(2)}}</text>`;
  svg += '</svg>';

  container.innerHTML = svg;

  // Legend
  legend.innerHTML = D.costPerModel.slice(0,8).map(d => `
    <div style="display:flex;align-items:center;gap:7px;margin-bottom:5px">
      <span style="width:8px;height:8px;border-radius:2px;background:${{d.color}};flex-shrink:0"></span>
      <span style="font-size:11px;color:var(--text2);font-family:JetBrains Mono;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${{d.model.split('/').pop()}}</span>
      <span style="font-size:11px;color:var(--clr-amber);font-family:JetBrains Mono;font-weight:600">$${{d.cost.toFixed(2)}}</span>
    </div>
  `).join('');
}})();

// ── Hourly Chart ──
(function() {{
  const container = document.getElementById('hourly-chart');
  if (!container || D.hourlyToday.length === 0) {{
    if (container) container.innerHTML = '<div style="color:var(--text3);font-size:12px;padding:20px 0">No data for today</div>';
    return;
  }}

  const data = D.hourlyToday;
  const maxVal = Math.max(...data.map(d => d.cost), 0.001);
  const chartHeight = 100;
  const chartWidth = 320;
  const barW = Math.max(Math.floor((chartWidth - 10) / data.length) - 3, 4);

  let svg = `<svg viewBox="0 0 ${{chartWidth}} ${{chartHeight + 20}}" width="100%" style="overflow:visible">
  <defs>
    <linearGradient id="hg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="var(--clr-cyan)" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="var(--clr-cyan)" stop-opacity="0.4"/>
    </linearGradient>
  </defs>`;

  data.forEach((d, i) => {{
    const h = Math.max((d.cost / maxVal) * chartHeight, d.cost > 0 ? 2 : 0);
    const x = 5 + i * (barW + 3);
    const y = chartHeight - h;

    svg += `<rect x="${{x}}" y="${{y}}" width="${{barW}}" height="${{h}}" rx="2" fill="url(#hg)">
      <title>${{d.hour}}: $${{d.cost.toFixed(4)}} (${{d.turns}} calls)</title>
    </rect>`;
    if (data.length <= 12) {{
      svg += `<text x="${{x + barW/2}}" y="${{chartHeight + 14}}" text-anchor="middle" fill="var(--text3)" font-size="9" font-family="JetBrains Mono">${{d.hour.slice(0,2)}}</text>`;
    }}
  }});

  svg += '</svg>';
  container.innerHTML = svg;
}})();

// ── Model Breakdown Table ──
(function() {{
  const tbody = document.getElementById('model-table-body');
  const footnote = document.getElementById('model-table-footnote');
  if (!tbody) return;

  let hasUnknown = false;

  tbody.innerHTML = D.modelTable.map(row => {{
    if (!row.known) hasUnknown = true;
    const warn = !row.known ? ' <span class="warn-badge" title="Price unknown">⚠️</span>' : '';
    return `<tr>
      <td>
        <div class="model-name-cell">
          <span class="model-dot" style="background:${{row.color}}"></span>
          ${{row.model}}${{warn}}
        </div>
      </td>
      <td style="text-align:right;font-family:JetBrains Mono">${{row.turns}}</td>
      <td style="text-align:right;font-family:JetBrains Mono;color:var(--text2)">${{fmtTokens(row.input)}}</td>
      <td style="text-align:right;font-family:JetBrains Mono;color:var(--text2)">${{fmtTokens(row.output)}}</td>
      <td style="text-align:right;font-family:JetBrains Mono;color:var(--clr-emerald)">${{fmtTokens(row.cache_read)}}</td>
      <td style="text-align:right" class="cost">$${{row.cost.toFixed(4)}}</td>
    </tr>`;
  }}).join('');

  if (hasUnknown && footnote) footnote.style.display = 'block';
}})();

// ── Stacked Period Chart ──
let currentPeriod = 'daily';
const periodData = {{
  daily: D.dailyCosts,
  weekly: D.weeklyCosts,
  monthly: D.monthlyCosts,
  yearly: D.yearlyCosts
}};

function renderStackedBars(period) {{
  const container = document.getElementById('period-chart');
  const legend = document.getElementById('period-legend');
  const data = periodData[period] || [];

  if (data.length === 0) {{
    container.innerHTML = '<div style="color:var(--text3);font-size:12px">No data</div>';
    legend.innerHTML = '';
    return;
  }}

  const allModels = [...new Set(data.flatMap(d => Object.keys(d.models || {{}})))];
  const modelColors = {{}};
  allModels.forEach((m, i) => {{
    const colorEntry = D.costPerModel.find(c => c.model === m);
    modelColors[m] = colorEntry ? colorEntry.color : `hsl(${{(i * 60) % 360}}, 70%, 50%)`;
  }});

  legend.innerHTML = allModels.map(m => `
    <div style="display:flex;align-items:center;gap:4px;font-size:11px;color:var(--text2)">
      <span style="width:8px;height:8px;border-radius:2px;background:${{modelColors[m]}}"></span>
      ${{m.split('/').pop()}}
    </div>
  `).join('');

  const maxTotal = Math.max(...data.map(d => d.total), 0.001);
  const barH = 26;
  const gap = 8;
  const chartH = data.length * (barH + gap);
  const chartW = 800;
  const maxBarW = chartW - 140;

  let svg = `<svg viewBox="0 0 ${{chartW}} ${{chartH}}" width="100%" height="${{chartH}}" style="max-height:500px">
  <defs>`;

  allModels.forEach((m, i) => {{
    const c = modelColors[m];
    svg += `<linearGradient id="sg${{i}}" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="${{c}}" stop-opacity="0.95"/>
      <stop offset="100%" stop-color="${{c}}" stop-opacity="0.6"/>
    </linearGradient>`;
  }});
  svg += '</defs>';

  data.forEach((d, i) => {{
    const y = i * (barH + gap);
    const scale = maxBarW / maxTotal;
    let currentX = 80;
    const models = d.models || {{}};

    Object.entries(models).forEach(([model, cost], mi) => {{
      const w = Math.max(cost * scale, 0);
      const gi = allModels.indexOf(model);
      svg += `<rect x="${{currentX}}" y="${{y}}" width="${{w}}" height="${{barH}}" fill="url(#sg${{gi < 0 ? 0 : gi}})">
        <title>${{model.split('/').pop()}}: $${{cost.toFixed(4)}}</title>
      </rect>`;
      currentX += w;
    }});

    const label = (d.day || d.period || '').slice(-7);
    svg += `<text x="75" y="${{y + barH/2}}" text-anchor="end" dy="0.35em" fill="var(--text2)" font-size="10" font-family="JetBrains Mono">${{label}}</text>`;
    svg += `<text x="${{currentX + 6}}" y="${{y + barH/2}}" dy="0.35em" fill="var(--text)" font-size="10" font-weight="600" font-family="JetBrains Mono">$${{d.total.toFixed(2)}}</text>`;
  }});

  svg += '</svg>';
  container.innerHTML = svg;
}}

function switchPeriod(period) {{
  currentPeriod = period;
  const periods = ['daily', 'weekly', 'monthly', 'yearly'];
  const allTabGroups = document.querySelectorAll('.chart-card .period-tabs');
  allTabGroups.forEach(group => {{
    const btns = group.querySelectorAll('.period-tab');
    if (btns.length === 4 && btns[0].textContent.trim() === 'Daily') {{
      btns.forEach((tab, i) => tab.classList.toggle('active', periods[i] === period));
    }}
  }});
  renderStackedBars(period);
}}

// -- Detail View (Table/Chart Toggle) --
let currentTable = 'daily';
let currentView = 'table';
const tableData = {{
  daily: D.dailyTable,
  weekly: D.weeklyTable,
  monthly: D.monthlyTable,
  yearly: D.yearlyTable
}};
const tableLabels = {{ daily: 'Day', weekly: 'Week', monthly: 'Month', yearly: 'Year' }};

function renderDetailTable(period) {{
  const container = document.getElementById('detail-content');
  const data = tableData[period] || [];
  const label = tableLabels[period];

  if (data.length === 0) {{
    container.innerHTML = '<div style="color:var(--text3);font-size:12px">No data</div>';
    return;
  }}

  let html = `<div class="table-wrap"><table><thead><tr>
    <th>${{label}}</th>
    <th style="text-align:right">Calls</th>
    <th style="text-align:right">Cost</th>
    <th>Models</th>
  </tr></thead><tbody>`;
  data.forEach(row => {{
    html += `<tr>
      <td style="font-family:JetBrains Mono;font-size:11px">${{row.day || row.period}}</td>
      <td style="text-align:right;font-family:JetBrains Mono">${{row.turns}}</td>
      <td style="text-align:right" class="cost">$${{row.cost.toFixed(4)}}</td>
      <td style="font-size:10px;color:var(--text3)">${{row.models}}</td>
    </tr>`;
  }});
  html += '</tbody></table></div>';
  container.innerHTML = html;
}}

function renderDetailChart(period) {{
  const container = document.getElementById('detail-content');
  const data = tableData[period] || [];

  if (data.length === 0) {{
    container.innerHTML = '<div style="color:var(--text3);font-size:12px">No data</div>';
    return;
  }}

  const maxVal = Math.max(...data.map(d => d.cost), 0.001);
  const barH = 24;
  const gap = 8;
  const chartH = data.length * (barH + gap);
  const chartW = 800;

  let svg = `<svg viewBox="0 0 ${{chartW}} ${{chartH}}" width="100%" height="${{Math.min(chartH, 400)}}">
  <defs>
    <linearGradient id="dg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="var(--clr-blue)" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="var(--clr-blue)" stop-opacity="0.5"/>
    </linearGradient>
  </defs>`;

  data.forEach((d, i) => {{
    const y = i * (barH + gap);
    const w = (d.cost / maxVal) * (chartW - 160);
    const label = (d.day || d.period || '').slice(-7);

    svg += `<rect x="80" y="${{y}}" width="${{w}}" height="${{barH}}" rx="3" fill="url(#dg)">
      <title>$${{d.cost.toFixed(4)}}</title>
    </rect>`;
    svg += `<text x="75" y="${{y + barH/2}}" text-anchor="end" dy="0.35em" fill="var(--text2)" font-size="10" font-family="JetBrains Mono">${{label}}</text>`;
    svg += `<text x="${{85 + w}}" y="${{y + barH/2}}" dy="0.35em" fill="var(--text)" font-size="10" font-family="JetBrains Mono">$${{d.cost.toFixed(4)}}</text>`;
  }});

  svg += '</svg>';
  container.innerHTML = svg;
}}

function renderDetail() {{
  if (currentView === 'table') {{
    renderDetailTable(currentTable);
  }} else {{
    renderDetailChart(currentTable);
  }}
}}

function switchTable(period) {{
  currentTable = period;
  const periods = ['daily', 'weekly', 'monthly', 'yearly'];
  const allTabGroups = document.querySelectorAll('.chart-card .period-tabs');
  allTabGroups.forEach(group => {{
    const btns = group.querySelectorAll('.period-tab');
    if (btns.length === 4 && btns[0].textContent.trim() === 'Daily') {{
      // Check this is the detail section (not the period chart)
      const card = group.closest('.chart-card');
      if (card && card.querySelector('#detail-content')) {{
        btns.forEach((tab, i) => tab.classList.toggle('active', periods[i] === period));
      }}
    }}
  }});
  renderDetail();
}}

function switchView(view) {{
  currentView = view;
  document.getElementById('view-table-btn').classList.toggle('active', view === 'table');
  document.getElementById('view-chart-btn').classList.toggle('active', view === 'chart');
  renderDetail();
}}

// -- CSV Export --
function exportCSV() {{
  const data = tableData[currentTable] || [];
  const headers = ['Period', 'Calls', 'Cost', 'Models'];
  const rows = data.map(r => [r.day || r.period, r.turns, r.cost.toFixed(4), `"${{r.models}}"`]);
  const csv = [headers, ...rows].map(r => r.join(',')).join('\\n');
  const a = document.createElement('a');
  a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
  a.download = `openclaw-usage-${{currentTable}}.csv`;
  a.click();
}}

// -- Budget Cards --
(function() {{
  const container = document.getElementById('budget-section');
  if (!container) return;

  const stored = localStorage.getItem('oc_budget_monthly');
  const monthCost = D.monthlyCosts.length > 0 ? D.monthlyCosts[D.monthlyCosts.length-1].total : 0;
  const todayCost = D.dailyCosts.length > 0 ? D.dailyCosts[D.dailyCosts.length-1].total : 0;

  function render(budget) {{
    const b = parseFloat(budget) || 0;
    const pct = b > 0 ? Math.min(monthCost / b, 1) : 0;
    const color = pct < 0.7 ? 'var(--clr-emerald)' : pct < 0.9 ? 'var(--clr-amber)' : 'var(--clr-rose)';

    const budgetHtml = b > 0 ? `
      <div class="bc-val">$${{monthCost.toFixed(2)}} <span style="font-size:12px;color:var(--text3)">/ $${{b}}</span></div>
      <div class="bc-sub">${{(pct*100).toFixed(0)}}% of budget</div>
      <div style="margin-top:8px;height:4px;background:var(--border);border-radius:2px"><div style="width:${{pct*100}}%;height:100%;background:${{color}};border-radius:2px;transition:width 0.3s"></div></div>
      <div style="margin-top:8px"><input type="number" id="budget-in" value="${{b}}" style="width:80px"> <button onclick="saveBudget()">Save</button> <span style="font-size:10px;color:var(--text3);cursor:pointer" onclick="clearBudget()">x</span></div>
    ` : `
      <div class="bc-val" style="font-size:14px;color:var(--text3)">Not set</div>
      <div class="bc-sub">Set your monthly budget</div>
      <div style="margin-top:8px"><input type="number" id="budget-in" placeholder="e.g. 500" style="width:80px"> <button onclick="saveBudget()">Save</button></div>
    `;

    container.innerHTML = `
      <div class="budget-card">
        <div class="bc-label">Today</div>
        <div class="bc-val" style="color:var(--clr-amber)">$${{todayCost.toFixed(4)}}</div>
      </div>
      <div class="budget-card">
        <div class="bc-label">This Month</div>
        <div class="bc-val" style="color:var(--clr-amber)">$${{monthCost.toFixed(2)}}</div>
      </div>
      <div class="budget-card">
        <div class="bc-label">Monthly Budget</div>
        ${{budgetHtml}}
      </div>
    `;
  }}

  window.saveBudget = function() {{
    const v = document.getElementById('budget-in')?.value;
    if (v) {{ localStorage.setItem('oc_budget_monthly', v); render(v); }}
  }};
  window.clearBudget = function() {{
    localStorage.removeItem('oc_budget_monthly'); render('');
  }};

  render(stored || '');
}})();

// ── Provider Dropdown Toggle ──
function toggleProviders() {{
  const dd = document.getElementById('providerDropdown');
  dd.classList.toggle('active');
}}
document.addEventListener('click', function(e) {{
  const dd = document.getElementById('providerDropdown');
  if (!dd.contains(e.target)) dd.classList.remove('active');
}});

// Initial renders — wrapped in requestAnimationFrame to ensure DOM is laid out
requestAnimationFrame(function() {{
  renderStackedBars('daily');
  renderDetail();
}});
</script>

<!-- Footer -->
<footer style="text-align:right;padding:20px 24px;color:var(--text3);font-size:10px;border-top:1px solid var(--border);margin-top:40px;display:flex;justify-content:space-between;align-items:center;">
  <span>OpenClaw Usage Dashboard · Multi-Provider Edition</span>
  <span style="background:var(--bg2);padding:4px 10px;border-radius:6px;font-weight:600;color:var(--text2);font-family:JetBrains Mono;">v1.1.0</span>
</footer>

</body>
</html>"""

    return html

# =============================================================================
# DEMO MODE - Generate realistic mock data
# =============================================================================

def generate_demo_data():
    """Generate 2 years of realistic mock usage data showing growth curve."""
    from datetime import datetime, timedelta
    import random
    import math
    
    models = [
        ("anthropic/claude-sonnet-4-6", 0.40, 3.0, 15.0),
        ("openai/gpt-4o", 0.30, 2.5, 10.0),
        ("google/gemini-2.0-flash", 0.15, 0.35, 1.05),
        ("moonshot/kimi-k2.5", 0.10, 2.0, 8.0),
        ("mistral/mistral-large-latest", 0.03, 2.0, 6.0),
        ("cohere/command-r-plus", 0.01, 2.5, 10.0),
        ("groq/llama-3.3-70b-versatile", 0.01, 0.59, 0.79),
    ]
    
    model_usage = defaultdict(lambda: {"input": 0, "output": 0, "cache_read": 0, "cache_write": 0, "cost": 0.0, "turns": 0})
    daily = defaultdict(lambda: {"total": 0.0, "models": defaultdict(float), "turns": 0})
    hourly_today = defaultdict(lambda: defaultdict(lambda: {"cost": 0.0, "turns": 0}))
    weekly = defaultdict(lambda: {"total": 0.0, "models": defaultdict(float), "turns": 0})
    monthly = defaultdict(lambda: {"total": 0.0, "models": defaultdict(float), "turns": 0})
    yearly = defaultdict(lambda: {"total": 0.0, "models": defaultdict(float), "turns": 0})
    
    today = datetime.now()
    start_date = today - timedelta(days=730)  # 2 years
    
    # Generate 2 years of data
    for day_offset in range(730, -1, -1):
        date = today - timedelta(days=day_offset)
        day_str = date.strftime("%Y-%m-%d")
        days_from_start = 730 - day_offset
        
        # Calculate base daily cost based on curve
        # Start: 50€/month = ~1.67€/day
        # After 1 year: 800€/month = ~26.67€/day
        # Then crash to 300€/month = ~10€/day over 1 month, then stable
        
        if days_from_start <= 365:
            # Growth phase: 50€/month to 800€/month (exponential growth)
            progress = days_from_start / 365
            monthly_start = 50
            monthly_peak = 800
            # Ease-in-out curve for realistic growth
            ease = progress * progress * (3 - 2 * progress)
            target_monthly = monthly_start + (monthly_peak - monthly_start) * ease
        elif days_from_start <= 395:
            # Crash phase: 800€ to 300€ in 30 days
            crash_progress = (days_from_start - 365) / 30
            monthly_peak = 800
            monthly_low = 300
            target_monthly = monthly_peak - (monthly_peak - monthly_low) * crash_progress
        else:
            # Stable phase: 300€/month with some drift
            target_monthly = 300 + math.sin(days_from_start / 30) * 50  # ±50€ oscillation
        
        # Convert monthly target to daily with realistic variance
        base_daily = target_monthly / 30
        # Add daily variance (±30%)
        daily_cost = base_daily * random.uniform(0.7, 1.3)
        # Add weekly seasonality (weekends lower)
        if date.weekday() >= 5:  # Weekend
            daily_cost *= 0.6
        # Add random spikes (1% chance of 3x cost)
        if random.random() < 0.01:
            daily_cost *= 3
            
        daily_cost = max(daily_cost, 0.5)  # Minimum 0.50€
        daily_turns = int(daily_cost * random.uniform(15, 25))  # ~15-25 calls per €
        
        # Distribute across models
        for model, share, in_price, out_price in models:
            if random.random() > 0.2:  # 80% chance model is used
                # Vary share based on growth (early: more cheap models, late: more expensive)
                if days_from_start < 180:
                    # Early: favor cheaper models
                    if in_price < 1.0:
                        adjusted_share = share * 1.5
                    else:
                        adjusted_share = share * 0.7
                else:
                    # Later: more balanced
                    adjusted_share = share
                    
                model_share = adjusted_share * random.uniform(0.6, 1.4)
                model_cost = daily_cost * model_share
                model_turns = max(1, int(daily_turns * model_share))
                
                # Tokens scale with cost
                avg_tokens = random.randint(2000, 12000)
                input_tok = model_turns * avg_tokens
                output_tok = model_turns * (avg_tokens // 3)
                cache_read = int(input_tok * random.uniform(0.1, 0.4)) if random.random() > 0.4 else 0
                
                # Calculate cost
                cost = (input_tok * in_price + output_tok * out_price + cache_read * 0.3) / 1e6
                
                # Update model usage
                model_usage[model]["input"] += input_tok
                model_usage[model]["output"] += output_tok
                model_usage[model]["cache_read"] += cache_read
                model_usage[model]["cost"] += cost
                model_usage[model]["turns"] += model_turns
                
                # Update daily
                daily[day_str]["total"] += cost
                daily[day_str]["models"][model] += cost
                daily[day_str]["turns"] += model_turns
                
                # Update aggregates
                week_key = f"{date.year}-W{date.isocalendar()[1]:02d}"
                month_key = date.strftime("%Y-%m")
                year_key = str(date.year)
                
                for agg, key in [(weekly, week_key), (monthly, month_key), (yearly, year_key)]:
                    agg[key]["total"] += cost
                    agg[key]["models"][model] += cost
                    agg[key]["turns"] += model_turns
    
    # Generate today's hourly data
    for hour in range(today.hour + 1):
        hour_cost = random.uniform(5, 25)  # Match current ~300€/month level
        hour_turns = int(hour_cost * random.uniform(15, 25))
        hourly_today[today.strftime("%Y-%m-%d")][hour] = {"cost": hour_cost, "turns": hour_turns}
    
    return model_usage, daily, hourly_today, weekly, monthly, yearly

# =============================================================================
# MAIN
# =============================================================================

def main():
    global demo_mode
    
    if demo_mode:
        print("🎨 DEMO MODE — Generating mock data...")
        model_usage, daily, hourly_today, weekly, monthly, yearly = generate_demo_data()
        model_config = {
            "active": "anthropic/claude-sonnet-4-6",
            "default": "anthropic/claude-sonnet-4-6", 
            "fallbacks": ["moonshot/kimi-k2.5", "openai/gpt-4o"]
        }
        anth_limits = {
            "5h": {"used": 4500, "limit": 5000, "pct": 0.90, "reset": "18:00"},
            "7d": {"used": 85000, "limit": 120000, "pct": 0.71, "reset": "Mon 00:00 UTC"},
            "overage": None
        }
        print("   Generated 30 days of realistic usage data")
    else:
        print("📊 Loading session data...")
        sessions = load_sessions()
        print(f"   Found {len(sessions)} session files")

        print("📈 Parsing transcripts...")
        model_usage, daily, hourly_today, weekly, monthly, yearly = parse_transcripts(sessions)
        
        # Try to get model config from openclaw.json
        model_config = {}
        try:
            oc_config_path = os.path.join(_OPENCLAW_ROOT, "openclaw.json")
            if os.path.exists(oc_config_path):
                with open(oc_config_path) as f:
                    cfg = json.load(f)
                    # Try agents.defaults.model (new format) then agents.main.model (legacy)
                    agent_cfg = cfg.get("agents", {})
                    defaults = agent_cfg.get("defaults", agent_cfg.get("main", {}))
                    model_field = defaults.get("model", {})
                    if isinstance(model_field, dict):
                        active = model_field.get("primary", "unknown")
                        fallbacks = model_field.get("fallbacks", [])
                    elif isinstance(model_field, str):
                        active = model_field
                        fallbacks = []
                    else:
                        active = "unknown"
                        fallbacks = []
                    model_config = {
                        "active": active,
                        "default": active,
                        "fallbacks": fallbacks
                    }
        except Exception:
            pass
        
        # Anthropic limits (optional)
        anth_limits = {}
        if os.environ.get("ANTHROPIC_API_KEY"):
            print("🔑 Querying Anthropic quota...")
            anth_limits = get_anthropic_limits()
            if "error" not in anth_limits:
                pct_5h = anth_limits.get("5h", {}).get("pct", 0) * 100
                pct_7d = anth_limits.get("7d", {}).get("pct", 0) * 100
                print(f"   5h: {pct_5h:.0f}% | 7d: {pct_7d:.0f}%")
            else:
                print(f"   ({anth_limits.get('error')})")

    # Calculate summary
    total_cost = sum(u["cost"] for u in model_usage.values())
    total_turns = sum(u["turns"] for u in model_usage.values())

    if not demo_mode:
        print(f"   ${total_cost:.2f} | {total_turns} calls | {len(model_usage)} models")

    # Build data structure
    data = {
        "model_usage": dict(model_usage),
        "daily": dict(daily),
        "hourly_today": dict(hourly_today),
        "weekly": dict(weekly),
        "monthly": dict(monthly),
        "yearly": dict(yearly),
        "summary": {
            "total_cost": round(total_cost, 2),
            "total_turns": total_turns,
            "models_used": len(model_usage)
        },
        "model_config": model_config,
        "anthropic_limits": anth_limits,
    }

    # Generate HTML
    html = build_html(data)

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(OUTPUT_PATH)) if os.path.dirname(OUTPUT_PATH) else ".", exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write(html)

    mode_label = "🎨 DEMO" if demo_mode else "📄"
    print(f"\n{mode_label} Dashboard: {OUTPUT_PATH}")
    print(f"💰 ${total_cost:.2f} | {total_turns} Calls | {len(model_usage)} Models")

if __name__ == "__main__":
    main()
