---
name: meituan
description: "CLI tool for Meituan food delivery and local services - search restaurants, find coupons, and manage orders"
---

# Meituan Skill

A command-line interface for Meituan (美团), China's leading platform for food delivery and local services.

## Features

- **Restaurant Search**: Find nearby restaurants with ratings, sales, and delivery info
- **Red Packet Query**: View available coupons and red packets
- **Order Management**: View order history
- **QR Code Login**: Support for QR code authentication

## Installation

```bash
# Install dependencies
pip install playwright

# Install browser
playwright install chromium
```

## Usage

### Search Restaurants

```bash
meituan food <keyword> [--location <city>] [--limit <number>]
```

Examples:
```bash
meituan food hotpot
meituan food bbq --location beijing --limit 20
meituan food sushi --location shanghai --json
```

### QR Code Login

```bash
meituan login
```

### View Red Packets

```bash
meituan redpacket
meituan redpacket --json
```

### View Orders

```bash
meituan order
meituan order --json
```

## Options

- `--location, -l`: Search location (default: Beijing)
- `--limit, -n`: Number of results (default: 20)
- `--headless`: Run in headless mode (default)
- `--no-headless`: Show browser window
- `--json, -j`: Output in JSON format

## Data Storage

All data is stored locally in `~/.openclaw/data/meituan/`:

| File | Purpose |
|------|---------|
| `meituan.db` | SQLite database for restaurants, orders, red packets |
| `cookies.json` | Login cookies (stored in plaintext) |

## Technical Architecture

- **Browser**: Playwright + Chromium
- **Data Storage**: SQLite
- **Cookie Storage**: JSON file (local plaintext)

## Notes

1. First-time use requires `playwright install chromium`
2. Some features require login
3. Cookies are stored as plaintext JSON locally - ensure device security
4. Recommend using `--headless` mode for background operation

## Troubleshooting

### Element Not Found

If page structure changes, CSS selectors may need updating. Check Meituan's latest HTML structure.

### Login Issues

- Ensure latest Chrome is installed
- Try deleting `~/.openclaw/data/meituan/` directory
- Check network connection

### Clear Data

```bash
rm -rf ~/.openclaw/data/meituan/
```
