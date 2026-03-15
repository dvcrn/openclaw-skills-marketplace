"""Kalshalyst — Claude-powered contrarian estimation.

Pipeline:
  Phase 1: FETCH — Kalshi markets with blocklist + timeframe filtering
  Phase 2: CLASSIFY — Disabled (Qwen unreliable). Markets pass through with defaults.
  Phase 3: ESTIMATE — Claude Sonnet contrarian estimation (sees price, finds disagreements)
  Phase 4: EDGE — Raw edge calculation (limit order assumption, no spread penalty)
  Phase 5: CACHE + ALERT — Write cache, alert on high-edge opportunities

Key change from prior versions: Claude now sees the market price and is prompted to find
reasons the market is wrong. Blind estimation produced consensus-matching
estimates with zero edge. Contrarian mode produces opinionated directional calls.
Falls back to Qwen if Claude is unavailable (offline/cooldown).

Usage:
    python kalshalyst.py [--dry-run] [--force]
"""

import json
import re
import sys
import time
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] Kalshalyst: %(message)s'
)
logger = logging.getLogger(__name__)


# ── API Schema Normalization ────────────────────────────────────────────────
def _normalize_market(m: dict) -> dict:
    """Normalize Kalshi API v3 dollar-string fields to integer cents.

    Kalshi API changed field names (e.g., yes_bid → yes_bid_dollars).
    This helper converts new dollar-string fields to integer cents the rest
    of the code expects. Only normalizes if new fields are present and old ones
    are missing (safe to call on already-normalized dicts).
    """
    def _dollars_to_cents(val):
        """Convert dollar string like '0.4500' to integer cents like 45."""
        if val is None:
            return 0
        if isinstance(val, (int, float)):
            return int(val) if val < 10 else int(val)  # already cents or needs conversion
        try:
            return int(round(float(val) * 100))
        except (ValueError, TypeError):
            return 0

    def _fp_to_int(val):
        """Convert float-point string like '1234.00' to integer."""
        if val is None:
            return 0
        if isinstance(val, int):
            return val
        try:
            return int(round(float(val)))
        except (ValueError, TypeError):
            return 0

    # Only normalize if new fields are present and old ones are missing
    if m.get("yes_bid") is None and "yes_bid_dollars" in m:
        m["yes_bid"] = _dollars_to_cents(m.get("yes_bid_dollars"))
        m["yes_ask"] = _dollars_to_cents(m.get("yes_ask_dollars"))
        m["no_bid"] = _dollars_to_cents(m.get("no_bid_dollars"))
        m["no_ask"] = _dollars_to_cents(m.get("no_ask_dollars"))
        m["last_price"] = _dollars_to_cents(m.get("last_price_dollars"))
        m["yes_price"] = m.get("yes_price") or _dollars_to_cents(m.get("yes_bid_dollars"))  # approximate
        m["previous_yes_bid"] = _dollars_to_cents(m.get("previous_yes_bid_dollars"))
        m["previous_yes_ask"] = _dollars_to_cents(m.get("previous_yes_ask_dollars"))
        m["previous_price"] = _dollars_to_cents(m.get("previous_price_dollars"))
        m["volume"] = _fp_to_int(m.get("volume_fp"))
        m["volume_24h"] = _fp_to_int(m.get("volume_24h_fp"))
        m["open_interest"] = _fp_to_int(m.get("open_interest_fp"))
        m["liquidity"] = _dollars_to_cents(m.get("liquidity_dollars"))
        m["notional_value"] = _dollars_to_cents(m.get("notional_value_dollars"))
    return m


# ── Category Filtering ──────────────────────────────────────────────────────

_ALLOWED_CATEGORIES = {
    "politics", "policy", "government", "election", "geopolitics",
    "economics", "macro", "fed", "regulation", "legal", "trade",
    "crypto", "finance", "technology", "ai",
}

_BLOCKED_TICKER_PREFIXES = {
    "KXHIGH", "KXLOW", "KXRAIN", "KXSNOW", "KXTEMP", "KXWIND", "KXWEATH",
    "INX", "NASDAQ", "FED-MR", "KXCELEB", "KXMOVIE", "KXTIKTOK", "KXYT",
    "KXTWIT", "KXSTREAM",
}

_BLOCKED_CATEGORIES_API = {
    "weather", "climate", "entertainment", "sports",
    "social-media", "streaming", "celebrities",
}

