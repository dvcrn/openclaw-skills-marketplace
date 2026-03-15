---
name: economic-calendar-pro
description: "Run a local script to fetch economic calendar events for a date range. Defaults to 7 days inclusive from the query day. Uses TradingEconomics when TRADING_ECONOMICS_API_KEY is present and falls back to Yahoo Finance otherwise."
homepage: https://docs.tradingeconomics.com/economic_calendar/snapshot/
---

# Skill: Economic Calendar

## When to use
- The user wants the economic calendar for today, this week, or a custom date range.
- The user asks for upcoming macro events, scheduled releases, or high/medium/low impact events.
- The user wants a forward-looking list of calendar items before trading.

## When NOT to use
- The user wants broad market news and sentiment only -> use `market-news-brief`
- The user wants a stock price or company-specific quote -> use `stock-price-checker-pro`
- The user wants company fundamentals -> use `stock-fundamentals`

## Authentication

- Preferred: set `TRADING_ECONOMICS_API_KEY` to your TradingEconomics credential string
- Supported value format: `client:secret`
- Optional: copy `.env.example` to `.env` at the repo root and fill in `TRADING_ECONOMICS_API_KEY`
- Fallback: if no API key is present, the script uses Yahoo Finance's economic calendar endpoint
- Important: Yahoo fallback can omit importance and market-expectation fields, and country values are returned as short codes like `US`, `EU`, or `JP`

## Commands

### Get the default calendar window

```bash
uv run /root/.openclaw/workspace/skills/economic-calendar-pro/src/main.py
```

Defaults to 7 days inclusive from the query day.

### Get a custom calendar window

```bash
uv run /root/.openclaw/workspace/skills/economic-calendar-pro/src/main.py <START_DATE> <END_DATE>
```

Dates must use `YYYY-MM-DD`.

### Examples

```bash
# Default window: query day plus the next 6 days
uv run /root/.openclaw/workspace/skills/economic-calendar-pro/src/main.py

# Start from a specific day and use 7 days inclusive
uv run /root/.openclaw/workspace/skills/economic-calendar-pro/src/main.py 2026-03-10

# Explicit date range
uv run /root/.openclaw/workspace/skills/economic-calendar-pro/src/main.py 2026-03-10 2026-03-24
```

## Output

The command returns:
- Requested date range
- Auth source used (`TradingEconomics API` or `Yahoo Finance fallback`)
- Total event count and covered day count
- Events grouped by day
- For each event: UTC time, country, event name, and available actual / forecast / previous values

## Notes

- The script reads `TRADING_ECONOMICS_API_KEY` from the environment first.
- If no env var is set, it also checks a repo-root `.env` file before falling back to Yahoo Finance.
- Yahoo fallback is better than guest TradingEconomics for current/future windows, but it does not expose the same richness of metadata.
- Do NOT use the `economic-calendar-pro.sh` wrapper in normal skill execution - call `uv run src/main.py` directly as shown above.
- Do NOT use web search for this workflow - use the script so the output is date-filtered and formatted consistently.
