---
name: polymarket-climate-trader
description: "Trades Polymarket prediction markets on weather extremes, climate milestones, natural disasters, and agricultural outcomes. Use when you want to capture alpha on temperature records, hurricane seasons, flood events, and CO2 threshold markets using meteorological data signals."
---

# Climate & Weather Trader

> **This is a template.**  
> The default signal is keyword discovery + NOAA/weather API data alignment — remix it with ForecastEx climate oracle feeds, satellite NDVI data for agriculture, or ensemble weather model outputs.  
> The skill handles all the plumbing (market discovery, trade execution, safeguards). Your agent provides the alpha.

## Strategy Overview

Climate prediction markets are one of the fastest-growing underserved categories. Polymarket has 151+ active climate markets but most are basic. This skill captures alpha on:

- **Temperature extremes** — record highs, heatwaves, frost events
- **Natural catastrophes** — hurricane counts, earthquake magnitudes, wildfire acreage
- **Climate milestones** — CO2 ppm thresholds, Arctic sea ice minimums
- **Agricultural impacts** — wheat yields, drought-driven crop failures, water allocations

Climate markets are uniquely suited for quantitative trading: the data sources are public, verifiable, and highly structured (NOAA, ECMWF, NASA).

## Signal Logic

### Default Signal: Model Ensemble Divergence

1. Discover active climate/weather markets on Polymarket
2. Pull current forecast data from open weather APIs (NOAA, Open-Meteo)
3. Compare model consensus probability vs. current market price
4. If divergence >12%, check context (flip-flop, slippage, edge)
5. Trade in direction of meteorological consensus

### Remix Ideas

- **ECMWF ensemble**: Use European Centre weather model for 15-day outlook as pricing signal
- **ENSO index**: Trade El Niño/La Niña markets using NOAA's ONI index
- **Insurance cat bond pricing**: Use ILS (insurance-linked securities) spreads as implied probability benchmarks
- **Copernicus climate data**: Real-time European climate services for local/regional markets

## Market Categories Tracked

```python
CLIMATE_KEYWORDS = [
    "temperature", "hurricane", "tornado", "flood", "drought",
    "wildfire", "earthquake", "CO2", "sea ice", "Arctic",
    "El Niño", "La Niña", "snowfall", "rainfall", "heatwave",
    "crop yield", "wheat", "harvest", "water shortage"
]
```

## Risk Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| Max position size | $20 USDC | Per market |
| Min market volume | $3,000 | Climate markets are less liquid |
| Max bid-ask spread | 12% | Wider allowed for niche markets |
| Min days to resolution | 14 | Weather requires sufficient lead time |
| Max open positions | 8 | Diversify across events |

## Key Data Sources

- **NOAA Climate Data Online**: https://www.ncdc.noaa.gov/cdo-web/
- **Open-Meteo API**: https://open-meteo.com/ (free, no key required)
- **Copernicus C3S**: https://cds.climate.copernicus.eu/
- **ForecastEx**: https://forecastex.com/

## Installation & Setup

```bash
clawhub install polymarket-climate-trader
```

Requires: `SIMMER_API_KEY` environment variable. Optional: `OPENMETEO_API_KEY`.

## Cron Schedule

Runs every 30 minutes (`*/30 * * * *`). Weather data updates every 1–6 hours; no need to poll faster.

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
| `SIMMER_CLIMATE_MAX_POSITION` | `20` | Max USDC per trade |
| `SIMMER_CLIMATE_MIN_VOLUME` | `3000` | Min market volume filter (USD) |
| `SIMMER_CLIMATE_MAX_SPREAD` | `0.12` | Max bid-ask spread (0.10 = 10%) |
| `SIMMER_CLIMATE_MIN_DAYS` | `14` | Min days until market resolves |
| `SIMMER_CLIMATE_MAX_POSITIONS` | `8` | Max concurrent open positions |

## Dependency

`simmer-sdk` is published on PyPI by Simmer Markets.
- PyPI: https://pypi.org/project/simmer-sdk/
- GitHub: https://github.com/SpartanLabsXyz/simmer-sdk
- Publisher: hello@simmer.markets

Review the source before providing live credentials if you require full auditability.