# Single words use word-boundary regex; multi-word phrases use substring match.
# This prevents "finals" from matching "Final GDP report" while still catching
# "NBA Finals" or "Stanley Cup Finals".
_SPORTS_WORDS = {
    "nfl", "nba", "mlb", "nhl", "mls", "ncaa", "pga", "ufc", "wwe",
    "wnba", "lpga", "nascar", "f1", "mma",
    "playoff", "playoffs", "heisman",
    "valorant", "atp", "wta", "itf",
    "baseball", "basketball", "football", "hockey", "soccer",
    "tennis", "cricket", "rugby", "boxing", "wrestling",
    "esports", "motorsport",
}

_SPORTS_PHRASES = {
    "super bowl", "superbowl", "march madness", "world series",
    "stanley cup", "nba finals", "nhl finals", "mlb finals",
    "premier league", "la liga", "serie a",
    "bundesliga", "ligue 1", "champions league", "europa league",
    "league of legends", "copa america", "copa del rey",
    "challenger tour", "challenger round",
    "world baseball classic", "indian wells", "grand prix",
    "world cup", "gold cup", "nations league",
    "college baseball", "college basketball", "college football",
    "wins by over", "total runs", "total goals", "total points",
    "first to score", "1+ goals", "2+ goals",
    "moneyline", "spread", "over under",
}

# Ticker prefixes that are always sports — hard block
_SPORTS_TICKER_PREFIXES = {
    "KXATP", "KXNFL", "KXNBA", "KXMLB", "KXNHL", "KXMLS",
    "KXNCAA", "KXPGA", "KXUFC", "KXWWE", "KXSOCCER", "KXTENNIS",
    "KXWBC", "KXCBB", "KXCFB", "KXWNBA", "KXLPGA", "KXF1",
    "KXNASCAR", "KXCRICKET", "KXRUGBY", "KXBOXING", "KXMMA",
    "KXESPORT", "KXLOL", "KXDOTA", "KXCSK",
}

_MICRO_TIMEFRAME_PATTERNS = {
    "in next 15 min", "in next 30 min", "in next 1 hour",
    "in next 5 min", "in next 10 min", "next 15 minutes",
    "next 30 minutes", "next hour", "price up in next",
    "price down in next",
}

_POLITICS_NOISE_PATTERNS = {
    "primary", "runoff", "special election", "city council",
    "state senate", "state house", "state rep", "alderman",
    "margin of victory", "vote share", "win by more than",
    "win by less than", "percentage of vote",
    "win between", "win above", "seats in the",
    "leave office next", "leave office first",
    "be 1st in the next", "be first in the next",
    "next presidential election first round",
    "dutch election", "czech election", "argentine election",
    "brazilian election", "mexican election", "colombian election",
    "peruvian election", "chilean election", "turkish election",
    "south korean election", "japanese election", "indian election",
    "australian election", "canadian election",
    "romanian presidential", "japanese house",
    "gorton and denton",
}

_PRICE_THRESHOLD_RE = re.compile(
    r"(price|close|drop|fall|rise|trade|open|hit|reach|touch|break|stay)"
    r"\s+(above|below|over|under|at or above|at or below)"
    r"\s+\$?[\d,]+",
    re.IGNORECASE,
)

_PRICE_ASSET_RE = re.compile(
    r"(bitcoin|btc|ethereum|eth|solana|sol|dogecoin|doge|xrp"
    r"|s&p|s&p 500|nasdaq|dow jones|djia|russell|vix"
    r"|gold|silver|oil|crude|wti|brent|natural gas"
    r"|aapl|amzn|goog|googl|msft|nvda|tsla|meta)"
    r"\s+.{0,20}(above|below|over|under|exceed|less than)\s+\$?[\d,]+",
    re.IGNORECASE,
)

_COINFLIP_PATTERNS = {
    "when will", "how many", "what will be the", "who will the next", "how much will",
}

_IPO_RE = re.compile(r"\bipo\b", re.IGNORECASE)


def _is_noise_market(title: str, price_cents: int = 50) -> str:
    """Return a noise reason for low-signal market prompts, else an empty string."""
    title_lower = title.lower()

    if _PRICE_THRESHOLD_RE.search(title):
        return "price_threshold"
    if _PRICE_ASSET_RE.search(title):
        return "price_asset"
    if any(pattern in title_lower for pattern in _POLITICS_NOISE_PATTERNS):
        return "politics_noise"
    if 40 <= price_cents <= 60:
        if _IPO_RE.search(title):
            return "coinflip_ipo"
        if any(pattern in title_lower for pattern in _COINFLIP_PATTERNS):
            return "coinflip_uncertain"
    return ""


