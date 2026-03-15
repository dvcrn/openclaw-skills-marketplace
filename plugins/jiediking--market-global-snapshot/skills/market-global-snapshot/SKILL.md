---
name: market-global-snapshot
description: "Generate a structured global market snapshot report including major stock indices and commodities. Use when user asks for market data, stock market report, daily market summary, or needs current prices and changes for indices (S&P 500, Dow Jones, NASDAQ, SSE Composite, Shenzhen, STAR Market, Nikkei 225, Sensex) and commodities (Gold, Silver, Crude Oil, Copper)."
---

# Market Report Skill

Generate a structured global market snapshot report with stock indices and commodities data.

## Fallback Order

1. **Yahoo Finance** (Primary) - Fast, comprehensive
2. **Trading Economics** (Fallback for most indices)
3. **Sina Finance** (Fallback for STAR Market Composite)

If Yahoo Finance fails (rate limit, error, no data), use Trading Economics as fallback.
For STAR Market Composite specifically, use Sina Finance as fallback.

## Primary: Yahoo Finance

### Ticker Symbols

Use these exact ticker symbols:
- S&P 500: `^GSPC`
- Dow Jones: `^DJI`
- NASDAQ: `^IXIC`
- SSE Composite: `000001.SS`
- Shenzhen Component: `399001.SZ`
- STAR Market: `000680.SS` (NOT 000688.SS)
- Nikkei 225: `^N225`
- Sensex: `^BSESN`
- Gold: `GC=F`
- Silver: `SI=F`
- Crude Oil: `CL=F`
- Copper: `HG=F`

### Query Method

Use curl to query Yahoo Finance API:

```bash
curl -s "https://query1.finance.yahoo.com/v8/finance/chart/{TICKER}?interval=1d&range=5d" -H "User-Agent: Mozilla/5.0"
```

## Fallback: Trading Economics

If Yahoo Finance fails, use Trading Economics web fetch:

### Indices URLs

- US (S&P 500): `https://tradingeconomics.com/united-states/stock-market`
- China (SSE): `https://tradingeconomics.com/china/stock-market`
- China (Shenzhen): `https://tradingeconomics.com/china/stock-market` (same page, different data)
- Japan (Nikkei): `https://tradingeconomics.com/japan/stock-market`
- India (Sensex): `https://tradingeconomics.com/india/stock-market`

### Extract Data from Trading Economics

From the page content, extract:
- **Actual** value: Current price (e.g., `6762.88`)
- **Previous** value: Previous close (e.g., `6830.71`)

Calculate:
- Change = Actual - Previous
- Percent = (Change / Previous) * 100

Example from US page:
```
Actual: 6762.88
Previous: 6830.71
Change: 6762.88 - 6830.71 = -67.83
Percent: -67.83 / 6830.71 * 100 = -0.99%
```

## Fallback: Sina Finance (STAR Market Composite Only)

If Yahoo Finance fails for STAR Market Composite (000680.SS), use Sina Finance:

### Query Method

```bash
curl -s "https://hq.sinajs.cn/list=sh000680" -H "Referer: https://finance.sina.com.cn" | iconv -f GB2312 -t UTF-8
```

### Response Format

```
var hq_str_sh000680="科创综指,open,prev_close,low,high,close,...
```

### Extract Data

Parse the response to extract:
- **Name:** 科创综指 (STAR Market Composite)
- **Current:** Field 6 (close price)
- **Previous:** Field 3 (previous close)

Example:
```
科创综指,1771.6386,1774.0261,1744.2182,1782.4838,1744.0835,...
                                         ↑            ↑
                                     previous      current
Change: 1744.0835 - 1774.0261 = -29.94
Percent: -29.94 / 1774.0261 * 100 = -1.69%
```

## Critical: Calculating Daily Change (Yahoo Finance)

**NEVER use chartPreviousClose** - it's often incorrect for Asian markets.

For Chinese indices (SSE, Shenzhen, STAR Market), always:
1. Query with `range=5d` to get multiple days
2. Find the LAST close value in the `indicators.quote[0].close` array - this is today's close
3. Find the SECOND TO LAST close value - this is previous trading day's close
4. Calculate: Today's Close - Previous Close = Change

Example for SSE:
```
close array: [4182.59, 4122.68, 4082.47, 4108.57, 4124.19]
                                                      ↑ today (last)
                                                  ↑ previous (second to last)
Change: 4124.19 - 4108.57 = +15.62
```

## Output Format

Generate at this exact format with timestamps:

```
Latest snapshot from the `market-global-snapshot` skill, generated at `UTC timestamp` and `China time`.

📊 Stock indices:

- 🇺🇸 S&P 500: `price` 📈/📉 `change` (`percent`)
- 🇺🇸 Dow Jones Industrial Average: `price` 📈/📉 `change` (`percent`)
- 🇺🇸 NASDAQ Composite: `price` 📈/📉 `change` (`percent`)

- 🇨🇳 SSE Composite: `price` 📈/📉 `change` (`percent`)
- 🇨🇳 Shenzhen Component Index: `price` 📈/📉 `change` (`percent`)
- 🇨🇳 STAR Market Composite: `price` 📈/📉 `change` (`percent`)

- 🇯🇵 Nikkei 225: `price` 📈/📉 `change` (`percent`)

- 🇮🇳 Sensex: `price` 📈/📉 `change` (`percent`)

🛢️ Commodities:

- 🟡 Gold: `price USD / troy oz` 📈/📉 `change` (`percent`)
- ⚪ Silver: `price USD / troy oz` 📈/📉 `change` (`percent`)
- 🛢️ Crude Oil: `price USD / barrel` 📈/📉 `change` (`percent`)
- 🟠 Copper: `price USD / lb` 📈/📉 `change` (`percent`)
```

## Error Handling

If Yahoo Finance, Trading Economics, AND Sina all fail:
1. Return partial data with available indices
2. Mark unavailable data as "N/A"
3. Include error message at bottom: "⚠️ Some data unavailable due to API errors"

## Historical Data

To get previous day's data instead of today:
- Use second-to-last close value in the array (not today's)
- This is the default behavior when asking for "yesterday"

Example:
```
close array: [4124.19, 4108.57, 4082.47, 4122.68, 4182.59]
                                        ↑            ↑
                                   yesterday      today
```

## Formatting Rules

- Use two decimal places for all numbers
- Wrap prices in backticks
- Use 📈 for positive, 📉 for negative
- Include + or - sign for changes
- Use percentage in parentheses with % sign
