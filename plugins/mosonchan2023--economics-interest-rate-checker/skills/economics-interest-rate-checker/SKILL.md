---
name: economics-interest-rate-checker
description: "Economics Interest Rate Checker"
---

# Economics Interest Rate Checker

Provides the latest interest rate decisions and targets from major central banks (e.g., Fed, ECB, BoJ, BoE).

## Features

- **Central Bank Rates**: Real-time interest rate levels
- **Meeting Calendars**: Stay informed on upcoming policy decisions
- **Historical Decisions**: View past rate changes and trends

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Forecasting monetary policy shifts
- Managing interest rate risk
- Valuing financial instruments

## Example Input

```json
{
  "bank": "Federal Reserve"
}
```

## Example Output

```json
{
  "success": true,
  "bank": "Federal Reserve",
  "current_rate": "5.25% - 5.50%",
  "last_meeting": "2024-03-20",
  "message": "Latest Fed interest rate data retrieved."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
