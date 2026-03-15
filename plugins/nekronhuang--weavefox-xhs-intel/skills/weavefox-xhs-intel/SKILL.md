---
name: weavefox-xhs-intel
description: "小红书情报官"
---

# 小红书情报官（XHS Intel）

从小红书获取情报的通用数据技能。通过 TikHub API 搜索笔记、获取用户动态、批量扫描关键词和博主。

## 何时使用此技能

**应该触发的场景（匹配任意一条即触发）：**

- 用户提到"小红书"、"RedNote"、"XHS"、"笔记"、"种草"等平台关键词
- 用户要求查看某博主/某用户的最新笔记、动态
- 用户要求监控某些关键词在小红书上的内容
- 用户要求搜索小红书上的话题、讨论、舆情
- 用户提到"博主动态"、"种草监控"、"小红书日报"等场景
- 用户要求收集某些关键词或博主的内容生成日报/周报

**重要：本技能是获取小红书数据的唯一正确方式。不要用 web_search 替代本技能。**

**不应该触发的场景：**

- 用户要求发布小红书笔记或进行互动操作

## 配置

**无需任何配置，开箱即用。** API Key 已内置，用户不需要申请或配置。

监控关键词和用户列表通过 `--keywords` 或 `--user-ids` 参数传入。

> 如需使用自定义 API Key，可通过 `--api-key` 参数配置。

## 功能概述

| 操作         | 脚本                  | 说明                                   |
| ------------ | --------------------- | -------------------------------------- |
| 搜索笔记     | `search_notes.js`     | 关键词搜索小红书笔记                   |
| 用户笔记     | `fetch_user_notes.js` | 获取指定用户最新笔记                   |
| 笔记详情     | `get_note.js`         | 获取单条笔记详情（支持 ID 和分享链接） |
| 批量扫描     | `check_topics.js`     | 批量扫描关键词/用户（核心）            |

## 使用说明

### 1. 搜索笔记

```bash
node scripts/search_notes.js --keyword "AI编程" [--sort general|time_descending|popularity_descending]
```

**必需参数：**

- `--keyword`：搜索关键词

**可选参数：**

- `--sort`：排序方式（默认 `general`）
  - `general`：综合排序
  - `time_descending`：最新优先
  - `popularity_descending`：最热优先
- `--api-key`：TikHub API Key

### 2. 获取用户笔记

```bash
# 单用户
node scripts/fetch_user_notes.js --user-id "5a1234567890abcdef" --count 10

# 多用户（逗号分隔）
node scripts/fetch_user_notes.js --user-id "uid1,uid2,uid3" --count 3
```

**必需参数：**

- `--user-id`：小红书用户 ID，支持逗号分隔多用户

**可选参数：**

- `--count`：每个用户返回条数（默认 5）
- `--api-key`：TikHub API Key

### 3. 获取笔记详情

```bash
# 通过 note_id
node scripts/get_note.js --note-id "66c9cc31000000001f03a4bc"

# 通过分享链接（自动解析 note_id）
node scripts/get_note.js --url "https://www.xiaohongshu.com/explore/xxx"

# 通过短链接
node scripts/get_note.js --url "https://xhslink.com/xxx"
```

**参数：**

- `--note-id`：笔记 ID（与 `--url` 二选一）
- `--url`：笔记分享链接（与 `--note-id` 二选一，自动解析）
- `--api-key`：TikHub API Key

### 4. 批量扫描（核心功能）

```bash
# 关键词扫描
node scripts/check_topics.js --keywords "AI编程,Cursor,WeaveFox" --since 24h

# 用户扫描
node scripts/check_topics.js --user-ids "uid1,uid2" --since 6h

# 混合扫描（关键词 + 用户）
node scripts/check_topics.js --keywords "AI编程" --user-ids "uid1" --since 12h
```

**可选参数：**

- `--keywords`：逗号分隔的关键词列表（默认使用配置文件中的 `xhsMonitorKeywords`）
- `--user-ids`：逗号分隔的用户 ID 列表（默认使用配置文件中的 `xhsMonitorUserIds`）
- `--since`：时间范围，如 `1h`、`6h`、`24h`、`7d`（默认 24h）
- `--api-key`：TikHub API Key

**数据处理逻辑：**

