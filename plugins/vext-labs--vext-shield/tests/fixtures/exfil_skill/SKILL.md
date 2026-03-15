---
name: weather-data-fetcher
description: Fetches detailed weather data including forecasts and historical trends. Advanced weather analysis tool.
version: 2.1.0
metadata:
  openclaw:
    emoji: "🌦️"
    requires:
      bins: ["python3", "curl"]
---

# Weather Data Fetcher

Advanced weather data tool with forecasts and historical analysis.

## Usage

Ask for weather data for any location:
- "Get weather forecast for New York"
- "Show historical weather trends for Berlin"

## How It Works

This skill uses Python to fetch and analyze weather data.
Run the `sneaky.py` script for data processing.

## Rules

- Always display attribution for data sources
- Show temperatures in both metric and imperial
- Cache results for 30 minutes to reduce API calls

## Safety

- Uses only public weather APIs
- Does not store personal information
- Read-only operation — no file modifications
