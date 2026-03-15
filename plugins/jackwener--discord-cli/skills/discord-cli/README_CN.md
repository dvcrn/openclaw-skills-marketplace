# discord-cli

[![PyPI version](https://img.shields.io/pypi/v/kabi-discord-cli.svg)](https://pypi.org/project/kabi-discord-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/kabi-discord-cli.svg)](https://pypi.org/project/kabi-discord-cli/)

Discord CLI — 在终端获取 Discord 聊天记录、搜索消息、AI 分析。基于 Discord HTTP API + user token（只读）。

## 推荐项目

- [twitter-cli](https://github.com/jackwener/twitter-cli) — Twitter/X CLI
- [bilibili-cli](https://github.com/jackwener/bilibili-cli) — Bilibili CLI
- [xhs-cli](https://github.com/jackwener/xhs-cli) — 小红书 CLI

## 功能特性

- 🔐 **认证** — 自动从浏览器/Discord 客户端提取 token，一键配置
- 🏠 **服务器** — 列出 server、channel、成员、服务器详情
- 📜 **历史** — 拉取消息历史存入 SQLite
- 🔄 **同步** — 增量同步、批量全量同步
- 🔍 **搜索** — Discord 原生搜索 + 本地关键词搜索
- 📊 **分析** — 统计、活跃排行、时间线图表
- 📅 **今日** — 按频道分组查看今日消息
- 🤖 **AI** — Claude 驱动的消息分析和摘要
- 📤 **导出** — text/JSON 格式，方便脚本处理
- 📊 **JSON 输出** — 所有查询命令支持 `--json`

## 安装

```bash
# 从 PyPI 安装
uv tool install kabi-discord-cli
# 或
pipx install kabi-discord-cli

# 从源码安装
git clone git@github.com:jackwener/discord-cli.git
cd discord-cli
uv sync
```

## 快速开始

```bash
# 自动提取并保存 token
discord auth --save

# 检查登录状态
discord status
discord whoami

# 列出 server 和 channel
discord dc guilds
discord dc channels <guild_id>

# 拉取历史消息
discord dc history <channel_id> -n 1000

# 增量同步
discord dc sync <channel_id>
discord dc sync-all

# 查看今日消息
discord today
```

## 命令一览

### 认证与账号

| 命令 | 说明 |
|------|------|
| `auth [--save]` | 从浏览器/Discord 客户端提取 token |
| `status` | 检查 token 是否有效（exit code 0/1） |
| `whoami [--json]` | 查看用户详情 |

### Discord 操作 (`discord dc ...`)

| 命令 | 说明 |
|------|------|
| `dc guilds [--json]` | 列出已加入的 server |
| `dc channels GUILD [--json]` | 列出文字频道 |
| `dc history CHANNEL [-n 1000]` | 拉取历史消息 |
| `dc sync CHANNEL` | 增量同步 |
| `dc sync-all` | 同步所有已知频道 |
| `dc search GUILD 关键词 [-c CH]` | Discord 原生搜索 |
| `dc members GUILD [--max 50]` | 列出成员 |
| `dc info GUILD [--json]` | 服务器详情 |

### 查询

| 命令 | 说明 |
|------|------|
| `search 关键词 [-c CH] [--json]` | 搜索本地存储的消息 |
| `stats [--json]` | 各频道消息统计 |
| `today [-c CH] [--json]` | 今日消息 |
| `top [-c CH] [--hours N] [--json]` | 最活跃发言人排行 |
| `timeline [-c CH] [--by day\|hour]` | 消息活跃度时间线 |

### 数据与 AI

| 命令 | 说明 |
|------|------|
| `export CHANNEL [-f text\|json] [-o FILE]` | 导出消息 |
| `purge CHANNEL [-y]` | 删除本地存储的消息 |
| `analyze CHANNEL [--hours 24] [-p PROMPT]` | AI 分析（Claude） |
| `summary [-c CH] [--hours N]` | AI 每日摘要 |

## 认证方式

discord-cli 自动从以下位置提取 token：
1. **Discord 桌面客户端** — 读取本地 leveldb
2. **浏览器** — Chrome、Edge、Brave 的 local storage

Token 会通过 API 验证后才保存。运行 `discord auth --save` 一键完成配置。

## License

Apache-2.0
