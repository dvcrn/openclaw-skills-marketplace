---
name: aerobase-travel-concierge
description: "Complete AI travel concierge - flights, hotels, lounges, awards, activities, deals. Powered by Aerobase."
---

⚠️ **TRANSPARENCY NOTICE**

This skill creates a small JSON file in your home directory for rate limiting:
- `~/aerobase-browser-searches.json` - Browser search count (max 10/day)

These files contain only:
- Date and count of operations
- Site queried (for browser searches)

**Data handling:**
- Gmail scanning only happens when user explicitly requests it
- No personal data is sent to external services beyond what's required

**External Services:**

| Service | Data Sent | Data NOT Sent |
|---------|-----------|---------------|
| Aerobase API | API requests with AEROBASE_API_KEY | N/A |
| Scrapling (SCRAPLING_URL) | URLs to fetch for price verification | Gmail content, payment info, stored credentials |

**Scrapling** is a stealth browsing service for price verification and deal discovery. It bypasses anti-bot systems to fetch live prices from Google Flights, Kayak, etc.

---

# Aerobase Travel Concierge ⭐ ALL-IN-ONE

Your personal AI travel agent that never sleeps. **This is the complete package** — all Aerobase skills in one installation.

## API-First Principle

**ALWAYS use the Aerobase API first** before any browser automation. The API is faster, more reliable, and doesn't trigger anti-bot systems.

Browser/scraping is only for:
- Verification of live prices
- Sites not covered by API
- Check-in automation (experimental)
- User explicitly requests external site check

---

# ✈️ Flight Search & Booking

## API Endpoints

**GET /api/v1/flights/search** — Search flights with jetlag scoring
**POST /api/v1/flights/score** — Score any flight option (0-100 jetlag)
**POST /api/v1/flights/compare** — Compare multiple options

Query params: `origin`, `destination`, `departure`, `return`, `cabin`, `maxPrice`, `limit`

## Example
```
POST /api/v1/flights/search
{ "origin": "JFK", "destination": "NRT", "departure": "2026-03-15", "cabin": "business" }
```

Returns flights with jetlag scores, recovery days, and recommendations.

---

# 🏆 Award Search

## API Endpoints

**POST /api/v1/awards/search** — Search 24+ airline loyalty programs
**GET /api/transfer-bonuses** — Current transfer partner bonuses

Query: `origin`, `destination`, `departure`, `return`, `cabin`, `maxMiles`

## Programs Supported
Aeromexico, Air Canada, Alaska, Alitalia, All Nippon, American, Avianca, British Airways, Cathay Pacific, Delta, Emirates, Etihad, Flying Blue, Iberia, Japan Airlines, JetBlue, Korean Air, Lufthansa, Qantas, Qatar, Singapore, Southwest, United, Virgin Atlantic

