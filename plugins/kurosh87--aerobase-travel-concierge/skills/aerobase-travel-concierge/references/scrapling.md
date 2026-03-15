# Scrapling Service Reference

The Scrapling service is a stealth web scraping service that bypasses anti-bot systems (Akamai, Cloudflare, Datadome) without needing residential proxies.

## Base URL

Configured via `SCRAPLING_URL` environment variable (provided by OpenClaw deployment).

## Endpoints

### GET /fetch
Fetch a web page and return JSON with parsed content.

**Parameters:**
- `url` (required) - Target URL
- `json=1` - Return JSON response
- `extract=css` - Extract using CSS selector
- `selector` - CSS selector for extraction
- `screenshot=1` - Include base64 screenshot
- `nocache=1` - Bypass 5-minute cache

**Example:**
```
GET {SCRAPLING_URL}/fetch?url=https://www.delta.com&json=1
```

**Response:**
```json
{
  "status": 200,
  "title": "Delta Air Lines - Check In",
  "challenge": "pass",
  "cached": false,
  "html": "...",
  "html_length": 45000
}
```

### POST /search
Pre-built search + parsing for aggregator sites.

**Body:**
```json
{
  "site": "google-flights",
  "origin": "LAX",
  "destination": "NRT",
  "departure": "2026-03-15",
  "return": "2026-03-22"
}
```

**Supported Sites:**
- `google-flights` - Flight search results
- `kayak` - Kayak flight search
- `booking` - Hotel search
- `secretflying` - Flight deals
- `theflightdeal` - Flight deals
- `travelpirates` - Flight deals

### POST /interact
Multi-step page interaction for forms and login.

**Body:**
```json
{
  "url": "https://www.example.com/form/",
  "steps": [
    {"action": "consent"},
    {"action": "fill", "selector": "#confirmationNumber", "value": "ABC123"},
    {"action": "fill", "selector": "#lastName", "value": "DOE"},
    {"action": "click", "selector": "button[type='submit']"},
    {"action": "wait", "ms": 5000},
    {"action": "screenshot"}
  ]
}
```

**Available Actions:**
- `consent` - Auto-dismiss cookie consent
- `fill` - Fill input by CSS selector
- `type` - Type with per-key delay
- `click` - Click element
- `wait` - Wait N milliseconds
- `wait_for` - Wait for selector
- `screenshot` - Capture page (base64)
- `extract` - Parse with CSS selector
- `select` - Select dropdown option

### POST /evaluate
Run JavaScript on a page.

**Body:**
```json
{
  "url": "https://seats.aero",
  "script": "document.title"
}
```

### GET /health
Check service health.

## Challenge Responses

- `pass` - Success, no blocking
- `captcha` - CAPTCHA required
- `blocked` - Access denied
- `challenge` - Cloudflare/akamai challenge

## Rate Limits

- Responses cached for 5 minutes
- Use `nocache=1` for time-sensitive data

## Documentation

See: https://scrapling.readthedocs.io/en/latest/overview.html