def _is_blocked(ticker: str, category: str = "", title: str = "", price_cents: int = 50) -> bool:
    """Check if a market should be excluded from analysis."""
    ticker_upper = ticker.upper()
    if any(ticker_upper.startswith(prefix) for prefix in _BLOCKED_TICKER_PREFIXES):
        return True
    if category and category.lower().strip() in _BLOCKED_CATEGORIES_API:
        return True
    title_lower = title.lower()
    if any(pat in title_lower for pat in _MICRO_TIMEFRAME_PATTERNS):
        return True
    if _is_noise_market(title, price_cents=price_cents):
        return True
    return False


def _is_sports(ticker: str, title: str) -> bool:
    """Detect sports markets using word-boundary matching.

    Three-layer check:
      1. Ticker prefix (KXATP*, KXNFL*, etc.) — always sports
      2. Single-word tokens with word boundaries — "finals" won't match "Final GDP"
      3. Multi-word phrases with substring match — "stanley cup" is unambiguous
    """
    ticker_upper = ticker.upper()
    if any(ticker_upper.startswith(p) for p in _SPORTS_TICKER_PREFIXES):
        return True

    combined = f"{ticker} {title}".lower()

    # Word-boundary match for single tokens
    for word in _SPORTS_WORDS:
        if re.search(rf'\b{re.escape(word)}\b', combined):
            return True

    # Substring match for multi-word phrases (unambiguous)
    for phrase in _SPORTS_PHRASES:
        if phrase in combined:
            return True

    return False


# ── Phase 1: Market Fetching ──────────────────────────────────────────────

def fetch_kalshi_markets(client, cfg: dict) -> list[dict]:
    """Fetch and pre-filter Kalshi markets.

    Args:
        client: Initialized Kalshi client
        cfg: Configuration dict with fetch parameters

    Returns:
        List of pre-filtered market dicts
    """
    min_volume = cfg.get("min_volume", 50)
    min_days = cfg.get("min_days_to_close", 7)
    max_days = cfg.get("max_days_to_close", 365)
    max_pages = cfg.get("max_pages", 10)
    fresh_mode = cfg.get("fresh_mode", False)
    max_age_hours = cfg.get("fresh_max_age_hours", 48)

    if fresh_mode:
        min_volume = 0
        min_days = 2
        logger.info(
            f"FRESH MODE: relaxed filters (min_vol=0, min_days=2, max_age={max_age_hours}h)"
        )

    all_markets = []
    cursor = None
    fetch_start = time.time()
    max_fetch_seconds = cfg.get("max_fetch_seconds", 30)

    for page in range(max_pages):
        if time.time() - fetch_start > max_fetch_seconds:
            logger.info(f"Fetch: hit {max_fetch_seconds}s budget at page {page}")
            break

        try:
            # Construct API URL
            url = (
                "https://api.elections.kalshi.com/trade-api/v2/markets"
                "?limit=200&status=open&mve_filter=exclude"
            )
            if cursor:
                url += f"&cursor={cursor}"

            # Make API call
            resp = client.call_api("GET", url)
            data = json.loads(resp.read())

            markets = [_normalize_market(m) for m in data.get("markets", [])]
            all_markets.extend(markets)
            cursor = data.get("cursor")

            if not cursor or not markets:
                break

            logger.info(f"Fetch: page {page}, got {len(markets)} markets (cursor: {cursor[:20] if cursor else 'none'})")

        except Exception as e:
            logger.error(f"Fetch error at page {page}: {e}")
            break

    logger.info(f"Fetch: {len(all_markets)} raw markets")

    # Pre-filter
    filtered = []
    stats = {
        "no_book": 0,
        "blocked": 0,
        "sports": 0,
        "volume": 0,
        "timeframe": 0,
        "stale": 0,
    }

    for m in all_markets:
        ticker = m.get("ticker", "")
        title = m.get("title", "")
        category = m.get("category", "") or m.get("series_ticker", "")
        volume = m.get("volume", 0) or 0
        yes_bid = m.get("yes_bid", 0) or 0
        yes_ask = m.get("yes_ask", 0) or 0
        yes_price = m.get("yes_price", 0) or 0
        last_price = m.get("last_price", 0) or 0

        # Resolve price
        if yes_bid and yes_ask:
            price = int((yes_bid + yes_ask) / 2)
            spread = yes_ask - yes_bid
        elif yes_price:
            price = yes_price
            spread = 2
        elif last_price:
            price = last_price
            spread = 2
        else:
            stats["no_book"] += 1
            continue

        if price <= 0 or price >= 100:
            stats["no_book"] += 1
            continue

        if _is_blocked(ticker, category, title, price_cents=price):
            stats["blocked"] += 1
            continue

        if volume < min_volume:
            stats["volume"] += 1
            continue

        is_sports = _is_sports(ticker, title)
        if is_sports:
            stats["sports"] += 1
            continue  # HARD BLOCK: never pass sports markets downstream

        days_to_close = _calc_days_to_close(m)
        if days_to_close is None or days_to_close < min_days or days_to_close > max_days:
            stats["timeframe"] += 1
            continue

        market_age_hours = _calc_market_age_hours(m)
        if fresh_mode and (market_age_hours is None or market_age_hours > max_age_hours):
            stats["stale"] += 1
            continue

        filtered.append({
            "ticker": ticker,
            "title": title[:80],
            "yes_bid": yes_bid,
            "yes_ask": yes_ask,
            "yes_price": price,
            "spread": spread,
            "volume": volume,
            "open_interest": m.get("open_interest", 0) or 0,
            "days_to_close": days_to_close,
            "market_age_hours": market_age_hours,
            "expiration_time": m.get("expiration_time", ""),
            "is_sports": is_sports,
        })

    logger.info(
        f"Fetch: {len(filtered)} passed filters (blocked={stats['blocked']}, "
        f"sports_tagged={stats['sports']}, volume={stats['volume']}, "
        f"timeframe={stats['timeframe']}, stale={stats['stale']})"
    )
    return filtered


