---
name: economics-inflation-tracker
description: "Economics Inflation Tracker"
---

# Economics Inflation Tracker

Tracks Consumer Price Index (CPI), Producer Price Index (PPI), and overall inflation rates across different economies to monitor purchasing power.

## Features

- **CPI/PPI Data**: Real-time updates on inflation indices
- **Core Inflation**: View inflation excluding volatile components (food, energy)
- **Forecasts**: Access projected inflation targets

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Monitoring cost of living
- Adjusting business pricing strategies
- Analyzing central bank policies

## Example Input

```json
{
  "region": "Eurozone",
  "index": "CPI"
}
```

## Example Output

```json
{
  "success": true,
  "region": "Eurozone",
  "index": "CPI",
  "rate": "2.4%",
  "message": "Inflation data updated for Eurozone."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
