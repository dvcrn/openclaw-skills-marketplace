# Extended Garmin Capabilities — Frisbee Edition

This skill supports **comprehensive frisbee performance tracking, time-based queries, and activity file analysis**.

## 🎯 Time-Based Queries

Ask questions like:
- "What was my heart rate at halftime yesterday?"
- "What was my Body Battery before the game started at 10am?"
- "How stressed was I between games?"

### Usage

```bash
# Heart rate at specific time
python3 scripts/garmin_query.py heart_rate "3:00 PM" --date 2026-03-08

# Body Battery (e.g., pre-game check)
python3 scripts/garmin_query.py body_battery "10:00 AM" --date 2026-03-08

# Stress level between games
python3 scripts/garmin_query.py stress "14:30"

# Steps at time
python3 scripts/garmin_query.py steps "17:00"
```

**Time formats supported:**
- `3:00 PM`, `3 PM` (12-hour)
- `15:00`, `15:30:45` (24-hour)
- `2026-03-08 15:30` (full datetime)

---

## 📊 Extended Metrics

### Training & Performance

```bash
# Training readiness (are you ready for today's game/practice?)
python3 scripts/garmin_data_extended.py training_readiness

# Training status (load, VO2 max trends — track fitness gains across season)
python3 scripts/garmin_data_extended.py training_status

# Endurance score (relevant for full-day tournament performance)
python3 scripts/garmin_data_extended.py endurance_score

# Max metrics (VO2 max — tracks aerobic capacity improvements)
python3 scripts/garmin_data_extended.py max_metrics

# Fitness age
python3 scripts/garmin_data_extended.py fitness_age
```

### Body Composition & Health

```bash
# Body composition (weight, body fat %, muscle mass, BMI)
python3 scripts/garmin_data_extended.py body_composition --date 2026-03-08

# Weight history (across season)
python3 scripts/garmin_data_extended.py weigh_ins --start 2026-01-01 --end 2026-03-08

# Blood oxygen (SPO2) — useful for altitude tournaments
python3 scripts/garmin_data_extended.py spo2 --date 2026-03-08

# Respiration (breathing rate — elevated after high-intensity game)
python3 scripts/garmin_data_extended.py respiration
```

### Activity Metrics

```bash
# Intraday steps (total movement across tournament day)
python3 scripts/garmin_data_extended.py steps --date 2026-03-08

# Intensity minutes (vigorous/moderate — compare game vs training weeks)
python3 scripts/garmin_data_extended.py intensity_minutes

# Hydration tracking (important during tournaments)
python3 scripts/garmin_data_extended.py hydration

# Detailed stress time-series (see stress between points/games)
python3 scripts/garmin_data_extended.py stress_detailed

# Intraday heart rate (all HR samples — see full game HR curve)
python3 scripts/garmin_data_extended.py hr_intraday
```

---

## 🗺️ Activity File Analysis (FIT/GPX)

Download and analyze FIT files from games to answer questions like:
- "How many sprints did I hit in the second half?"
- "What was my top speed during the final?"
- "Was I running slower by the last game of the tournament?"

### Download Activity Files

```bash
# Download FIT file (contains raw speed, HR, GPS data)
python3 scripts/garmin_activity_files.py download --activity-id 12345678 --format fit

# Download GPX file (for route/field visualization)
python3 scripts/garmin_activity_files.py download --activity-id 12345678 --format gpx
```

### Parse Activity Files

```bash
# Parse FIT file (sprint detection, speed, HR zones)
python3 scripts/garmin_activity_files.py parse --file /tmp/activity_12345678.fit

# Parse GPX file (movement heatmap, field coverage)
python3 scripts/garmin_activity_files.py parse --file /tmp/activity_12345678.gpx
```

**FIT files contain (relevant to frisbee):**
- GPS coordinates (lat/lon) — field coverage heatmap
- Speed (m/s) — sprint detection
- Heart rate — HR zone analysis
- Lap splits — per-point or per-half breakdown
- Altitude/elevation — useful for outdoor field context
- Temperature

### Query Activity Data

```bash
# What was my HR/speed at a specific point in the game?
python3 scripts/garmin_activity_files.py query --file /tmp/activity_12345678.fit --distance 1500

# What was my data at a specific time during the game?
python3 scripts/garmin_activity_files.py query --file /tmp/activity_12345678.fit --time "2026-03-08T10:15:30"
```

### Analyze Activity

```bash
# Get comprehensive game statistics
python3 scripts/garmin_activity_files.py analyze --file /tmp/activity_12345678.fit
```

**Returns (frisbee-relevant):**
- Average/max/min heart rate
- Average/max speed → top sprint speed
- Total distance → field coverage
- Duration
- Elevation gain

---

## 🔍 Frisbee Use Cases

### Post-Game Analysis
- "How many sprints did I hit in yesterday's game?"
- "What was my top sprint speed?"
- "Was my Sprint Fatigue Index above 0.85?"
- "How long was I in Zone 4+ during the game?"

### Tournament Day Monitoring
- "What was my Body Battery before game 1, 2, and 3?"
- "How did my HR recovery look after each game?"
- "Did I have enough rest stress between games?"

### Training Quality
- "Is my practice intensity matching game intensity?"
- "Are my weekly training minutes enough to maintain fitness?"
- "How does my VO2 max trend across the season?"

### Recovery Tracking
- "What's my training readiness today after the tournament?"
- "When did my Body Battery start draining yesterday?"
- "Did I get enough deep sleep the night before the final?"

### Season-Long Trends
- "Is my top speed improving across games this season?"
- "Is my HRV trending up as I get fitter?"
- "How does my sleep quality compare during tournament weeks vs training weeks?"

---

## 📦 Dependencies

```bash
pip3 install garminconnect fitparse gpxpy
```

- **garminconnect**: Garmin Connect API wrapper
- **fitparse**: Parse FIT files (Garmin's binary format) — required for sprint detection
- **gpxpy**: Parse GPX files (GPS track format)

---

## 🛠️ Advanced Tips

### Get Activity ID

The activity ID is visible in the Garmin Connect URL:
```
https://connect.garmin.com/modern/activity/12345678
                                        ^^^^^^^^
```

Or find it programmatically:
```bash
python3 scripts/garmin_data.py activities --days 7
# Look for "activityId" in each activity
```

### Batch Processing a Tournament

```bash
# Get activity IDs for tournament weekend
activities=$(python3 scripts/garmin_data.py activities --days 3 | jq -r '.activities[].activityId')

# Download all FIT files
for id in $activities; do
  python3 scripts/garmin_activity_files.py download --activity-id $id --format fit
done
```

### Visualization Ideas

1. **Sprint heatmap**: Color GPS track by speed (slow = blue, sprint = red)
2. **HR zone timeline**: Color-coded chart across full game duration
3. **Sprint peak trend**: Bar chart of each sprint's peak speed — detect fatigue
4. **Field coverage**: GPS heatmap showing which areas of the field you covered
5. **Tournament fatigue curve**: Body Battery across all tournament days

---

## 🚀 Future Enhancements

- [ ] Automatic frisbee activity classification (detect field sport from GPS + HR pattern)
- [ ] Point-by-point HR recovery analysis
- [ ] Sprint count vs. game outcome correlation
- [ ] Weather/temperature impact on performance
- [ ] Season fitness trajectory (VO2 max trend aligned with tournament calendar)
- [ ] Team comparison (if multiple players use this skill)
