---
name: aerobase-browser
description: "Browser-based flight search and airline check-in automation"
---

# Browser-Based Flight Search

USE BROWSER ONLY WHEN:
- User specifically asks to check Google Flights / Kayak / Skyscanner
- API search returned no results and user wants broader coverage
- Price comparison requested against external sources

## Browser Commands (OpenClaw Playwright-on-CDP with ARIA Snapshots)

- `browser snapshot` — get ARIA tree with [ref=eN] element references
- `browser type [ref=eN] "value"` — type into an input field
- `browser click [ref=eN]` — click an element
- `browser screenshot` — capture current page state

## Google Flights

1. Navigate to `https://www.google.com/travel/flights`
2. `browser snapshot` → ARIA tree
3. Fill origin, destination, dates using [ref] locators
4. Click search, wait 5s for results
5. `browser snapshot` → extract airlines, prices, durations, stops
6. Enrich with jetlag scores via POST /api/v1/flights/score before presenting

## Kayak

1. Navigate to `https://www.kayak.com`
2. Same snapshot → fill → search → extract pattern

## Skyscanner

1. Navigate to `https://www.skyscanner.com`
2. Same snapshot → fill → search → extract pattern

## Always

- Present browser results as "comparison data" — recommend booking through our API
- Random delays (3-8s) between browser actions
- Max 10 browser searches per day per user
- Enrich all results with jetlag scores before presenting to user

## Rate Limits

- Max 10 browser flight searches per day per user.
- Back off 24 hours if any site blocks the browser.

## Rate Limit Tracking

Track all browser searches in workspace file `~/browser-searches.json`:

```json
{
  "date": "2026-02-22",
  "count": 3,
  "searches": [
    { "site": "google-flights", "query": "JFK-NRT 2026-03-15", "timestamp": "2026-02-22T10:30:00Z" }
  ],
  "blockedUntil": null
}
```

Before each browser search:
1. Read `~/browser-searches.json` (create if missing)
2. If `date` differs from today, reset `count` to 0 and clear `searches`
3. If `blockedUntil` is set and in the future, refuse — tell user blocked by site
4. If `count >= 10`, refuse — tell user daily browser search limit reached
5. After each search, increment `count` and append to `searches`
6. If a site blocks the browser, set `blockedUntil` to 24 hours from now

## Browser Best Practices

### Context Selection
DIRECT (no proxy): Google Flights, Kayak, Booking.com, Google Hotels, Lufthansa
SCRAPLING (stealth service, no proxy needed): Delta, British Airways, SecretFlying,
  seats.aero, Southwest, Hilton, Hyatt, TripAdvisor, TheFlightDeal, Going,
  SeatGuru, Google Travel (flights + hotels)
PROXY (residential): United, American Airlines, Air Canada, KLM, TravelPirates
SKIP BROWSER (use API):
  - Hotel search → LiteAPI first, browser for enrichment only
  - Deal discovery → Aerobase Deals API first, browser for verification only
  - Tours/activities → Aerobase Tours API first, browser rarely needed
  - Flight pricing → Amadeus/Kiwi API, browser for visual comparison
  - Award search → seats.aero API, browser for airline-specific lookups

### Scrapling Service (Anti-Bot Bypass)

When browser automation is blocked by anti-bot systems (Akamai, Cloudflare, Datadome, etc.),
use the stealth scrapling service configured via `SCRAPLING_URL` environment variable.
This service bypasses detection WITHOUT needing residential proxies.

