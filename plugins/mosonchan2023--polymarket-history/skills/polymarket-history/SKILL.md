---
name: polymarket-history
description: "Polymarket History"
---

# Polymarket History

Get historical price data and trading volume for Polymarket markets. Analyze trends and market movement.

## Features

- **Price History**: OHLCV data for any market
- **Volume History**: Trading volume over time
- **Market Analytics**: Price movement statistics

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Analyze election market trends
- Study price movement patterns
- Backtest trading strategies

## Example Input

```json
{
  "question": "Will BTC reach $100k by 2025?",
  "interval": "1d",
  "days": 30
}
```

## Example Output

```json
{
  "question": "Will BTC reach $100k by 2025?",
  "interval": "1d",
  "data": [
    {"date": "2025-01-01", "open": 0.35, "high": 0.38, "low": 0.34, "close": 0.37, "volume": 50000},
    {"date": "2025-01-02", "open": 0.37, "high": 0.42, "low": 0.36, "close": 0.42, "volume": 75000}
  ],
  "note": "Historical data simulation. Connect to Polymarket API for real data."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
