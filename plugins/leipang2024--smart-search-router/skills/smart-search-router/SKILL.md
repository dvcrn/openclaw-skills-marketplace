---
name: smart-search-router
description: "Smart Search Router"
---

# Smart Search Router Skill

智能搜索路由 - 根据查询复杂度自动选择 SearXNG 或 Gemini Search

## 使用方式

本技能提供 `smart_search` 工具，自动选择最佳搜索引擎。

## 配置

需要配置 SearXNG 和 Gemini API：

```json
{
  "smart-search-router": {
    "searxngBaseUrl": "YOUR_SEARXNG_URL",
    "geminiApiKey": "YOUR_API_KEY",
    "complexityThreshold": 0.6
  }
}
```

## 详细说明

请查看 README.md
