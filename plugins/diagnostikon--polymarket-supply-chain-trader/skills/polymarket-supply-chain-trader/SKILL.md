---
name: polymarket-supply-chain-trader
description: "Trades Polymarket prediction markets focused on supply chain disruptions, port congestion, shipping delays, commodity prices, and logistics outcomes. Use when you want to capture alpha on global trade flow events, raw material price markets, and demand spike predictions."
---

# Supply Chain & Logistics Trader

> **This is a template.**  
> The default signal is keyword-based market discovery (shipping, port, logistics, commodity, supply chain) — remix it with freight index APIs (Baltic Dry Index), satellite AIS vessel tracking data, or real-time port authority feeds.  
> The skill handles all the plumbing (market discovery, trade execution, safeguards). Your agent provides the alpha.

## Strategy Overview

Supply chain prediction markets are among the most underserved categories on Polymarket. This skill identifies and trades markets related to:

- **Port congestion** — Rotterdam, Suez Canal, LA/Long Beach delays
- **Commodity prices** — Brent crude, steel, lithium thresholds
- **Demand spikes** — GPU/chip shortages, EV battery supply
- **Company logistics** — Tesla delivery delays, Maersk shipping times, Amazon Prime SLAs

Research shows prediction markets can reduce supply chain forecasting errors by 20–50% vs traditional methods (CFTC data). This makes these markets both tradable AND informative.

## Signal Logic

### Default Signal: Keyword Discovery + Liquidity Filter

1. Search Polymarket for active markets containing supply-chain keywords
2. Filter for markets with >$5,000 volume and bid-ask spread <10%
3. Apply probability mean-reversion: markets deviating >15% from 30-day moving average are flagged
4. Check context for flip-flop risk and slippage before entering
5. Enter YES if market probability is abnormally depressed despite strong fundamentals, NO otherwise

### Remix Ideas

- **Baltic Dry Index signal**: Long YES on shipping delay markets when BDI spikes >15% week-over-week
- **USDA crop report**: Trade agricultural supply markets around report release dates
- **Port authority RSS feeds**: Real-time congestion data as entry trigger
- **Satellite AIS tracking**: Vessel queue counts for LA/Long Beach as direct oracle

## Market Categories Tracked

```python
SUPPLY_CHAIN_KEYWORDS = [
    "shipping", "port", "container", "supply chain", "logistics",
    "commodity", "crude oil", "steel price", "lithium", "semiconductor",
    "chip shortage", "delivery delay", "Maersk", "Rotterdam", "Suez",
    "GPU demand", "battery supply", "Amazon Prime"
]
```

## Risk Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| Max position size | $25 USDC | Per market |
| Min market volume | $5,000 | Liquidity filter |
| Max bid-ask spread | 10% | Slippage guard |
| Min days to resolution | 7 | Avoid last-minute noise |
| Max open positions | 5 | Concentration limit |

## Installation & Setup

```bash
clawhub install polymarket-supply-chain-trader
```

Requires: `SIMMER_API_KEY` environment variable.

## Cron Schedule

Runs every 15 minutes (`*/15 * * * *`). Markets are slow-moving enough that high-frequency execution is unnecessary.

## Safety & Execution Mode

**The skill defaults to paper trading (`venue="sim"`). Real trades only execute when `--live` is passed explicitly.**

| Scenario | Mode | Financial risk |
|----------|------|----------------|
| `python trader.py` | Paper (sim) | None |
| Cron / automaton | Paper (sim) | None |
| `python trader.py --live` | Live (polymarket) | Real USDC |

The automaton cron is set to `null` — it does not run on a schedule until you configure it in the Simmer UI. `autostart: false` means it won't start automatically on install.

## Required Credentials

| Variable | Required | Notes |
|----------|----------|-------|
| `SIMMER_API_KEY` | Yes | Trading authority — keep this credential private. Do not place a live-capable key in any environment where automated code could call `--live`. |

## Tunables (Risk Parameters)

All risk parameters are declared in `clawhub.json` as `tunables` and adjustable from the Simmer UI without code changes. They use `SIMMER_`-prefixed env vars so `apply_skill_config()` can load them securely.

| Variable | Default | Purpose |
|----------|---------|---------|
| `SIMMER_SUPPLY_MAX_POSITION` | `25` | Max USDC per trade |
| `SIMMER_SUPPLY_MIN_VOLUME` | `5000` | Min market volume filter (USD) |
| `SIMMER_SUPPLY_MAX_SPREAD` | `0.10` | Max bid-ask spread (0.10 = 10%) |
| `SIMMER_SUPPLY_MIN_DAYS` | `7` | Min days until market resolves |
| `SIMMER_SUPPLY_MAX_POSITIONS` | `5` | Max concurrent open positions |

## Dependency

`simmer-sdk` is published on PyPI by Simmer Markets.
- PyPI: https://pypi.org/project/simmer-sdk/
- GitHub: https://github.com/SpartanLabsXyz/simmer-sdk
- Publisher: hello@simmer.markets

Review the source before providing live credentials if you require full auditability.
