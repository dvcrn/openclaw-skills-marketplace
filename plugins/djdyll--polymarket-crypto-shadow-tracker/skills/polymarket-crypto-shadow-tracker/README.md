# Polymarket Crypto Shadow Tracker

Most traders pick a strategy, throw money at it, and hope. This skill makes you do the work first. Shadow-trade every parameter variant simultaneously — different coins, timeframes, thresholds — with zero capital at risk. When a variant proves itself statistically, you promote it to live trading. You don't guess what works. You measure it.

The framework is signal-agnostic. You bring the alpha — your data sources, your indicators, your edge. It handles variant generation, trade logging, resolution tracking, statistical comparison, and promotion gating. Paper-trade 18 variants at once and know exactly which one deserves real money.

## Quick Start

```bash
# 1. Install
clawhub install polymarket-crypto-shadow-tracker

# 2. Copy the plugin template and implement your strategy
cp crypto_momentum_plugin.py my_btc_plugin.py

# 3. Run shadows
python shadow_tracker.py run --strategy my_btc_plugin.py --dry-run
```

Requires `SIMMER_API_KEY` in your environment. Get one from [simmer.markets/dashboard](https://simmer.markets/dashboard) → SDK tab.

## How It Works

Six stages. Each one earns its place.

1. **Plugin** — You write a `StrategyPlugin` subclass: which markets to trade, how to generate signals, how to check resolution. This is the only code you write.

2. **Variant Grid** — Your `param_grid` generates every parameter combination as a named variant. 2 coins × 3 timeframes × 3 thresholds = 18 variants, each tracked independently. Example: `coinBTC_time5m_thre0.02`.

3. **Shadow Log** — Every signal logs to a JSONL file (`data/shadow/shadow_{name}.jsonl`), deduplicated by variant + market ID. No money moves.

4. **Resolve** — The framework checks Simmer's positions endpoint for resolved markets and marks each shadow trade as win or loss. Falls back to your plugin's `is_win()` method.

5. **Stats** — Per-variant win rate, EV, entry price range, and delta vs baseline. No storytelling — just numbers.

6. **Promote** — Checks a variant against your promotion gates (`min_n`, `min_wr`, `min_ev_delta`). Outputs a recommendation — never auto-applies. You make the call.

## Example Plugin — Crypto Momentum with Gates

This is a structural template, not a working strategy. Every gate is annotated with the reasoning behind it — lessons from real trading, not theory.

```python
from datetime import datetime, timezone
from shadow_plugin_base import StrategyPlugin, TradeSignal, ShadowTrade


class BTCMomentumPlugin(StrategyPlugin):
    name = "btc_momentum"

    default_params = {
        "coin": "BTC",
        "timeframe": "5m",
        "threshold": 0.03,
        "min_volume": 5000.0,
    }

    param_grid = {
        "coin": ["BTC", "ETH"],
        "timeframe": ["5m", "15m", "1h"],
        "threshold": [0.02, 0.03, 0.05],
    }
    # ^ Generates 18 variants: coinBTC_thre0.02_time5m, coinETH_thre0.05_time1h, etc.

    min_n = 30          # Don't promote with fewer than 30 resolved trades
    min_wr = 0.58       # Need 58%+ win rate
    min_ev_delta = 0.02 # Must beat baseline by at least $0.02 EV

    def get_markets(self, client=None) -> list[dict]:
        if client is None:
            return []

        # fast-markets is the right endpoint for BTC/ETH/XRP/SOL —
        # these aren't reliably listed on the standard active markets endpoint.
        markets = client.get_fast_markets()

        coin = self.default_params["coin"]  # params not passed here — filter broadly
        now = datetime.now(timezone.utc)

        filtered = []
        for m in markets:
            # Gate: must mention the coin in the question
            if coin.upper() not in m.get("question", "").upper():
                continue

            # Gate: skip if resolves too soon (< 1h) — not enough time for signal to play out
            resolves_at = m.get("resolves_at")
            if resolves_at:
                try:
                    rt = datetime.fromisoformat(resolves_at.replace("Z", "+00:00"))
                    hours_left = (rt - now).total_seconds() / 3600
                    if hours_left < 1 or hours_left > 48:
                        continue  # Too soon or too far out
                except Exception:
                    pass

            filtered.append(m)
        return filtered

    def evaluate(self, market: dict, params: dict) -> TradeSignal | None:
        price = market.get("current_probability", 0.5)
        volume = market.get("volume_24h", 0) or 0

        # Gate: skip low-volume markets — thin books, bad fills,
        # and you're eating spread for breakfast
        if volume < params["min_volume"]:
            return None

        # Gate: avoid extreme prices — little room to move, high fee impact
        if price < 0.05 or price > 0.95:
            return None

        # Gate: skip markets already near consensus — no edge when it's a coin flip
        if 0.45 < price < 0.55:
            return None

        # ──────────────────────────────────────────────────────────
        # YOUR SIGNAL HERE — fetch your data source, compute your indicator
        # signal_value = fetch_my_signal(params["coin"], params["timeframe"])
        # if signal_value is None:
        #     return None
        raise NotImplementedError("Fetch your signal and compute momentum here")

        # Example: if momentum is bullish above threshold → buy YES
        # if signal_value > params["threshold"]:
        #     return TradeSignal(
        #         market_id=market["id"],
        #         side="YES",
        #         entry_price=price,
        #         signal=f"{params['coin']} momentum {signal_value:.3f} > {params['threshold']}",
        #     )
        # return None
        # ──────────────────────────────────────────────────────────

    def is_win(self, trade: ShadowTrade, market: dict | None = None) -> bool | None:
        if market is None:
            return None
        outcome = market.get("outcome", "").lower()
        if not outcome:
            return None
        return outcome == trade.side.lower()
```

## CLI Reference

Everything you need, nothing you don't.

| Command | What it does |
|---------|-------------|
| `run` | Evaluate markets across all variants, log new shadow trades |
| `resolve` | Check resolved markets, mark wins/losses |
| `stats` | Per-variant WR%, EV, price range, delta vs baseline |
| `variants` | Rank variants by EV, optionally filtered by sample size |
| `promote` | Check a variant against your promotion gates |

### Usage

```bash
# Set config
python shadow_tracker.py --set max_trades_per_run=20

# Shadow-trade (dry run — preview without writing)
python shadow_tracker.py run --strategy my_plugin.py --dry-run

# Shadow-trade (log trades)
python shadow_tracker.py run --strategy my_plugin.py

# Resolve outcomes
python shadow_tracker.py resolve --strategy my_plugin.py

# View stats
python shadow_tracker.py stats --strategy my_plugin.py

# Rank variants with at least 30 resolved trades
python shadow_tracker.py variants --strategy my_plugin.py --min-n 30

# Check a specific variant for promotion
python shadow_tracker.py promote --strategy my_plugin.py --variant coinBTC_thre0.02_time5m

# Override promotion thresholds
python shadow_tracker.py promote --strategy my_plugin.py --variant best --min-n 50 --min-wr 0.60 --min-ev-delta 0.03
```

### Example `stats` Output

```
Variant                      N  Res    WR%      EV       Prices  vs Base
─────────────────────────────────────────────────────────────────────────
coinBTC_thre0.02_time5m     87   71   64.8%  +0.031   0.31–0.68  +0.008
coinBTC_thre0.03_time5m     92   76   61.8%  +0.023   0.28–0.71     —
coinBTC_thre0.02_time15m    54   41   58.5%  +0.018   0.33–0.65  -0.005
coinETH_thre0.03_time5m     48   38   52.6%  +0.009   0.40–0.62  -0.014
```

### Automaton Mode

Run without a subcommand to execute `run` + `resolve` automatically — built for cron:

```bash
export SHADOW_CRYPTO_PLUGIN=my_plugin.py
python shadow_tracker.py
```

The skill's `clawhub.json` configures a `*/15 * * * *` cron by default.

## Variant Naming

Variants are auto-named from `param_grid` keys using a 4-character prefix of the key + the value. Given:

```python
param_grid = {
    "coin": ["BTC", "ETH"],
    "timeframe": ["5m", "15m", "1h"],
    "threshold": [0.02, 0.03, 0.05],
}
```

The framework generates 18 variants (keys sorted alphabetically):

```
coinBTC_thre0.02_time5m
coinBTC_thre0.02_time15m
coinBTC_thre0.02_time1h
coinBTC_thre0.03_time5m
...
coinETH_thre0.05_time1h
```

Variant names are stable IDs across runs. Same name, same JSONL row. Change your param names or grid values, and that variant's history starts from zero. This is by design — if your parameters changed, your old data doesn't apply.

If `param_grid` is empty, all trades log under the single variant `default`.

## Promotion Gates

Most traders promote on vibes. You promote on data. Each gate exists because crypto fast-markets will punish you if you skip it.

| Gate | Default | Why |
|------|---------|-----|
| `min_n` | `30` | Crypto markets are high variance. 20 resolved trades isn't enough to separate signal from luck. You need volume before you trust the numbers. |
| `min_wr` | `0.58` | After ~2% taker fees on paid markets, you need real edge above 55% just to break even. 58% gives you a margin of safety — not comfort, survival. |
| `min_ev_delta` | `0.02` | The variant must beat baseline by at least $0.02 per dollar risked. If it's barely better than default, it's not worth the complexity. Keep it simple until something genuinely earns its spot. |

The `promote` command outputs a recommendation — **it never auto-applies**. You review the stats, inspect the trade history, and make the call. The framework gives you conviction, not permission.

Override gates per-run:

```bash
python shadow_tracker.py promote -s my_plugin.py --variant best --min-n 50 --min-wr 0.60
```

## Environment Variables & Config

| Key | Env Var | Default | Description |
|-----|---------|---------|-------------|
| `max_trades_per_run` | `SHADOW_CRYPTO_MAX_TRADES` | `10` | Max shadow trades logged per run |
| `min_volume` | `SHADOW_CRYPTO_MIN_VOLUME` | `5000` | Min 24h volume filter (dollars) |
| `data_dir` | `SHADOW_DATA_DIR` | `data/shadow` | Directory for JSONL trade logs |
| `plugin` | `SHADOW_CRYPTO_PLUGIN` | — | Path to strategy plugin `.py` file |

Additional env vars used by the framework:

| Env Var | Description |
|---------|-------------|
| `SIMMER_API_KEY` | **Required.** Simmer SDK API key |
| `TRADING_VENUE` | Trading venue (default: `polymarket`) |
| `AUTOMATON_MANAGED` | Set by OpenClaw when running as an automaton |

View or update config:

```bash
python shadow_tracker.py --config
python shadow_tracker.py --set max_trades_per_run=20
python shadow_tracker.py --set plugin=my_plugin.py
```

Config persists to disk via `simmer_sdk.skill` and merges with env vars (env takes precedence).

## Writing Your Own Plugin

1. **Copy the template:** `cp crypto_momentum_plugin.py my_strategy_plugin.py`
2. **Rename the class** and set `name = "my_strategy"` — must be unique per strategy
3. **Define `default_params`** — your baseline parameter set
4. **Define `param_grid`** — every key maps to a list of values to sweep
5. **Implement `get_markets(client)`** — fetch and filter candidate markets from Simmer
6. **Implement `evaluate(market, params)`** — apply your gates and signal logic, return `TradeSignal` or `None`
7. **Implement `is_win(trade, market)`** — check resolution outcome (`True`/`False`/`None`)
8. **Test:** `python shadow_tracker.py run --strategy my_strategy_plugin.py --dry-run`

Your plugin file just needs to import from `shadow_plugin_base` and define one `StrategyPlugin` subclass. The framework discovers it automatically.

## Tips

- **Start narrow.** 1 coin, 1 timeframe, vary only `threshold` (3 values). You'll have usable signal faster than sweeping a full grid from day one. Expand when you've earned the right to.
- **Don't blow out the variant grid early.** Adding dimensions multiplies the trades you need before anything is statistically meaningful. More variants = longer time to conviction.
- **`fast-markets` is the right endpoint** for crypto. BTC/ETH/XRP/SOL aren't reliably on the standard active markets list. Don't waste time looking.
- **`timeframe` is YOUR signal interval**, not market resolution time. A `5m` timeframe means you're reading 5-minute candles, not that the market resolves in 5 minutes.
- **Shadow for at least 2 weeks** before trusting win rate stats. Crypto markets are sparse and resolution clusters will skew short-term numbers. Be patient or be wrong.
- **Run `resolve` daily.** It only processes markets you held shadow positions on. Skip days, and your stats drift behind reality.
- **`--dry-run` every time you change your plugin.** Commit to logging only after you've confirmed it does what you think it does.

## Requirements

- Python 3.10+
- [`simmer-sdk`](https://pypi.org/project/simmer-sdk/) (`pip install simmer-sdk`)
- `SIMMER_API_KEY` environment variable
