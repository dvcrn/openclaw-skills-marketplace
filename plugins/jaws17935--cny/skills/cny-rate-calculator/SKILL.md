---
name: cny-rate-calculator
description: "Auto-fetch Bank of Taiwan CNY exchange rates and calculate tiered pricing (base cost, 10K discount, 50K discount) using the Prairie Grasslands formula. Use when: (1) User needs current CNY exchange rate calculations, (2) Setting up automated CNY rate monitoring, (3) Calculating exchange rates with tiered discounts for business purposes. REQUIRES channel configuration to send output. Supports Telegram, Discord, Slack, Signal, WhatsApp, iMessage, IRC, Google Chat, and webhooks. Auto-detects OpenClaw system configuration."
---

# CNY Rate Calculator (大草原匯率計算器)

Automatically fetch Bank of Taiwan CNY exchange rates and calculate tiered pricing.

## ⚠️ Required Setup

**You MUST configure a channel before using this skill.**

This skill will **auto-detect** your OpenClaw system configuration if available. If auto-detection fails, you'll need to edit `config.json`.

## Auto-Detection

This skill will automatically detect your channel from:

1. **config.json** - Explicit configuration (highest priority)
2. **OpenClaw system config** - Your existing OpenClaw channel settings
3. **Environment variables** - Tokens and webhooks

If auto-detection succeeds, you'll see a message like:
```
✅ Auto-detected Telegram channel: 123456789
```

## Supported Channels

| Channel | Type | Target | Required Environment Variable |
|---------|------|--------|------------------------------|
| Telegram | `telegram` | Chat ID | `TELEGRAM_BOT_TOKEN` |
| Discord | `discord` | Webhook URL | None |
| Slack | `slack` | Webhook URL | None |
| Google Chat | `googlechat` | Webhook URL | None |
| Signal | `signal` | Phone/Group ID | `OPENCLAW_GATEWAY_TOKEN` (recommended) |
| WhatsApp | `whatsapp` | Phone number | `OPENCLAW_GATEWAY_TOKEN` (required) |
| iMessage | `imessage` | Contact name/number | `OPENCLAW_GATEWAY_TOKEN` (recommended) or macOS |
| IRC | `irc` | Channel name | `OPENCLAW_GATEWAY_TOKEN` (required) |
| Webhook | `webhook` | URL | None |
| Console | `console` | `null` | None |

## Quick Start

### Option 1: Auto-Detect (Recommended)

If you already have OpenClaw configured with Telegram or other channels, just run:

```bash
python scripts/cny_rate.py
```

The skill will automatically detect and use your existing configuration.

### Option 2: Manual Configuration

1. **Configure channel** in `config.json`
2. **Set environment variables** (if needed for your channel)
3. **Run**:
   ```bash
   python scripts/cny_rate.py
   ```

Or use `--setup` to see the full setup guide:
```bash
python scripts/cny_rate.py --setup
```

## What It Does

1. **Fetch Rates**: Gets live CNY exchange rates from Bank of Taiwan
2. **Calculate**: Applies the Prairie Grasslands formula:
   - Mid price = (Buy + Sell) / 2
   - Base cost = Mid + 0.05
   - 10K discount = Mid + 0.03
   - 50K discount = Mid + 0.015
3. **Send**: Outputs to configured channel

## Configuration Examples

### Telegram
```json
{
  "channel": {
    "type": "telegram",
    "target": "123456789"
  }
}
```
Environment: `TELEGRAM_BOT_TOKEN=your_bot_token`

### Discord
```json
{
  "channel": {
    "type": "discord",
    "target": "https://discord.com/api/webhooks/..."
  }
}
```

### Slack
```json
{
  "channel": {
    "type": "slack",
    "target": "https://hooks.slack.com/services/..."
  }
}
```

### Signal (via OpenClaw Gateway)
```json
{
  "channel": {
    "type": "signal",
    "target": "+886123456789"
  }
}
```
Environment: `OPENCLAW_GATEWAY_TOKEN=your_token`

### WhatsApp (via OpenClaw Gateway)
```json
{
  "channel": {
    "type": "whatsapp",
    "target": "+886123456789"
  }
}
```
Environment: `OPENCLAW_GATEWAY_TOKEN=your_token`

### iMessage (macOS)
```json
{
  "channel": {
    "type": "imessage",
    "target": "Contact Name"
  }
}
```
Requires macOS or OpenClaw Gateway with `OPENCLAW_GATEWAY_TOKEN`

### IRC (via OpenClaw Gateway)
```json
{
  "channel": {
    "type": "irc",
    "target": "#channel-name"
  }
}
```
Environment: `OPENCLAW_GATEWAY_TOKEN=your_token`

### Google Chat
```json
{
  "channel": {
    "type": "googlechat",
    "target": "https://chat.googleapis.com/v1/spaces/..."
  }
}
```

### Generic Webhook
```json
{
  "channel": {
    "type": "webhook",
    "target": "https://your-api.com/webhook"
  }
}
```

### Console Only
```json
{
  "channel": {
    "type": "console",
    "target": null
  }
}
```

## Environment Variables

| Variable | Required For | Description |
|----------|--------------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram | Your bot token from @BotFather |
| `DISCORD_WEBHOOK_URL` | Discord | Webhook URL (alternative to config.json) |
| `SLACK_WEBHOOK_URL` | Slack | Webhook URL (alternative to config.json) |
| `OPENCLAW_GATEWAY_URL` | Signal, WhatsApp, iMessage, IRC | OpenClaw gateway URL (default: http://127.0.0.1:18790) |
| `OPENCLAW_GATEWAY_TOKEN` | Signal, WhatsApp, iMessage, IRC | Your OpenClaw gateway token |

## Schedule (Cron)

**Windows Task Scheduler:**
- Program: `python`
- Arguments: `scripts/cny_rate.py`
- Schedule: Mon-Fri 9:00-16:00 hourly

**Linux/macOS Cron:**
```cron
# Every hour, Mon-Fri, 9AM-4PM
0 9-16 * * 1-5 cd /path/to/skill && python scripts/cny_rate.py
```

## Formula Details

| Tier | Delta | Label |
|------|-------|-------|
| Base cost | +0.05 | 基礎成本 |
| 10K discount | +0.03 | 滿萬優惠 |
| 50K discount | +0.015 | 五萬優惠 |

## Data Sources

- **Bank of Taiwan**: https://rate.bot.com.tw/xrt
- **Prairie Grasslands Calculator**: https://78lion.com/CNY.html

## Files

- `scripts/cny_rate.py` - Main calculator script
- `config.json` - Configuration (formula, channel settings)
- `scripts/run.bat` - Windows runner
- `scripts/run.sh` - Linux/macOS runner

## Troubleshooting

**"Channel configuration required" error**
- The skill couldn't auto-detect your channel
- Edit `config.json` and set a valid `channel.type` and `channel.target`
- Run `python scripts/cny_rate.py --setup` to see all options

**Auto-detection not working**
- Make sure your OpenClaw configuration is in standard locations:
  - `~/.openclaw/config.json`
  - `%APPDATA%/openclaw/config.json` (Windows)
  - `%LOCALAPPDATA%/openclaw/config.json` (Windows)
- Or set environment variables directly

**Telegram not working**
- Verify `TELEGRAM_BOT_TOKEN` is set
- Make sure the bot is added to the chat and has permission to send messages

**Signal/WhatsApp/iMessage/IRC not working**
- These require OpenClaw Gateway
- Set `OPENCLAW_GATEWAY_TOKEN` environment variable
- Verify your OpenClaw Gateway is running
