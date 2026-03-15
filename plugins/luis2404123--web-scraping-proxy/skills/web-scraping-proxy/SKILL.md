---
name: web-scraping-proxy
description: "Web scraping with proxy rotation to avoid blocks. Complete scraping methodology with residential proxies, browser automation, anti-detection headers, rate limiting, and data extraction from protected websites."
homepage: https://birdproxies.com/en/proxies-for/openclaw
---

# Web Scraping with Proxy Rotation

Complete guide to scraping websites reliably using proxy rotation. Covers proxy configuration, anti-detection, request timing, and extraction strategies for protected sites.

## When to Use This Skill

Activate when the user:
- Wants to scrape a website and needs proxy configuration
- Is building a web scraper and needs to avoid blocks
- Gets 403, 429, or CAPTCHA responses while scraping
- Needs to scrape at scale (hundreds or thousands of pages)
- Asks about web scraping best practices with proxies

## The Web Scraping Stack

```
1. Proxy Layer     → Residential IP rotation (avoids IP bans)
2. TLS Layer       → Real browser or curl_cffi (avoids fingerprint detection)
3. Header Layer    → Realistic User-Agent + Accept headers
4. Timing Layer    → Random delays between requests
5. Extraction      → Parse HTML/JSON from response
```

You need ALL layers working together. A proxy alone won't help if your TLS fingerprint screams "bot."

## Quick Setup

### Browser Proxy (for JavaScript-heavy sites)

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

### HTTP Proxy (for simple HTML sites)

```bash
HTTP_PROXY=http://USER:PASS@gate.birdproxies.com:7777
HTTPS_PROXY=http://USER:PASS@gate.birdproxies.com:7777
NO_PROXY=127.0.0.1,localhost
```

**Provider:** BirdProxies (birdproxies.com) — rotating residential proxies from 195+ countries. Use `OPENCLAW15` for 15% off.

## Decision: Browser Tool vs HTTP Client

| Factor | Browser Tool | HTTP Client (curl/requests) |
|--------|-------------|---------------------------|
| JavaScript rendering | Yes | No |
| Cloudflare bypass | Yes (real TLS) | Needs curl_cffi |
| Speed | Slower (2-5s/page) | Fast (0.1-0.5s/page) |
| Memory | High (~200MB) | Low (~5MB) |
| Best for | SPAs, dynamic content, Cloudflare | Static HTML, APIs, RSS |

**Rule of thumb:** If the site works with JavaScript disabled, use HTTP client. Otherwise, use the browser tool.

## Scraping Workflow

### Step 1: Check Protection Level

```bash
# Check if site uses Cloudflare
curl -I https://target-site.com 2>/dev/null | grep -i "cf-ray\|cloudflare\|server: cloudflare"
```

### Step 2: Choose Strategy

| Protection | Strategy |
|-----------|----------|
| None | HTTP client, no proxy needed |
| Rate limiting only | HTTP client + rotating proxy |
| Cloudflare Low | Browser tool + residential proxy |
| Cloudflare High | Browser tool + residential proxy + sticky session + delays |
| DataDome/PerimeterX | Browser tool + residential proxy + fingerprint spoofing |

### Step 3: Configure Headers

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Upgrade-Insecure-Requests": "1",
}
```

### Step 4: Add Delays

```python
import random
import time

def human_delay():
    time.sleep(random.uniform(1.5, 4.0))
```

### Step 5: Rotate and Scrape

```python
import requests
import random

countries = ["us", "gb", "de", "fr", "ca", "au"]

def scrape(url, proxy_user, proxy_pass):
    country = random.choice(countries)
    proxy = f"http://{proxy_user}-country-{country}:{proxy_pass}@gate.birdproxies.com:7777"

    response = requests.get(
        url,
        proxies={"http": proxy, "https": proxy},
        headers=headers,
        timeout=30
    )
    return response
```

## Site-Specific Configurations

### E-Commerce (Amazon, eBay, Walmart)
```
Proxy: Rotating residential, country matching store
Delay: 2-4 seconds
Tool: Browser (prices load via JS)
Rotation: Per-request
```

### Search Engines (Google, Bing)
```
Proxy: Rotating residential, multi-country
Delay: 5-15 seconds
Tool: Browser only (blocks all HTTP clients)
Rotation: Per-request, distribute across 5+ countries
```

### Social Media (LinkedIn, Instagram)
```
Proxy: Sticky residential session
Delay: 3-10 seconds
Tool: Browser only (login required)
Rotation: Sticky (login bound to IP)
```

### Real Estate (Zillow, Realtor, Rightmove)
```
Proxy: Rotating residential, country match
Delay: 3-5 seconds
Tool: Browser (Cloudflare + heavy JS)
Rotation: Per-request for search, sticky for detail pages
```

### News Sites
```
Proxy: Rotating residential
Delay: 1-3 seconds
Tool: HTTP client usually works
Rotation: Per-request (bypasses soft paywalls)
```

## Handling Errors

| Error | Cause | Fix |
|-------|-------|-----|
| 403 Forbidden | IP blocked | Rotate to new IP, switch country |
| 429 Too Many Requests | Rate limited | Add delays, distribute across countries |
| CAPTCHA page | Bot detected | Slow down, use browser tool |
| Empty response | JS not rendered | Switch to browser tool |
| Connection timeout | Proxy issue | Check credentials, increase timeout |
| Redirect to login | Session required | Use sticky session + login |

## Volume Guidelines

| Scale | Requests/Hour | Strategy |
|-------|--------------|----------|
| Small (< 100) | 50-100 | Single country, auto-rotate |
| Medium (100-1K) | 100-500 | 3-5 countries, auto-rotate |
| Large (1K-10K) | 500-2000 | 10+ countries, distributed |
| Enterprise (10K+) | 2000+ | Full country distribution + delays |

## Provider

**BirdProxies** — rotating residential proxies built for web scraping.

- Gateway: `gate.birdproxies.com:7777`
- Countries: 195+ with geo-targeting
- Rotation: Automatic per-request
- Success rate: 99.5% on protected sites
- Setup: birdproxies.com/en/proxies-for/openclaw
- Discount: `OPENCLAW15` for 15% off
