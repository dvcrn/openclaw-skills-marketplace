---
name: tech-news-daily
description: "获取今日最热门的科技资讯，特别是 AI 大模型领域的最新动态。使用 Tavily Search API 搜索并整理 Top 10 热点新闻，适合每日科技简报、行业资讯收集、AI 领域跟踪等场景。"
---

# 科技资讯日报技能

每日获取最热门的科技资讯，重点关注 AI 大模型领域的最新进展。

## 前置要求

### 配置 Tavily Search API

此技能需要 Tavily Search API 密钥才能实时搜索新闻：

#### 方式 1：设置环境变量（推荐）

```bash
export TAVILY_API_KEY=your_tavily_api_key_here
```

在 Gateway 配置中添加：
```json
{
  "env": {
    "TAVILY_API_KEY": "your_tavily_api_key_here"
  }
}
```

#### 方式 2：在脚本中直接配置

编辑 `scripts/fetch_tech_news_tavily.py`，将 API key 写入脚本（不推荐用于生产环境）。

### 获取 Tavily API Key

1. 访问 https://tavily.com/
2. 注册账号并登录
3. 在 Dashboard 中生成 API Key
4. 免费额度：每月 1000 次搜索

**文档**: https://docs.tavily.com/

## 使用方式

### 触发场景

当用户提到以下关键词时触发此技能：
- "今日科技资讯"
- "科技新闻"
- "AI 大模型动态"
- "科技热点"
- "今日科技头条"
- "获取科技资讯"

### 基本用法

用户直接询问即可：
- "播报今日科技资讯"
- "今天有什么 AI 大模型的新闻？"
- "获取今日最热门的十个科技资讯"

## 搜索策略

### 核心搜索词

使用以下搜索词获取最相关的资讯（参考 `scripts/fetch_tech_news_tavily.py`）：

1. `AI 大模型 最新进展 2026`
2. `人工智能 科技新闻 今日热点`
3. `LLM GPT Claude Gemini 最新动态`
4. `OpenAI Anthropic Google DeepMind AI 新闻`
5. `科技资讯 AI 机器学习 深度学习`

### Tavily 搜索参数

- **search_depth**: `advanced` - 深度搜索获取更准确结果
- **max_results**: 5 (每个查询)
- **include_answer**: `false` - 不需要 AI 总结
- **include_raw_content**: `false` - 只需要摘要

## 输出格式

### 标准格式

```markdown
📰 今日科技资讯 Top 10
更新时间：YYYY-MM-DD HH:MM
==================================================

1. [新闻标题]
   [摘要内容]...
   🔗 [来源链接]

2. [新闻标题]
   ...

==================================================
💡 如需深入了解某条新闻，可以让我详细搜索
```

### 分类整理（可选）

如果新闻较多，可以按主题分类：
- 🤖 AI 大模型进展
- 💻 硬件/芯片动态
- 🚀 创业/融资新闻
- 📱 消费科技产品
- 🔬 科研突破

## 注意事项

1. **API 密钥**：没有 Brave API 密钥时，需提示用户配置
2. **时效性**：使用 `freshness: pd` 确保只获取当日新闻
3. **去重**：合并相似新闻，避免重复
4. **来源可靠性**：优先选择权威科技媒体（36 氪、机器之心、量子位、TechCrunch 等）
5. **链接格式**：在飞书/微信等平台，多个链接用 `<>` 包裹避免嵌入预览

## 进阶用法

### 定时推送

可以配合 cron 实现每日定时推送：

```json
{
  "name": "每日科技资讯",
  "schedule": {"kind": "cron", "expr": "0 8 * * *", "tz": "Asia/Shanghai"},
  "payload": {"kind": "agentTurn", "message": "播报今日科技资讯，特别是 AI 大模型方面的新闻"},
  "sessionTarget": "isolated"
}
```

### 主题定制

用户可以指定特定主题：
- "只关注 AI 大模型相关的新闻"
- "我想看芯片/半导体行业的动态"
- "关注自动驾驶领域的进展"

### 深度分析

对于重要新闻，可以进一步：
1. 使用 `web_fetch` 获取文章全文
2. 整理核心要点
3. 分析行业影响

## 相关文件

- `scripts/fetch_tech_news_tavily.py` - Tavily API 搜索脚本
- `references/search-queries.md` - 详细搜索词列表（如需扩展）

## 故障排查

| 问题 | 解决方案 |
|------|----------|
| 返回 API 密钥错误 | 确认 `TAVILY_API_KEY` 环境变量已设置 |
| 搜索结果过时 | Tavily 默认返回最新结果，可检查查询词是否包含时间关键词 |
| 结果太少 | 增加搜索词多样性，或调整 `max_results` 参数 |
| 中文结果少 | 同时搜索中英文关键词 |
| 网络请求失败 | 检查网络连接，确认 Tavily API 服务正常 |