## CPP Calculation
Use Scrapling to get cash prices for cents-per-point calculation:
```
POST {SCRAPLING_URL}/search
{"site":"google-flights","origin":"JFK","destination":"LHR","departure":"2026-04-01","return":"2026-04-08"}
```
Reference: [Scrapling Docs](https://scrapling.readthedocs.io/en/latest/overview.html)

---

# 🏧 Airport Lounges

## API Endpoints

**GET /api/v1/lounges** — Search with filters: `airport`, `airline`, `network`, `tier`, `search`
**GET /api/airports/{code}/lounges** — Lounges at specific airport

Data sourced from LR (LoungeReview) tables with detailed information.

## Jetlag-Relevant Fields
- **recoveryScore**: 1-10, higher = better for recovery
- **hasShowers**: Boolean - freshen up between flights
- **hasSpa**: Boolean - premium recovery
- **hasSleepPods**: Boolean - rest between flights
- **quietZone**: Boolean - circadian alignment
- **naturalLight**: Boolean - jetlag adjustment

## Scrapling — Priority Pass Hours
Use for real-time hours verification:
```
web_fetch {SCRAPLING_URL}/fetch?url=https://www.prioritypass.com/lounges/united-states/new-york-ny/jfk-john-f-kennedy-intl&json=1&extract=css&selector=.lounge-card
```
Reference: [Scrapling Docs](https://scrapling.readthedocs.io/en/latest/overview.html)

---

# 🏨 Hotel Search

## API Endpoints

**GET /api/v1/hotels** — Search with filters: `airport`, `city`, `country`, `chain`, `tier`, `stars`, `jetlagFriendly`, `search`
**GET /api/hotels/near-airport/{code}** — Airport-adjacent hotels

## Day-Use Hotels (Layovers)

**GET /api/dayuse?airport={code}** — Day-use hotels for layover passengers (book by the day, no overnight)
**GET /api/hotels?dayuse=true** — Filter hotels to day-use only

For layovers > 8 hours, recommend day-use hotels.

---

# 🎫 Tours & Activities

## API Endpoints

**GET /api/v1/tours** — Viator tours and attractions
Query: `airport`, `destination`, `category`, `duration`, `priceRange`

## Scrapling — TripAdvisor Discovery
Use for supplementary activity discovery:
```
web_fetch {SCRAPLING_URL}/fetch?url=https://www.tripadvisor.com/Attractions-g294217-Activities-Tokyo_Tokyo_Prefecture_Kanto.html&json=1&extract=css&selector=.listing_title
```
Reference: [Scrapling Docs](https://scrapling.readthedocs.io/en/latest/overview.html)

---

# 💰 Flight Deals

## API Endpoint

**GET /api/v1/deals** — Curated flight deals
Query: `origin`, `destination`, `maxPrice`, `minScore`, `dateFrom`, `dateTo`, `cabin`, `sort`, `limit`

Returns up to 50 results (3 for free tier).

## Data Sources
The Deals API includes deals scraped from:
- SecretFlying
- TheFlightDeal
- TravelPirates
- Going.com

These sources are scraped periodically and stored in our database.

## Scrapling — Deal Verification
Only use for verification or when user explicitly asks:
```
POST {SCRAPLING_URL}/search
{"site":"secretflying"}
POST {SCRAPLING_URL}/search
{"site":"google-flights","origin":"JFK","destination":"NRT","departure":"2026-03-15","return":"2026-03-22"}
```
Reference: [Scrapling Docs](https://scrapling.readthedocs.io/en/latest/overview.html)

---

# 💳 Points & Wallet

## API Endpoints

**GET /api/v1/credit-cards** — Credit card transfer partners
**GET /api/v1/loyalty/balances** — (Premium) Gmail scanning required

## Gmail Loyalty Scanning (Premium)

⚠️ **User Consent Required:** Only use this feature when:

1. User explicitly asks "scan my Gmail for points" or "show my loyalty balances"
2. User has already connected Gmail via OAuth in Aerobase settings (handled by Aerobase, not this skill)
3. Never scan Gmail proactively - only after user request

**How it works:**
- Users connect Gmail via OAuth in Aerobase settings. Only loyalty/points data is extracted - email contents are never shared.
- The skill calls `GET /api/v1/loyalty/balances` - Aerobase server handles the Gmail API call
- Only points/loyalty numbers are returned - never email content

---

# 😴 Jetlag Recovery Plans (PREMIUM)

## API Endpoint

**POST /api/v1/recovery/plan** — Generate personalized recovery plan

Requires: `flight` (origin, destination, departureTime), `chronotype` (earlyBird, nightOwl, neutral), `tripDuration`

Returns:
- Pre-trip preparation schedule
- In-flight strategies
- Day-by-day recovery timeline
- Light exposure timing
- Sleep and diet adjustments

---

# 🔧 Browser Automation

**USE BROWSER ONLY WHEN:**
- User specifically asks to check Google Flights / Kayak / Skyscanner
- API search returned no results and user wants broader coverage
- Price comparison requested
- Check-in automation (experimental)

## Browser Commands (OpenClaw Playwright-on-CDP)

- `browser snapshot` — get ARIA tree with [ref=eN] element references
- `browser type [ref=eN] "value"` — type into input field
- `browser click [ref=eN]` — click element
- `browser screenshot` — capture current page state

## Context Selection

| Type | Use For |
|------|---------|
| DIRECT | Google Flights, Kayak, Booking.com, Google Hotels, Lufthansa |
| SCRAPLING | Delta, British Airways, SecretFlying, seats.aero, Southwest, Hilton, Hyatt, TripAdvisor, TheFlightDeal, Going, SeatGuru, Google Travel |
| PROXY | United, American Airlines, Air Canada, KLM, TravelPirates |

## Scrapling Service (Anti-Bot Bypass)

When browser automation is blocked by anti-bot systems (Akamai, Cloudflare, Datadome), use the stealth scrapling service configured via `SCRAPLING_URL` environment variable.

Reference: [Scrapling Documentation](https://scrapling.readthedocs.io/en/latest/overview.html)

### Fetch a page
```
web_fetch {SCRAPLING_URL}/fetch?url=https://www.delta.com&json=1
```

### Run JavaScript
```
POST {SCRAPLING_URL}/evaluate
Body: {"url": "https://seats.aero", "script": "document.title"}
```

### Multi-step interaction (forms)
```
POST {SCRAPLING_URL}/interact
{
  "url": "https://www.example.com/form/",
  "steps": [
    {"action": "consent"},
    {"action": "fill", "selector": "#confirmationNumber", "value": "<PNR>"},
    {"action": "fill", "selector": "#passengerLastName", "value": "<LAST>"},
    {"action": "click", "selector": "button#form-mixin--submit-button"},
    {"action": "wait", "ms": 5000},
    {"action": "screenshot"}
  ]
}
```

### Aggregator Search
```
POST {SCRAPLING_URL}/search
{"site":"google-flights","origin":"LAX","destination":"NRT","departure":"2026-03-15","return":"2026-03-22"}
```

## Rate Limits

- Browser searches: max 10/day per user
- Scrapling: follow cache rules (5-min cache)
- API: varies by endpoint (see each section)

---

# 📋 Rate Limits Summary

**Combined API calls: 5/day total** (all endpoints share the same quota)

| Feature | Notes |
|---------|-------|
| Combined API | 5/day (shared across all endpoints) |
| Browser searches | 10/day (tracked in `~/aerobase-browser-searches.json`) |

---

# 📁 Additional Files

## Helper Scripts (`scripts/`)
- `browser-tracking.mjs` - Track browser search limits

## API References (`references/`)
- `aerobase-api.md` - Complete Aerobase API endpoint reference
- `scrapling.md` - Scrapling service endpoints and parameters

## Full Documentation
- OpenAPI Spec: https://aerobase.app/api/v1/openapi
- Scrapling Docs: https://scrapling.readthedocs.io/en/latest/overview.html

---

# 🔒 Privacy, Security & Credentials

## Required Environment Variables

| Variable | Purpose | Provided By |
|----------|---------|-------------|
| `AEROBASE_API_KEY` | Main API access | User gets from aerobase.app/settings |
| `SCRAPLING_URL` | Stealth scraping service | Configured by OpenClaw deployment |
| OAuth tokens | Gmail access | User connects via Aerobase OAuth (never stored by skill) |

**Note:** `SCRAPLING_URL` is configured by the OpenClaw deployment - users do not need to provide this.

## Gmail OAuth - How It Works

1. User navigates to https://aerobase.app/settings
2. Clicks "Connect Gmail" - goes to Google's OAuth flow
3. User grants read-only access to loyalty/points emails only
4. Aerobase receives OAuth token - **token is stored by Aerobase, NOT by this skill**
5. Skill calls `GET /api/v1/loyalty/balances` - Aerobase server makes the Gmail API call
6. **Email contents never leave Aerobase servers** - only extracted points balances returned

**What data is extracted:**
- Loyalty program account numbers (from airline/hotel point statements)
- Point balances mentioned in emails
- Credit card spend categories

**What is NOT accessed:**
- Email body/content
- Personal messages
- Contacts
- Calendar

## Local File Storage

The skill creates a small JSON file in the user's home directory to track rate limits:

- `~/aerobase-browser-searches.json` - Browser search count and history

**Contents stored:**
- Date and count of browser searches
- Site queried and timestamp

These files are used only for rate limiting - no personal data beyond search counts.

**User control:**
- User can revoke access anytime from Google's account settings
- Aerobase deletes tokens on disconnect

See: https://aerobase.app/privacy

## Scrapling Service

The `{SCRAPLING_URL}` service is operated by the OpenClaw deployment. It is used for:
- Price verification (Google Flights, Kayak)
- Deal site checks (SecretFlying, TheFlightDeal)

**Data sent to Scrapling:**
- URLs requested by the skill (price verification, deal discovery)
- No user credentials or PII

**Not used for:**
- Gmail access
- Payment information
- Storing user data

## Browser Automation

For live price verification:
- Fetches current prices from travel sites
- No user credentials required

---

**Security & Privacy Links:**
- Aerobase Privacy Policy: https://aerobase.app/privacy
- Aerobase Terms: https://aerobase.app/terms
- OpenClaw Security: https://openclaw.ai/security

---

# 🚀 Quick Reference

## Always
1. Query API first - faster, reliable, no blocks
2. Show API results to user immediately
3. Use browser/scrapling only for verification or explicit requests
4. Enrich results with jetlag scores

## Fallback Chain
1. Try API first
2. Try Scrapling service (no proxy needed)
3. Try native browser + proxy
4. Screenshot and explain to user if all fail
