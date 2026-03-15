---
name: geocode
description: "Convert place names or addresses to latitude/longitude, or coordinates to a human-readable place, via Nominatim (OpenStreetMap) using curl. Use for forward geocoding, reverse geocoding, location disambiguation, and JSON geocoding lookups. Triggers on geocode, reverse geocode, lat/lng, latitude/longitude, address to coordinates, coordinates to address, 地址转经纬度, 经纬度转地址, 坐标查地点."
homepage: https://nominatim.org/release-docs/develop/api/Overview/
---

# geocode

Resolve place names and addresses to coordinates, or coordinates back to a place name.

Provider: public Nominatim (OpenStreetMap) API via `curl`.

## Quick Start

```bash
{baseDir}/scripts/geocode.sh search "1600 Amphitheatre Parkway, Mountain View, CA" --lang en --limit 3
{baseDir}/scripts/geocode.sh reverse 37.819929 -122.478255 --lang en
{baseDir}/scripts/geocode.sh search "上海迪士尼乐园" --lang zh-CN
```

## When to Use

- "Geocode this address"
- "What are the coordinates for this place?"
- "Reverse geocode 37.819929, -122.478255"
- "Address to lat/lng"
- "Coordinates to address"
- "把这个地址转成经纬度"
- "根据经纬度查地点"

## When NOT to Use

- Rich place details, reviews, opening hours, or POI metadata: use `goplaces`
- Routing, distance matrices, or navigation
- High-volume batch geocoding
- Legal/property-grade address validation

## Query Rules

- If the place is ambiguous, add city, state/province, or country before retrying.
- For reverse geocoding, pass decimal latitude and longitude.
- Prefer the user's language in `accept-language` when known.
- Return both coordinates and the normalized display name when useful.

## Config

- `GEOCODE_BASE_URL` optionally points at another Nominatim-compatible endpoint for testing or self-hosting.
- `GEOCODE_USER_AGENT` overrides the default identifying `User-Agent`.

## Public API Limits

- Use Nominatim only for low-frequency, interactive lookups.
- Send an identifying `User-Agent`; do not use default curl UA for repeated calls.
- Do not loop, bulk geocode, or aggressively retry against the public endpoint.
- If the task needs heavy usage, switch to another provider or a self-hosted service.

## Commands

### Scripted Forward Geocode

```bash
{baseDir}/scripts/geocode.sh search "1600 Amphitheatre Parkway, Mountain View, CA" --lang en --limit 5
```

```bash
{baseDir}/scripts/geocode.sh search "Paris" --lang fr --countrycodes fr --limit 3
```

### Scripted Reverse Geocode

```bash
{baseDir}/scripts/geocode.sh reverse 37.819929 -122.478255 --lang en
```

```bash
{baseDir}/scripts/geocode.sh reverse 31.14337 121.65707 --lang zh-CN --zoom 18
```

### Raw Forward Geocode

```bash
curl --get 'https://nominatim.openstreetmap.org/search' \
  -A 'openclaw-geocode-skill/1.0 (interactive use)' \
  --data-urlencode 'q=1600 Amphitheatre Parkway, Mountain View, CA' \
  --data 'format=jsonv2' \
  --data 'limit=5' \
  --data-urlencode 'accept-language=en'
```

### Raw Reverse Geocode

```bash
curl --get 'https://nominatim.openstreetmap.org/reverse' \
  -A 'openclaw-geocode-skill/1.0 (interactive use)' \
  --data 'lat=37.819929' \
  --data 'lon=-122.478255' \
  --data 'format=jsonv2' \
  --data-urlencode 'accept-language=en'
```

### Raw Chinese Output

```bash
curl --get 'https://nominatim.openstreetmap.org/search' \
  -A 'openclaw-geocode-skill/1.0 (interactive use)' \
  --data-urlencode 'q=上海迪士尼乐园' \
  --data 'format=jsonv2' \
  --data 'limit=5' \
  --data-urlencode 'accept-language=zh-CN'
```

## What to Return

- Best-match place name
- Latitude and longitude
- Country/region if ambiguity matters
- A short ambiguity note when multiple plausible matches exist

## Notes

- The bundled script prints raw JSON to stdout and keeps dependencies to `curl` only.
- `search` returns an array; prefer the top result only when the query is clearly specific.
- `reverse` returns one best match, not a ranked list.
- Coordinates are strings in JSON; parse carefully before numeric comparisons.
- If the user actually wants a business/place profile, switch to `goplaces` instead of stretching geocoding output beyond its purpose.
