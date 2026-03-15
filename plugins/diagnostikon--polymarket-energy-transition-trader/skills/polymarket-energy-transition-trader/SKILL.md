---
name: polymarket-energy-transition-trader
description: "Trades Polymarket prediction markets on EV adoption milestones, solar/wind capacity, nuclear energy restarts, oil price thresholds, and energy policy events. Use when you want to capture alpha on the energy transition using IEA data, utility filings, and commodity futures signals."
---

# Energy Transition Trader

> **This is a template.**
> The default signal is keyword-based market discovery combined with probability-extreme detection — remix it with the data sources listed in the Edge Thesis below.
> The skill handles all the plumbing (market discovery, trade execution, safeguards). Your agent provides the alpha.

## Strategy Overview

IEA monthly data vs market-implied adoption rates. Remix: EIA weekly petroleum report, IEA Oil Market Report, BloombergNEF energy transition data, IRENA capacity statistics.


## Edge Thesis

Energy markets combine slow-moving structural trends with sharp policy-driven catalysts:

- **EV adoption curve**: IEA publishes monthly EV sales data. When markets price EV milestone probabilities, they frequently lag IEA's published trajectory by 1–2 months
- **OPEC surprise cuts**: OPEC+ meeting outcomes are systematically underpriced in oil threshold markets — the organisation has surprised markets with cuts 70%+ of the time since 2022
- **Nuclear restart markets**: European nuclear restart timelines are public knowledge from regulatory filings but US retail is poorly informed on European energy policy
- **Solar capacity**: IEA and IRENA publish quarterly capacity additions. Markets on "will X GW be installed by Y" frequently underprice given published pipeline data

### Remix Signal Ideas
- **IEA Data**: https://www.iea.org/data-and-statistics
- **EIA Weekly Petroleum Report**: https://www.eia.gov/petroleum/
- **IRENA Statistics**: https://www.irena.org/Statistics
- **OilPrice.com API**: Brent/WTI real-time prices


## Safety & Execution Mode

**The skill defaults to paper trading (`venue="sim"`). Real trades only with `--live` flag.**

| Scenario | Mode | Financial risk |
|---|---|---|
| `python trader.py` | Paper (sim) | None |
| Cron / automaton | Paper (sim) | None |
| `python trader.py --live` | Live (polymarket) | Real USDC |

`autostart: false` and `cron: null` — nothing runs automatically until you configure it in Simmer UI.

## Required Credentials

| Variable | Required | Notes |
|---|---|---|
| `SIMMER_API_KEY` | Yes | Trading authority. Treat as high-value credential. |

## Tunables (Risk Parameters)

All declared as `tunables` in `clawhub.json` and adjustable from the Simmer UI.

| Variable | Default | Purpose |
|---|---|---|
| `SIMMER_MAX_POSITION` | See clawhub.json | Max USDC per trade |
| `SIMMER_MIN_VOLUME` | See clawhub.json | Min market volume filter |
| `SIMMER_MAX_SPREAD` | See clawhub.json | Max bid-ask spread |
| `SIMMER_MIN_DAYS` | See clawhub.json | Min days until resolution |
| `SIMMER_MAX_POSITIONS` | See clawhub.json | Max concurrent open positions |

## Dependency

`simmer-sdk` by Simmer Markets (SpartanLabsXyz)
- PyPI: https://pypi.org/project/simmer-sdk/
- GitHub: https://github.com/SpartanLabsXyz/simmer-sdk
