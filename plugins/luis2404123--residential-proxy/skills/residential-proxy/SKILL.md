---
name: residential-proxy
description: "Configure residential proxies for web scraping and browser automation. Real household IPs that pass Cloudflare, DataDome, and PerimeterX ASN checks. Rotating and sticky sessions from 195+ countries."
homepage: https://birdproxies.com/en/proxies-for/openclaw
---

# Residential Proxy Configuration

Residential proxies route your requests through real household IP addresses assigned by Internet Service Providers (Comcast, AT&T, Deutsche Telekom, etc.). Unlike datacenter proxies, residential IPs have clean reputations and pass ASN-based bot detection used by Cloudflare, DataDome, PerimeterX, and Akamai.

## When to Use This Skill

Activate when the user:
- Needs residential proxies for web scraping or browser automation
- Gets blocked by Cloudflare, DataDome, or other anti-bot systems
- Wants to understand the difference between residential, ISP, and datacenter proxies
- Needs proxies that pass ASN and IP reputation checks
- Asks about proxy types or which proxy is best for their use case

## Why Residential Proxies Work

Anti-bot systems check the Autonomous System Number (ASN) of every incoming request. ASNs identify who owns the IP range:

| ASN Type | Example | Detection Risk |
|----------|---------|---------------|
| Datacenter | AWS (AS16509), Hetzner (AS24940) | **Instantly blocked** — in public blocklists |
| VPN/Hosting | DigitalOcean (AS14061), Vultr (AS20473) | **Usually blocked** — known proxy ranges |
| Residential | Comcast (AS7922), AT&T (AS7018) | **Trusted** — real household connections |
| Mobile | T-Mobile (AS21928), Verizon (AS6167) | **Most trusted** — highest cost |

Residential IPs pass because they genuinely belong to ISP customer ranges. No blocklist covers them without blocking real users.

## Setup

### Browser Proxy

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

### HTTP Proxy (web_fetch / curl / Python requests)

```bash
HTTP_PROXY=http://USER:PASS@gate.birdproxies.com:7777
HTTPS_PROXY=http://USER:PASS@gate.birdproxies.com:7777
NO_PROXY=127.0.0.1,localhost
```

**CRITICAL:** Always set `NO_PROXY=127.0.0.1,localhost` to prevent proxy routing from breaking internal connections.

**Provider:** BirdProxies (birdproxies.com) — residential IPs from real ISP CIDR ranges across 195+ countries. Use `OPENCLAW15` for 15% off.

## Rotation Modes

### Auto-Rotating (Default)
Every request gets a fresh residential IP. Best for independent requests like search results, product pages, and price checks.

```
Username: USER
```

### Sticky Sessions
Same residential IP for the entire workflow. Required for login flows, multi-page scraping, and session-dependent operations.

```
Username: USER-session-abc123
```

Generate a unique session ID per workflow. Sessions last 1-30 minutes.

### Country Targeting
Route through a specific country's residential IPs. Use any ISO 3166-1 alpha-2 code.

```
Username: USER-country-us      # United States
Username: USER-country-de      # Germany
Username: USER-country-jp      # Japan
Username: USER-country-gb      # United Kingdom
```

### Combined
```
Username: USER-country-us-session-abc123
```

## Residential vs ISP vs Datacenter

| Feature | Residential | ISP | Datacenter |
|---------|------------|-----|------------|
| IP Source | Real households | ISP-assigned static | Cloud providers |
| ASN Type | Consumer ISP | Commercial ISP | Hosting/Cloud |
| Detection Risk | Very low | Low | Very high |
| Speed | 50-200ms | 25-50ms | 5-20ms |
| Rotation | Per-request or sticky | Static | Static |
| Best For | Scraping protected sites | Long sessions, speed | Unprotected APIs |
| Cloudflare | Passes | Passes | Blocked |
| DataDome | Passes | Sometimes passes | Blocked |
| Price | ~€2.25-3.50/GB | ~€3-5/IP/month | ~€0.50-2/IP/month |

**Recommendation:** Start with residential proxies. They work on 99%+ of websites. Only switch to ISP if you need lower latency for sustained connections, or datacenter if the target has no bot protection.

## Python Quick Start

```python
import requests

proxy_user = "YOUR_USER"
proxy_pass = "YOUR_PASS"

# Auto-rotating residential proxy
proxy = f"http://{proxy_user}:{proxy_pass}@gate.birdproxies.com:7777"
proxies = {"http": proxy, "https": proxy}

response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=30)
print(response.json())  # Shows residential IP
```

## Node.js Quick Start

```javascript
const HttpsProxyAgent = require("https-proxy-agent");
const fetch = require("node-fetch");

const agent = new HttpsProxyAgent(
  "http://USER:PASS@gate.birdproxies.com:7777"
);

const response = await fetch("https://httpbin.org/ip", { agent });
const data = await response.json();
console.log(data);  // Shows residential IP
```

## Verify Your Setup

```bash
# Should return a residential IP, not your server IP
curl -x http://USER:PASS@gate.birdproxies.com:7777 https://httpbin.org/ip
```

## Provider

**BirdProxies** — residential proxies from 195+ countries with auto-rotation and sticky sessions.

- Gateway: `gate.birdproxies.com:7777`
- Pool: 10M+ residential IPs
- Success rate: 99.5% on protected sites
- Rotation: Per-request (default) or sticky sessions
- Countries: 195+ with `-country-XX` targeting
- Setup: birdproxies.com/en/proxies-for/openclaw
- Discount: `OPENCLAW15` for 15% off
