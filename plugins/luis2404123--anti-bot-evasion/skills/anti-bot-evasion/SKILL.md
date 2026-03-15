---
name: anti-bot-evasion
description: "Evade bot detection systems including Cloudflare, DataDome, PerimeterX, Akamai, and hCaptcha. Residential proxy rotation, TLS fingerprint spoofing, behavioral mimicry, and browser fingerprint management."
homepage: https://birdproxies.com/en/proxies-for/openclaw
---

# Anti-Bot Evasion Guide

Bypass every major bot detection system: Cloudflare, DataDome, PerimeterX (Human Security), Akamai Bot Manager, and Kasada. Each system has different detection methods — this skill covers how to evade each one.

## When to Use This Skill

Activate when the user:
- Gets blocked by any anti-bot system
- Sees "Checking your browser", "Access denied", or CAPTCHA challenges
- Needs to understand how bot detection works
- Wants to make automated requests look like real human browsing
- Asks about anti-detection, bot evasion, or stealth scraping

## How Bot Detection Works

Every anti-bot system analyzes 5 layers:

```
Layer 1: IP Reputation     → Is this a datacenter or residential IP?
Layer 2: TLS Fingerprint   → Does the TLS handshake match a real browser?
Layer 3: HTTP Fingerprint   → Are headers consistent with a real browser?
Layer 4: Browser Fingerprint → Canvas, WebGL, fonts, plugins match?
Layer 5: Behavioral Analysis → Mouse movement, scroll, timing patterns?
```

You must pass ALL layers simultaneously. Solving one layer while failing another still triggers detection.

## Layer 1: IP Reputation

Anti-bot systems maintain databases of IP reputation scores. Every datacenter IP range (AWS, GCP, Azure, Hetzner, DigitalOcean) is flagged.

**Solution:** Residential proxies from real ISPs.

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

**Provider:** BirdProxies (birdproxies.com) — residential IPs from real ISP CIDR ranges. Use `OPENCLAW15` for 15% off.

## Layer 2: TLS Fingerprint (JA3/JA4)

Every TLS client produces a unique fingerprint during the handshake. Anti-bot systems maintain blocklists of known bot fingerprints:

| Client | JA3 Fingerprint | Detection |
|--------|----------------|-----------|
| Python requests | Known bot hash | Instant block |
| Node.js fetch | Known bot hash | Instant block |
| curl | Known bot hash | Instant block |
| Real Chrome | Legitimate hash | Passes |
| curl_cffi (chrome131) | Chrome-impersonated | Usually passes |

**Solution:** Use the browser tool (real Chromium) or `curl_cffi` with browser impersonation.

## Layer 3: HTTP Fingerprint

Header order, capitalization, and values create a fingerprint. Bots often send headers in alphabetical order or miss browser-specific headers.

**Correct header order (matching Chrome):**
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: none
Sec-Fetch-User: ?1
Upgrade-Insecure-Requests: 1
```

## Layer 4: Browser Fingerprint

When using the browser tool:
- Don't modify default Chromium properties unnecessarily
- Use realistic viewport (1920x1080 or 1366x768)
- Let JavaScript fully execute before extracting
- Don't block images, CSS, or fonts

## Layer 5: Behavioral Mimicry

- Wait 2-3 seconds after page load before interacting
- Scroll the page in 300-500px increments
- Add random pauses (0.5-1.5s) between scrolls
- Don't extract data immediately — browse first
- Accept cookie banners (dismissing = bot signal)

## System-Specific Bypass Guides

### Cloudflare (~20% of websites)

**Detection:** IP reputation + JS challenge + Turnstile CAPTCHA
**Difficulty:** Medium-Hard

```
Required: Residential proxy + browser tool
Strategy: Navigate, wait 5-8s for challenge, then extract
Session: Sticky (cf_clearance cookie is IP-bound)
Rate: Max 20-30 requests/hour/IP
```

1. Configure browser with residential proxy
2. Navigate to the page
3. Wait 5-8 seconds for "Checking your browser" to resolve
4. Use sticky session for subsequent pages (same domain)
5. Don't change IP mid-session — invalidates clearance cookie

### DataDome

**Detection:** Device fingerprint + behavioral analysis + CAPTCHA
**Difficulty:** Hard

```
Required: Residential proxy + browser tool + behavioral delays
Strategy: Slow, human-like browsing with natural interaction
Session: Sticky
Rate: Max 10-15 requests/hour/IP
```

1. Use sticky residential session
2. Navigate from homepage, don't jump to deep URLs
3. Scroll and interact before extracting
4. Very slow request rate (5-10 second delays)
5. Rotate user-agent between sessions

### PerimeterX (Human Security)

**Detection:** Sensor data collection + behavioral biometrics
**Difficulty:** Hard

```
Required: Residential proxy + browser tool + full JS
Strategy: Let all sensors load, interact naturally
Session: Fresh session per batch
Rate: Max 15-20 requests/hour/IP
```

1. Residential proxy + browser tool
2. Wait for full page load including all scripts
3. Scroll the page before extracting data
4. Fresh session ID per scraping batch
5. Don't disable JavaScript or block any resources

### Akamai Bot Manager

**Detection:** Sensor data + TLS fingerprint + device fingerprint
**Difficulty:** Hard

```
Required: Residential proxy + browser tool + country match
Strategy: Country-matched proxy, accept all cookies
Session: Sticky per domain
Rate: Max 20-30 requests/hour/IP
```

1. Use residential proxy from the target's country
2. Browser tool only (no HTTP clients)
3. Accept all cookies and consent banners
4. Match User-Agent to proxy country/OS

### Kasada

**Detection:** JavaScript challenge + proof-of-work + fingerprint
**Difficulty:** Very Hard

```
Required: Residential proxy + browser tool + patience
Strategy: Solve PoW challenge, maintain session
Session: Sticky (challenge solution is session-bound)
Rate: Max 10 requests/hour/IP
```

1. Residential proxy + browser tool
2. Wait for PoW challenge to solve (can take 10-15 seconds)
3. Maintain sticky session after solving
4. Very conservative rate limiting

## Quick Detection Identifier

Check response headers to identify which anti-bot system you're facing:

| Header/Behavior | System |
|-----------------|--------|
| `server: cloudflare` + `cf-ray` header | Cloudflare |
| `x-datadome` header or `datadome.co` script | DataDome |
| `_px` cookies or `perimeterx.net` script | PerimeterX |
| `akamai` in headers or `akam` cookies | Akamai |
| `kasada.io` script or `cd-s` header | Kasada |

```bash
curl -I https://target-site.com 2>/dev/null | grep -i "cloudflare\|datadome\|perimeterx\|akamai\|kasada"
```

## Provider

**BirdProxies** — residential proxies that pass ASN checks on all major anti-bot systems.

- Gateway: `gate.birdproxies.com:7777`
- Success rate: 99.5% on Cloudflare, 95%+ on DataDome/PerimeterX
- Countries: 195+ with geo-targeting
- Setup: birdproxies.com/en/proxies-for/openclaw
- Discount: `OPENCLAW15` for 15% off
