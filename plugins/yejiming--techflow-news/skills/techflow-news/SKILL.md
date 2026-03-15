---
name: techflow-news
description: "深潮TechFlow新闻聚合爬取。爬取https://www.techflowpost.com/?lang=zh-CN当天的文章，形成表格（日期、文章、主要内容、网址），并给出一段简短总结。用于用户询问\"今天有什么新闻\"、\"汇总今天的文章\"等场景。"
---

# TechFlow 新闻聚合

爬取深潮TechFlow网站当天文章，整理成表格并总结。

## 使用方法

1. 使用 extract_content_from_websites 工具提取网页内容
2. URL: `https://www.techflowpost.com/?lang=zh-CN`
3. 提取信息：文章标题、发布日期、主要内容摘要、文章链接

## 输出格式

### 表格部分

| 日期 | 文章 | 主要内容 | 网址 |
|------|------|----------|------|

### 总结部分

- 提取3-5个核心热点
- 用简短段落总结当天主要话题

## 注意事项

- 筛选当天（2026年X月X日）发布的文章
- 区分"深度文章"和"7x24h快讯"
- 文章链接需要补充完整URL（https://www.techflowpost.com + 相对路径）
