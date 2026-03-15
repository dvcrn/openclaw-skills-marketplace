#!/usr/bin/env python3
"""
shadow_tracker.py — Crypto-oriented plugin-based shadow trading tracker framework.

Part of the polymarket-crypto-shadow-tracker skill.
Uses SimmerClient from simmer_sdk for market data and resolution checks.
Optimized for Polymarket crypto fast-markets (BTC, ETH, XRP, SOL).

Commands:
    run       Evaluate markets and log shadow trades for all variants
    resolve   Check unresolved trades and update outcomes
    stats     Show per-variant statistics
    variants  Compare variants side-by-side
    promote   Recommend a variant for live trading

Usage:
    python shadow_tracker.py run     --strategy crypto_momentum_plugin.py
    python shadow_tracker.py resolve --strategy crypto_momentum_plugin.py
    python shadow_tracker.py stats   --strategy crypto_momentum_plugin.py
    python shadow_tracker.py variants --strategy crypto_momentum_plugin.py --min-n 20
    python shadow_tracker.py promote --strategy crypto_momentum_plugin.py --variant best

Config:
    python shadow_tracker.py --config
    python shadow_tracker.py --set max_trades_per_run=20

Automaton mode (no subcommand):
    Runs 'run' + 'resolve' using SHADOW_CRYPTO_PLUGIN env var.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Force line-buffered stdout (required for cron/Docker/OpenClaw visibility)
sys.stdout.reconfigure(line_buffering=True)

from shadow_plugin_base import StrategyPlugin, ShadowTrade, TradeSignal

TRADE_SOURCE = "sdk:crypto-shadow"  # Shadow-only — no real trades executed

# ─── Config System ──────────────────────────────────────────────────────────

from simmer_sdk.skill import load_config, update_config, get_config_path

SKILL_SLUG = "polymarket-crypto-shadow-tracker"

CONFIG_SCHEMA = {
    "max_trades_per_run": {"env": "SHADOW_CRYPTO_MAX_TRADES", "default": 10, "type": int},
    "min_volume": {"env": "SHADOW_CRYPTO_MIN_VOLUME", "default": 5000.0, "type": float},
    "data_dir": {"env": "SHADOW_DATA_DIR", "default": "data/shadow", "type": str},
    "plugin": {"env": "SHADOW_CRYPTO_PLUGIN", "default": "", "type": str},
}

_config = load_config(CONFIG_SCHEMA, __file__, slug=SKILL_SLUG)

# ─── Simmer Client ──────────────────────────────────────────────────────────

_client = None


def get_client():
    """Lazy-init SimmerClient singleton."""
    global _client
    if _client is None:
        try:
            from simmer_sdk import SimmerClient
        except ImportError:
            print("Error: simmer-sdk not installed. Run: pip install simmer-sdk")
            sys.exit(1)
        api_key = os.environ.get("SIMMER_API_KEY")
        if not api_key:
            print("Error: SIMMER_API_KEY environment variable not set")
            print("Get your API key from: simmer.markets/dashboard -> SDK tab")
            sys.exit(1)
        venue = os.environ.get("TRADING_VENUE", "polymarket")
        _client = SimmerClient(api_key=api_key, venue=venue)
    return _client


# ─── Storage ────────────────────────────────────────────────────────────────

DATA_DIR = Path(_config["data_dir"])


def log_path(strategy_name: str) -> Path:
    return DATA_DIR / f"shadow_{strategy_name}.jsonl"


def read_trades(strategy_name: str) -> list[ShadowTrade]:
    path = log_path(strategy_name)
    if not path.exists():
        return []
    trades = []
    for line in path.read_text().splitlines():
        if line.strip():
            trades.append(ShadowTrade.from_dict(json.loads(line)))
    return trades


def write_trades(strategy_name: str, trades: list[ShadowTrade]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = log_path(strategy_name)
    with open(path, "w") as f:
        for t in trades:
            f.write(t.to_json() + "\n")


def append_trade(strategy_name: str, trade: ShadowTrade) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(log_path(strategy_name), "a") as f:
        f.write(trade.to_json() + "\n")


# ─── Plugin Loader ──────────────────────────────────────────────────────────

def load_plugin(path: str) -> StrategyPlugin:
    """Load a StrategyPlugin subclass from a Python file."""
    spec = importlib.util.spec_from_file_location("strategy_module", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module from {path}")
    mod = importlib.util.module_from_spec(spec)

    # Make shadow_plugin_base importable from the framework dir
    framework_dir = str(Path(__file__).parent)
    if framework_dir not in sys.path:
        sys.path.insert(0, framework_dir)

    spec.loader.exec_module(mod)

    # Find the StrategyPlugin subclass
    candidates = []
    for attr_name in dir(mod):
        attr = getattr(mod, attr_name)
        if (isinstance(attr, type)
                and issubclass(attr, StrategyPlugin)
                and attr is not StrategyPlugin):
            candidates.append(attr)

    if not candidates:
        raise RuntimeError(f"No StrategyPlugin subclass found in {path}")
    if len(candidates) > 1:
        print(f"Warning: multiple plugins found, using {candidates[0].__name__}")

    return candidates[0]()


# ─── Dedup ───────────────────────────────────────────────────────────────────

def _trade_key(variant: str, market_id: str) -> str:
    return f"{variant}:{market_id}"


def existing_keys(trades: list[ShadowTrade]) -> set[str]:
    return {_trade_key(t.variant, t.market_id) for t in trades}


# ─── Commands ────────────────────────────────────────────────────────────────

def cmd_run(plugin: StrategyPlugin, client: Any = None, dry_run: bool = False) -> int:
    """Evaluate markets across all variants, log new shadow trades."""
    variants = plugin.variants()
    markets = plugin.get_markets(client)
    trades = read_trades(plugin.name)
    seen = existing_keys(trades)
    new_count = 0
    max_trades = _config["max_trades_per_run"]

    print(f"Strategy: {plugin.name}")
    print(f"Variants: {len(variants)}, Markets: {len(markets)}")
    print("─" * 50)

    for variant_name, params in variants:
        for market in markets:
            if new_count >= max_trades:
                break

            mid = market.get("id") or market.get("market_id", "unknown")
            key = _trade_key(variant_name, mid)
            if key in seen:
                continue

            signal = plugin.evaluate(market, params)
            if signal is None:
                continue

            trade = ShadowTrade(
                variant=variant_name,
                market_id=signal.market_id,
                side=signal.side,
                entry_price=signal.entry_price,
                signal=signal.signal,
                params=params,
                timestamp=datetime.now(timezone.utc).isoformat(),
                meta=signal.meta,
            )

            if dry_run:
                print(f"  [DRY] {variant_name} → {signal.market_id} "
                      f"@ {signal.entry_price:.3f} ({signal.signal})")
            else:
                append_trade(plugin.name, trade)
                seen.add(key)
                print(f"  [NEW] {variant_name} → {signal.market_id} "
                      f"@ {signal.entry_price:.3f} ({signal.signal})")
            new_count += 1

    print(f"\n{'Would log' if dry_run else 'Logged'} {new_count} new shadow trades.")

    # Automaton reporting
    if os.environ.get("AUTOMATON_MANAGED"):
        print(json.dumps({"automaton": {
            "signals": new_count,
            "trades_attempted": 0,
            "trades_executed": 0,
            "skip_reason": "shadow_only" if new_count == 0 else None
        }}))

    return new_count


def cmd_resolve(plugin: StrategyPlugin, client: Any = None) -> int:
    """Check unresolved trades and update outcomes via positions endpoint."""
    trades = read_trades(plugin.name)
    resolved_count = 0

    # Fetch resolved positions to get outcome data
    outcome_map: dict[str, str] = {}
    if client:
        try:
            resolved_positions = client._request(
                "GET", "/api/sdk/positions", params={"status": "resolved"}
            )
            outcome_map = {
                p["market_id"]: p["outcome"]
                for p in resolved_positions.get("positions", [])
                if "market_id" in p and "outcome" in p
            }
        except Exception as e:
            print(f"  ⚠ Failed to fetch resolved positions: {e}")

    for trade in trades:
        if trade.resolved:
            continue

        # Check outcome from positions endpoint
        outcome = outcome_map.get(trade.market_id)
        if outcome is None:
            # Fallback: let the plugin decide
            market_data = None
            if client:
                try:
                    m = client.get_market_by_id(trade.market_id)
                    if m:
                        market_data = {
                            "id": m.id,
                            "question": m.question,
                            "status": m.status,
                            "current_probability": m.current_probability,
                        }
                except Exception:
                    pass
            result = plugin.is_win(trade, market_data)
        else:
            # Resolved via positions endpoint
            resolved_yes = outcome.lower() == "yes"
            traded_yes = trade.side.upper() == "YES"
            result = resolved_yes == traded_yes

        if result is None:
            continue

        trade.resolved = True
        trade.outcome = "win" if result else "loss"
        if trade.outcome == "win":
            trade.payout = (1.0 / trade.entry_price) - 1.0 if trade.entry_price > 0 else 0
        else:
            trade.payout = -1.0
        resolved_count += 1

    if resolved_count:
        write_trades(plugin.name, trades)
    print(f"Resolved {resolved_count} trades for {plugin.name}.")

    # Automaton reporting
    if os.environ.get("AUTOMATON_MANAGED"):
        print(json.dumps({"automaton": {
            "signals": 0,
            "trades_attempted": 0,
            "trades_executed": 0,
            "skip_reason": f"resolved_{resolved_count}" if resolved_count else "no_resolutions"
        }}))

    return resolved_count


@dataclass
class VariantStats:
    variant: str
    n: int = 0
    wins: int = 0
    losses: int = 0
    unresolved: int = 0
    total_payout: float = 0.0
    prices: list = None

    def __post_init__(self):
        if self.prices is None:
            self.prices = []

    @property
    def resolved(self) -> int:
        return self.wins + self.losses

    @property
    def wr(self) -> float | None:
        return self.wins / self.resolved if self.resolved else None

    @property
    def ev(self) -> float | None:
        return self.total_payout / self.resolved if self.resolved else None

    @property
    def price_range(self) -> str:
        if not self.prices:
            return "—"
        return f"{min(self.prices):.2f}–{max(self.prices):.2f}"


def compute_stats(trades: list[ShadowTrade]) -> dict[str, VariantStats]:
    by_variant: dict[str, VariantStats] = {}
    for t in trades:
        vs = by_variant.setdefault(t.variant, VariantStats(variant=t.variant))
        vs.n += 1
        vs.prices.append(t.entry_price)
        if not t.resolved:
            vs.unresolved += 1
        elif t.outcome == "win":
            vs.wins += 1
            vs.total_payout += t.payout or 0
        else:
            vs.losses += 1
            vs.total_payout += t.payout or -1.0
    return by_variant


def cmd_stats(plugin: StrategyPlugin) -> None:
    """Print per-variant statistics."""
    trades = read_trades(plugin.name)
    if not trades:
        print(f"No shadow trades for {plugin.name}.")
        return

    stats = compute_stats(trades)
    baseline = stats.get("default")

    print(f"\n{'Variant':<28} {'N':>4} {'Res':>4} {'WR%':>6} {'EV':>7} "
          f"{'Prices':>12} {'vs Base':>8}")
    print("─" * 76)

    for name in sorted(stats):
        vs = stats[name]
        wr = f"{vs.wr * 100:.1f}" if vs.wr is not None else "—"
        ev = f"{vs.ev:+.3f}" if vs.ev is not None else "—"
        delta = ""
        if baseline and name != "default" and vs.ev is not None and baseline.ev is not None:
            d = vs.ev - baseline.ev
            delta = f"{d:+.3f}"
        print(f"{name:<28} {vs.n:>4} {vs.resolved:>4} {wr:>6} {ev:>7} "
              f"{vs.price_range:>12} {delta:>8}")

    unresolved = sum(1 for t in trades if not t.resolved)
    print(f"\nTotal: {len(trades)} trades, {unresolved} unresolved")


def cmd_variants(plugin: StrategyPlugin, min_n: int = 0) -> None:
    """List variants filtered by minimum sample size."""
    trades = read_trades(plugin.name)
    stats = compute_stats(trades)

    filtered = {k: v for k, v in stats.items() if v.resolved >= min_n}
    if not filtered:
        print(f"No variants with >= {min_n} resolved trades.")
        return

    ranked = sorted(filtered.values(),
                    key=lambda v: v.ev if v.ev is not None else -999,
                    reverse=True)

    print(f"\nVariants with >= {min_n} resolved trades (ranked by EV):\n")
    print(f"{'#':>3} {'Variant':<28} {'N':>4} {'WR%':>6} {'EV':>7}")
    print("─" * 52)
    for i, vs in enumerate(ranked, 1):
        wr = f"{vs.wr * 100:.1f}" if vs.wr is not None else "—"
        ev = f"{vs.ev:+.3f}" if vs.ev is not None else "—"
        print(f"{i:>3} {vs.variant:<28} {vs.resolved:>4} {wr:>6} {ev:>7}")


def cmd_promote(plugin: StrategyPlugin, variant: str | None = None,
                min_n: int | None = None, min_wr: float | None = None,
                min_ev_delta: float | None = None) -> None:
    """Evaluate a variant (or best) for promotion to live trading."""
    _min_n = min_n if min_n is not None else plugin.min_n
    _min_wr = min_wr if min_wr is not None else plugin.min_wr
    _min_ev = min_ev_delta if min_ev_delta is not None else plugin.min_ev_delta

    trades = read_trades(plugin.name)
    stats = compute_stats(trades)
    baseline = stats.get("default")

    if variant and variant != "best":
        if variant not in stats:
            print(f"Variant '{variant}' not found.")
            return
        candidates = [stats[variant]]
    else:
        candidates = sorted(
            [v for v in stats.values() if v.variant != "default"],
            key=lambda v: v.ev if v.ev is not None else -999,
            reverse=True,
        )

    print(f"\n{'='*60}")
    print(f"PROMOTION ANALYSIS — {plugin.name}")
    print(f"Thresholds: min_n={_min_n}, min_wr={_min_wr*100:.0f}%, "
          f"min_ev_delta={_min_ev:+.3f}")
    print(f"{'='*60}\n")

    promoted = False
    for vs in candidates[:5]:
        checks = []
        pass_all = True

        ok = vs.resolved >= _min_n
        checks.append(f"  N >= {_min_n}: {vs.resolved} {'✓' if ok else '✗'}")
        pass_all &= ok

        if vs.wr is not None:
            ok = vs.wr >= _min_wr
            checks.append(f"  WR >= {_min_wr*100:.0f}%: {vs.wr*100:.1f}% {'✓' if ok else '✗'}")
            pass_all &= ok
        else:
            checks.append(f"  WR >= {_min_wr*100:.0f}%: no data ✗")
            pass_all = False

        if vs.ev is not None and baseline and baseline.ev is not None:
            delta = vs.ev - baseline.ev
            ok = delta >= _min_ev
            checks.append(f"  EV delta >= {_min_ev:+.3f}: {delta:+.3f} {'✓' if ok else '✗'}")
            pass_all &= ok
        elif vs.ev is not None:
            checks.append(f"  EV delta: no baseline (skipped)")
        else:
            checks.append(f"  EV delta: no data ✗")
            pass_all = False

        status = "✅ PROMOTE" if pass_all else "❌ NOT READY"
        print(f"Variant: {vs.variant}  →  {status}")
        for c in checks:
            print(c)

        if pass_all:
            print(f"\n  Recommendation: adopt '{vs.variant}' params:")
            for t in trades:
                if t.variant == vs.variant:
                    for k, v in t.params.items():
                        print(f"    {k}: {v}")
                    break
            promoted = True
            break
        print()

    if not promoted:
        print("No variant meets promotion criteria yet. Keep collecting data.")


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Crypto shadow trading tracker framework (BTC/ETH/XRP/SOL)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--config", action="store_true", help="Show current config")
    parser.add_argument("--set", action="append", metavar="KEY=VALUE",
                        help="Set config value (e.g. --set max_trades_per_run=20)")
    parser.add_argument("--live", action="store_true",
                        help="(No-op for shadow tracker — all trades are paper)")
    parser.add_argument("--dry-run", action="store_true",
                        help="(Default) Preview mode")

    sub = parser.add_subparsers(dest="command")

    # run
    p_run = sub.add_parser("run", help="Evaluate markets and log shadow trades")
    p_run.add_argument("--strategy", "-s", help="Path to strategy plugin .py")
    p_run.add_argument("--dry-run", action="store_true", help="Don't write, just preview")

    # resolve
    p_res = sub.add_parser("resolve", help="Resolve unresolved trades")
    p_res.add_argument("--strategy", "-s")

    # stats
    p_stats = sub.add_parser("stats", help="Show per-variant statistics")
    p_stats.add_argument("--strategy", "-s", required=True)

    # variants
    p_var = sub.add_parser("variants", help="Rank variants by performance")
    p_var.add_argument("--strategy", "-s", required=True)
    p_var.add_argument("--min-n", type=int, default=0, help="Min resolved trades")

    # promote
    p_promo = sub.add_parser("promote", help="Evaluate variant for promotion")
    p_promo.add_argument("--strategy", "-s", required=True)
    p_promo.add_argument("--variant", default="best", help="Variant name or 'best'")
    p_promo.add_argument("--min-n", type=int, default=None)
    p_promo.add_argument("--min-wr", type=float, default=None)
    p_promo.add_argument("--min-ev-delta", type=float, default=None)

    args = parser.parse_args()

    # Handle --set
    if args.set:
        updates = {}
        for item in args.set:
            if "=" in item:
                key, value = item.split("=", 1)
                if key in CONFIG_SCHEMA:
                    type_fn = CONFIG_SCHEMA[key].get("type", str)
                    try:
                        value = type_fn(value)
                    except (ValueError, TypeError):
                        pass
                updates[key] = value
        if updates:
            updated = update_config(updates, __file__)
            print(f"Config updated: {updates}")
            print(f"Saved to: {get_config_path(__file__)}")
        return

    # Handle --config
    if args.config:
        print(f"Config path: {get_config_path(__file__)}")
        print(f"Current config:")
        for k, v in _config.items():
            schema = CONFIG_SCHEMA.get(k, {})
            env = schema.get("env", "—")
            print(f"  {k}: {v}  (env: {env})")
        return

    # Resolve plugin path: CLI arg or config
    plugin_path = getattr(args, 'strategy', None) or _config.get("plugin") or os.environ.get("SHADOW_CRYPTO_PLUGIN")

    # Automaton mode: no subcommand → run + resolve
    if not args.command:
        if not plugin_path:
            print("Error: set SHADOW_CRYPTO_PLUGIN env var, config plugin, or use --strategy/-s")
            sys.exit(1)
        plugin = load_plugin(plugin_path)
        client = get_client()
        cmd_run(plugin, client=client)
        cmd_resolve(plugin, client=client)
        return

    if not plugin_path:
        print("Error: --strategy/-s is required (or set SHADOW_CRYPTO_PLUGIN env var)")
        sys.exit(1)

    plugin = load_plugin(plugin_path)

    if args.command == "run":
        client = get_client()
        cmd_run(plugin, client=client, dry_run=args.dry_run)
    elif args.command == "resolve":
        client = get_client()
        cmd_resolve(plugin, client=client)
    elif args.command == "stats":
        cmd_stats(plugin)
    elif args.command == "variants":
        cmd_variants(plugin, min_n=args.min_n)
    elif args.command == "promote":
        cmd_promote(plugin, variant=args.variant,
                    min_n=args.min_n, min_wr=args.min_wr,
                    min_ev_delta=args.min_ev_delta)


if __name__ == "__main__":
    main()
