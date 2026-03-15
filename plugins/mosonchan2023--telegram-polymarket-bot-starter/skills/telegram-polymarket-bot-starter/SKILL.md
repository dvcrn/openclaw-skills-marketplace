---
name: telegram-polymarket-bot-starter
description: "Telegram Polymarket Bot Starter"
---

# Telegram Polymarket Bot Starter

Assists in setting up a custom Telegram bot for interactive Polymarket queries, price checks, and position tracking.

## Features

- **Bot Setup Assistance**: Guide through BotFather registration and API key configuration
- **Initial Command Setup**: Configure basic commands (/price, /trending, /portfolio)
- **Deployment Templates**: Get deployment scripts for various platforms

## Pricing

- **Price**: 0.001 USDT per API call
- **Payment**: Integrated via SkillPay.me

## Use Cases

- Building community bots
- Creating personal trading assistants
- Automating market research

## Example Input

```json
{
  "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
  "features": ["price_check", "trending_alerts"]
}
```

## Example Output

```json
{
  "success": true,
  "config": {
    "bot_name": "MyPolymarketBot",
    "commands": ["/price", "/trending"],
    "webhook_url": "..."
  },
  "message": "Bot configuration generated successfully."
}
```

## Integration

This skill is integrated with SkillPay.me for automatic micropayments. Each call costs 0.001 USDT.
