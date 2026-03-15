---
name: news-alert-tracker
description: "Track breaking news and set alerts for specific keywords or topics. Each call charges 0.001 USDT via SkillPay."
---

# News Alert Tracker

## 功能

- 追踪特定关键词的新闻
- 设置实时提醒
- 支持 Telegram 通知
- 监控多个数据源

## 使用方法

```json
{
  "action": "add",
  "keywords": ["Bitcoin", "Fed", "Ethereum"],
  "notify": true
}
```

## 输出

```json
{
  "success": true,
  "alert_id": "alert_123",
  "keywords": ["Bitcoin", "Fed", "Ethereum"],
  "status": "active"
}
```

## 定价

每次调用: 0.001 USDT
