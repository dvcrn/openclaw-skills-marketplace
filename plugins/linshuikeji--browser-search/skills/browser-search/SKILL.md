---
name: browser-search
description: "浏览器自动化搜索技能 - 使用本地浏览器进行网页搜索和内容提取。\n 支持 Bing、Google、Baidu 等搜索引擎，无需 API 配置。\n 适合：实时搜索、信息收集、资料整理、竞品分析等场景。"
---

# Browser Search 技能

使用本地浏览器进行自动化搜索和内容提取。

## 核心功能

- 🌐 **多搜索引擎支持**：Bing、Google、Baidu、DuckDuckGo 等
- 📄 **内容提取**：自动提取搜索结果、文章摘要、链接
- 🎯 **智能路由**：根据需求自动选择最佳搜索引擎
- 💾 **结果保存**：自动保存搜索结果到文件
- 🔍 **深度搜索**：支持分页浏览、关键词过滤

## 使用场景

- 查找最新新闻和资讯
- 收集竞品分析资料
- 搜索技术文档和教程
- 市场调研和数据收集
- 内容创作素材搜集

## 触发词

当用户说：
- "搜索..."
- "查找..."
- "用浏览器搜索..."
- "帮我找..."
- "获取最新..."

## 快速开始

### 基本搜索

```bash
# 命令行调用
browser-search "人工智能 2026"

# 带引擎选择
browser-search "AI 趋势" --engine bing

# 保存到文件
browser-search "Python 教程" --output ai_tutorials.md
```

### 高级用法

```bash
# 指定引擎
browser-search "量子计算" --engine bing --engine baidu

# 提取特定内容
browser-search "深度学习论文" --extract abstract --max 5

# 实时监控
browser-search "股市新闻" --interval 60
```

## 配置

### 搜索引擎设置

```bash
# 添加自定义搜索引擎
browser-search config add --engine custom \
  --name 知乎 \
  --url "https://www.zhihu.com/search?q={query}" \
  --selector ".ResultPost"
```

### 默认引擎

```bash
browser-search config set-default bing
```

## 输出格式

```json
{
  "query": "人工智能 2026",
  "engine": "bing",
  "results": [
    {
      "title": "2026 AI 趋势预测",
      "url": "https://...",
      "snippet": "...",
      "source": "腾讯云开发"
    }
  ],
  "extracted": {
    "summary": "AI Agent 成为核心趋势...",
    "links": ["...", "..."]
  }
}
```

## 注意事项

- 需要浏览器服务正常运行
- 搜索结果可能受地区限制
- 部分网站可能有反爬虫机制
- 建议设置合理的搜索间隔

## 相关技能

- `web-search` - 需要 API 配置的搜索
- `agent-browser` - 浏览器自动化基础
- `web-fetch` - 网页内容提取
