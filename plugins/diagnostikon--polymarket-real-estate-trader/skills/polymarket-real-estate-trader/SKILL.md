---
name: polymarket-real-estate-trader
description: "Trades Polymarket prediction markets on housing prices, mortgage rates, Fed rate decisions, real estate crash scenarios, and regional property market milestones. Use when you want to capture alpha on macro housing markets using Fed minutes, Case-Shiller data, and mortgage rate signals."
---

# Real Estate & Housing Trader

> **This is a template.**
> The default signal is keyword-based market discovery combined with probability-extreme detection — remix it with the data sources listed in the Edge Thesis below.
> The skill handles all the plumbing (market discovery, trade execution, safeguards). Your agent provides the alpha.

## Strategy Overview

Fed Funds Futures divergence from Polymarket rate-decision markets. Remix: CME FedWatch tool, Case-Shiller index releases, Zillow Research API, FRED economic data.


## Edge Thesis

Housing and Fed rate markets are priced by retail traders who follow mainstream media narratives. Quantitative traders with access to Fed Funds Futures data have a significant edge:

- **CME FedWatch vs Polymarket**: Fed Funds Futures (professional market) often diverges from Polymarket's rate decision markets by 5–15%. The futures market is better calibrated
- **Case-Shiller release lag**: The index is published monthly with a 2-month lag — markets sometimes underprice the known trajectory
- **Regional divergence**: National housing crash scenarios may be mispriced when regional data (Phoenix, Austin, Miami) already shows inflection
- **Commercial RE narrative**: Office vacancy markets are emotionally driven by WFH debate — actual CBRE/JLL vacancy data provides hard edge

### Remix Signal Ideas
- **CME FedWatch**: https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html
- **FRED API**: https://fred.stlouisfed.org/docs/api/fred/ — Federal Reserve economic data
- **Zillow Research**: https://www.zillow.com/research/data/
- **Redfin Data Center**: https://www.redfin.com/news/data-center/


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
