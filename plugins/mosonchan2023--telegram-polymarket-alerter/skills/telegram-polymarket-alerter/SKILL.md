---
name: telegram-polymarket-alerter
description: "Telegram Polymarket Alerter"
---

# Telegram Polymarket Alerter

Sends real-time Telegram alerts when specific price or probability thresholds are met on Polymarket markets.

## Features

- **Price Thresholds**: Get alerted when a "Yes" price hits a target
- **Volume Alerts**: Get alerted for unusual market volume
- **Custom Notifications**: Configure Telegram messages for specific events

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Monitoring election odds changes
- Tracking sports betting movements
- Alerting on news-driven price spikes

## Example Input

```json
{
  "market": "Will BTC reach $100k by 2025?",
  "threshold": 0.5,
  "telegram_chat_id": "123456789"
}
```

## Example Output

```json
{
  "success": true,
  "alert_status": "ACTIVE",
  "message": "Alert set for 'Will BTC reach $100k by 2025?' at threshold 0.5."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
