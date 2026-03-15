---
name: polymarket-food-agriculture-trader
description: "Trades Polymarket prediction markets on food commodity prices, crop yields, drought-driven supply shocks, alternative protein milestones, and agricultural policy events. Use when you want to capture alpha on food markets using USDA crop reports, futures curves, and weather-agriculture correlation signals."
---

# Food & Agriculture Trader

> **This is a template.**
> The default signal is keyword-based market discovery combined with probability-extreme detection — remix it with the data sources listed in the Edge Thesis below.
> The skill handles all the plumbing (market discovery, trade execution, safeguards). Your agent provides the alpha.

## Strategy Overview

USDA WASDE report vs futures curve divergence. Remix: USDA NASS crop progress reports, FAO Food Price Index (monthly), CME agricultural futures term structure, World Bank commodity price data.


## Edge Thesis

Agricultural markets are driven by hard data (USDA reports, satellite crop monitoring) but traded by retail participants who follow headlines:

- **USDA WASDE calendar**: The WASDE (World Agricultural Supply and Demand Estimates) report is published monthly on a known date. Markets on crop yield thresholds frequently misprice in the days before release when satellite data already indicates the direction
- **Coffee/cocoa supply concentration**: 70% of cocoa comes from Côte d'Ivoire and Ghana — any weather event in West Africa is a strong signal for cocoa price markets. Retail frequently underprices supply shock probability
- **El Niño agricultural impact**: ENSO forecasts from NOAA give 3–6 month lead time on major crop-growing regions. Markets on annual yield milestones rarely incorporate this correctly
- **Alternative protein regulatory**: Lab-grown meat approval timelines are public record from FDA/USDA FSIS filings — markets frequently underprice based on regulatory calendar

### Remix Signal Ideas
- **USDA NASS**: https://www.nass.usda.gov/Data_and_Statistics/ — free crop progress API
- **FAO Food Price Index**: https://www.fao.org/worldfoodsituation/foodpricesindex/
- **World Bank Commodity Prices**: https://www.worldbank.org/en/research/commodity-markets
- **Planet Labs crop monitoring**: Satellite NDVI for major crop regions (paid but powerful)


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
