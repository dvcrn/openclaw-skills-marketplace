---
name: nws-warning-bot
description: "Monitors NWS severe weather alerts for a specific address using polygon-based detection.\n \n Unlike county-level alerts, this checks if warning polygons (tornado, severe thunderstorm)\n actually intersect your home coordinates—not just your county. Useful for filtering out\n warnings that affect distant parts of your county while ensuring you know when storms\n are actually headed your way.\n \n Use when a user wants location-specific severe weather alerts, filtering noisy county-wide\n alerts to only their actual address, or building emergency notification systems."
homepage: https://github.com/openclaw/nws-warning-bot
---

# NWS Warning Bot

Polygon-level severe weather monitoring for your actual address.

## What This Does

Standard weather alerts are county-level. If you're in a county with 500 square miles,
a tornado warning 40 miles north of you triggers the same alert as one approaching
your house. This bot changes that.

**Core feature:** Checks if NWS warning polygons actually contain your coordinates.
Only alerts when warnings physically overlap your location—not just your zip code,
not just your county—your actual lat/lon.

## Quick Start

### 1. Find Your Coordinates

Options:
- **Google Maps:** Right-click your house → "What's here?" → copy decimals
- **GPS device** or phone app
- **Address geocoder:** `curl "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=YOUR%20ADDRESS&format=json"`

### 2. Set Environment Variables

```bash
export WARNING_BOT_LAT=YOUR_LAT      # Your latitude
export WARNING_BOT_LON=YOUR_LON      # Your longitude  
export WARNING_BOT_ADDRESS="Your Address, City, State"
export WARNING_BOT_STATE="OH"        # Your state code
```

### 3. Run Manual Check

```bash
python3 scripts/warning-bot.py
```

- Exit code 0: No warnings for your address
- Exit code 1: Warning detected, saved to `data/alert-pending.txt`

### 4. Automate with Cron

```bash
*/5 * * * * /path/to/warning-bot/scripts/warning-bot-cron.sh
```

Then wire `data/alert-pending.txt` to your notification system (Telegram, email, etc.)

## How It Works

| Component | Purpose |
|-----------|---------|
| `warning-bot.py` | Core: fetches NWS alerts, checks polygons, deduplicates |
| `warning-bot-cron.sh` | Atomic lock + cron wrapper + alert file output |
| SQLite DB | Tracks sent alerts (24h expiry) |
| `data/alert-pending.txt` | Alert output for external notification |

**Polygon detection:** Uses ray-casting algorithm to test if your lat/lon falls inside
NWS GeoJSON warning polygons. Handles both `Polygon` and `MultiPolygon` geometries.

**Deduplication:** SQLite tracks alert IDs for 24h to prevent repeat notifications
for the same warning.

**Monitoring:** By default watches Tornado Warning, Severe Thunderstorm Warning,
Tornado Watch, Severe Thunderstorm Watch.

## Configuration

| Environment Variable | Required | Default | Description |
|---------------------|----------|---------|-------------|
| `WARNING_BOT_LAT` | ✅ | — | Your latitude (decimal) |
| `WARNING_BOT_LON` | ✅ | — | Your longitude (decimal) |
| `WARNING_BOT_ADDRESS` | ❌ | "Unknown" | Human-readable address for messages |
| `WARNING_BOT_STATE` | ❌ | "OH" | NWS state code |

## Output Files

| File | Purpose |
|------|---------|
| `data/warning-bot.db` | SQLite deduplication database |
| `data/warning-bot.log` | Cron execution logs |
| `data/alert-pending.txt` | Alert message (when warning detected) |

## Testing

Validate your coordinates:

```python
# Test if bot detects warnings for your location
python3 -c "
import os
os.environ['WARNING_BOT_LAT'] = 'YOUR_LAT'
os.environ['WARNING_BOT_LON'] = 'YOUR_LON'
os.environ['WARNING_BOT_ADDRESS'] = 'Test Location'

from scripts.warning_bot import point_in_polygon

# Mock warning polygon (approximate bounding box around test area)
test = [[-83.0, 40.5], [-82.0, 40.5], [-82.0, 41.5], [-83.0, 41.5], [-83.0, 40.5]]
print('Inside:', point_in_polygon(YOUR_LAT, YOUR_LON, test))
"
```

## Requirements

- Python 3.7+
- `sqlite3` (stdlib)
- `urllib`, `json`, `datetime` (stdlib)
- No external dependencies

## API Notes

Uses `api.weather.gov/alerts/active?area={STATE}` with:
- 10s timeout
- GeoJSON format
- Standard User-Agent header (update with your email in production)

NWS requires respectful usage. Don't poll more than every 5 minutes.
Rate limits are generous but undocumented—be a good citizen.

## Integration Examples

**Telegram notification:**
```bash
if [ -f data/alert-pending.txt ]; then
  cat data/alert-pending.txt | telegram-send --stdin
  rm data/alert-pending.txt
fi
```

**Email notification:**
```bash
if [ -s data/alert-pending.txt ]; then
  mail -s "Severe Weather Alert" user@example.com < data/alert-pending.txt
fi
```

## Limitations

- **US only:** NWS API covers United States
- **Polygon-dependent:** If NWS issues a watch without detailed polygons,
  those are skipped (typically county-level watches lack geometry)
- **No forecast:** Only monitors active alerts, not future risk
- **Point-based:** Uses single lat/lon; doesn't account for property size

## Safety Notes

This tool **augment**s official sources—doesn't replace them.

- Keep NOAA Weather Radio as backup
- Don't disable county-level alerts entirely
- Test the system before severe weather season
- Monitor NWS directly during active events

## Credits

Built on NWS API (api.weather.gov) with GeoJSON polygon data.
Ray-casting algorithm standard in computational geometry.
