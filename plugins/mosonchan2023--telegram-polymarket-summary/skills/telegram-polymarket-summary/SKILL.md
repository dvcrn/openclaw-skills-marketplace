---
name: telegram-polymarket-summary
description: "Telegram Polymarket Summary"
---

# Telegram Polymarket Summary

Sends a consolidated summary of trending and high-volume Polymarket prediction markets directly to your Telegram chat.

## Features

- **Daily/Weekly Recaps**: Get summaries of the most important market shifts
- **Trending Markets**: Identify markets with the most activity
- **Custom Focus**: Filter summaries by categories (e.g., Politics, Sports, Crypto)

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Staying updated on election trends
- Tracking sports betting sentiment
- Monitoring crypto market predictions

## Example Input

```json
{
  "telegram_chat_id": "123456789",
  "categories": ["Politics", "Crypto"]
}
```

## Example Output

```json
{
  "success": true,
  "summary_sent": true,
  "message": "Polymarket summary for Politics and Crypto categories sent to Telegram."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
