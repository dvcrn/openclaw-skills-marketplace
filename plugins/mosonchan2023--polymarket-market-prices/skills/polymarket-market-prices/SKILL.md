---
name: polymarket-market-prices
description: "Polymarket Market Prices"
---

# Polymarket Market Prices

Get real-time prices for any Polymarket prediction market. Returns current probabilities, volume, and market details.

## Features

- **Real-time Prices**: Get current Yes/No probabilities for any market
- **Market Details**: Volume, liquidity, end date, and market description
- **Multi-market Support**: Query multiple markets at once
- **Search**: Find markets by keyword

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Check election odds (Trump vs Biden)
- Sports betting probabilities
- Crypto market predictions
- News event likelihoods

## Example Input

```json
{
  "question": "Will BTC reach $100k by 2025?"
}
```

## Example Output

```json
{
  "question": "Will BTC reach $100k by 2025?",
  "yesPrice": 0.42,
  "noPrice": 0.58,
  "volume": "1.2M",
  "liquidity": "850K",
  "endDate": "2025-12-31",
  "marketUrl": "https://polymarket.com/market/btc-100k-2025"
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
