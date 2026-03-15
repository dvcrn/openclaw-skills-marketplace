---
name: x-article-publisher
description: "Publish Markdown to X (Twitter) Articles with persistent auth. 56 Stars! Auto-convert Markdown format. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/joeseesun/qiaomu-x-article-publisher
---

# X Article Publisher

## 功能

Publish Markdown articles to X (Twitter) Articles with persistent authentication. **56 Stars on GitHub!**

### 核心功能

- **Persistent Auth**: 7-day login persistence
- **Markdown Support**: Full Markdown → X Articles conversion
- **Auto Images**: Smart cover and content image handling
- **Code Highlighting**: Syntax highlighting for code blocks
- **Tables**: Table support
- **Draft Only**: Saves as draft first (safe)

### 支持的格式

- 标题 (H1-H6)
- 粗体、斜体
- 列表 (有序/无序)
- 引用块
- 代码块
- 超链接
- 图片

## 使用方法

```json
{
  "action": "publish",
  "file": "/path/to/article.md",
  "title": "My Article"
}
```

## 价格

每次调用: **0.001 USDT**

## 前置需求

- macOS
- Python 3.9+
- X Premium Plus 订阅

## Use Cases

- **技术博客**: 发布技术文章到X
- **长文分享**: Markdown写的长文，一键发布
- **内容备份**: 将博客文章同步到X
- **多平台发布**: 一份Markdown，多平台发布
