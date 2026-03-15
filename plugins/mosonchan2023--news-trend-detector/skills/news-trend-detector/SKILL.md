---
name: news-trend-detector
description: "Detect trending topics and emerging news trends in real-time. Each call charges 0.001 USDT via SkillPay."
---

# News Trend Detector

## 功能

- 实时检测热门话题
- 追踪新闻传播趋势
- 识别新兴话题
- 预测话题热度

## 使用方法

```json
{
  "timeframe": "24h",
  "category": "all",
  "limit": 10
}
```

## 输出

```json
{
  "success": true,
  "trends": [
    {"topic": "...", "volume": 15000, "velocity": "high", "sentiment": "positive"}
  ]
}
```

## 定价

每次调用: 0.001 USDT
