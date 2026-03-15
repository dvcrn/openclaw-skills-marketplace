---
name: news-api-aggregator
description: "Aggregate news from multiple sources into a unified API. Each call charges 0.001 USDT via SkillPay."
---

# News API Aggregator

## 功能

- 聚合多个新闻源的数据
- 统一格式输出
- 支持关键词搜索
- 过滤和排序选项

## 使用方法

```json
{
  "query": "Bitcoin",
  "sources": ["reuters", "bloomberg", "coindesk"],
  "limit": 10
}
```

## 输出

```json
{
  "success": true,
  "count": 10,
  "articles": [
    {"title": "...", "source": "reuters", "url": "...", "publishedAt": "..."}
  ]
}
```

## 定价

每次调用: 0.001 USDT
