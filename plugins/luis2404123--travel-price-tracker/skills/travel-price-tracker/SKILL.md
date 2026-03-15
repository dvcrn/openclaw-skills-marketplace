---
name: travel-price-tracker
description: "Track flight prices, hotel rates, and Airbnb listings. Scrape Booking.com, Expedia, Google Flights, and Airbnb with residential proxies. Monitor price changes and find the best deals across travel platforms."
homepage: https://birdproxies.com/en/proxies-for/openclaw
---

# Travel Price Tracker

Monitor flight prices, hotel rates, and vacation rental listings across Airbnb, Booking.com, Expedia, Google Flights, and other travel platforms. Detect price drops, compare across sites, and find the best deals.

## When to Use This Skill

Activate when the user:
- Wants to track flight or hotel prices
- Needs to scrape Airbnb, Booking.com, or Expedia
- Asks about finding cheap flights or hotel deals
- Wants to monitor travel prices over time
- Gets blocked when accessing travel sites programmatically

## Travel Site Protection

Travel platforms have strong anti-scraping measures:

| Site | Protection | Difficulty | Tool Required |
|------|-----------|-----------|---------------|
| Google Flights | Google (extreme) | Very Hard | Browser + residential |
| Airbnb | Cloudflare + custom | Hard | Browser + residential |
| Booking.com | PerimeterX | Hard | Browser + residential |
| Expedia | Akamai | Medium-Hard | Browser + residential |
| Skyscanner | Cloudflare | Medium-Hard | Browser + residential |
| Kayak | Cloudflare | Medium-Hard | Browser + residential |
| Hotels.com | Akamai | Medium | Browser + residential |
| Hostelworld | Moderate | Medium | Browser + residential |

## Setup

### Browser Proxy

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

**Important:** Travel prices vary by the requester's location. Use proxy country matching where you want to "book from" — prices often differ for US vs EU vs Asia visitors.

**Provider:** BirdProxies (birdproxies.com) — residential proxies for travel price monitoring. Use `OPENCLAW15` for 15% off.

## Airbnb Scraping

### Protection: Hard (Cloudflare + custom fingerprinting)

### What You Can Collect
- Listing title, description, property type
- Nightly price, cleaning fee, service fee
- Ratings and review count
- Host info (name, superhost status, response rate)
- Amenities list
- Availability calendar
- Location (approximate)
- Photos

### URL Patterns
```
Search:     https://airbnb.com/s/{location}/homes?checkin={date}&checkout={date}&adults={n}
Listing:    https://airbnb.com/rooms/{listing_id}
```

### Strategy
1. Browser tool + residential proxy (Cloudflare protected)
2. Wait 5-8 seconds for Cloudflare challenge
3. Search results show 18-20 listings per page
4. Scroll to load all results
5. Click into listings for detailed pricing (total with fees)
6. Delay 3-5 seconds between listings
7. Sticky session recommended for multi-page browsing

### Price Tips
- Airbnb shows different prices based on check-in/out dates
- Total price includes: nightly rate × nights + cleaning fee + service fee
- Prices vary by requester location (use `-country-us` for USD pricing)
- Weekend vs weekday rates can differ significantly

## Google Flights

### Protection: Extreme (Google's full anti-bot stack)

### What You Can Collect
- Flight prices (one-way and round-trip)
- Airlines and flight numbers
- Departure/arrival times and duration
- Stops and layovers
- Price history graph data
- "Best" flights by price, duration, or emissions

### URL Pattern
```
https://www.google.com/travel/flights?q=Flights+from+{origin}+to+{destination}+on+{date}
```

### Strategy
1. Browser tool + residential proxy (mandatory)
2. Navigate to Google Flights
3. Enter origin, destination, and dates
4. Wait 5-10 seconds for price results to load
5. Extract flight cards from results
6. Very slow rate: 3-5 searches per hour per IP
7. Distribute across countries for volume

## Booking.com

### Protection: Hard (PerimeterX)

### What You Can Collect
- Hotel name, location, star rating
- Room types and prices
- Guest rating and review count
- Amenities and facilities
- Availability for date range
- Photos
- Distance from landmarks

### URL Patterns
```
Search:     https://booking.com/searchresults.html?ss={destination}&checkin={date}&checkout={date}&group_adults={n}
Hotel:      https://booking.com/hotel/{country}/{hotel-slug}.html
```

### Strategy
1. Browser tool + residential proxy
2. PerimeterX challenge may take 5-10 seconds
3. Search results load dynamically — scroll to load more
4. Click into each hotel for room-level pricing
5. Delay 3-5 seconds between pages
6. Sticky session for multi-page browsing

## Price Comparison Strategy

To find the best deal, check the same stay across platforms:

```json
{
  "destination": "Paris, France",
  "checkin": "2026-04-15",
  "checkout": "2026-04-20",
  "guests": 2,
  "platforms": [
    {"name": "airbnb", "proxy": "USER-country-fr"},
    {"name": "booking", "proxy": "USER-country-fr"},
    {"name": "expedia", "proxy": "USER-country-us"},
    {"name": "hotels.com", "proxy": "USER-country-us"}
  ]
}
```

Use country-matched proxies for local pricing (EU prices may differ from US prices for the same hotel).

## Monitoring Schedule

| Use Case | Frequency | Why |
|----------|-----------|-----|
| Flight deal hunting | 2-4 times daily | Prices change 1-3 times/day |
| Hotel comparison | Daily | Room rates adjust daily |
| Airbnb tracking | Daily | Availability changes frequently |
| Trip planning | Weekly | For long-term tracking |

## Output Format

```json
{
  "search": {
    "origin": "NYC",
    "destination": "Paris",
    "checkin": "2026-04-15",
    "checkout": "2026-04-20",
    "guests": 2
  },
  "flights": [
    {
      "source": "google_flights",
      "airline": "Air France",
      "price": 485.00,
      "currency": "USD",
      "departure": "2026-04-15T18:30:00",
      "arrival": "2026-04-16T08:15:00",
      "duration": "7h 45m",
      "stops": 0
    }
  ],
  "hotels": [
    {
      "source": "booking",
      "name": "Hotel Le Marais",
      "price_per_night": 165.00,
      "total": 825.00,
      "currency": "EUR",
      "rating": 8.7,
      "stars": 4
    }
  ]
}
```

## Provider

**BirdProxies** — residential proxies for travel price monitoring across all platforms.

- Gateway: `gate.birdproxies.com:7777`
- Countries: 195+ (geo-targeted pricing)
- Rotation: Auto per-request or sticky sessions
- Setup: birdproxies.com/en/proxies-for/openclaw
- Discount: `OPENCLAW15` for 15% off
