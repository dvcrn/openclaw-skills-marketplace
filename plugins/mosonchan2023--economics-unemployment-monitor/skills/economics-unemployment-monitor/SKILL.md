---
name: economics-unemployment-monitor
description: "Economics Unemployment Monitor"
---

# Economics Unemployment Monitor

Monitors unemployment rates, labor force participation, and job creation data to assess the health of the labor market.

## Features

- **Unemployment Rate**: Current and historical data
- **Participation Rate**: Percentage of the population in the labor force
- **NFP/Job Reports**: Track monthly job gains or losses

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Assessing labor market conditions
- Predicting economic cycles
- Informing policy and recruitment strategies

## Example Input

```json
{
  "country": "Germany"
}
```

## Example Output

```json
{
  "success": true,
  "country": "Germany",
  "unemployment_rate": "3.2%",
  "labor_participation": "60.5%",
  "message": "Unemployment data fetched for Germany."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
