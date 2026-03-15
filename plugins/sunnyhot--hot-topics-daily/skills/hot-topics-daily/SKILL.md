---
name: hot-topics-daily
description: "每日热搜速览推送 - 自动抓取微博、知乎、百度、B站等平台热搜并发送到 Discord。Use when users want to schedule daily hot topics push, or ask about trending topics on Chinese social media platforms."
---

# 每日热搜速览推送

自动抓取国内主流平台热搜，定时推送到 Discord。

---

## 支持的平台

| 平台 | API 端点 | 有热度 |
|------|----------|--------|
| 微博 | `/v2/weibo` | ✅ |
| 知乎 | `/v2/zhihu` | ✅ |
| 百度 | `/v2/baidu/hot` | ✅ |
| B站 | `/v2/bili` | ❌ |
| 抖音 | `/v2/douyin` | ✅ |
| 今日头条 | `/v2/toutiao` | ✅ |

**API Base**: `https://60s.viki.moe/v2`

---

## 使用方法

### 1. 手动推送

```bash
node /Users/xufan65/.openclaw/workspace/skills/hot-topics-daily/scripts/push.cjs
```

### 2. 定时推送（Cron）

已配置的定时任务：
- **Cron ID**: `5498e5c4-b707-4524-b8f6-d39f964ef777`
- **时间**: 每天 08:30（北京时间）
- **推送位置**: Discord 子区 `1482024661033287771`

查看/修改定时任务：
```bash
# 查看任务状态
openclaw cron list | grep hot-topics

# 手动触发一次
openclaw cron run 5498e5c4-b707-4524-b8f6-d39f964ef777
```

---

## 推送格式

```
📅 **YYYY-MM-DD HH:MM** 每日热搜速览

**🔥 微博热搜 TOP 5**
**1.** [话题标题](链接) `热度`
...

**💡 知乎热榜 TOP 5**
**1.** [话题标题](链接) `热度`
...

**🔍 百度热搜 TOP 5**
**1.** [话题标题](链接) `热度`
...

**📺 B站热门 TOP 5**
**1.** [话题标题](链接)
...

---
_由 OpenClaw 自动推送_
```

---

## 配置

### Discord 推送目标

在 `scripts/push.cjs` 中修改：
```javascript
const THREAD_ID = "1482024661033287771";  // Discord 子区 ID
```

### 平台选择

在脚本中修改 `platforms` 数组来启用/禁用平台：
```javascript
const platforms = [
  { name: '微博', key: 'weibo', emoji: '🔥' },
  { name: '知乎', key: 'zhihu', emoji: '💡' },
  { name: '百度', key: 'baidu/hot', emoji: '🔍' },
  { name: 'B站', key: 'bili', emoji: '📺' }
];
```

---

## API 响应格式

### 微博
```json
{
  "title": "话题标题",
  "hot_value": 1234567,
  "link": "https://s.weibo.com/..."
}
```

### 知乎
```json
{
  "title": "问题标题",
  "hot_value_desc": "1234 万热度",
  "link": "https://www.zhihu.com/..."
}
```

### 百度
```json
{
  "title": "话题标题",
  "score_desc": "123.45w",
  "url": "https://www.baidu.com/..."
}
```

### B站
```json
{
  "title": "视频标题",
  "link": "https://search.bilibili.com/..."
}
```

---

## 文件结构

```
skills/hot-topics-daily/
├── SKILL.md           # 技能说明
└── scripts/
    └── push.cjs       # 推送脚本
```

---

## 依赖

- Node.js >= 18
- `node-fetch`（内置）
- Discord 频道配置（通过 message tool）

---

## 更新日志

### v1.0.0 (2026-03-13)
- 初始版本
- 支持微博、知乎、百度、B站热搜
- Discord 定时推送
