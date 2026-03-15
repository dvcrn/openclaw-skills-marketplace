"""
polymarket-weather-high-temp-sniper  v2.0.0
============================================
Scans Polymarket daily high-temperature markets, auto-imports new ones,
then snipes YES positions between 9–10 AM local time when forecast and
reality converge.

Usage:
    python sniper.py              # Dry-run (default) — show signals, no trades
    python sniper.py --live       # Execute real trades on Polymarket

Hard rules followed:
    1. Always uses SimmerClient — never calls Polymarket CLOB directly
    2. Defaults to dry-run — pass --live (or set AUTOMATON_MANAGED) for real trades
    3. Always tags trades with source + skill_slug
    4. Always includes reasoning (shown publicly on Simmer)
    5. Reads API keys from env — never hardcoded
    6. skill_slug matches ClawHub slug exactly
    7. Framed as remixable template (see SKILL.md)
"""

import os
import sys
import json
import time
import logging
import argparse
import requests
from datetime import datetime
from typing import Optional

import pytz

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from simmer_sdk import SimmerClient
except ImportError:
    print("Error: simmer-sdk not installed. Run: pip install simmer-sdk")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Skill identity — skill_slug MUST match ClawHub slug exactly (Hard Rule #6)
# ---------------------------------------------------------------------------
SKILL_SLUG   = "polymarket-weather-high-temp-sniper"
TRADE_SOURCE = f"sdk:{SKILL_SLUG}"          # Hard Rule #3
SIMMER_BASE  = "https://api.simmer.markets"
VENUE        = "polymarket"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(SKILL_SLUG)

# ---------------------------------------------------------------------------
# Config — all from env vars, never hardcoded (Hard Rule #5)
# ---------------------------------------------------------------------------
def _fenv(k: str, d: float) -> float:
    try:
        return float(os.environ.get(k, str(d)))
    except ValueError:
        return d

def _ienv(k: str, d: int) -> int:
    try:
        return int(os.environ.get(k, str(d)))
    except ValueError:
        return d

PRICE_THRESHOLD = max(0.01, min(0.99, _fenv("PRICE_THRESHOLD", 0.60)))
MAX_AMOUNT_USD  = max(0.10, min(100.0, _fenv("MAX_AMOUNT_USD",  1.0)))
MAX_RETRY       = max(0,    min(10,    _ienv("MAX_RETRY",        1)))
REPORT_INTERVAL = max(60,              _ienv("REPORT_INTERVAL",  240))
ENABLE_TP_SL    = os.environ.get("ENABLE_TP_SL", "false").lower() == "true"
TAKE_PROFIT_PCT = _fenv("TAKE_PROFIT", 0.50)
STOP_LOSS_PCT   = _fenv("STOP_LOSS",   0.25)

# ---------------------------------------------------------------------------
# Singleton SimmerClient (Hard Rule #1 — always use SimmerClient)
# ---------------------------------------------------------------------------
_client: Optional[SimmerClient] = None

def get_client(live: bool = False) -> SimmerClient:
    """Lazy-init singleton SimmerClient."""
    global _client
    if _client is None:
        api_key = os.environ.get("SIMMER_API_KEY")
        if not api_key:
            log.error("SIMMER_API_KEY not set. Get yours at simmer.markets/dashboard.")
            sys.exit(1)
        _client = SimmerClient(
            api_key=api_key,
            venue=VENUE,
            live=live,
        )
    return _client

# ---------------------------------------------------------------------------
# City → Timezone map (swappable signal layer per SKILL.md remix guide)
# ---------------------------------------------------------------------------
CITY_TZ_MAP: dict[str, str] = {
    "new york": "America/New_York",      "nyc": "America/New_York",
    "new york city": "America/New_York", "laguardia": "America/New_York",
    "la guardia": "America/New_York",    "boston": "America/New_York",
    "miami": "America/New_York",         "atlanta": "America/New_York",
    "washington": "America/New_York",    "philadelphia": "America/New_York",
    "chicago": "America/Chicago",        "houston": "America/Chicago",
    "dallas": "America/Chicago",         "austin": "America/Chicago",
    "minneapolis": "America/Chicago",    "o'hare": "America/Chicago",
    "ohare": "America/Chicago",          "dfw": "America/Chicago",
    "denver": "America/Denver",          "salt lake city": "America/Denver",
    "phoenix": "America/Phoenix",        "las vegas": "America/Los_Angeles",
    "los angeles": "America/Los_Angeles","san francisco": "America/Los_Angeles",
    "seattle": "America/Los_Angeles",    "sea-tac": "America/Los_Angeles",
    "portland": "America/Los_Angeles",   "toronto": "America/Toronto",
    "vancouver": "America/Vancouver",    "montreal": "America/Toronto",
    "calgary": "America/Edmonton",       "london": "Europe/London",
    "paris": "Europe/Paris",             "berlin": "Europe/Berlin",
    "madrid": "Europe/Madrid",           "rome": "Europe/Rome",
    "amsterdam": "Europe/Amsterdam",     "brussels": "Europe/Brussels",
    "vienna": "Europe/Vienna",           "stockholm": "Europe/Stockholm",
    "oslo": "Europe/Oslo",               "copenhagen": "Europe/Copenhagen",
    "helsinki": "Europe/Helsinki",       "warsaw": "Europe/Warsaw",
    "prague": "Europe/Prague",           "budapest": "Europe/Budapest",
    "athens": "Europe/Athens",           "istanbul": "Europe/Istanbul",
    "moscow": "Europe/Moscow",           "barcelona": "Europe/Madrid",
    "lisbon": "Europe/Lisbon",           "dublin": "Europe/Dublin",
    "munich": "Europe/Berlin",           "hamburg": "Europe/Berlin",
    "frankfurt": "Europe/Berlin",        "milan": "Europe/Rome",
    "tokyo": "Asia/Tokyo",               "osaka": "Asia/Tokyo",
    "seoul": "Asia/Seoul",               "beijing": "Asia/Shanghai",
    "shanghai": "Asia/Shanghai",         "hong kong": "Asia/Hong_Kong",
    "taipei": "Asia/Taipei",             "singapore": "Asia/Singapore",
    "bangkok": "Asia/Bangkok",           "jakarta": "Asia/Jakarta",
    "kuala lumpur": "Asia/Kuala_Lumpur", "manila": "Asia/Manila",
    "mumbai": "Asia/Kolkata",            "delhi": "Asia/Kolkata",
    "bangalore": "Asia/Kolkata",         "sydney": "Australia/Sydney",
    "melbourne": "Australia/Melbourne",  "brisbane": "Australia/Brisbane",
    "perth": "Australia/Perth",          "auckland": "Pacific/Auckland",
    "buenos aires": "America/Argentina/Buenos_Aires",
    "sao paulo": "America/Sao_Paulo",    "lima": "America/Lima",
    "bogota": "America/Bogota",          "santiago": "America/Santiago",
    "mexico city": "America/Mexico_City",
    "cairo": "Africa/Cairo",             "johannesburg": "Africa/Johannesburg",
    "nairobi": "Africa/Nairobi",         "lagos": "Africa/Lagos",
    "hartsfield": "America/New_York",    "mia": "America/New_York",
    "katl": "America/New_York",          "kord": "America/Chicago",
    "ksea": "America/Los_Angeles",       "klga": "America/New_York",
    "kdfw": "America/Chicago",           "kmia": "America/New_York",
}

# Polymarket discovery search terms for high-temperature markets
DISCOVERY_TERMS = [
    "highest temperature", "high temperature",
    "temperature nyc", "temperature new york",
    "temperature chicago", "temperature los angeles",
    "temperature miami", "temperature dallas",
    "temperature seattle", "temperature atlanta",
    "temperature houston", "temperature london",
    "temperature tokyo", "temperature paris",
]

# ---------------------------------------------------------------------------
# Helpers: timezone
# ---------------------------------------------------------------------------
def detect_timezone(question: str) -> Optional[pytz.BaseTzInfo]:
    q = question.lower()
    for city in sorted(CITY_TZ_MAP, key=len, reverse=True):
        if city in q:
            return pytz.timezone(CITY_TZ_MAP[city])
    return None

def local_hhmm(tz: pytz.BaseTzInfo) -> tuple[int, int]:
    n = datetime.now(tz)
    return n.hour, n.minute

def is_in_scan_window(tz: pytz.BaseTzInfo) -> bool:
    h, m = local_hhmm(tz)
    return h == 9 and m <= 55

def is_fallback_moment(tz: pytz.BaseTzInfo) -> bool:
    h, m = local_hhmm(tz)
    return h == 10 and m < 5

# ---------------------------------------------------------------------------
# Helpers: market classification (swappable signal — see SKILL.md)
# ---------------------------------------------------------------------------
def is_highest_temp_market(question: str) -> bool:
    """
    Return True only for 'highest/max temperature, exceeds X°F' direction.
    Filters out lowest/minimum/below markets and unrelated topics.
    REMIX: Replace this function with your own signal logic.
    """
    q = question.lower()
    temp_kw = [
        "temperature", "°c", "°f", "celsius", "fahrenheit",
        "high temp", "highest temp", "max temp",
        "daily high", "daily maximum", "high temperature",
        "highest temperature", "maximum temperature",
    ]
    if not any(kw in q for kw in temp_kw):
        return False
    noise = [
        "crypto", "bitcoin", "ethereum", "solana", "token", "defi",
        "president", "election", "vote", "senate", "congress",
        "football", "basketball", "soccer", "nba", "nfl", "mlb",
        "stock", "nasdaq", "dow", "s&p", "oil", "gold", "spread:",
    ]
    if any(kw in q for kw in noise):
        return False
    low_kw = [
        "lowest temp", "minimum temp", "low temp", "daily low",
        "daily minimum", "minimum temperature", "lowest temperature",
        "below", "fall below", "drop below", "low temperature",
    ]
    if any(kw in q for kw in low_kw):
        return False
    return True

def get_market_price(market: dict) -> float:
    """
    Resolve YES probability from market dict.
    Priority: current_probability → external_price_yes → price_yes → probability → 0.0
    REMIX: Replace with NOAA forecast, OpenMeteo, or your own model probability.
    """
    for field in ("current_probability", "external_price_yes", "price_yes", "probability"):
        v = market.get(field)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return 0.0

# ---------------------------------------------------------------------------
# Context check (recommended per Building Skills guide)
# ---------------------------------------------------------------------------
def check_context(market_id: str, my_probability: float) -> tuple[bool, list[str]]:
    """
    Fetch /context and apply safeguards:
      - Severe flip-flop warning → skip
      - Slippage > 15% → skip
      - Edge recommendation SKIP → skip
    Returns (should_trade, [reasons]).
    """
    try:
        ctx = get_client().get_market_context(market_id, my_probability=my_probability)
    except Exception as e:
        log.debug(f"[CTX] context fetch failed ({e}), proceeding")
        return True, []

    if not ctx:
        return True, []

    reasons: list[str] = []

    # Flip-flop detection
    discipline = ctx.get("discipline", {}) or {}
    wlevel = discipline.get("warning_level", "none")
    if wlevel == "severe":
        return False, [f"Severe flip-flop: {discipline.get('flip_flop_warning', '')}"]
    if wlevel == "mild":
        reasons.append("mild flip-flop warning")

    # Slippage check
    slippage = ctx.get("slippage", {}) or {}
    estimates = slippage.get("estimates", []) or []
    if estimates:
        slip_pct = estimates[0].get("slippage_pct", 0)
        if slip_pct > 0.15:
            return False, [f"Slippage too high: {slip_pct:.1%}"]

    # Edge analysis
    edge = ctx.get("edge", {}) or {}
    rec = edge.get("recommendation", "")
    if rec == "SKIP":
        return False, ["Edge analysis: SKIP (market resolved or invalid)"]
    if rec == "TRADE":
        reasons.append(f"Edge analysis: TRADE (edge={edge.get('user_edge', 0):.1%})")

    return True, reasons

# ---------------------------------------------------------------------------
# State persistence
# ---------------------------------------------------------------------------
_STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

def load_state() -> dict:
    if os.path.exists(_STATE_FILE):
        try:
            with open(_STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"traded_today": [], "tp_sl_registered": [], "last_report_ts": 0, "date": ""}

def save_state(state: dict) -> None:
    try:
        with open(_STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        log.warning(f"[STATE] save failed: {e}")

def reset_if_new_day(state: dict) -> dict:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    if state.get("date") != today:
        log.info("New UTC day — resetting daily state.")
        state = {"traded_today": [], "tp_sl_registered": [], "last_report_ts": 0, "date": today}
        save_state(state)
    return state

# ---------------------------------------------------------------------------
# Positions
# ---------------------------------------------------------------------------
def get_open_positions() -> dict[str, object]:
    """Returns {market_id: position} for active YES positions."""
    for attempt in range(3):
        try:
            positions = get_client().get_positions()
            return {
                (getattr(p, "market_id", None) or getattr(p, "id", "")): p
                for p in (positions or [])
                if (getattr(p, "shares_yes", 0) or 0) > 0
            }
        except Exception as e:
            log.warning(f"[POS] attempt {attempt+1}/3 failed: {e}")
            if attempt < 2:
                time.sleep(2 ** attempt)
    return {}

def already_holds(mid: str, open_pos: dict, traded_today: list) -> bool:
    return mid in open_pos or mid in traded_today

# ---------------------------------------------------------------------------
# Market discovery (Phase 1)
# ---------------------------------------------------------------------------
def discover_and_import() -> int:
    """
    Discover new high-temp markets on Polymarket and import to Simmer.
    Rate limit: 6 imports/min free, 10/day free.
    """
    imported = 0
    seen: set[str] = set()
    for term in DISCOVERY_TERMS:
        try:
            results = get_client().list_importable_markets(
                q=term, venue="polymarket", min_volume=500, limit=20
            )
        except Exception as e:
            log.debug(f"[DISCOVER] '{term}' search failed: {e}")
            continue
        for m in (results or []):
            url = m.get("url", "")
            q   = (m.get("question") or "").lower()
            if not url or url in seen:
                continue
            seen.add(url)
            if "temperature" not in q and "°f" not in q and "°c" not in q:
                continue
            if not url.startswith("https://polymarket.com/"):
                continue
            try:
                res    = get_client().import_market(url)
                status = (res or {}).get("status", "")
                if status == "imported":
                    imported += 1
                    log.info(f"[DISCOVER] imported: {m.get('question', url)[:70]}")
            except Exception as e:
                err = str(e)
                if "rate limit" in err.lower() or "429" in err:
                    log.warning("[DISCOVER] rate-limited, stopping discovery")
                    return imported
                log.debug(f"[DISCOVER] import failed: {e}")
    log.info(f"[DISCOVER] newly imported: {imported}")
    return imported

# ---------------------------------------------------------------------------
# Market fetch (Phase 2)
# ---------------------------------------------------------------------------
def fetch_weather_markets() -> list[dict]:
    """
    GET /api/sdk/markets?tags=weather   (correct path; v1.0.0 used /api/markets which 404s)
    Fallback: q=temperature text search.
    """
    api_key = os.environ.get("SIMMER_API_KEY", "")
    hdrs    = {"Authorization": f"Bearer {api_key}"}

    for params in (
        {"tags": "weather",      "status": "active", "limit": 200},
        {"q":    "temperature",  "status": "active", "limit": 200},
    ):
        try:
            r = requests.get(f"{SIMMER_BASE}/api/sdk/markets",
                             params=params, headers=hdrs, timeout=15)
            if r.ok:
                markets = r.json().get("markets", [])
                log.info(f"[FETCH] params={list(params.keys())[0]} → {len(markets)} markets")
                if markets:
                    return markets
            else:
                log.warning(f"[FETCH] {r.status_code}: {r.text[:80]}")
        except Exception as e:
            log.warning(f"[FETCH] error: {e}")
    return []

# ---------------------------------------------------------------------------
# Risk monitor (Phase 5)
# ---------------------------------------------------------------------------
def register_tp_sl(market_id: str) -> bool:
    """
    POST /api/sdk/positions/{market_id}/monitor
    Uses stop_loss_pct / take_profit_pct (percentages, NOT prices).
    v1.0.0 bug: used stop_loss_price/take_profit_price (wrong field names).
    """
    if not ENABLE_TP_SL:
        return False
    api_key = os.environ.get("SIMMER_API_KEY", "")
    try:
        r = requests.post(
            f"{SIMMER_BASE}/api/sdk/positions/{market_id}/monitor",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"side": "yes", "stop_loss_pct": STOP_LOSS_PCT,
                  "take_profit_pct": TAKE_PROFIT_PCT, "venue": VENUE},
            timeout=10,
        )
        if r.ok:
            log.info(f"[TP/SL] set SL={STOP_LOSS_PCT:.0%} TP={TAKE_PROFIT_PCT:.0%} | {market_id}")
            return True
        log.warning(f"[TP/SL] failed ({r.status_code}): {r.text[:80]}")
    except Exception as e:
        log.warning(f"[TP/SL] error: {e}")
    return False

# ---------------------------------------------------------------------------
# Execute trade (Hard Rules #1 #3 #4)
# ---------------------------------------------------------------------------
def execute_trade(
    market_id: str,
    question:  str,
    price:     float,
    reasoning: str,         # Hard Rule #4 — always include reasoning
    state:     dict,
    dry_run:   bool,
) -> bool:
    traded_today    = state["traded_today"]
    tp_sl_registered = state.setdefault("tp_sl_registered", [])
    amount = min(round(price, 4), MAX_AMOUNT_USD)
    if amount < 0.01:
        log.warning(f"[TRADE] amount too small ({amount:.4f}), skip {market_id}")
        return False

    tag = "[DRY-RUN]" if dry_run else "[LIVE]"
    log.info(f"{tag} → '{question[:55]}' | YES%={price:.0%} | amount=${amount:.4f}")
    log.info(f"{tag}   reasoning: {reasoning[:120]}")

    if dry_run:
        return True  # Hard Rule #2 — dry-run never places real orders

    for attempt in range(1, 2 + MAX_RETRY):
        try:
            # Hard Rule #1: Always use SimmerClient
            result = get_client().trade(
                market_id  = market_id,
                side       = "yes",
                amount     = amount,
                venue      = VENUE,
                source     = TRADE_SOURCE,   # Hard Rule #3
                skill_slug = SKILL_SLUG,     # Hard Rule #6
                reasoning  = reasoning,      # Hard Rule #4
            )
            shares = getattr(result, "shares_bought", "?")
            cost   = getattr(result, "cost", amount)
            log.info(f"[LIVE] ✅ filled | shares≈{shares} | cost=${cost:.4f}")
            traded_today.append(market_id)
            state["traded_today"] = traded_today
            save_state(state)
            if ENABLE_TP_SL and market_id not in tp_sl_registered:
                if register_tp_sl(market_id):
                    tp_sl_registered.append(market_id)
                    state["tp_sl_registered"] = tp_sl_registered
                    save_state(state)
            return True
        except Exception as e:
            log.warning(f"[TRADE] attempt {attempt}/{1+MAX_RETRY} failed: {e}")
            if attempt < 1 + MAX_RETRY:
                time.sleep(3)

    log.error(f"[TRADE] ❌ all retries failed: {market_id}")
    return False

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def print_report(open_positions: dict) -> None:
    log.info("=" * 65)
    log.info(f"📊 REPORT | {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    log.info("=" * 65)
    if not open_positions:
        log.info("  No open positions.")
    else:
        for mid, p in open_positions.items():
            q        = getattr(p, "question", mid)[:55]
            shares   = getattr(p, "shares_yes", 0)
            avg      = getattr(p, "avg_cost", 0) or getattr(p, "avg_cost_basis", 0)
            val      = getattr(p, "current_value", 0)
            pnl      = getattr(p, "pnl", 0) or getattr(p, "unrealized_pnl", 0)
            pnl_pct  = ((val / avg - 1) * 100) if avg and avg > 0 else 0
            log.info(f"  {q} | shares={shares:.3f} | avg=${avg:.3f} | now=${val:.3f} | PnL={pnl:+.3f} ({pnl_pct:+.1f}%)")
    log.info("=" * 65)

# ---------------------------------------------------------------------------
# Main strategy
# ---------------------------------------------------------------------------
def run(dry_run: bool = True) -> None:
    """
    Core strategy loop.
    dry_run=True  → show signals and log reasoning, no real orders placed (Hard Rule #2)
    dry_run=False → live trading on Polymarket
    """
    mode = "DRY-RUN" if dry_run else "LIVE"
    log.info(f"🌡️  {SKILL_SLUG} v2.0.0 | {mode} | threshold={PRICE_THRESHOLD:.0%} | max=${MAX_AMOUNT_USD}")

    if dry_run:
        log.info("[DRY-RUN] No real trades will be placed. Pass --live for real trading.")

    # Init client
    get_client(live=not dry_run)

    state          = reset_if_new_day(load_state())
    traded_today   = state["traded_today"]
    open_positions = get_open_positions()

    # Periodic report
    if time.time() - state.get("last_report_ts", 0) >= REPORT_INTERVAL:
        print_report(open_positions)
        state["last_report_ts"] = time.time()
        save_state(state)

    # ── PHASE 1: discover & import ────────────────────────────────────────
    log.info("=== PHASE 1: Discover & import high-temp markets ===")
    try:
        discover_and_import()
    except Exception as e:
        log.warning(f"[PHASE1] discovery error: {e}")

    # ── PHASE 2: fetch & filter ───────────────────────────────────────────
    log.info("=== PHASE 2: Fetch & filter ===")
    all_markets  = fetch_weather_markets()
    temp_markets = [
        m for m in all_markets
        if is_highest_temp_market(m.get("question", ""))
        and m.get("status", "active").lower()
            not in ("closed", "settled", "finalized", "resolved")
    ]
    log.info(f"[FILTER] {len(all_markets)} total → {len(temp_markets)} high-temp markets")

    if not temp_markets:
        log.warning("[FILTER] No high-temp markets found.")
        _automaton_report(signals=0, attempted=0, executed=0, reason="no_high_temp_markets")
        return

    # ── PHASE 3: timezone pre-scan ────────────────────────────────────────
    log.info("=== PHASE 3: Timezone pre-scan ===")
    for m in temp_markets:
        tz = detect_timezone(m.get("question", ""))
        if tz is None:
            log.warning(f"  [NO TZ] {m.get('question','')[:70]}")
        else:
            h, mn = local_hhmm(tz)
            log.info(
                f"  [{tz.zone}] {h:02d}:{mn:02d} "
                f"scan={is_in_scan_window(tz)} fb={is_fallback_moment(tz)} "
                f"| {m.get('question','')[:50]}"
            )

    # ── PHASE 4: trade windows ────────────────────────────────────────────
    log.info("=== PHASE 4: Scan & snipe trading window ===")
    signals    = 0
    attempted  = 0
    executed   = 0
    fallback_pool: list[dict] = []

    for m in temp_markets:
        mid      = m.get("id")
        question = m.get("question", "")
        if not mid:
            continue
        if already_holds(mid, open_positions, traded_today):
            log.debug(f"[SKIP] already holds: {mid}")
            continue
        tz = detect_timezone(question)
        if tz is None:
            log.warning(f"[SKIP] unknown timezone: {question[:60]}")
            continue

        price     = get_market_price(m)   # REMIX: swap with your own signal here
        h, mn     = local_hhmm(tz)
        local_str = f"{h:02d}:{mn:02d} {tz.zone}"

        # 9:00–9:55 AM scan window
        if is_in_scan_window(tz):
            if price >= PRICE_THRESHOLD:
                signals += 1

                # Context safeguard (recommended)
                ok_trade, reasons = check_context(mid, my_probability=price)
                if not ok_trade:
                    log.info(f"[CTX BLOCK] {reasons[0]} | {question[:50]}")
                    continue
                if reasons:
                    log.info(f"[CTX] warnings: {'; '.join(reasons)}")

                reasoning = (
                    f"[SCAN {local_str}] YES%={price:.0%} >= threshold={PRICE_THRESHOLD:.0%}. "
                    f"9AM local: daily high-temp trajectory already set, forecast-reality "
                    f"convergence window. Signal source: market price."
                )
                attempted += 1
                ok = execute_trade(mid, question, price, reasoning, state, dry_run)
                if ok:
                    executed += 1
                    if not dry_run:
                        open_positions = get_open_positions()
            else:
                log.info(f"[WATCH] YES%={price:.0%} < {PRICE_THRESHOLD:.0%} | {question[:50]}")
                fallback_pool.append(m)

        # 10:00 AM fallback pool
        elif is_fallback_moment(tz):
            fallback_pool.append(m)
        else:
            log.debug(f"[SKIP] out of window {local_str}: {question[:50]}")

    # Fallback at 10AM — crowd-follow highest YES%
    log.info(f"[FALLBACK] pool size: {len(fallback_pool)}")
    eligible = [
        m for m in fallback_pool
        if (detect_timezone(m.get("question", "")) is not None
            and is_fallback_moment(detect_timezone(m.get("question", "")))
            and not already_holds(m.get("id"), open_positions, traded_today))
    ]
    if eligible:
        best       = max(eligible, key=get_market_price)
        best_price = get_market_price(best)
        if best_price > 0:
            mid      = best.get("id")
            question = best.get("question", "")
            tz       = detect_timezone(question)
            h, mn    = local_hhmm(tz)
            local_str = f"{h:02d}:{mn:02d} {tz.zone}"
            signals  += 1

            ok_trade, reasons = check_context(mid, my_probability=best_price)
            if ok_trade:
                reasoning = (
                    f"[FALLBACK 10AM {local_str}] No strong signal during 9AM scan "
                    f"(all YES% < {PRICE_THRESHOLD:.0%}). Crowd-following: highest-YES% "
                    f"unowned market at {best_price:.0%}. 10AM: ~3-4h before daily temp "
                    f"peak, market consensus converging with observed temperature."
                )
                attempted += 1
                ok = execute_trade(mid, question, best_price, reasoning, state, dry_run)
                if ok:
                    executed += 1
            else:
                log.info(f"[CTX BLOCK fallback] {reasons[0]}")

    # ── Wrap up ───────────────────────────────────────────────────────────
    state["traded_today"]    = traded_today
    state["tp_sl_registered"] = state.get("tp_sl_registered", [])
    save_state(state)
    log.info(f"Cycle done | signals={signals} attempted={attempted} executed={executed}")
    _automaton_report(signals, attempted, executed,
                      reason="no_signal_in_window" if signals == 0 else None)


def _automaton_report(signals: int, attempted: int, executed: int,
                      reason: Optional[str] = None) -> None:
    """Emit JSON report for Automaton manager (only when AUTOMATON_MANAGED is set)."""
    if not os.environ.get("AUTOMATON_MANAGED"):
        return
    r: dict = {
        "signals":          signals,
        "trades_attempted": attempted,
        "trades_executed":  executed,
        "amount_usd":       round(executed * MAX_AMOUNT_USD, 2),
    }
    if reason:
        r["skip_reason"] = reason
    elif signals > 0 and executed == 0:
        r["skip_reason"] = "trade_execution_failed"
    print(json.dumps({"automaton": r}))


# ---------------------------------------------------------------------------
# Entry point — Hard Rule #2: always default to dry-run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Automaton: AUTOMATON_MANAGED env var → always live (no --live flag needed in cron)
    automaton = bool(os.environ.get("AUTOMATON_MANAGED"))

    parser = argparse.ArgumentParser(description=SKILL_SLUG)
    parser.add_argument(
        "--live",
        action="store_true",
        default=False,
        help="Execute real trades. Default is dry-run (show signals only).",
    )
    args = parser.parse_args()

    live = args.live or automaton
    run(dry_run=not live)
