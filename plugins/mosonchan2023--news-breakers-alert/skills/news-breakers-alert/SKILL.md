---
name: news-breakers-alert
description: "Get instant alerts for breaking news and emergency updates. Each call charges 0.001 USDT via SkillPay."
---

# News Breakers Alert

## 功能

- 即时推送突发新闻
- 紧急事件提醒
- 重大新闻推送
- 自定义关键词监控

## 使用方法

```json
{
  "action": "subscribe",
  "keywords": ["earthquake", "election", "stock market crash"],
  "priority": "high"
}
```

## 输出

```json
{
  "success": true,
  "alert_id": "alert_xxx",
  "status": "active",
  "keywords": [...]
}
```

## 定价

每次调用: 0.001 USDT
