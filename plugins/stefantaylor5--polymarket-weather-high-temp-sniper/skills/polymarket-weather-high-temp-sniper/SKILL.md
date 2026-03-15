---
name: polymarket-weather-high-temp-sniper
description: "Scans Polymarket daily high-temperature markets, auto-imports new ones, then snipes YES positions between 9–10 AM local time when forecast and reality converge — buys YES at ≥$0.60 during the scan window, or follows crowd volume at 10 AM sharp."
---

# Weather High-Temp Sniper

> **This is a template.** The default signal is the YES market price for Polymarket daily high-temperature markets — remix it by swapping in a NOAA forecast API, OpenMeteo live data, or a custom ML model. The skill handles all the plumbing (market discovery, import, timezone detection, trade execution, TP/SL). Your agent provides the alpha.

## Strategy

Polymarket lists daily maximum temperature markets per city (e.g. "Will NYC's highest temperature exceed 72°F on March 12?"). By 9–10 AM local time, the day's temperature trajectory is already largely determined. This skill exploits that convergence window, trading only the **YES / warm / above-threshold** side.

## Phase Overview

```
Every 5 minutes (cron):
│
├─ PHASE 1 — Auto-Discovery
│   └─ list_importable_markets("highest temperature", "temperature NYC", …)
│       └─ import_market(url) for any untracked Polymarket high-temp market
│
├─ PHASE 2 — Fetch & Filter
│   └─ GET /api/sdk/markets?tags=weather&status=active
│       └─ Keep only "above/exceed" high-temp markets; exclude "below/lowest"
│
├─ PHASE 3 — Timezone Pre-scan
│   └─ Detect city → timezone from question title; log local window status
│
├─ PHASE 4 — Trading Windows
│   ├─ 9:00–9:55 AM local: SCAN → If YES% ≥ PRICE_THRESHOLD → buy 1 share
│   └─ 10:00 AM local: FALLBACK → buy highest-YES% unowned market
│
└─ PHASE 5 — Risk Monitor (optional, ENABLE_TP_SL=true)
    └─ POST /api/sdk/positions/{id}/monitor (stop_loss_pct / take_profit_pct)
```

## What's Swappable (Remix Guide)

| Component | Default | How to remix |
|---|---|---|
| **Signal** | Market YES% price | Replace with NOAA API forecast, OpenMeteo, custom ML model |
| **Threshold** | `PRICE_THRESHOLD=0.60` | Lower for more trades, raise for higher conviction |
| **Window** | 9–10 AM local | Adjust `is_in_scan_window()` / `is_fallback_moment()` |
| **Direction** | YES only (warm/high) | Flip to NO for cold/low markets (edit `is_highest_temp_market()`) |

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SIMMER_API_KEY` | ✅ Yes | — | API key from simmer.markets dashboard |
| `ENABLE_TP_SL` | No | `false` | Enable take-profit / stop-loss monitoring |
| `PRICE_THRESHOLD` | No | `0.60` | Minimum YES% to trigger a buy |
| `MAX_AMOUNT_USD` | No | `1.0` | Max spend per trade in USD |
| `MAX_RETRY` | No | `1` | Retry count on trade failure |
| `TAKE_PROFIT` | No | `0.50` | TP ratio (e.g. 0.50 = +50%) |
| `STOP_LOSS` | No | `0.25` | SL ratio (e.g. 0.25 = −25%) |
| `REPORT_INTERVAL` | No | `240` | Seconds between status reports |

## Running

```bash
# Dry-run (show opportunities, no real trades — default)
python sniper.py

# Live trading
python sniper.py --live
```
