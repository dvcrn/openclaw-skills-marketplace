---
name: smart-search
description: "智能搜索引擎切换。根据问题类型自动选择 SearXNG 或 Tavily，既满足需求又节省 Token。"
---

# Smart Search - 智能搜索引擎切换

根据问题类型自动选择最优搜索引擎（SearXNG 或 Tavily），既满足需求又节省 Token。

## 决策逻辑

| 场景 | 引擎 | 原因 |
|------|------|------|
| 写文案/小红书/公众号 | Tavily | AI 内容生成，需要摘要 |
| 日常查询/深度调研 | SearXNG → Tavily | 先尝试免费，失败自动降级 |
| 用户指定 | 按用户要求 | 尊重用户选择 |

**降级策略：** SearXNG 公共实例不稳定时，自动切换到 Tavily

## 工具调用

### Tavily 搜索
```bash
python3 ~/.openclaw/workspace/skills/openclaw-tavily-search/scripts/tavily_search.py --query "查询内容" --max-results 5 --format md
```

### SearXNG 搜索
```bash
curl -s "https://searx.be/search?q=查询内容&format=json"
```

## 使用示例

**AI 内容生成**
```bash
# 调用 Tavily
python3 {baseDir}/../openclaw-tavily-search/scripts/tavily_search.py --query "小红书文案 AI 工具" --max-results 5 --format md
```

**日常查询**
```bash
# 调用 SearXNG
curl -s "https://searx.be/search?q=区块链是什么&format=json"
```

## 配置

确保以下环境变量已设置：
```bash
# ~/.openclaw/.env
SEARXNG_URL=https://searx.be
TAVILY_API_KEY=tvly-xxx
```

## Token 对比

| 引擎 | Token/次 | 使用场景 |
|------|---------|----------|
| SearXNG | ~350 | 日常搜索（60%） |
| Tavily | ~950 | AI 内容生成（40%） |

**智能切换节省约 38% Token**
