#!/usr/bin/env python3
"""
Market Morning Brief — Daily market intelligence digest.

Combines portfolio positions, prediction market opportunities, cross-platform
divergences, crypto prices, and X signals into a 30-second morning read.

Usage:
    python morning_brief.py [--config CONFIG] [--dry-run] [--debug]

Outputs plain text to stdout (no markdown, no emojis — SMS/iMessage compatible).
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Optional dependencies
try:
    import requests
except ImportError:
    requests = None

try:
    import yaml
except ImportError:
    yaml = None

try:
    from kalshi_python import KalshiClient
except ImportError:
    KalshiClient = None


def log(msg, debug=False):
    """Log message to stderr if debug enabled."""
    if debug:
        print(f"[DEBUG] {msg}", file=sys.stderr)


def format_time(ts_str):
    """Format ISO timestamp to readable string."""
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts_str


def check_cache_age(cache_file, max_age_seconds):
    """Check if cache is fresh. Returns ('fresh', age_secs) or ('stale', age_secs) or ('missing', 0).

    Handles both ISO "cached_at" strings and unix epoch "timestamp" floats.
    """
    try:
        with open(cache_file) as f:
            data = json.load(f)

        # Try ISO "cached_at" first, then unix epoch "timestamp"
        cached_at = data.get("cached_at")
        timestamp = data.get("timestamp")

        if cached_at:
            try:
                dt = datetime.fromisoformat(cached_at.replace("Z", "+00:00"))
                age_seconds = (datetime.now(timezone.utc) - dt).total_seconds()
            except (ValueError, TypeError):
                age_seconds = None
        elif timestamp:
            try:
                import time as _time
                age_seconds = _time.time() - float(timestamp)
            except (ValueError, TypeError):
                age_seconds = None
        else:
            return "missing", 0

        if age_seconds is None:
            return "error", 0

        if age_seconds > max_age_seconds:
            return "stale", age_seconds
        return "fresh", age_seconds
    except FileNotFoundError:
        return "missing", 0
    except Exception:
        return "error", 0


def format_portfolio_section(kalshi, config, debug=False):
    """Fetch and format portfolio section."""
    section_lines = []

    if not kalshi:
        return "PORTFOLIO: unavailable (Kalshi API not configured)"

    try:
        # Use get_positions() (correct SDK method), not get_portfolio()
        try:
            resp = kalshi.get_positions(limit=100, settlement_status="unsettled")
        except (TypeError, Exception):
            resp = kalshi.get_positions()

        # Handle SDK v3 (.positions) and v2 (.market_positions)
        if isinstance(resp, dict):
            positions = resp.get("positions", resp.get("market_positions", []))
        else:
            positions = getattr(resp, "positions", None)
            if positions is None:
                positions = getattr(resp, "market_positions", [])
            positions = positions or []

        if not positions:
            return "PORTFOLIO: (no positions)"

        total_unrealized = 0.0
        lines = [f"PORTFOLIO ({len(positions)} positions):"]

        for pos in positions:
            ticker = pos.get("ticker", "?")
            side = "YES" if pos.get("yes_price") else "NO"
            quantity = pos.get("quantity", 0)
            avg_price = pos.get("average_price", 0) / 100 if pos.get("average_price") else 0

            # Fetch market data ONCE per ticker (not twice)
            current_price = avg_price
            days_to_exp = 0
            try:
                market = kalshi.get_market(ticker)
                if market.get("last_price"):
                    current_price = market["last_price"] / 100
                exp_ts = market.get("close_datetime")
                if exp_ts:
                    exp_dt = datetime.fromisoformat(exp_ts.replace("Z", "+00:00"))
                    days_to_exp = (exp_dt - datetime.now(timezone.utc)).days
            except Exception:
                pass

            cost = quantity * avg_price
            unrealized = quantity * (current_price - avg_price)
            total_unrealized += unrealized

            unrealized_str = f"+${unrealized:.0f}" if unrealized >= 0 else f"-${abs(unrealized):.0f}"
            line = f"{ticker:20} {side:3}  {quantity:3}@{current_price*100:.0f}¢  ${cost:.0f} cost  {unrealized_str:6} (exp: {days_to_exp}d)"

            lines.append(line)

        total_str = f"+${total_unrealized:.0f}" if total_unrealized >= 0 else f"-${abs(total_unrealized):.0f}"
        lines[0] = f"PORTFOLIO ({len(positions)} positions, {total_str} unrealized):"

        return "\n".join(lines)

    except Exception as e:
        log(f"Portfolio fetch error: {e}", debug)
        return f"PORTFOLIO: unavailable ({str(e)[:40]})"


def format_kalshalyst_section(cache_path, config, debug=False):
    """Read Kalshalyst edges from cache."""
    freshness, age = check_cache_age(cache_path, 7200)  # 2 hour tolerance

    if freshness == "missing":
        return "EDGES: unavailable (install Kalshalyst skill for contrarian analysis)"

    if freshness == "stale":
        log(f"Kalshalyst cache stale: {age}s old", debug)
        return "EDGES: unavailable (Kalshalyst data stale — check skill)"

    try:
        with open(cache_path) as f:
            data = json.load(f)

        insights = data.get("insights", [])[:3]
        if not insights:
            return "EDGES: none found"

        lines = [f"EDGES (Kalshalyst, top {len(insights)}):"]

        for i, edge in enumerate(insights, 1):
            ticker = edge.get("ticker", "?")
            market_prob = edge.get("market_prob", 0.5)
            estimated_prob = edge.get("estimated_prob", 0.5)

            # Determine side
            side = "NO" if estimated_prob > market_prob else "YES"

            edge_pct = edge.get("edge_pct", 0)
            confidence = edge.get("confidence", 0)

            lines.append(
                f"{i}. {ticker:20}  {side} @ {market_prob*100:.0f}%  (+{edge_pct:.0f}% edge, {confidence*100:.0f}% conf)"
            )

        return "\n".join(lines)

    except Exception as e:
        log(f"Kalshalyst parse error: {e}", debug)
        return "EDGES: unavailable (cache corrupted)"


def format_arbiter_section(cache_path, config, debug=False):
    """Read Arbiter divergences from cache."""
    freshness, age = check_cache_age(cache_path, 21600)  # 6 hour tolerance

    if freshness == "missing":
        return "DIVERGENCES: unavailable (install Prediction Market Arbiter for cross-platform analysis)"

    if freshness == "stale":
        log(f"Arbiter cache stale: {age}s old", debug)
        return "DIVERGENCES: unavailable (Arbiter data stale)"

    try:
        with open(cache_path) as f:
            data = json.load(f)

        # Support both "divergences" (new) and "matches" (legacy) keys
        divergences = data.get("divergences", data.get("matches", []))[:2]
        if not divergences:
            return "DIVERGENCES: none found today"

        lines = ["DIVERGENCES (Arbiter, Kalshi ↔ Polymarket):"]

        for div in divergences:
            ticker = div.get("ticker", div.get("kalshi_title", "?"))[:20]
            kalshi_p = div.get("kalshi_price", 0)
            pm_p = div.get("polymarket_price", div.get("pm_price", 0))

            # Handle both 0-1 float (new) and integer cents (legacy)
            if kalshi_p > 1:
                kalshi_p = kalshi_p / 100.0
            if pm_p > 1:
                pm_p = pm_p / 100.0

            spread_cents = div.get("spread_cents", div.get("delta", 0))

            lines.append(
                f"{ticker:20}  Kalshi {kalshi_p*100:.0f}% ↔ PM {pm_p*100:.0f}%  ({spread_cents}¢ spread)"
            )

        return "\n".join(lines)

    except Exception as e:
        log(f"Arbiter parse error: {e}", debug)
        return "DIVERGENCES: unavailable (cache corrupted)"


def format_xpulse_section(cache_path, config, debug=False):
    """Read Xpulse signals from cache, filter to last 24h."""
    freshness, age = check_cache_age(cache_path, 14400)  # 4 hour tolerance

    if freshness == "missing":
        return "X SIGNALS: unavailable (install Xpulse for social sentiment analysis)"

    if freshness == "stale":
        log(f"Xpulse cache stale: {age}s old", debug)
        return "X SIGNALS: unavailable (Xpulse data stale)"

    try:
        with open(cache_path) as f:
            data = json.load(f)

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=24)

        signals = []
        for sig in data.get("signals", []):
            ts_str = sig.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if ts > cutoff:
                    signals.append(sig)
            except Exception:
                pass

        # Sort by confidence, take top 2
        signals.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        signals = signals[:2]

        if not signals:
            return "X SIGNALS: none found (check Xpulse directly)"

        lines = ["X SIGNALS (last 24h):"]

        for sig in signals:
            signal_text = sig.get("signal", "?")
            confidence = sig.get("confidence", 0)
            reach = sig.get("reach", 0)

            # Format reach
            if reach > 1000:
                reach_str = f"{reach/1000:.1f}K"
            else:
                reach_str = str(reach)

            lines.append(f"{signal_text:40}  ({confidence*100:.0f}% conf, {reach_str} reach)")

        return "\n".join(lines)

    except Exception as e:
        log(f"Xpulse parse error: {e}", debug)
        return "X SIGNALS: unavailable (cache corrupted)"


def format_crypto_section(config, debug=False):
    """Fetch crypto prices from Coinbase."""
    if not requests:
        return "CRYPTO: unavailable (requests library not installed)"

    coinbase_cfg = config.get("coinbase", {})
    if not coinbase_cfg.get("enabled"):
        return "CRYPTO: unavailable (configure Coinbase API for crypto prices)"

    api_key = coinbase_cfg.get("api_key")
    if not api_key:
        return "CRYPTO: unavailable (Coinbase API key not configured)"

    tickers = coinbase_cfg.get("tickers", ["BTC", "ETH"])

    lines = ["CRYPTO:"]
    prices = []

    for ticker in tickers:
        try:
            url = f"https://api.coinbase.com/v2/prices/{ticker}-USD/spot"
            resp = requests.get(url, timeout=3, headers={"Authorization": f"Bearer {api_key}"})
            resp.raise_for_status()

            data = resp.json()
            price = float(data.get("data", {}).get("amount", 0))
            prices.append(f"{ticker:5}  ${price:10,.2f}")

        except Exception as e:
            log(f"Crypto fetch error ({ticker}): {e}", debug)

    if not prices:
        return "CRYPTO: unavailable (Coinbase API error)"

    # Format as pairs
    lines = ["CRYPTO:"]
    for i in range(0, len(prices), 2):
        if i + 1 < len(prices):
            lines.append(f"{prices[i]}  | {prices[i+1]}")
        else:
            lines.append(prices[i])

    return "\n".join(lines)


def format_polymarket_section(config, debug=False):
    """Fetch top Polymarket markets."""
    if not requests:
        return "POLYMARKET: unavailable (requests library not installed)"

    try:
        # Use Gamma API (market listing), not CLOB API (order-book focused)
        url = "https://gamma-api.polymarket.com/markets?closed=false&limit=10&order=volume&ascending=false"
        resp = requests.get(url, timeout=10, headers={
            "Accept": "application/json",
            "User-Agent": "OpenClaw-MorningBrief/1.0",
        })
        resp.raise_for_status()

        data = resp.json()
        markets = data if isinstance(data, list) else data.get("data", [])
        if not markets:
            return "POLYMARKET: no markets available"

        # Take top 3 by volume
        markets = markets[:3]

        lines = ["POLYMARKET (top 3 by volume):"]

        for market in markets:
            question = market.get("question", market.get("title", "?"))[:50]
            volume = float(market.get("volume", 0) or 0)

            # Get implied probability from outcomePrices
            prices_raw = market.get("outcomePrices", "[]")
            if isinstance(prices_raw, str):
                try:
                    prices_raw = json.loads(prices_raw)
                except Exception:
                    prices_raw = []

            if prices_raw:
                implied_prob = float(prices_raw[0]) * 100
            else:
                implied_prob = 50

            volume_m = volume / 1_000_000 if volume > 0 else 0

            lines.append(f"{question:45}  ${volume_m:.1f}M vol, {implied_prob:.0f}%")

        return "\n".join(lines)

    except Exception as e:
        log(f"Polymarket fetch error: {e}", debug)
        return "POLYMARKET: unavailable (check Polymarket directly)"


def build_morning_brief(config, kalshi=None, debug=False):
    """Build complete morning brief."""
    now = datetime.now()
    header = f"MARKET MORNING BRIEF — {now.strftime('%A, %B %d, %Y')}"

    sections = [header]

    # Portfolio (required)
    if config.get("include", {}).get("portfolio", True):
        portfolio = format_portfolio_section(kalshi, config, debug)
        sections.append(portfolio)

    # Kalshalyst edges (optional)
    if config.get("include", {}).get("kalshalyst_edges", True):
        cache_path = config.get("cache_paths", {}).get("kalshalyst")
        if cache_path:
            edges = format_kalshalyst_section(cache_path, config, debug)
            sections.append(edges)

    # Arbiter divergences (optional)
    if config.get("include", {}).get("arbiter_divergences", True):
        cache_path = config.get("cache_paths", {}).get("arbiter")
        if cache_path:
            divergences = format_arbiter_section(cache_path, config, debug)
            sections.append(divergences)

    # Xpulse signals (optional)
    if config.get("include", {}).get("xpulse_signals", True):
        cache_path = config.get("cache_paths", {}).get("xpulse")
        if cache_path:
            signals = format_xpulse_section(cache_path, config, debug)
            sections.append(signals)

    # Crypto (optional)
    if config.get("include", {}).get("crypto", False):
        crypto = format_crypto_section(config, debug)
        sections.append(crypto)

    # Polymarket (optional)
    if config.get("include", {}).get("polymarket", True):
        pm = format_polymarket_section(config, debug)
        sections.append(pm)

    return "\n\n".join(sections)


def load_config(config_path=None):
    """Load config from YAML file or return defaults."""
    if config_path and Path(config_path).exists():
        if yaml:
            with open(config_path) as f:
                data = yaml.safe_load(f)
                return data.get("market_morning_brief", {})

    # Default config
    return {
        "enabled": True,
        "kalshi": {"enabled": False},
        "cache_paths": {
            "kalshalyst": str(Path.home() / ".openclaw" / "state" / "kalshalyst_cache.json"),
            "arbiter": str(Path.home() / ".openclaw" / "state" / "arbiter_cache.json"),
            "xpulse": str(Path.home() / ".openclaw" / "state" / "x_signal_cache.json"),
        },
        "include": {
            "portfolio": True,
            "kalshalyst_edges": True,
            "arbiter_divergences": True,
            "xpulse_signals": True,
            "crypto": False,
            "polymarket": True,
        },
    }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Market Morning Brief")
    parser.add_argument("--config", help="Path to config.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Don't send, just print")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    config = load_config(args.config)

    # Initialize Kalshi client if configured
    kalshi = None
    if config.get("kalshi", {}).get("enabled") and KalshiClient:
        try:
            api_key_id = config["kalshi"].get("api_key_id")
            private_key_file = config["kalshi"].get("private_key_file")

            if api_key_id and private_key_file:
                with open(private_key_file) as f:
                    private_key = f.read()
                kalshi = KalshiClient(key_id=api_key_id, private_key=private_key)
        except Exception as e:
            log(f"Kalshi init error: {e}", args.debug)

    brief = build_morning_brief(config, kalshi, debug=args.debug)

    print(brief)

    if args.debug:
        print("\n[DEBUG] Brief generated successfully", file=sys.stderr)


if __name__ == "__main__":
    main()
