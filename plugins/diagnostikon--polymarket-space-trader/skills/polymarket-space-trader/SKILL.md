---
name: polymarket-space-trader
description: "Trades Polymarket prediction markets on space launches, SpaceX milestones, satellite deployments, Mars missions, and commercial spaceflight outcomes. Use when you want to capture alpha on the rapidly growing space exploration market with 22% CAGR and clear binary resolution criteria."
---

# Space & Launch Trader

> **This is a template.**  
> The default signal is keyword discovery + FAA/SpaceX launch schedule alignment — remix it with NASA launch manifest APIs, TLE (Two-Line Element) satellite tracking data, or social media sentiment from SpaceX/Blue Origin announcements.  
> The skill handles all the plumbing (market discovery, trade execution, safeguards). Your agent provides the alpha.

## Strategy Overview

Space prediction markets have shown $120M+ cumulative volume (2020–2025) with 22% CAGR. Polymarket currently lists 106+ active space markets. This skill trades:

- **SpaceX milestones** — Starship orbital tests, launch counts, Starlink constellation size
- **Mars missions** — NASA/private mission announcements and landing events
- **Commercial spaceflight** — Blue Origin, Virgin Galactic, Axiom Space timelines
- **Satellite & telecom** — Orbital congestion, direct-to-cell launch milestones
- **Regulatory events** — FAA approvals, international launch cadence comparisons

Key insight: volatility spikes ~25% around launch events, creating short-window entry opportunities for informed traders.

## Signal Logic

### Default Signal: Launch Schedule Divergence

1. Discover active space/launch markets on Polymarket
2. Query public launch databases (Rocket Watch, Next Spaceflight) for upcoming dates
3. Compare scheduled launch date probability with current market price
4. Before confirmed launches, markets often underprice success (retail pessimism bias)
5. After anomalies (Falcon 9 hold, weather scrub), markets may overreact — fade the overreaction

### Remix Ideas

- **Twitter/X sentiment**: SpaceX tweet activity correlates with 30% volume spikes — use as momentum signal
- **FAA NOTAM filings**: File of Notice to Air Missions is public and indicates imminent launches days ahead
- **Satellite tracker APIs**: Real orbital data to verify Starlink counts vs market claims
- **NASA API**: https://api.nasa.gov/ for real-time mission status feeds

## Market Categories Tracked

```python
SPACE_KEYWORDS = [
    "SpaceX", "Starship", "Starlink", "launch", "rocket",
    "Mars", "NASA", "Blue Origin", "Virgin Galactic", "Axiom",
    "satellite", "orbital", "ISS", "FAA", "Falcon",
    "space station", "lunar", "Artemis", "ESA"
]
```

## Risk Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| Max position size | $30 USDC | Space markets have good liquidity |
| Min market volume | $2,500 | Space community is engaged |
| Max bid-ask spread | 8% | Tighter than climate markets |
| Min days to resolution | 3 | Short-window launch events are tradable |
| Max open positions | 6 | Space events cluster by launch window |

## Volatility Note

Space markets spike sharply on anomaly news. If a launch is scrubbed, NO prices spike immediately. The skill detects these via context flip-flop warnings and pauses during high-volatility windows unless edge is strong.

## Installation & Setup

```bash
clawhub install polymarket-space-trader
```

Requires: `SIMMER_API_KEY` environment variable.

## Cron Schedule

Runs every 10 minutes (`*/10 * * * *`). Launch events can resolve rapidly; tighter loop than other categories.

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
| `SIMMER_SPACE_MAX_POSITION` | `30` | Max USDC per trade |
| `SIMMER_SPACE_MIN_VOLUME` | `2500` | Min market volume filter (USD) |
| `SIMMER_SPACE_MAX_SPREAD` | `0.08` | Max bid-ask spread (0.10 = 10%) |
| `SIMMER_SPACE_MIN_DAYS` | `3` | Min days until market resolves |
| `SIMMER_SPACE_MAX_POSITIONS` | `6` | Max concurrent open positions |

## Dependency

`simmer-sdk` is published on PyPI by Simmer Markets.
- PyPI: https://pypi.org/project/simmer-sdk/
- GitHub: https://github.com/SpartanLabsXyz/simmer-sdk
- Publisher: hello@simmer.markets

Review the source before providing live credentials if you require full auditability.
