---
name: polymarket-sports-live-trader
description: "Trades Polymarket prediction markets on sports championships, tournament outcomes, MVP awards, transfer windows, and season milestones. Use when you want to capture alpha on sports markets using league table data, injury reports, and Elo rating signals."
---

# Sports & Championships Trader

> **This is a template.**
> The default signal is keyword-based market discovery combined with probability-extreme detection — remix it with the data sources listed in the Edge Thesis below.
> The skill handles all the plumbing (market discovery, trade execution, safeguards). Your agent provides the alpha.

## Strategy Overview

Elo/power-ranking divergence from market price. Remix: SofaScore/FotMob API, Elo rating systems, injury report feeds, transfermarkt.com data, ESPN API.


## Edge Thesis

Sports prediction markets are dominated by passionate fans who bet emotionally on their teams. This creates systematic pricing inefficiencies:

- **Fan loyalty bias**: Supporters of popular clubs (Real Madrid, Liverpool, Man City, Lakers) consistently overpay YES, creating structural NO value
- **Injury information lag**: Injury reports drop on official team websites 24–48h before markets fully reprice — medical staff confirms availability closer to match
- **Elo vs market divergence**: Quantitative Elo/power rankings are well-calibrated; when they diverge >15% from Polymarket implied probability, edge exists
- **DAZN-Polymarket partnership**: Live broadcast embeds mean high-frequency in-game markets are becoming available — volatility spikes at goals/red cards

### Remix Signal Ideas
- **Club Elo**: https://www.clubelo.com/API — football Elo ratings, free
- **FiveThirtyEight NBA Elo**: https://projects.fivethirtyeight.com/nba-model/
- **Transfermarkt API**: Player valuations and injury status
- **ESPN hidden API**: `https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard`


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
