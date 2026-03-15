---
name: polymarket-crypto-shadow-tracker
description: "Stop guessing which crypto strategy works. Shadow-trade every variant simultaneously on Polymarket — BTC, ETH, XRP, SOL across timeframes and thresholds — then promote the winner to live capital based on real stats, not vibes. The backtesting layer serious traders were missing."
---

# Polymarket Crypto Shadow Tracker

Every strategy looks good in your head. This one makes you prove it first. Shadow-trade every parameter variant on Polymarket crypto fast-markets — zero capital at risk — then promote the winner when the numbers say so.

## What It Does

1. **Discovers** crypto fast-markets via Simmer API (`get_fast_markets(asset=, window=)`)
2. **Evaluates** each market against your strategy plugin's signal logic
3. **Logs** shadow trades per variant — no real money touches the chain
4. **Resolves** outcomes using the positions endpoint
5. **Ranks** variants by win rate and EV — see what's actually working
6. **Promotes** the best variant when it clears your statistical gates

## Starter Template Plugin

The included `crypto_momentum_plugin.py` is your starting point — drop in your signal logic, define your parameter grid, and the framework handles everything else.

### Quick Start

```bash
# Shadow-trade BTC/ETH momentum variants
python shadow_tracker.py run -s crypto_momentum_plugin.py

# Resolve outcomes
python shadow_tracker.py resolve -s crypto_momentum_plugin.py

# Compare variants
python shadow_tracker.py stats -s crypto_momentum_plugin.py

# Find the best variant
python shadow_tracker.py promote -s crypto_momentum_plugin.py
```

### Automaton Mode

Set `SHADOW_CRYPTO_PLUGIN=crypto_momentum_plugin.py` and run without a subcommand — it executes `run` + `resolve` automatically.

## Config

| Key | Env Var | Default | Description |
|-----|---------|---------|-------------|
| `max_trades_per_run` | `SHADOW_CRYPTO_MAX_TRADES` | 10 | Max shadow trades logged per run |
| `min_volume` | `SHADOW_CRYPTO_MIN_VOLUME` | 5000 | Min 24h volume filter |
| `data_dir` | `SHADOW_DATA_DIR` | `data/shadow` | Directory for trade logs |
| `plugin` | `SHADOW_CRYPTO_PLUGIN` | — | Path to strategy plugin .py |

```bash
# View config
python shadow_tracker.py --config

# Update config
python shadow_tracker.py --set max_trades_per_run=20
```

## Writing Custom Plugins

Subclass `StrategyPlugin` from `shadow_plugin_base.py`:

```python
from shadow_plugin_base import StrategyPlugin, TradeSignal, ShadowTrade

class MyStrategy(StrategyPlugin):
    name = "my_crypto_strategy"
    default_params = {"coin": "BTC", "threshold": 0.05}
    param_grid = {"coin": ["BTC", "ETH"], "threshold": [0.03, 0.05, 0.08]}

    # Promotion thresholds
    min_n = 30
    min_wr = 0.58
    min_ev_delta = 0.02

    def get_markets(self, client=None):
        """Fetch markets. Use client.get_fast_markets() for crypto."""
        markets = client.get_fast_markets(asset="BTC", window="15m", limit=50)
        return [{"id": m.id, "price": m.current_probability, ...} for m in markets]

    def evaluate(self, market, params):
        """Return TradeSignal or None."""
        ...

    def is_win(self, trade, market=None):
        """Return True/False/None. Resolution also handled by framework."""
        ...
```

### Plugin Interface

| Method | Returns | Purpose |
|--------|---------|---------|
| `get_markets(client)` | `list[dict]` | Fetch candidate markets |
| `evaluate(market, params)` | `TradeSignal \| None` | Generate signal for a market+params combo |
| `is_win(trade, market)` | `bool \| None` | Check resolution (fallback — framework uses positions API) |

### Fast-Markets Fields (from Simmer SDK)

| Field | Type | Description |
|-------|------|-------------|
| `m.id` | str | Simmer market ID |
| `m.question` | str | Market question text |
| `m.current_probability` | float | Current YES price (0-1) |
| `m.resolves_at` | str | ISO timestamp of resolution |
| `m.is_live_now` | bool | Whether market is actively tradeable |
| `m.spread_cents` | float | Current spread in cents |
| `m.external_price_yes` | float | External reference price |
| `m.liquidity_tier` | str | Liquidity classification |

## Requirements

- `simmer-sdk` (pip)
- `SIMMER_API_KEY` environment variable
