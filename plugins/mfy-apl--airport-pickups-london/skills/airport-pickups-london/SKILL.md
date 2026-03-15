---
name: airport-pickups-london
description: "Book UK airport and cruise port transfers via Airport Pickups London. Get instant fixed-price quotes, validate flights, and create real bookings for all London airports (Heathrow, Gatwick, Stansted, Luton, City), Edinburgh, and cruise ports (Southampton, Dover, Portsmouth, Tilbury, Harwich). TfL-licensed, 24/7 service. Supports A2A pricing negotiation (up to 5% discount)."
homepage: https://www.airport-pickups-london.com
---

# Airport Pickups London — Transfer Booking Skill

This skill connects your agent to Airport Pickups London's booking API via MCP, giving it the ability to get transfer quotes, validate flights, and create real bookings.

## What Your Agent Can Do

- **Get instant quotes** for any UK route — airports, cruise ports, addresses, postcodes
- **Validate flight numbers** — auto-detect terminal, airline, arrival time
- **Create real bookings** — confirmed reservations with booking reference and driver tracking link

## Setup

Add the APL MCP server to your OpenClaw config.

**Step 1 — Get an API key** (one-time, instant):

Send a POST request to the registration endpoint:

```bash
curl -X POST https://mcp.airport-pickups-london.com/a2a/register \
  -H "Content-Type: application/json" \
  -d '{"name": "Your Agent Name", "email": "you@example.com"}'
```

This returns your API key immediately. Free, no approval needed.

**Step 2 — Add to your config:**

```json
{
  "mcpServers": {
    "airport-pickups-london": {
      "url": "https://mcp.airport-pickups-london.com/mcp",
      "headers": {
        "x-api-key": "YOUR_API_KEY"
      }
    }
  }
}
```

## Available Tools

### `get_quote`
Get prices for any UK transfer route.

**Example prompts your agent will handle:**
- "How much is a taxi from Heathrow to central London?"
- "Get me a quote from Gatwick to Brighton for 4 passengers"
- "What's the price from Southampton cruise port to London?"

### `validate_flight`
Verify a flight number and get terminal, airline, arrival time, and meeting point.

**Example prompts:**
- "Check flight BA2534 arriving on April 15th"
- "What terminal does EK007 arrive at?"

### `book_transfer`
Create a confirmed transfer booking.

**Returns:**
- Booking reference (e.g. APL-CJ5KDJ)
- Manage booking URL — customer can view details, pay online, track driver, amend or cancel
- Meeting point instructions (e.g. "Heathrow T3 — in front of WH Smith under the Welcome Board")
- Confirmation email automatically sent to the passenger
- Price, car type, pickup time, and all booking details

**Example prompts:**
- "Book a People Carrier from Heathrow to W1K 1LN for John Smith, phone +447123456789, flight BA2534, April 15th at 3pm"

## Pricing Negotiation (A2A Extension)

Agents can request a discount by including `requestedDiscountPercent` in the quote request. The maximum discount is **5%** — requests above this are automatically capped. The response includes `appliedDiscountPercent` showing the actual discount given.

**Non-negotiable items:** peak surcharges, event pricing (Christmas, bank holidays), child seats.

```json
// Request
{ "origin": "Heathrow", "destination": "W1", "requestedDiscountPercent": 3 }

// Response includes
{ "appliedDiscountPercent": 3, "cars": [{ "car_type": "Saloon", "price_gbp": 72.75 }] }
```

## Pricing Info

- All prices in GBP (£), per vehicle (not per person)
- Fixed prices — no surge, no hidden charges
- Includes meet & greet, waiting time, parking, tolls
- Free cancellation 24+ hours before pickup

## Vehicle Types

| Car Type | Passengers | Suitcases | From |
|----------|-----------|-----------|------|
| Saloon | Up to 3 | 3 | ~£33 |
| People Carrier | Up to 5 | 5 | ~£45 |
| 8 Seater | Up to 8 | 8 | ~£55 |
| Executive Saloon | Up to 3 | 3 | ~£65 |
| Executive MPV | Up to 7 | 7 | ~£85 |

## Important Rules for Agents

1. **ALWAYS call get_quote before booking** — never guess prices
2. **NEVER call book_transfer without user confirmation** — always show the price and get a "yes" first
3. Flight validation is optional and never blocks a booking
4. For airport pickups, recommend clearance: domestic 15min, European 45min, international 60min after landing

## Support

- 24/7 Phone: +44 208 688 7744
- WhatsApp: +44 73 8790 1028
- Website: www.airport-pickups-london.com
- Email: info@aplcars.com

## Ratings

TripAdvisor 4.7/5 | Trustpilot 4.9/5 | Reviews.io 4.9/5