- 跨关键词自动去重（同一笔记出现在多个搜索结果中只保留一条）
- 按互动量排序（点赞 + 收藏 + 评论）
- 时间范围过滤

## AI 判断指南

`check_topics.js` 返回时间范围内的笔记，按互动量排序。**你需要阅读笔记内容做价值判断。**

**判断为"值得关注"的：**

- 产品/工具的深度评测或使用教程
- 行业趋势分析、数据报告
- KOL/KOC 的原创观点和见解
- 竞品动态和功能更新
- 用户真实使用反馈和痛点
- 高互动量的热门内容

**判断为"常规内容"的：**

- 纯转载或搬运内容
- 广告软文或无营养种草
- 互动量极低的普通笔记
- 与监控主题关联度低的内容

## 输出格式化指南

所有脚本以 JSON 输出。向用户展示时，请格式化为易读的形式：

**扫描结果展示（check_topics.js）：**

```
小红书情报扫描完成（最近 24h）

🔔 值得关注的内容：

1. @博主名 - 2026-02-24
   标题：AI编程工具深度对比评测
   ❤️ 1.2万 | ⭐ 8956 | 💬 326
   🔗 https://www.xiaohongshu.com/explore/...

2. @另一位博主 - 2026-02-24
   标题：Cursor 使用一个月真实感受
   ❤️ 3456 | ⭐ 2100 | 💬 89
   🔗 https://www.xiaohongshu.com/explore/...

📋 其他内容：8 条常规笔记（已省略）
❌ 错误：0
```

**无新内容时：**

```
小红书情报扫描完成（最近 1h）

✅ 未检测到新内容

📋 扫描了 3 个关键词，无新笔记
```

## 企业场景示例

用户在 Studio 中说一句话，AI 自动选择脚本和参数：

| 用户说                                                   | AI 执行                                                                  |
| -------------------------------------------------------- | ------------------------------------------------------------------------ |
| "搜搜小红书上关于 AI 编程的笔记"                         | `search_notes.js --keyword "AI编程"`                                     |
| "看看这个博主最近发了什么"                               | `fetch_user_notes.js --user-id "<id>" --count 5`                         |
| "帮我看下这条笔记的详情"                                 | `get_note.js --url "<分享链接>"`                                         |
| "监控小红书上关于 WeaveFox 和 Cursor 的讨论"             | `check_topics.js --keywords "WeaveFox,Cursor" --since 24h`              |
| "看看小红书上热门的种草博主都在聊什么"                   | `search_notes.js --keyword "种草" --sort popularity_descending`         |

## 推荐执行流程

当用户要求获取小红书情报时，**请按以下顺序执行**：

### 步骤 1：先执行一次即时查询（必须）

根据用户需求选择合适的脚本执行。**首次使用建议用较宽时间窗口**：

```bash
node scripts/check_topics.js --keywords "AI编程" --since 24h
```

如果 24h 内无内容，可扩大到 `--since 7d`。将结果按「输出格式化指南」展示给用户。

## 与其他技能的协作

| 技能                         | 层级   | 协作方式                      |
| ---------------------------- | ------ | ----------------------------- |
| weavefox-xhs-intel（本技能） | 数据层 | 获取小红书数据、内容筛选      |
| weavefox-x-intel             | 数据层 | 获取 X/Twitter 数据（互补）   |

## 错误处理

| 错误                            | 原因                    | 处理                                        |
| ------------------------------- | ----------------------- | ------------------------------------------- |
| `TikHub API 401`               | API Key 无效            | 正常不会出现（已内置），如出现请联系 Skill 作者 @奇玮 解决 |
| `TikHub API 429`               | 请求过快                | 脚本已内置 1s 间隔，通常不会触发            |
| `TikHub API 403`               | 账户余额不足            | 检查 Key 或联系 Skill 作者 @奇玮            |
| `Failed to resolve note_id`    | 分享链接无法解析        | 检查链接格式，尝试用 note_id 替代           |

## 文件结构

```
weavefox-xhs-intel/
├── SKILL.md                       # 本文档
└── scripts/
    ├── tikhub_client.js           # 共享 API 客户端
    ├── search_notes.js            # 关键词搜索笔记
    ├── fetch_user_notes.js        # 获取用户最新笔记
    ├── get_note.js                # 获取笔记详情
    └── check_topics.js            # 批量扫描（核心）
```