def _calc_days_to_close(m: dict) -> Optional[float]:
    """Calculate days until market closes."""
    expiration = m.get("expiration_time") or m.get("close_time", "")
    if not expiration or not isinstance(expiration, str):
        return None
    try:
        exp_str = expiration.replace("Z", "+00:00")
        exp_dt = datetime.fromisoformat(exp_str)
        return max(0, (exp_dt - datetime.now(timezone.utc)).total_seconds() / 86400)
    except (ValueError, TypeError):
        return None


def _calc_market_age_hours(m: dict) -> Optional[float]:
    """Calculate hours since market opened for trading."""
    open_time = m.get("open_time", "")
    if not open_time or not isinstance(open_time, str):
        return None
    try:
        open_str = open_time.replace("Z", "+00:00")
        open_dt = datetime.fromisoformat(open_str)
        age_hours = (datetime.now(timezone.utc) - open_dt).total_seconds() / 3600
        return max(0, age_hours)
    except (ValueError, TypeError):
        return None


# ── Phase 3: Claude Estimation ────────────────────────────────────────────

def estimate_with_claude(
    market_title: str,
    market_price_cents: int,
    days_to_close: Optional[float],
    news: Optional[list[dict]] = None,
    economic_context: Optional[dict] = None,
    x_signal: Optional[dict] = None,
) -> Optional[dict]:
    """Estimate probability using Claude Sonnet (contrarian mode).

    Claude sees the market price and is asked to find reasons it's WRONG.
    Falls back to Qwen if Claude is unavailable.
    """
    from claude_estimator import estimate_probability

    return estimate_probability(
        market_title=market_title,
        days_to_close=days_to_close,
        news_context=news,
        economic_context=economic_context,
        x_signal=x_signal,
        market_price_cents=market_price_cents,
    )


