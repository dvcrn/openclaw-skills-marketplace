---
name: fly-flight
description: "Query China domestic flights from publicly accessible Tongcheng flight pages, without requiring an API key. Use when a user wants China domestic flight options, departure and arrival times, airport details, or public reference fares from open web pages rather than a private API."
---

# Fly Flight

Use the local Python script in this skill to query China domestic flights from publicly accessible Tongcheng flight pages. This version does not require an API key, but it depends on the current page structure of the public site and may break if that site changes.

Public source:

- `https://www.ly.com/flights/`

## Quick Start

Run a direct query:

```bash
python3 {baseDir}/scripts/domestic_flight_public_service.py search \
  --from 北京 --to 上海 --date 2026-03-20 --sort-by price --pretty
```

Round trip:

```bash
python3 {baseDir}/scripts/domestic_flight_public_service.py search \
  --from 北京 --to 上海 --date 2026-03-20 --return-date 2026-03-23 \
  --direct-only --sort-by price --pretty
```

Optional reusable local HTTP mode:

```bash
python3 {baseDir}/scripts/domestic_flight_public_service.py serve --port 8766
```

## Workflow

1. Resolve the user's origin and destination.
   Accept Chinese city names, airport names, or IATA codes.

2. Fetch the public Tongcheng route page.
   Extract the `window.__NUXT__` payload and read `state.book1.flightLists`.

3. Apply useful filters when the user asks.
   Support sorting by `price`, `departure`, `arrival`, or `duration`.
   Support `direct_only`.
   Support airport preference for departure and arrival airports.
   Support airline filtering by code or name.
   For round trips, run outbound and return lookups separately and present them as two legs.

4. Summarize the result.
   Mention airline, flight number, departure and arrival airport, departure and arrival time, duration, and `ticket_price`.
   Call the price `公开页面参考价` or `参考票价`, not a guaranteed bookable fare.

5. Handle failure as a website scraping problem.
   If parsing fails, tell the user the public source page likely changed.
   If the route is missing, say that no public flight result was found for that route/date.

## Output Rules

- Sort results by lowest `ticket_price` first.
- When the user asks for earliest departure or shortest duration, use the matching sort mode instead of price.
- Prefer up to 5 options unless the user asked for more.
- State the exact travel date in `YYYY-MM-DD`.
- Explain that public-page prices can differ from final checkout prices.
- For round trips, clearly separate `outbound` and `return` results.

## Resources

- Use [scripts/domestic_flight_public_service.py](./scripts/domestic_flight_public_service.py) for CLI and optional HTTP modes.
- Use [scripts/extract_tongcheng_state.js](./scripts/extract_tongcheng_state.js) to decode the public page payload.
- Use [assets/data/domestic_city_codes.json](./assets/data/domestic_city_codes.json) and [assets/data/airport_aliases.json](./assets/data/airport_aliases.json) for Chinese name resolution.
- Read [references/provider-public-web.md](./references/provider-public-web.md) for public-source notes and limitations.
