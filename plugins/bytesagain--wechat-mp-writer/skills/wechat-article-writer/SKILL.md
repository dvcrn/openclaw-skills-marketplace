---
name: wechat-article-writer
description: "WeChat Official Account article generator. 微信公众号文章、公众号写作、公众号文案、自媒体写作、10万+爆文、微信运营、公众号运营、微信推文、订阅号文章、服务号文章、微信SEO、公众号涨粉、爆款标题、朋友圈转发、公众号排版、自媒体爆文、新媒体写作、内容运营、系列文章、A/B测试标题、数据型文章、行动号召CTA。Generate WeChat articles, viral titles, summaries, outlines, CTA templates, series planning, A/B headline testing, and data-driven articles. Use when: (1) writing WeChat Official Account articles, (2) generating 10w+ viral titles, (3) creating article summaries for sharing in Moments, (4) planning article outlines, (5) writing follow/share CTA endings, (6) exploring trending WeChat topics, (7) planning article series, (8) A/B testing headlines, (9) writing data-driven articles. 适用场景：写公众号文章、生成爆款标题、写朋友圈转发语、做文章大纲、写引导关注结尾、选题策划、系列文章规划、A/B标题测试、数据型文章。"
---

# wechat-article-writer

微信公众号文章生成器。生成微信公众号风格的完整文章、10w+爆款标题、文章摘要（朋友圈转发语）、文章大纲、引导关注/转发结尾模板，以及热门选题方向建议。

## 为什么用这个 Skill？ / Why This Skill?

- **公众号调性**：专门针对微信公众号的写作风格，短段落+加粗金句+emoji，不是通用文章
- **10万+标题公式**：内置数字+情绪+好奇心的爆款标题生成逻辑
- **完整工作流**：从选题→大纲→正文→标题→摘要→CTA一条龙
- Compared to asking AI directly: purpose-built for WeChat's unique formatting, reading habits, and viral mechanics — not generic blog writing

## 功能说明

- **文章生成**：根据主题生成完整公众号文章（标题+导语+正文+结语+引导关注），支持干货、故事、评测、教程、观点等风格
- **标题优化**：为任意主题生成5个10w+爆款标题，运用数字+情绪+好奇心公式
- **摘要生成**：生成适合朋友圈转发的精炼摘要
- **大纲生成**：快速生成文章结构大纲
- **CTA模板**：生成引导点赞、在看、转发的结尾模板
- **热门选题**：输出当前热门公众号选题方向

## 公众号风格要点

- 标题：数字+情绪+好奇心，善用"竟然""居然""必看""揭秘"等词
- 正文：短段落，多用**加粗**，穿插金句
- 结尾：引导点赞、在看、转发

## 使用方式

运行脚本 `scripts/wechat.sh`：

```bash
# 生成完整公众号文章（默认干货风格）
wechat.sh article "主题" [--style 干货|故事|评测|教程|观点]

# 生成5个10w+爆款标题
wechat.sh title "主题"

# 生成文章摘要（朋友圈转发语）
wechat.sh summary "主题"

# 生成文章大纲
wechat.sh outline "主题"

# 生成行动号召结尾（按类型）
wechat.sh cta "关注|转发|留言"

# 热门公众号选题方向
wechat.sh trending

# 系列文章规划（默认5篇）
wechat.sh series "主题" [篇数]

# A/B测试标题（5对对照标题）
wechat.sh headline-ab "主题"

# 数据型文章模板
wechat.sh data-article "数据主题"

# 帮助信息
wechat.sh help
```

See also: `examples.md` for 10 viral article templates.

## 技术要求

- Bash + Python3（兼容 Python 3.6+）
- 纯模板化输出，不依赖外部 API
- 无需安装额外依赖
