---
name: content-to-podcast
description: "Transform ANY content into AI Podcast/PPT/MindMap/Quiz using NotebookLM. 431 Stars! Multi-source: YouTube, PDF, URL, WeChat → Audio. Each call charges 0.001 USDT."
homepage: https://github.com/joeseesun/anything-to-notebooklm
---

# Content to Podcast (Anything to NotebookLM)

## 功能

Transform ANY content into Podcast/PPT/MindMap/Quiz using Google NotebookLM. **431 Stars on GitHub!** The most popular open-source content-to-audio tool.

### 支持的内容源 (15+ 种)

- 📱 **微信公众号** (绕过反爬虫)
- 📺 **YouTube 视频** (自动字幕)
- 🌐 **任意网页**
- 📄 **PDF, EPUB, Word**
- 🖼️ **图片** (OCR)
- 🎵 **音频** (转录)
- 📝 **Notion**
- 💬 **Discord**

### 输出的格式

| 格式 | 用途 | 时间 |
|------|------|------|
| 🎙️ 播客 | 通勤听 | 2-5分钟 |
| 📊 PPT | 团队分享 | 1-3分钟 |
| 🗺️ 思维导图 | 理清结构 | 1-2分钟 |
| 📝 Quiz | 自测 | 1-2分钟 |

## 使用方法

```json
{
  "action": "podcast",
  "source": "https://youtube.com/watch?v=...",
  "format": "podcast"
}
```

## 价格

每次调用: **0.001 USDT**

## 前置需求

- Python 3.9+
- Google NotebookLM 账号

## 安装

```bash
git clone https://github.com/joeseesun/anything-to-notebooklm
cd anything-to-notebooklm
./install.sh
```

## Use Cases

- **通勤学习**: YouTube视频转播客，听新闻、学课程
- **内容创作**: 长文章转PPT，用于分享和展示
- **知识整理**: 文档转思维导图，理清思路
- **学习测验**: 材料转Quiz，自测记忆效果
- **公众号备份**: 绕过微信付费，保存内容
