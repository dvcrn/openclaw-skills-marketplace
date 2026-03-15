---
name: news-content-extractor
description: "输入新闻 URL，通过远程 API 高效提取网页的正文、标题、作者和时间。"
---

# 新闻内容提取器 (Pro 版)

这是一个采用前后端分离架构的新闻内容提取 Skill。

## 特点
- **零本地依赖**: 客户端使用 Node.js，无需安装复杂的 Python 库。
- **身份验证**: 使用 `EASYALPHA_API_KEY` 保护 API 调用。
- **高性能解析**: 由远端基于 `trafilatura` 的后端服务驱动。

## 配置要求

使用此 Skill 必须设置以下环境变量：

1. `EASYALPHA_API_KEY`: 您的身份验证 Token。
2. `NEWS_EXTRACTOR_SERVER_URL`: (可选) 后端服务端地址，默认为本地测试地址。

## 使用方法

**用户**: "抓取这个网页的内容：https://www.bbc.com/news/uk-12345678"

**Agent 行为**:
- 运行 `node scripts/extract_news.js https://www.bbc.com/news/uk-12345678`
- 脚本自动携带 Token 向服务器发起请求。
- 解析并展示结果。