Reference: [Scrapling Documentation](https://scrapling.readthedocs.io/en/latest/overview.html)

**When to use Scrapling:**
- Site shows reCAPTCHA, "Access denied", or challenge page
- Normal browser is blocked or redirected
- Need to extract data from JS-heavy sites

**How to invoke:**

Fetch a page (returns JSON with status, title, HTML, challenge detection):
```
web_fetch {SCRAPLING_URL}/fetch?url=https://www.delta.com&json=1
```

Run JavaScript on a page:
```
POST {SCRAPLING_URL}/evaluate
Body: {"url": "https://seats.aero", "script": "document.title"}
```

Check service health:
```
web_fetch {SCRAPLING_URL}/health
```

**Response fields:**
- `status`: HTTP status code (200 = success)
- `title`: Page title
- `challenge`: "pass" | "captcha" | "blocked" | "challenge"
- `cached`: true if served from 5-min cache
- `html`: Page HTML (truncated to 50KB in JSON mode)
- `html_length`: Full HTML length

**Fallback chain:**
1. Try Scrapling service first for listed domains
2. If challenge != "pass": fall back to native browser + residential proxy
3. If proxy also fails: screenshot and tell user

**Important:** Scrapling responses are cached for 5 minutes. For time-sensitive
data (live prices, seat maps), append `&nocache=1` or wait for cache expiry.

### Aggregator Search (Scrapling /search)

Pre-built search + Python-side parsing. Returns structured JSON — no browser
snapshot/type/click needed. Results are parsed server-side via Scrapling's
Adaptor engine (CSS selectors, find_similar for self-healing).

**Google Flights:**
```
POST {SCRAPLING_URL}/search
{"site":"google-flights","origin":"LAX","destination":"NRT","departure":"2026-03-15","return":"2026-03-22"}
```
Returns: `{"results": [{"airline":"...","price":"...","duration":"...","stops":"..."}], "count": N}`

**Kayak:**
```
POST {SCRAPLING_URL}/search
{"site":"kayak","origin":"LAX","destination":"NRT","departure":"2026-03-15","return":"2026-03-22"}
```

**Booking.com hotels:**
```
POST {SCRAPLING_URL}/search
{"site":"booking","destination":"Tokyo","checkin":"2026-03-15","checkout":"2026-03-22","guests":2}
```
Returns: `{"results": [{"name":"...","price":"...","rating":"...","location":"..."}], "count": N}`

**Deal sites:**
```
POST {SCRAPLING_URL}/search
{"site":"secretflying"}
POST {SCRAPLING_URL}/search
{"site":"theflightdeal"}
```
Returns: `{"results": [{"title":"...","url":"..."}], "count": N}`

Check `challenge` field — if not "pass", results may be incomplete (consent wall, bot block).

### Multi-Step Interaction (Scrapling /interact)

For flows needing form fill, click, screenshot (check-in, login, registration):

```
POST {SCRAPLING_URL}/interact
{
  "url": "https://www.southwest.com/air/check-in/",
  "steps": [
    {"action": "consent"},
    {"action": "fill", "selector": "#confirmationNumber", "value": "ABC123"},
    {"action": "fill", "selector": "#firstName", "value": "John"},
    {"action": "fill", "selector": "#lastName", "value": "Doe"},
    {"action": "click", "selector": "button#form-mixin--submit-button"},
    {"action": "wait", "ms": 5000},
    {"action": "screenshot"},
    {"action": "extract", "css": "h1::text"}
  ]
}
```

**Available actions:**
- `consent` — auto-dismiss cookie consent walls
- `fill` — fill input by CSS selector (instant, like paste)
- `type` — type with per-key delay (more human-like, use for sensitive fields)
- `click` — click element by CSS selector
- `wait` — wait N milliseconds
- `wait_for` — wait for selector to appear (with timeout)
- `screenshot` — capture current page (returned as base64 in `screenshots` array)
- `extract` — parse page with CSS selector (results in `extracted` array)
- `select` — select dropdown option

### Fetch with Screenshot or CSS Extraction

```
web_fetch {SCRAPLING_URL}/fetch?url=https://www.delta.com&json=1&screenshot=1
web_fetch {SCRAPLING_URL}/fetch?url=https://www.secretflying.com&json=1&extract=css&selector=article
```

### Search + Book Pattern

1. Fire API search (Kiwi/Duffel) immediately — don't wait for browser
2. Fire Scrapling `/search` in parallel for comparison data
3. Show API results first (faster, <2s)
4. Merge Scrapling results: "Google Flights also shows..." / "Kayak prices..."
5. For booking: use API (Duffel hold → user confirms → API completes)
6. For airline-direct booking: navigate user to airline site via VNC
7. NEVER automate payment card entry via browser

### Booking Flow

- **API booking** (Duffel/Kiwi): Agent can search, hold, and complete with user approval
- **Browser booking**: Navigate to site, user completes payment via VNC
- **NEVER** automate payment card entry via browser (PCI compliance, 3D Secure blocks)
- For held bookings: confirm with user before paying (Duffel supports 24-72h holds)

### API-First + Browser-Concurrent Pattern
For any task where we have an API:
1. Fire API request immediately (don't wait for browser)
2. Show API results to user as they arrive
3. Launch browser concurrently if enrichment would help
4. Merge browser findings: "I also found..." / "For comparison..."
5. Highlight discrepancies between API and browser data
This gives the user instant results + richer context seconds later.

### Launch Checklist
1. Stealth plugin is auto-loaded — no action needed
2. Choose direct or proxy context based on target domain
3. Set viewport 1440x900, locale en-US, timezone America/New_York
4. Set 30s default timeout for navigation
5. ALWAYS register error handler: page.on('pageerror', ...)

### Memory Management (CRITICAL)
- Chrome watchdog kills process at 1800MB RSS
- Max 2 concurrent tabs safely (tested: 3 tabs = 1795MB = danger zone)
- ALWAYS close context after task: await context.close()
- Prefer sequential tabs over concurrent
- If opening multiple tabs: close each before opening next
- Monitor with: process.memoryUsage().rss

### Cookie Consent (EU server — Helsinki)
Scrapling service handles consent dismissal automatically via `page_action`.
For native browser, patterns to try in order:
1. button:has-text("Reject all")
2. button:has-text("Decline")
3. button:has-text("Alle ablehnen")
4. button:has-text("I decline")
5. [data-testid="reject-button"]
6. button:has-text("Manage") → then "Reject all" in second dialog
Timeout: 5s for consent dialog, then proceed (some sites don't show it)

### Bot Detection Response
If you see any of these, you're being blocked:
- reCAPTCHA iframe or badge
- "Please verify you are a human"
- "Access denied" / "403 Forbidden"
- Datadome challenge page
- Blank page with Cloudflare "checking your browser"
- "Pardon our interruption" (Akamai)

Response:
1. If domain is in Scrapling list: try Scrapling service first (no proxy cost)
2. If Scrapling returns challenge != "pass": fall back to native browser + PROXY
3. If on DIRECT: retry with PROXY context
4. If already on PROXY: screenshot and fallback to alternative site
5. Tell user: "I'm seeing a verification on [site]. Let me try [alternative]."
6. NEVER attempt to solve CAPTCHAs
7. Max 2 retries per site per session

### Screenshot Best Practices
- Full page: page.screenshot({ fullPage: true }) — use for results
- Viewport only: page.screenshot() — use for errors/blocks
- Element: element.screenshot() — use for specific data extraction
- Always save to /tmp/ with descriptive name
- Offer to show screenshots to user when relevant

### Geo-Awareness
Server is in Helsinki, Finland (EU). This means:
- Airline sites redirect to EU versions (/eu/en, .de, etc.)
- Prices show in EUR by default on many sites
- Cookie consent walls appear on almost every site
- Some US-only features/deals may not be accessible
- With US residential proxy: sites see US IP, show USD, US content

### Performance Targets
- Page load: <10s acceptable, <5s ideal
- Search results: <15s acceptable
- Check-in form: <10s
- If exceeding 30s: abort, screenshot, try alternative