def calculate_edges(markets: list[dict], cfg: dict) -> list[dict]:
    """Phase 3+4: Claude estimation + edge calculation."""
    from claude_estimator import estimate_batch

    max_to_analyze = cfg.get("max_markets_to_analyze", 50)

    # Sort by priority
    def _priority_score(m: dict) -> float:
        mid = m.get("yes_price", 50)
        oi = m.get("open_interest", 0)
        centrality = 1 - abs(mid - 50) / 50
        return centrality * (oi ** 0.3) * (m.get("volume", 0) ** 0.2)

    markets.sort(key=_priority_score, reverse=True)
    candidates = markets[:max_to_analyze]

    logger.info(f"Edge: analyzing {len(candidates)} markets with Claude")

    # Run Claude batch
    results = estimate_batch(candidates, economic_context=None, max_markets=max_to_analyze)

    # Filter by minimum edge
    min_edge = cfg.get("min_edge_pct", 3.0)
    edges = [r for r in results if r.get("effective_edge_pct", 0) >= min_edge]

    edges.sort(key=lambda x: x.get("effective_edge_pct", 0), reverse=True)
    logger.info(f"Edge: {len(edges)} with >= {min_edge}% effective edge")

    return edges


# ── Phase 4.5: Post-estimation Market Filter ────────────────────────────────

def _apply_market_filter(edges: list[dict], cfg: dict) -> list[dict]:
    """Post-estimation filter: remove low-quality edges before execution.

    Applied AFTER Claude estimation, so we can filter on estimated values
    like confidence, edge size, and direction — not just raw market data.

    Filters:
      - min_effective_edge_pct: minimum edge after confidence adjustment (default 3.0)
      - min_confidence: minimum estimator confidence (default 0.2)
      - exclude_fair: drop edges with direction == "fair" (default True)
      - max_spread_cents: skip if bid/ask spread too wide (default 10)
    """
    min_edge = cfg.get("min_edge_pct", 3.0)
    min_conf = cfg.get("min_confidence", 0.2)
    exclude_fair = cfg.get("exclude_fair_direction", True)
    max_spread = cfg.get("max_spread_cents", 10)
    if cfg.get("fresh_mode", False):
        max_spread = 25

    before = len(edges)
    filtered = []
    stats = {"low_edge": 0, "low_conf": 0, "fair": 0, "wide_spread": 0}

    for e in edges:
        eff_edge = e.get("effective_edge_pct", 0)
        conf = e.get("confidence", 0)
        direction = e.get("direction", "fair")
        spread = e.get("spread", 0)

        if eff_edge < min_edge:
            stats["low_edge"] += 1
            continue
        if conf < min_conf:
            stats["low_conf"] += 1
            continue
        if exclude_fair and direction == "fair":
            stats["fair"] += 1
            continue
        if max_spread and spread > max_spread:
            stats["wide_spread"] += 1
            continue

        filtered.append(e)

    # Sort by effective edge descending
    filtered.sort(key=lambda x: x.get("effective_edge_pct", 0), reverse=True)

    logger.info(
        f"MarketFilter: {before} → {len(filtered)} edges "
        f"(low_edge={stats['low_edge']}, low_conf={stats['low_conf']}, "
        f"fair={stats['fair']}, wide_spread={stats['wide_spread']})"
    )
    return filtered


def format_insight(edge: dict) -> dict:
    """Format edge result for output."""
    est = edge.get("estimated_probability", 0.5)
    mkt = edge.get("market_implied", 0.5)
    direction = edge.get("direction", "fair")

    return {
        "ticker": edge.get("ticker", "?"),
        "title": edge.get("title", "?")[:60],
        "side": "YES" if direction == "underpriced" else "NO",
        "confidence": "high" if edge.get("confidence", 0) > 0.6 else "medium",
        "yes_bid": edge.get("yes_bid", 0),
        "yes_ask": edge.get("yes_ask", 0),
        "volume": edge.get("volume", 0),
        "open_interest": edge.get("open_interest", 0),
        "days_to_close": edge.get("days_to_close"),
        "market_age_hours": edge.get("market_age_hours"),
        "is_fresh": (edge.get("market_age_hours") or 999) <= 48,
        "market_prob": round(mkt, 4),
        "estimated_prob": round(est, 4),
        "edge_pct": edge.get("edge_pct", 0),
        "effective_edge_pct": edge.get("effective_edge_pct", 0),
        "direction": direction,
        "reasoning": edge.get("reasoning", ""),
        "estimator": edge.get("estimator", "unknown"),
    }


