---
name: bark-push
description: "Send push notifications to iOS devices via Bark. Use when you need to send a push notification to user's iPhone. Triggered by phrases like \"send a notification\", \"push to phone\", \"bark notify\", or when explicitly asked to send a push."
---

# Bark Push Notification

Send push notifications to iOS via Bark API.

## Setup

Bark API endpoint: `https://api.day.app/{device_key}`

Device key can be:
1. Set via environment variable: `BARK_KEY`
2. Provided in each request

## Sending Notifications

### Simple Push (GET)
```bash
curl "https://api.day.app/$BARK_KEY/标题/内容"
```

### With Parameters (GET)
```bash
curl "https://api.day.app/$BARK_KEY/标题/内容?badge=1&sound=minuet"
```

### JSON Push (POST)
```bash
curl -X POST "https://api.day.app/$BARK_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"title": "标题", "body": "内容", "badge": 1}'
```

## Parameters

| 参数 | 说明 |
|------|------|
| title | 推送标题 |
| body | 推送内容 |
| subtitle | 副标题 |
| badge | 角标数字 |
| sound | 铃声名称 |
| image | 图片URL |
| url | 点击跳转URL |
| group | 分组 |
| level | 中断级别 (critical/active/timeSensitive/passive) |

## Common Sounds
- default
- minut
- alarm
- bird
- bell
- cha_ching
- doorbell
- droplet
- horn
- light
- mail
- rimba
- siren
- spinebreak
- spring
- streak
- sword
- tip
