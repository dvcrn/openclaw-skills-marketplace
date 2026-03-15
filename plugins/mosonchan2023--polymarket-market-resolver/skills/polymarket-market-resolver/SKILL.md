---
name: polymarket-market-resolver
description: "Polymarket Market Resolver"
---

# Polymarket Market Resolver

Resolve a Polymarket prediction market. Returns the outcome (Yes/No) and confirms resolution.

## Features

- **Resolve Market**: Submit resolution for any closed market
- **Check Status**: Verify if a market is resolved
- **Outcome Verification**: Confirm the winning outcome

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Resolve election markets after results
- Resolve sports markets after games
- Resolve crypto markets after events

## Example Input

```json
{
  "question": "Will BTC reach $100k by 2025?",
  "outcome": "yes"
}
```

## Example Output

```json
{
  "success": true,
  "question": "Will BTC reach $100k by 2025?",
  "outcome": "yes",
  "resolvedAt": "2025-01-15T10:30:00Z"
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
