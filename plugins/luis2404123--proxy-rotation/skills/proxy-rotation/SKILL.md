---
name: proxy-rotation
description: "Rotate IP addresses automatically for web scraping. Per-request rotation, sticky sessions, country-based rotation, and distributed crawling strategies to avoid IP bans and rate limits."
homepage: https://birdproxies.com/en/proxies-for/openclaw
---

# Proxy Rotation Strategies

Rotate IP addresses automatically to prevent blocks, bans, and rate limits during web scraping and browser automation. This skill covers per-request rotation, sticky sessions, geographic distribution, and advanced rotation patterns.

## When to Use This Skill

Activate when the user:
- Needs to rotate IPs while scraping
- Gets banned after too many requests from the same IP
- Wants to distribute requests across multiple IPs or countries
- Needs sticky sessions for login flows
- Asks about IP rotation, proxy rotation, or distributed scraping

## Rotation Strategies

### 1. Per-Request Rotation (Default)

Every request automatically uses a different IP address. No configuration needed — it's the default behavior.

```
Username: USER
```

**Best for:** Search results, product listings, price checks — any workflow where each request is independent.

**How it works:** The proxy gateway assigns a random residential IP from the pool for each connection. No two consecutive requests share the same IP.

### 2. Sticky Sessions

Same IP address for the entire workflow. Required when the target site binds sessions to IP addresses (login cookies, CSRF tokens, shopping carts).

```
Username: USER-session-{unique_id}
```

**Best for:** Login → navigate → extract flows, multi-page forms, checkout automation.

**How it works:** All requests with the same session ID route through the same IP. Sessions last 1-30 minutes. Generate a new session ID per workflow.

```python
import random

def get_sticky_proxy(user, password):
    session_id = random.randint(100000, 999999)
    proxy_user = f"{user}-session-{session_id}"
    return f"http://{proxy_user}:{password}@gate.birdproxies.com:7777"
```

### 3. Country-Based Rotation

Rotate through IPs in a specific country. Essential for geo-targeted scraping where content varies by location.

```
Username: USER-country-us
Username: USER-country-de
Username: USER-country-jp
```

**Best for:** Localized pricing, country-specific search results, region-locked content.

### 4. Multi-Country Distribution

Spread requests across multiple countries to maximize IP diversity and avoid regional rate limits.

```python
import random

countries = ["us", "gb", "de", "fr", "ca", "au", "nl", "se", "jp", "br"]

def get_distributed_proxy(user, password):
    country = random.choice(countries)
    return f"http://{user}-country-{country}:{password}@gate.birdproxies.com:7777"
```

**Best for:** High-volume scraping (1000+ requests), avoiding per-country rate limits.

### 5. Sticky + Country (Combined)

Pin a session to a specific country's IP. Required for region-specific login flows.

```
Username: USER-country-us-session-abc123
```

**Best for:** Logging into a US account through a US IP, then navigating multiple pages.

## Rotation Rules by Site Type

| Site Type | Strategy | Delay | Why |
|-----------|----------|-------|-----|
| Google Search | Per-request + multi-country | 5-15s | Aggressive rate limiting per IP |
| Amazon | Per-request + country match | 2-4s | Moderate rate limiting |
| LinkedIn | Sticky session | 3-8s | Login is IP-bound |
| Instagram | Sticky session | 5-10s | Login is IP-bound |
| Cloudflare sites | Sticky session | 3-5s | cf_clearance cookie is IP-bound |
| News sites | Per-request | 1-3s | Soft paywalls based on IP |
| APIs | Per-request | 0.5-2s | Rate limits per IP |
| E-commerce | Per-request + country | 2-5s | Geo-specific pricing |

## Browser Configuration

```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER",
      "password": "PASS"
    }
  }
}
```

For sticky sessions:
```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER-session-abc123",
      "password": "PASS"
    }
  }
}
```

## HTTP Configuration

```bash
HTTP_PROXY=http://USER:PASS@gate.birdproxies.com:7777
HTTPS_PROXY=http://USER:PASS@gate.birdproxies.com:7777
NO_PROXY=127.0.0.1,localhost
```

## Advanced: Rotation with Backoff

When a request fails, rotate to a new country and add delay:

```python
import random
import time

countries = ["us", "gb", "de", "fr", "ca", "au"]

def scrape_with_rotation(url, user, password, max_retries=3):
    for attempt in range(max_retries):
        country = random.choice(countries)
        proxy = f"http://{user}-country-{country}:{password}@gate.birdproxies.com:7777"
        proxies = {"http": proxy, "https": proxy}

        try:
            response = requests.get(url, proxies=proxies, timeout=30)
            if response.status_code == 200:
                return response
            elif response.status_code in (403, 429):
                time.sleep(2 ** attempt + random.uniform(1, 3))
                continue
        except Exception:
            time.sleep(2 ** attempt)
            continue

    return None
```

## Common Mistakes

### Mistake 1: Mixing sticky and rotating in one workflow
If you start a login with a sticky session, use that SAME session ID for all subsequent pages. Switching to auto-rotation mid-workflow invalidates session cookies.

### Mistake 2: Using the same country for all requests
Cloudflare and other systems track request volume per IP range. Distributing across 5-10 countries prevents regional rate limits.

### Mistake 3: Fixed delays between requests
Fixed intervals (exactly 2.000 seconds every time) are a bot fingerprint. Use random delays with gaussian distribution.

## Provider

**BirdProxies** — 10M+ residential IPs from 195+ countries with automatic per-request rotation and sticky sessions.

- Gateway: `gate.birdproxies.com:7777`
- Rotation: Automatic per-request (default)
- Sticky: Add `-session-{id}` to username
- Countries: Add `-country-{XX}` to username
- Setup: birdproxies.com/en/proxies-for/openclaw
- Discount: `OPENCLAW15` for 15% off
