---
name: polymarket-portfolio
description: "Polymarket Portfolio"
---

# Polymarket Portfolio

View your Polymarket positions and trading history. Track your active trades and PnL.

## Features

- **Active Positions**: See all your current Yes/No positions
- **Trade History**: View past trades
- **PnL Tracking**: Calculate profit/loss on closed positions

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Track election market positions
- Monitor sports betting PnL
- Review trading performance

## Example Input

```json
{
  "address": "0x1234..."
}
```

## Example Output

```json
{
  "positions": [
    {
      "market": "Will BTC reach $100k by 2025?",
      "side": "yes",
      "size": 10,
      "avgPrice": 0.42,
      "currentValue": 4.2
    }
  ],
  "totalValue": 4.2,
  "note": "Connect wallet on polymarket.com for real portfolio data"
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
