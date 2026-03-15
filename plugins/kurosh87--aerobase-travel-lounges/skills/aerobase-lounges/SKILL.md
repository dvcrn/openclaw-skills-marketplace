---
name: aerobase-lounges
description: "Airport lounge access and recovery recommendations"
---

# Airport Lounge Access & Recovery

Help users find airport lounges for jetlag recovery. Frame recommendations in terms of recovery: "The Delta Sky Club has showers and a quiet zone — perfect for a 3-hour rest before your red-eye."

## Search (v1 API - Preferred)

**GET /api/v1/lounges** — Search airport lounges with filters
Query params: `airport`, `airline`, `network`, `tier`, `search`, `limit`, `offset`
Returns: lounges with jetlagFeatures, amenities, recovery scores

Example: `GET /api/v1/lounges?airport=JFK&tier=1`

## Legacy Search

**GET /api/lounges** — `{ airport?, airline?, network?, tier?, search? }`
**GET /api/airports/{code}/lounges** — lounges at specific airport

Data sourced from LR tables with detailed lounge information.

## Lounge Data

The database contains lounges with these jetlag-relevant fields:
- **recoveryScore**: 1-10 scale, higher = better for recovery
- **hasShowers**: Boolean - important for freshening up between flights
- **hasSpa**: Boolean - premium recovery option
- **hasSleepPods**: Boolean - for rest between flights
- **quietZone**: Boolean - important for circadian alignment
- **naturalLight**: Boolean - helps with jetlag adjustment
- **amenities**: Array - food, bar, showers, spa, sleep pods, quiet zone, etc.

## Always

- Show recovery score alongside lounge recommendations
- Recommend showers for long-haul arrivals
- Suggest quiet zones for red-eye flights
- Note Priority Pass acceptance for access options
- Consider layover duration when recommending lounge vs. hotel

## Rate Limits

- Lounge search: max 30/hr
- Airport-specific queries: max 20/hr

## Browser Automation — Lounge Verification

Only use browser for:
- Visual verification of lounge location/quality
- Real-time hours verification
- Access requirement confirmation (Priority Pass, airline status, etc.)

### Scrapling — Priority Pass Lounge Lookup

Priority Pass is in the scrapling tier (no proxy needed). Use for real-time hours verification
and access requirement confirmation:

Reference: [Scrapling Documentation](https://scrapling.readthedocs.io/en/latest/overview.html)

```
web_fetch {SCRAPLING_URL}/fetch?url=https://www.prioritypass.com/lounges/united-states/new-york-ny/jfk-john-f-kennedy-intl&json=1&extract=css&selector=.lounge-card
```

Replace the country/city/airport path segments for other locations. Returns lounge details
including opening hours, access methods, and amenities.

For lounge card rendering, see **aerobase-ui** SKILL for LoungeCard component spec.

### When to SKIP browser
- General lounge search → API has comprehensive data
- Access verification → API shows Priority Pass, airline, etc.
- Only use browser for visual confirmation or hours check
