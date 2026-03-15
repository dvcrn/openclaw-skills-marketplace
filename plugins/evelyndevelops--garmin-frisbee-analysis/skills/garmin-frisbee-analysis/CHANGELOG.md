# Changelog

## v1.0.0 (2026-03-11)

### Initial Release

Ultimate Frisbee performance analytics skill for Clawdbot, built on Garmin Connect data.

**Frisbee Scripts:**
- `frisbee_activity.py` — Post-game dashboard: sprint count, top speed, Sprint Fatigue Index, HR zone distribution, speed timeline with sprint highlight bands
- `frisbee_tournament.py` — Tournament review dashboard: Body Battery fatigue curve, per-game HR comparison, Heart Rate Recovery curves, overnight sleep/HRV
- `frisbee_compare.py` — Comparison & season analysis: training vs game intensity, top speed trends, volume over time (modes: training / tournament / cross / season)
- `frisbee_chart.py` — Frisbee-specific chart generation

**General Garmin Scripts:**
- `garmin_data.py` — Fetch health metrics (sleep, Body Battery, HRV, heart rate, activities, stress)
- `garmin_chart.py` — Generate interactive HTML health dashboards
- `garmin_data_extended.py` — Extended metrics (training readiness, VO2 max, body composition, SPO2, intensity minutes)
- `garmin_activity_files.py` — Download and parse FIT/GPX activity files
- `garmin_query.py` — Time-based queries ("what was my HR at 3pm?")
- `garmin_auth.py` — Authentication and token management

**Key Metrics:**
- Sprint detection: speed > 14.4 km/h sustained ≥ 2 seconds
- Sprint Fatigue Index: last 3 sprint peaks ÷ first 3 sprint peaks (< 0.85 = significant fatigue)
- Heart Rate Recovery curves post-game (30 min window)
- Body Battery pre-game readiness (≥ 75 = ready, ≥ 50 = manageable, < 50 = compromised)

**Configuration:**
- Clawdbot config (`skills.entries.garmin-frisbee-analysis.env`)
- Local `config.json` support
- Environment variables (`GARMIN_EMAIL`, `GARMIN_PASSWORD`)

**Requirements:**
- Python 3.7+
- garminconnect, fitparse, gpxpy
- Garmin Connect account with GPS-enabled wearable (tested on Garmin 265S)
