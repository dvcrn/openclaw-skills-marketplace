---
name: aerobase-travel-flights
description: "Search, compare, and score flights with jetlag optimization. Includes booking via Kiwi/Duffel APIs"
---

# Aerobase Travel Flights 🛫

## Search

**POST /api/v1/flights/search** — live Kiwi search + DB fallback
Body: `{ from: "JFK", to: "LHR", date: "2026-03-15", returnDate?: "2026-03-22", cabinClass?: "economy" }`
Free tier: 5 results. Concierge: 50 results. Sorted by jetlag composite DESC, then price ASC.

**POST /api/flights/search/agent** — multi-provider parallel search (Kiwi + Duffel)
Same body. Returns UnifiedFlight[] with provider, price, jetlagScore, segments.
15-second per-provider timeout. Dedup by flight number + departure time (5min tolerance, 5% price).

## Booking (API — preferred track)

**POST /api/flights/validate** — pre-booking price check
Body: `{ flightId, provider, offerId }`
Returns: `{ valid, currentPrice, priceChanged }`

**POST /api/flights/book** — book via AgentBookingService
Body: `{ flightId, provider, offerId, passengers: [...], payment: { stripePaymentMethodId } }`
- Kiwi: 3-phase (check_flights → save_booking → confirm_payment). 5% price tolerance.
- Duffel: instant order with balance payment.
- Neither available: returns deepLink URL for manual/browser booking.

**NEVER submit payment without explicit user approval.**

## Booking (browser — fallback track)

Only when API returns deepLink or provider unavailable:
1. Open airline website via browser
2. Fill passenger details from user profile
3. Screenshot pre-payment page, send for approval
4. Only submit after explicit "yes"

## Comparison & Scoring

**POST /api/v1/flights/compare** — compare 2-10 flights with recommendation + deltas
**POST /api/v1/flights/score** — jetlag K2 score (0-100), direction, recoveryDays, strategies
**GET /api/v1/flights/lookup/{carrier}/{number}** — live Amadeus + mv_flight_schedules fallback
**GET /api/flights/providers/status** — circuit breaker state for Kiwi and Duffel (check before booking)

## Rate Limits

- Search: max 20/hr (Kiwi rate limit). Agent search: max 10/hr (parallel providers)
- Validate: max 5/hr per offer. Book: max 2/hr (irreversible)
- Score/Compare: max 50/hr (lightweight). Lookup: max 30/hr (Amadeus quota)

## Scrapling Flight Search (Preferred over Native Browser)

Use the Scrapling `/search` endpoint for aggregator searches. Returns pre-parsed structured JSON —
no browser snapshot/type/click needed. Helsinki server shows EUR prices.

Reference: [Scrapling Documentation](https://scrapling.readthedocs.io/en/latest/overview.html)

### Google Flights
```
POST {SCRAPLING_URL}/search
{"site":"google-flights","origin":"LAX","destination":"NRT","departure":"2026-03-15","return":"2026-03-22"}
```
Returns: `{"results": [{"airline":"..","price":"€1,216","duration":"11 hr 50 min","stops":"Nonstop"}], "count": N}`

### Kayak (may hit captcha — falls back to proxy)
```
POST {SCRAPLING_URL}/search
{"site":"kayak","origin":"LAX","destination":"NRT","departure":"2026-03-15","return":"2026-03-22"}
```

### API-First + Scrapling-Concurrent Pattern
1. Fire API search (Kiwi/Duffel) immediately — show results to user
2. Fire Scrapling `/search` in parallel for comparison data
3. Merge: "Google Flights also shows €1,216 nonstop for the same route"
4. Highlight discrepancies between API and browser data

### Fallback to Native Browser
If Scrapling returns `challenge != "pass"` or 0 results:
1. Try native browser with PROXY context
2. Follow manual form-fill workflow (see aerobase-browser SKILL)
3. Max 2 retries per site per session

### Important Notes
- Helsinki server → EUR prices by default. Convert if user expects USD
- Google Flights typically returns 15-50 results per search
- Kayak often hits captcha — Google Flights is more reliable via Scrapling
- Skyscanner blocks entirely — skip it
