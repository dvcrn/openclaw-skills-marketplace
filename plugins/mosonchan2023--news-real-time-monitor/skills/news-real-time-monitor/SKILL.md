---
name: news-real-time-monitor
description: "Monitor news in real-time with live updates and streaming. Each call charges 0.001 USDT via SkillPay."
---

# News Real-Time Monitor

## 功能

- 实时新闻监控
- 流式更新
- 多主题同时监控
- 即时推送通知

## 使用方法

```json
{
  "topics": ["Bitcoin", "AI", "Fed"],
  "mode": "stream",
  "duration": 60
}
```

## 输出

```json
{
  "success": true,
  "stream_url": "wss://...",
  "topics": [...],
  "status": "connected"
}
```

## 定价

每次调用: 0.001 USDT
