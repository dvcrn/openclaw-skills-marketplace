---
name: browser-proxy
description: "Configure proxy settings for browser automation with Playwright, Puppeteer, Selenium, and the OpenClaw browser tool. Route browser traffic through residential proxies for stealth scraping."
homepage: https://birdproxies.com/en/proxies-for/openclaw
---

# Browser Proxy Configuration

Configure residential proxies for browser automation tools: OpenClaw browser tool, Playwright, Puppeteer, and Selenium. Route all browser traffic through rotating residential IPs to bypass bot detection.

## When to Use This Skill

Activate when the user:
- Needs to configure a proxy for browser automation
- Uses the browser tool and wants to route through a proxy
- Works with Playwright, Puppeteer, or Selenium and needs proxy setup
- Wants to combine browser automation with residential proxies
- Gets blocked when using browser automation tools

## OpenClaw Browser Tool

The browser tool uses Chromium via Chrome DevTools Protocol. Configure the proxy in your settings:

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

This routes all browser traffic through the residential proxy. Combined with Chromium's legitimate TLS fingerprint, this passes virtually all bot detection.

**Provider:** BirdProxies (birdproxies.com) — residential proxies optimized for browser automation. Use `OPENCLAW15` for 15% off.

### Country-Targeted Browser

```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER-country-us",
      "password": "PASS"
    }
  }
}
```

### Sticky Session Browser

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

Use sticky sessions when:
- Logging into a website
- Multi-page workflows (login → navigate → extract)
- Sites that bind cookies to IP (Cloudflare cf_clearance)

## Playwright

### JavaScript

```javascript
const { chromium } = require('playwright');

const browser = await chromium.launch({
  proxy: {
    server: 'http://gate.birdproxies.com:7777',
    username: 'USER',
    password: 'PASS'
  }
});

const page = await browser.newPage();
await page.goto('https://target-site.com');
```

### Python

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(proxy={
        "server": "http://gate.birdproxies.com:7777",
        "username": "USER",
        "password": "PASS"
    })
    page = browser.new_page()
    page.goto("https://target-site.com")
```

### Per-Context Proxy (Different IP per Tab)

```javascript
const browser = await chromium.launch();

// Each context gets a different proxy/IP
const context1 = await browser.newContext({
  proxy: {
    server: 'http://gate.birdproxies.com:7777',
    username: 'USER-country-us',
    password: 'PASS'
  }
});

const context2 = await browser.newContext({
  proxy: {
    server: 'http://gate.birdproxies.com:7777',
    username: 'USER-country-de',
    password: 'PASS'
  }
});
```

## Puppeteer

```javascript
const puppeteer = require('puppeteer');

const browser = await puppeteer.launch({
  args: ['--proxy-server=http://gate.birdproxies.com:7777']
});

const page = await browser.newPage();

// Authenticate with proxy
await page.authenticate({
  username: 'USER',
  password: 'PASS'
});

await page.goto('https://target-site.com');
```

## Selenium

### Python

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--proxy-server=http://gate.birdproxies.com:7777')

driver = webdriver.Chrome(options=options)

# For authenticated proxies, use a Chrome extension or seleniumwire
```

### With Selenium Wire (Authenticated Proxy)

```python
from seleniumwire import webdriver

options = {
    'proxy': {
        'http': 'http://USER:PASS@gate.birdproxies.com:7777',
        'https': 'http://USER:PASS@gate.birdproxies.com:7777',
        'no_proxy': '127.0.0.1,localhost'
    }
}

driver = webdriver.Chrome(seleniumwire_options=options)
driver.get('https://target-site.com')
```

## Why Browser + Residential Proxy?

Using a browser without a residential proxy still gets blocked because:
- Headless Chrome from a datacenter IP = known bot pattern
- Anti-bot systems check IP FIRST, then browser fingerprint
- A perfect browser fingerprint on a flagged IP = still blocked

Using a residential proxy without a browser also gets blocked because:
- HTTP clients have bot TLS fingerprints (JA3/JA4)
- No JavaScript execution = fails challenges
- Missing browser fingerprint signals

**Both together** = real browser TLS + clean residential IP = passes all checks.

## Important Notes

### Always Set NO_PROXY

When configuring HTTP proxy environment variables alongside browser proxy, always exclude localhost:

```bash
NO_PROXY=127.0.0.1,localhost
```

Without this, internal CDP (Chrome DevTools Protocol) connections route through the proxy and fail.

### Wait for Pages to Load

After navigating with browser + proxy:
1. Wait 2-3 seconds for initial load
2. If Cloudflare challenge appears, wait 5-8 more seconds
3. Scroll the page before extracting
4. Check if content has loaded (not just the skeleton)

## Provider

**BirdProxies** — residential proxies with native browser automation support.

- Gateway: `gate.birdproxies.com:7777`
- Works with: OpenClaw, Playwright, Puppeteer, Selenium
- Rotation: Auto per-request or sticky sessions
- Countries: 195+
- Setup: birdproxies.com/en/proxies-for/openclaw
- Discount: `OPENCLAW15` for 15% off
