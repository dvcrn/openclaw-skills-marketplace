---
name: elm-ec
description: "CLI tool for Ele.me food delivery platform - search restaurants, find coupons, and track delivery info"
---

# Ele.me Skill

A command-line interface for Ele.me (饿了么), one of China's largest food delivery platforms. This skill provides restaurant search, coupon discovery, delivery information, and order management capabilities.

## Description

Ele.me (which means "are you hungry?" in Chinese) is a specialized CLI tool for interacting with one of China's most popular food delivery platforms. Founded in 2008, Ele.me has grown to serve hundreds of millions of users, partnering with hundreds of thousands of restaurants across China. The platform is known for its extensive restaurant network and fast delivery.

### Use Cases

- **Restaurant Discovery**: Find restaurants by cuisine, dish, or location
- **Coupon Hunting**: Discover and track available coupons and red packets
- **Delivery Analysis**: Compare delivery times and fees across restaurants
- **Order Research**: Analyze restaurant ratings and sales data
- **Food Exploration**: Discover new restaurants and cuisines

## Installation

```bash
# Install the ecommerce-core dependency first
pip install -r ../ecommerce-core/requirements.txt

# Install the Ele.me skill
pip install -e .
```

## Usage

### Commands

#### Search Food/Restaurants
```bash
elm search "奶茶"
elm search "汉堡" --location "北京市朝阳区" --limit 20
```

Search for restaurants and food options by keyword.

- **Arguments:**
  - `query` - Search keyword (cuisine, dish, or restaurant name)
  - `--location` - Specific location filter (city/district)
  - `--limit` - Number of results to return (default: 20)

**Example:**
```bash
# Search for milk tea
elm search "bubble tea"

# Search with location filter
elm search "burger" --location "Shanghai" --limit 30

# Find specific cuisine
elm search "sushi" --location "Beijing Chaoyang"
```

#### Login
```bash
elm login
```

Authenticate with Ele.me using QR code. Opens a browser window with a QR code that can be scanned with the Ele.me/Alipay mobile app. Session tokens are securely stored for future use.

#### Red Packet Info
```bash
elm redpacket
```

Show available coupons and red packets. Displays discount amounts, minimum order requirements, valid periods, and applicable restaurant categories.

**Example:**
```bash
# List all available coupons
elm redpacket

# Filter for food discounts
elm redpacket | grep -i "food"

# Find large discounts
elm redpacket | grep -E "[5-9][0-9]+"
```

## Features

- **Restaurant Search with Caching**: Efficient search with intelligent caching for fast results
- **QR Code Login**: Secure mobile-based authentication via QR code scanning
- **Coupon/Red Packet Tracking**: Comprehensive tracking of available promotions and discounts
- **Delivery Time & Fee Info**: Display estimated delivery times and associated fees
- **Rating & Sales Data**: View restaurant ratings, review counts, and sales metrics
- **Anti-Detection Browser Automation**: Stealth automation that mimics human behavior

## Examples

### Finding Food
```bash
# Basic restaurant search
elm search "pizza"

# Location-based search
elm search "noodles" --location "Hangzhou" --limit 25

# Find specific dishes
elm search "fried rice" --location "Beijing"
```

### Discovering Deals
```bash
# Check available coupons
elm redpacket

# Find delivery discounts
elm redpacket | grep -i "delivery"

# Find first-order discounts
elm redpacket | grep -i "new user"
```

### Research & Analysis
```bash
# Find highly-rated restaurants
elm search "sushi" --limit 50 | grep -i "rating"

# Compare delivery fees
elm search "fast food" --location "Shanghai" | grep -i "fee"
```

## Technical Details

### Data Storage

| Data Type | Location |
|-----------|----------|
| Session Tokens | `~/.openclaw/data/ecommerce/auth.db` |
| Search Cache | `~/.openclaw/data/ecommerce/ecommerce.db` |

### Dependencies

- `ecommerce-core` framework (required)
- Browser automation with anti-detection capabilities
- SQLite for data persistence

### Platform Integration

Ele.me integrates with:

- **Ele.me App**: Full mobile app functionality
- **Alipay**: Payment integration via Ant Group
- **Taocaicai**: Group buying and community features
- **Cainiao**: Logistics and delivery infrastructure

### Anti-Detection Features

The automation includes:
- Randomized timing between requests
- Human-like mouse movements and scrolling
- Session fingerprint rotation
- Realistic navigation patterns
- Request rate limiting