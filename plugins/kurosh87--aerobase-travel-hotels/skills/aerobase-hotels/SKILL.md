---
name: aerobase-hotels
description: "Hotel search with jetlag-friendly features, day-use availability, and price comparison"
---

# Hotel Booking & Layover Accommodation

Frame hotel recommendations in terms of recovery: "Your layover is 9 hours. An 8-minute shuttle
to the Hilton gives you 5 hours of sleep at a time when your body clock says 2 AM — $89 for the
room could save you a full day of jetlag on the next leg."

## Search (v1 API - Preferred)

**GET /api/v1/hotels** — Search hotels with filters
Query params: `airport`, `city`, `country`, `chain`, `tier`, `stars`, `jetlagFriendly`, `search`, `limit`, `offset`
Returns: hotels with jetlagFeatures, amenities, pricing

Example: `GET /api/v1/hotels?airport=JFK&jetlagFriendly=true`

## Search (Legacy)

**POST /api/hotels/search** — `{ destination, checkin, checkout, guests }`
2. **RATES**: GET /api/hotels/rates/{hotelId} — rooms, cancellation policies, nightly rates
3. **PREBOOK**: POST /api/hotels/prebook — validate rate, get prebookId (price may change!)
4. **BOOK**: POST /api/hotels/book — `{ prebookId, guests, payment }` → confirmation
5. **MANAGE**: GET /api/hotels/bookings, DELETE /api/hotels/bookings/{id}

## Special

- **GET /api/dayuse?airport={code}** — Day-use hotels for layover passengers (book by the day, no overnight stay)
- **GET /api/hotels?dayuse=true** — Filter hotels to day-use only
- **GET /api/hotels/near-airport/{code}** — airport-adjacent hotels

## Always

- Show cancellation policy before booking
- Layovers > 8 hours: recommend day-use hotels
- Consider jetlag recovery: blackout curtains, gym, pool for long-haul arrivals

## Rate Limits

- Search: max 20/hr. Rates: max 10/hr. Prebook: max 5/hr (holds inventory).
- Book: max 2/hr (irreversible payment). Near-airport: max 10/hr.

## Data Sources — Hotels

### Primary: LiteAPI (FREE, always query first)
- Hit LiteAPI for availability, pricing, and property details FIRST
- Returns structured JSON: property name, price, rating, amenities, photos
- No rate limits concern at current usage
- Response time: fast, no browser overhead

### Secondary: Browser (concurrent enrichment)
Launch browser search IN PARALLEL with LiteAPI call for:
- Visual verification of property (screenshots)
- Reviews/ratings from Booking.com that LiteAPI may not include
- Price comparison across OTAs (Booking.com vs Google Hotels vs LiteAPI)
- Neighborhood context (Google Maps street view, nearby attractions)

### Workflow
1. User asks "Find hotels in Tokyo for March 15-20"
2. IMMEDIATELY fire two concurrent requests:
   a. LiteAPI query (structured data, fast)
   b. Browser → Booking.com search (visual enrichment, slower)
3. Show LiteAPI results first (they arrive faster)
4. Enrich with browser data as it arrives: "I also found these on Booking.com for comparison..."
5. Highlight price differences: "LiteAPI shows $120/night, Booking.com has $135 for the same property"

### Scrapling — Booking.com Hotel Search

Use Scrapling `/search` for structured hotel extraction:

Reference: [Scrapling Documentation](https://scrapling.readthedocs.io/en/latest/overview.html)

```
POST {SCRAPLING_URL}/search
{"site":"booking","destination":"Tokyo","checkin":"2026-03-15","checkout":"2026-03-22","guests":2}
```
Returns: `{"results": [{"name":"..","price":"..","rating":"..","location":".."}], "count": N}`

**Note:** Booking.com is in the "challenge" tier — consent walls may block search params.
If `challenge != "pass"` and count is 0, fall back to native browser with PROXY.

### Browser — Google Hotels Workflow (DIRECT, no proxy)
1. Navigate to https://www.google.com/travel/hotels
2. Dismiss cookie consent if shown
3. Type destination, wait for suggestions
4. Results show aggregated prices from multiple booking sites
5. Useful for: "Is LiteAPI's price competitive?"

### When to SKIP browser entirely
- User just wants quick availability check → LiteAPI only
- User asks for specific hotel by name → LiteAPI lookup, no need to scrape
- Budget/simple queries → LiteAPI is sufficient
- Only use browser when user wants comparison, reviews, or visual confirmation
