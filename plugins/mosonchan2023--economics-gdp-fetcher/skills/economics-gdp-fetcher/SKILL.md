---
name: economics-gdp-fetcher
description: "Economics Gdp Fetcher"
---

# Economics GDP Fetcher

Fetches current and historical Gross Domestic Product (GDP) data for various countries and regions, providing insights into economic growth and output.

## Features

- **Country GDP**: Real-time GDP data for over 200 countries
- **GDP Growth**: Calculate annual and quarterly growth rates
- **Historical Trends**: View GDP performance over multiple years

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Economic research and analysis
- Macroeconomic forecasting
- Investment decision support

## Example Input

```json
{
  "country": "USA",
  "year": 2023
}
```

## Example Output

```json
{
  "success": true,
  "country": "USA",
  "gdp": "27.36 trillion USD",
  "growth_rate": "2.5%",
  "message": "GDP data fetched successfully."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
