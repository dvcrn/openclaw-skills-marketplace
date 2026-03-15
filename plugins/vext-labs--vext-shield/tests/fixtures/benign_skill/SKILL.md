---
name: weather-lookup
description: Look up current weather conditions for any city using the Open-Meteo API. No API key required.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🌤️"
    requires:
      bins: ["curl", "python3"]
---

# Weather Lookup

Get current weather conditions for any city worldwide.

## Usage

Tell me the weather in any city and I'll look it up for you.

Examples:
- "What's the weather in San Francisco?"
- "Check the temperature in Tokyo"
- "Is it raining in London?"

## How It Works

1. Uses the Open-Meteo geocoding API to resolve city names to coordinates
2. Fetches current weather from `api.open-meteo.com`
3. Returns temperature, humidity, wind speed, and conditions

## Rules

- Only use the Open-Meteo API (no other weather APIs)
- Always show temperature in both Celsius and Fahrenheit
- Do not cache results — always fetch fresh data
- Do not store any user data or location history

## Safety

- This skill only makes GET requests to api.open-meteo.com
- No API keys are required or used
- No user data is collected or transmitted
- No files are read or written outside of displaying results
