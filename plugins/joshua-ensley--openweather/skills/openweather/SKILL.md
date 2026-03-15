---
name: openweather
description: "Get current weather, hourly forecasts, and 8-day daily forecasts for any location worldwide using OpenWeather One Call API 3.0. Use when the user asks about weather, temperature, rain, snow, forecast, or conditions for any city or location."
---

# OpenWeather Skill

OpenWeather One Call API 3.0 via a small Python CLI (stdlib only).

## Commands

City is optional if `OPENWEATHER_DEFAULT_LOCATION` is set.

python3 {skillDir}/scripts/weather.py current [city]
python3 {skillDir}/scripts/weather.py forecast [city] --days 5
python3 {skillDir}/scripts/weather.py hourly [city] --hours 12

## Rules

- If no location is mentioned, use `OPENWEATHER_DEFAULT_LOCATION` when configured; otherwise ask the user for a location.
- Do not make more than 2 API calls per request (1 geocode + 1 onecall).
- If the API returns 401, tell the user the key may be invalid or One Call 3.0 may not be enabled for that key.
- Do not claim to use curl; this skill uses Python urllib.
