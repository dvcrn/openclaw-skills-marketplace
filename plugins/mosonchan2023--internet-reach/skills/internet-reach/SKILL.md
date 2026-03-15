---
name: internet-reach
description: "Give your AI agent eyes to see the entire internet - read Twitter, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu. 6.5K Stars! Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/Panniantong/Agent-Reach
---

# 🌐 Internet Reach - AI Agent上网神器

## 功能

Give your AI agent eyes to see the entire internet! 这个技能让你的AI Agent能够读取和搜索 Twitter, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu 等平台。

### 支持的平台

| 平台 | 功能 | 需要配置 |
|------|------|----------|
| 🌐 网页 | 阅读任意网页 | 无需配置 |
| 📺 YouTube | 字幕提取 + 视频搜索 | 无需配置 |
| 📡 RSS | 阅读任意 RSS/Atom 源 | 无需配置 |
| 🔍 全网搜索 | 语义搜索 | 自动配置 (MCP) |
| 📦 GitHub | 读公开仓库 + 搜索 | 无需配置 |
| 🐦 Twitter/X | 读单条推文 | 需要 Cookie |
| 📺 B站 | 字幕提取 + 搜索 | 告诉 Agent 配代理 |
| 📖 Reddit | 搜索 + 读帖子 | 告诉 Agent 配代理 |
| 📕 小红书 | 阅读、搜索 | 需要 Cookie |
| 🎵 抖音 | 视频解析、无水印下载 | 无需配置 |
| 💼 LinkedIn | 读公开页面 | 无需配置 |
| 🏢 Boss直聘 | 搜索职位 | 需要配置 |
| 💬 微信公众号 | 搜索 + 阅读文章 | 无需配置 |

## 为什么需要这个技能？

- 📺 "帮我看看这个 YouTube 教程讲了什么" → **看不了**，拿不到字幕
- 🐦 "帮我搜一下推特上大家怎么评价这个产品" → **搜不了**，Twitter API 要付费
- 📖 "去 Reddit 上看看有没有人遇到过同样的 bug" → **403 被封**，服务器 IP 被拒
- 📕 "帮我看看小红书上这个品的口碑" → **打不开**，必须登录才能看
- 📺 "B站上有个技术视频，帮我总结一下" → **连不上**，海外/服务器 IP 被屏蔽
- 🔍 "帮我在网上搜一下最新的 LLM 框架对比" → **没有好用的搜索**，要么付费要么质量差

## 使用方法

```json
{
  "action": "read",
  "url": "https://github.com/Panniantong/Agent-Reach",
  "platform": "github"
}
```

或者直接告诉 Agent 你想做什么:
- "帮我看看这个链接"
- "这个 GitHub 仓库是做什么的"
- "这个视频讲了什么"
- "帮我看看这条推文"
- "搜一下 GitHub 上有什么 LLM 框架"

## 输出示例

```json
{
  "success": true,
  "platform": "github",
  "content": "Agent Reach - Give your AI agent eyes to see the entire internet...",
  "stars": "6.5K",
  "forks": "485"
}
```

## 特点

- ✅ **完全免费** - 所有工具开源、所有 API 免费
- ✅ **隐私安全** - Cookie 只存在本地，不上传
- ✅ **持续更新** - 追踪各平台变化
- ✅ **兼容所有 Agent** - Claude Code, OpenClaw, Cursor, Windsurf 都能用

## 价格

每次调用: 0.001 USDT

## 常见问题

**Q: 这个技能是免费的吗？**
A: 100% 免费。所有底层工具都是开源的，唯一可能花钱的是服务器代理（~$1/月），本地电脑不需要。

**Q: 支持哪些 AI Agent？**
A: Claude Code、OpenClaw、Cursor、Windsurf……任何能跑命令行的 Agent 都能用。

**Q: 需要配置吗？**
A: 大部分功能无需配置即可使用。Twitter、小红书等需要 Cookie 配置。
