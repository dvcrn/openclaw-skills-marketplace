---
version: "1.1.0"
---

---
name: trip
description: "CLI tool for Trip.com travel booking - flight search, hotel search, and price monitoring"
---

# Trip.com (Ctrip) Travel Assistant

Automation tool for Trip.com / Ctrip.com, supporting flight search, hotel search, order management, and price monitoring.

## Features

- **Flight Search**: Search flights and compare prices
- **Hotel Search**: Search hotels with filtering options
- **Order Management**: View booking history
- **Price Monitoring**: Track product price changes
- **QR Login**: Support for QR code authentication

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
playwright install chromium
```

## Usage

### Flight Search

```bash
trip flight <origin> <destination> <date>
```

Examples:
```bash
trip flight Beijing Shanghai 2026-03-15
trip flight Shanghai Shenzhen 2026-03-20 --json
```

### Hotel Search

```bash
trip hotel <city> <check-in> <check-out>
```

Examples:
```bash
trip hotel Shanghai 2026-03-15 2026-03-17
trip hotel Beijing 2026-04-01 2026-04-03 --json
```

### View Orders

```bash
trip order
trip order --json
```

### Price Monitoring

```bash
trip price <url>
```

Example:
```bash
trip price https://www.trip.com/hotels/shanghai-hotel/12345/
```

### QR Code Login

```bash
trip login
```

## Options

- `--headless`: Run in headless mode (no browser window)
- `--json`: Output results in JSON format

## Data Storage

All data is stored in `~/.openclaw/data/ecommerce/`:

- `auth.db` - Authentication sessions
- `ecommerce.db` - Cache and price history
- `trip_profile/` - Browser profile
- `trip_cookies.json` - Cookie files

## Technical Architecture

- **Framework**: Based on ecommerce-core framework
- **Browser**: Playwright + Chromium
- **Data Cache**: SQLite
- **Anti-detection**: Automation control feature hiding

## Notes

1. First-time use requires running `playwright install chromium` to install the browser
2. Some features require login to use
3. Recommended to use `--headless` mode for background operation
4. Price monitoring data is retained for 30 days

## Troubleshooting

### Element Not Found

If the page structure changes, CSS selectors may need updating. Check the latest HTML structure on Trip.com.

### Login Issues

- Ensure the latest Chrome is installed
- Try deleting the `~/.openclaw/data/ecommerce/trip_profile/` directory and retry
- Check network connection

### Cache Issues

Clear cache:
```bash
rm ~/.openclaw/data/ecommerce/ecommerce.db
```
