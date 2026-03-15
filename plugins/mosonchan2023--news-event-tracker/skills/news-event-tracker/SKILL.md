---
name: news-event-tracker
description: "Track upcoming news events, earnings, conferences, and announcements. Each call charges 0.001 USDT via SkillPay."
---

# News Event Tracker

## 功能

- 追踪即将发布的新闻事件
- 财报日期追踪
- 会议和演讲日程
- 宏观经济事件日历

## 使用方法

```json
{
  "category": "earnings",
  "date_from": "2026-03-01",
  "date_to": "2026-03-31"
}
```

## 输出

```json
{
  "success": true,
  "events": [
    {"date": "2026-03-15", "company": "AAPL", "event": "Q1 Earnings", "time": "After Close"},
    {"date": "2026-03-20", "company": "MSFT", "event": "Build Conference", "time": "10:00 AM"}
  ]
}
```

## 定价

每次调用: 0.001 USDT
