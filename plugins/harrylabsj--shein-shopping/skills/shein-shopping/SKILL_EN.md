---
name: shein-ec
description: "CLI tool for SHEIN fashion e-commerce platform - search products, track prices, and browse new arrivals"
---

# SHEIN Skill

A command-line interface for SHEIN, a leading global fast-fashion e-commerce platform. This skill enables automated product search, price tracking, and new arrivals browsing.

## Description

SHEIN is a comprehensive CLI tool designed for interacting with the SHEIN fashion platform. It provides product search capabilities with intelligent caching, real-time price tracking with historical data, and access to new arrivals. The tool is ideal for fashion shopping, price comparison, and trend discovery.

### Use Cases

- **Fashion Shopping**: Search for clothing, accessories, and fashion items
- **Price Monitoring**: Track product prices over time to find the best buying opportunity
- **New Arrivals**: Discover the latest fashion trends and new products
- **Market Analysis**: Extract pricing data for competitive analysis
- **Trend Discovery**: Stay updated with the latest fashion trends

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install browser
playwright install chromium

# Install the SHEIN skill

```

## Usage

### Commands

#### Search Products
```bash
shein search "dress"
shein search "summer shoes" --page 2 --limit 20
```

Search for products by keyword. Supports pagination and result limit control.

- **Arguments:**
  - `query` - Search keyword (required)
  - `--page` - Page number (default: 1)
  - `--limit` - Number of results per page (default: 20)

#### Login
```bash
shein login
```

Authenticate with SHEIN using QR code. Opens a browser window with a QR code that can be scanned with the SHEIN mobile app. Session tokens are securely stored for future use.

#### Get Price
```bash
shein price <product-url>
```

Fetch current price and historical price data for a specific product.

- **Arguments:**
  - `product-url` - Full SHEIN product URL (required)

**Example:**
```bash
shein price "https://www.shein.com/p/product-id.html"
```

#### New Arrivals
```bash
shein new
shein new women
shein new men
shein new accessories
```

Browse new arrivals by category.

- **Arguments:**
  - `category` - Category name (optional, default: all)

## Features

- **Product Search with Caching**: Fast repeated searches using intelligent caching to reduce API calls and improve response time
- **QR Code Login**: Secure browser-based authentication via QR code scanning
- **Price Tracking & History**: Monitor price changes over time with historical data visualization
- **New Arrivals**: Access to latest products and fashion trends
- **Anti-Detection Browser Automation**: Stealth browser automation that mimics human behavior to avoid detection
- **Session Management**: Persistent authentication tokens for seamless re-authentication

## Examples

### Basic Product Search
```bash
# Search for a specific product
shein search "summer dress"

# Search with custom pagination
shein search "handbags" --page 3 --limit 50
```

### Price Monitoring
```bash
# Get current price and history for a product
shein price "https://www.shein.com/p/product-id.html"

# Check if price dropped
shein price "https://www.shein.com/p/product-id.html" | grep -i "current"
```

### New Arrivals
```bash
# Get all new arrivals
shein new

# Get new arrivals by category
shein new women
shein new men
shein new kids
```

### Authentication
```bash
# Initialize login (one-time setup)
shein login
# Browser opens with QR code - scan with SHEIN app
```

## Technical Details

### Data Storage

| Data Type | Location |
|-----------|----------|
| Session Tokens | `~/.openclaw/data/shein/cookies.json` |
| Search Cache | `~/.openclaw/data/shein/shein.db` |

### Dependencies

- `playwright>=1.40.0` - Browser automation
- Browser automation with anti-detection capabilities
- SQLite for data persistence

### Rate Limiting

The tool implements caching and rate limiting to respect SHEIN's terms of service and avoid account restrictions.

### Anti-Detection

All browser automation includes:
- Random delay intervals between actions
- Human-like scrolling and navigation patterns
- User agent rotation
- Request fingerprint randomization
