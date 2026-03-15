---
name: kmb-bus-arrival
description: "Retrieve real-time KMB bus arrival information (route, stop, ETA) using the official Data Hub API. Provides up-to-date next bus times for any KMB route and stop."
---

# Implementation Notes for Jeffery

## API Endpoints (Base URL: https://data.etabus.gov.hk)

- Route List: `/v1/transport/kmb/route/`
- Route Directions: `/v1/transport/kmb/route/{route}` (returns route details including bound/direction)
- Route‑Stop: `/v1/transport/kmb/route-stop/{route}/{direction}/{service_type}` (service_type=1 normally)
- Stop List: `/v1/transport/kmb/stop` (all stops) or `/v1/transport/kmb/stop?name={name}` to filter
- Route ETA: `/v1/transport/kmb/route-eta/{route}/{service_type}`
- Stop ETA: `/v1/transport/kmb/stop-eta/{stop}/{service_type}`

## Script: kmb_bus.py

Place this Python script in the same directory as this SKILL.md. It will be invoked with subcommands as defined above.

### Behavior

- **getRouteDirection {route}**
  - Fetch `/v1/transport/kmb/route/{route}` (or route list) to determine available directions.
  - Return JSON: `{ "route": "...", "directions": [{ "bound": "O", "name_tc": "往荃灣", "name_en": "Outbound" }, ...] }`

- **getRouteInfo {route} {direction}**
  - Fetch `/v1/transport/kmb/route-stop/{route}/{direction}/1`.
  - For each entry in `data`, extract `seq`, `stop`, `name_tc`, `name_en`.
  - Return JSON list of stops in order.

- **getBusStopID {name}**
  - Fetch `/v1/transport/kmb/stop?name={name}` (simple substring match; the API supports name filtering? Actually the endpoint is `/v1/transport/kmb/stop` which returns all stops; client can filter locally. Better: fetch full stop list once and cache, then filter by name_tc or name_en containing the query. For simplicity, fetch `/v1/transport/kmb/stop` and filter locally by name.
  - Return JSON: `[ { "stop": "ST871", "name_en": "YU CHUI COURT BUS TERMINUS", "name_tc": "愉翠苑巴士總站" }, ... ]`

- **getNextArrivals {route} {direction} {stopId}**
  - Step 1: Fetch route‑stop for the route/direction to find the `seq` corresponding to `stopId`.
  - Step 2: Fetch route‑eta: `/v1/transport/kmb/route-eta/{route}/1`. The response is a list of ETA objects (or an object with `data` array). Each has `dir`, `seq`, `eta`, `eta_seq`, `dest_tc`, `rmk_tc`, etc.
  - Step 3: Filter items where `dir==direction` and `seq==stop_seq`.
  - Step 4: Sort by `eta_seq` (bus order) and take the first 3.
  - Step 5: Format each ETA as `HH:MM HKT` using `datetime.fromisoformat`.
  - Return JSON: `{ "stopId": "...", "stopName": "...", "direction": "...", "arrivals": [ "17:35 HKT", "17:47 HKT", "18:00 HKT" ] }`
  - If no arrivals, return `"No active ETAs"` with explanation.

### Error Handling
- If any API returns non-200 or empty data, return a clear error message in JSON under `error`.
- Network timeouts should be caught and reported.

### Caching
- Cache the full stop list for ~1 hour to avoid repeated downloads for name searches.
- Cache route‑stop mappings for the same route/direction for 5 minutes.

## Testing
Test the script manually before enabling:
- `python3 kmb_bus.py getRouteDirection 182`
- `python3 kmb_bus.py getRouteInfo 182 outbound` (should include seq for ST871 if it’s on that route)
- `python3 kmb_bus.py getBusStopID "愉翠苑巴士總站"`
- `python3 kmb_bus.py getNextArrivals 182 outbound ST871`

## Integration
Ensure the `command` fields in the tool definitions point to `python3 kmb_bus.py <subcommand> ...` with proper placeholders. The skill directory must contain this `kmb_bus.py` file.

## Notes
- The KMB Data Hub may return no ETAs outside operating hours (approx 06:00–23:00). Handle gracefully.
- Some stops have multiple IDs; prefer the one that appears in the route‑stop list.