def run_kalshalyst(client, cfg: dict, dry_run: bool = False) -> bool:
    """Main Kalshalyst pipeline."""
    logger.info("=" * 60)
    logger.info("Kalshalyst starting (Claude contrarian estimation)...")
    logger.info("=" * 60)

    # Phase 1: Fetch
    markets = fetch_kalshi_markets(client, cfg)
    if not markets:
        if cfg.get("fresh_mode", False):
            logger.info("FRESH: No new markets in last 48h")
        else:
            logger.info("Kalshalyst: no markets passed filters")
        return False

    # Phase 3+4: Estimate + edge
    edges = calculate_edges(markets, cfg)
    edges = _apply_market_filter(edges, cfg)

    # Phase 5: Cache + alert
    cache_payload = {
        "insights": [format_insight(e) for e in edges[:20]],
        "macro_count": len(edges),
        "total_scanned": len(markets),
        "scanner_version": "1.0.0",
        "cached_at": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(f"Kalshalyst: {len(edges)} opportunities found")

    # Phase 5: Write cache for morning-brief consumption
    cache_dir = Path.home() / ".openclaw" / "state"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / "kalshalyst_cache.json"
    try:
        with open(cache_path, "w") as f:
            json.dump(cache_payload, f, indent=2)
        logger.info(f"Cache written to {cache_path}")
    except OSError as e:
        logger.warning(f"Could not write cache: {e}")

    if dry_run:
        logger.info("[DRY RUN] Would send alerts")
        for e in edges[:3]:
            logger.info(f"  - {e.get('title', '?')[:40]} | {e.get('effective_edge_pct', 0):.1f}% edge")
        return True

    # Alert on high-edge opportunities
    alert_threshold = cfg.get("alert_edge_pct", 6.0)
    alert_candidates = [e for e in edges if e.get("effective_edge_pct", 0) >= alert_threshold]

    if alert_candidates:
        logger.info(f"Kalshalyst: {len(alert_candidates)} above alert threshold ({alert_threshold}%)")
        for i, e in enumerate(alert_candidates[:3], 1):
            side = "YES" if e.get("direction") == "underpriced" else "NO"
            logger.info(f"  {i}. {e.get('title', '?')[:45]}")
            logger.info(f"     {side} @ {e.get('market_implied', 0):.0%} | {e.get('effective_edge_pct', 0):.0f}% edge")

    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Kalshalyst")
    parser.add_argument("--dry-run", action="store_true", help="Don't send alerts")
    parser.add_argument("--force", action="store_true", help="Force run (ignore interval)")
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Scan only markets listed in last 48h with relaxed filters",
    )

    args = parser.parse_args()
    cfg = {}
    if args.fresh:
        cfg["fresh_mode"] = True

    # ── Load config from ~/.openclaw/config.yaml ──
    try:
        import yaml
    except ImportError:
        logger.error("pyyaml not installed — run: pip3 install pyyaml")
        sys.exit(1)

    config_path = Path.home() / ".openclaw" / "config.yaml"
    if not config_path.exists():
        logger.error(f"Config not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        file_config = yaml.safe_load(f) or {}

    kalshi_cfg = file_config.get("kalshi", {})
    key_id = kalshi_cfg.get("api_key_id", "")
    pk_file = kalshi_cfg.get("private_key_file", "")
    pk_path = Path(pk_file).expanduser()
    if not pk_path.is_absolute():
        pk_path = Path.home() / ".openclaw" / "keys" / pk_path

    if not key_id or not pk_path.exists():
        logger.error(f"Kalshi credentials missing — key_id={bool(key_id)}, pk_exists={pk_path.exists()}")
        sys.exit(1)

    # ── Initialize Kalshi SDK client ──
    try:
        try:
            from kalshi_python_sync import Configuration, KalshiClient
        except ImportError:
            from kalshi_python import Configuration, KalshiClient

        base_url = "https://api.elections.kalshi.com/trade-api/v2"
        sdk_config = Configuration(host=base_url)
        with open(pk_path, "r") as f:
            sdk_config.private_key_pem = f.read()
        sdk_config.api_key_id = key_id
        client = KalshiClient(sdk_config)
        sdk_config.private_key_pem = None  # clear PEM from memory

        # Verify auth
        try:
            client.get_positions(limit=1)
        except (TypeError, AttributeError):
            pass  # SDK version difference — client is still valid
        logger.info("Kalshi client initialized successfully")
    except Exception as e:
        logger.error(f"Kalshi client init failed: {e}")
        sys.exit(1)

    # ── Run pipeline ──
    if args.force:
        cfg["force"] = True
    success = run_kalshalyst(client, cfg, dry_run=args.dry_run)
    sys.exit(0 if success else 1)
