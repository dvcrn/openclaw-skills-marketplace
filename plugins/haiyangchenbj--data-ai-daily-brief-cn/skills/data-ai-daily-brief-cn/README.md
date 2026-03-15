# 📰 AI 驱动的行业情报日报

> **把任何行业变成一份每日情报简报 — 自动搜索、过滤、编写、多渠道推送。**
>
> **[English Documentation →](README.md)**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-CodeBuddy%20%7C%20WorkBuddy-green.svg)](#)
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-pink.svg)](../../sponsors)
[![Bilingual](https://img.shields.io/badge/docs-EN%20%7C%20中文-orange.svg)](README.md)

---

## 🤔 你是否遇到过这些问题？

你想给自己或团队做一份每日行业简报——精准、结构化、有来源、每天早上自动推到群里。但实际操作起来：

- **每天手动搜索几十个信源**，费时费力
- **信噪比极低** — 80% 是噪音、二手报道、标题党
- **多渠道同步** — 在 Slack、邮件、企微、飞书之间复制粘贴
- **难以坚持** — 偶尔忘了，日报就断了

**如果 AI 能帮你在 3 分钟内搞定这一切呢？**

## 💡 解决方案

这是一个开箱即用的 [CodeBuddy](https://www.codebuddy.ai/) / WorkBuddy **Skill**，可以把你的 AI 助手变成一个专业的行业情报分析师。只需要说一句话：

> *"生成今天的行业日报"*

AI 就会自动完成：

1. 🔍 **全网搜索** — 采集你所在行业的最新动态
2. 🎯 **严格过滤** — 只保留一手来源，去除噪音和标题党
3. 📝 **结构化编写** — 生成带来源、摘要和影响分析的专业日报
4. 📤 **多渠道推送** — 一键发送到 9 大渠道

### 🏭 适用于任何行业

默认配置以 **Data+AI 基础设施** 为例（数据平台、湖仓架构、流批处理、数据治理等），但 **你可以将它定制为任何行业**：

| 你的行业 | 只需修改 `focus_areas` + `SKILL.md` 中的 Prompt |
|---|---|
| 金融科技 / 银行业 | 支付、数字银行、RegTech、DeFi |
| 医疗科技 / BioAI | 临床 AI、药物发现、电子病历、FDA 审批 |
| 网络安全 | 威胁情报、零信任、CVE、安全厂商动态 |
| DevTools / 平台工程 | CI/CD、可观测性、IaC、开发者体验 |
| 电商 / 零售科技 | 个性化推荐、物流科技、平台策略 |
| *你的细分领域* | 任何有公开新闻源的行业 |

👉 详见 [自定义指南](#-自定义)。

## ✨ 功能特色

- 🔍 **自动情报采集** — 联网搜索 + 信源验证
- 🎯 **严格信噪过滤** — 仅一手来源，拒绝搬运和标题党
- 📝 **结构化输出** — Top Signals、Product & Tech、People & Views、Analyst Insights、Watchlist 五大板块
- 🎯 **宁缺毋滥** — 板块无合格内容时留空，绝不降低准入标准凑数
- 🌐 **9 大推送渠道** — 企微 · 钉钉 · 飞书 · Slack · Discord · Telegram · Teams · 邮件 · GitHub Pages
- 🎨 **精美 HTML 报告** — 卡片式布局，来源链接可点击（链接仅在 HTML 完整版中呈现，摘要保持纯文本）
- ⚙️ **完全可配置** — 行业方向、厂商列表、输出语言、推送渠道
- 🌍 **中英文双语** — 默认中文输出，可切换任何语言

## 📦 项目结构

```
data-ai-daily-brief-skill/
├── SKILL.md                    # Skill 定义文件（核心指令）
├── README.md                   # 英文文档
├── README_zh.md                # 中文文档（本文件）
├── LICENSE                     # MIT 开源协议
├── CONTRIBUTING.md             # 贡献指南
├── daily-brief-config.json     # 配置文件（由 init_config.py 生成）
├── scripts/
│   ├── init_config.py          # 初始化默认配置
│   ├── send_wecom.py           # 🇨🇳 企业微信推送
│   ├── send_dingtalk.py        # 🇨🇳 钉钉推送
│   ├── send_feishu.py          # 🇨🇳 飞书推送
│   ├── send_slack.py           # 🌍 Slack 推送
│   ├── send_discord.py         # 🌍 Discord 推送
│   ├── send_telegram.py        # 🌍 Telegram 推送
│   ├── send_teams.py           # 🌍 Microsoft Teams 推送
│   ├── send_email.py           # 📧 邮件推送
│   └── deploy_github.py        # 🌐 GitHub Pages 部署
├── .github/
│   └── FUNDING.yml             # GitHub Sponsors 配置
└── assets/
    └── report-template.html    # HTML 报告模板
```

## 🚀 快速开始

### 方式 1：作为 CodeBuddy / WorkBuddy Skill 使用

1. **复制 Skill 到项目中**：
   ```bash
   cp -r data-ai-daily-brief-skill .codebuddy/skills/data-ai-daily-brief
   ```

2. **对 AI 说**：
   - "生成今天的行业日报"
   - "帮我生成 2026-03-10 的 Data+AI 日报"
   - Skill 会自动触发并按流程执行

3. **配置推送渠道**（可选）：
   ```bash
   python .codebuddy/skills/data-ai-daily-brief/scripts/init_config.py
   ```
   编辑生成的 `daily-brief-config.json`，填入你的推送渠道信息。

### 方式 2：导入 Skill

1. 打开 CodeBuddy / WorkBuddy 设置页面
2. 找到 **Skills** 管理区域
3. 点击 **"导入 Skill"**
4. 选择本 Skill 文件夹

### 方式 3：独立使用脚本

```bash
# 初始化配置
python scripts/init_config.py

# === 国内渠道 ===
python scripts/send_wecom.py 2026-03-11          # 企业微信
python scripts/send_dingtalk.py 2026-03-11       # 钉钉
python scripts/send_feishu.py 2026-03-11         # 飞书
python scripts/send_feishu.py --card --link-url https://...  # 飞书交互卡片

# === 国际渠道 ===
python scripts/send_slack.py 2026-03-11          # Slack
python scripts/send_discord.py 2026-03-11        # Discord
python scripts/send_telegram.py 2026-03-11       # Telegram
python scripts/send_teams.py 2026-03-11          # Microsoft Teams

# === 通用渠道 ===
python scripts/send_email.py 2026-03-11          # 邮件
python scripts/deploy_github.py 2026-03-11       # GitHub Pages
```

## ⚙️ 配置说明

### daily-brief-config.json

```json
{
  "adapters": {
    "wechatwork": { "enabled": true, "webhook_url": "你的企微 Webhook URL" },
    "dingtalk":   { "enabled": true, "webhook_url": "你的钉钉 URL", "secret": "可选加签密钥" },
    "feishu":     { "enabled": true, "webhook_url": "你的飞书 URL", "secret": "可选签名密钥" },
    "slack":      { "enabled": true, "webhook_url": "你的 Slack URL" },
    "discord":    { "enabled": true, "webhook_url": "你的 Discord URL" },
    "telegram":   { "enabled": true, "bot_token": "你的 Bot Token", "chat_id": "你的 Chat ID" },
    "teams":      { "enabled": true, "webhook_url": "你的 Teams URL" },
    "email":      { "enabled": true, "smtp_host": "smtp.example.com", "smtp_user": "..." },
    "github":     { "enabled": true, "github_user": "your_username", "github_repo": "daily-brief" }
  },
  "customization": {
    "language": "zh-CN",
    "max_items": 12,
    "focus_areas": ["大数据", "数据平台", "数据治理", "..."]
  }
}
```

### 环境变量

#### 🇨🇳 国内渠道

| 变量名 | 用途 | 必需 |
|--------|------|------|
| `WECOM_WEBHOOK_URL` | 企业微信 Webhook URL | 使用企微时 |
| `DINGTALK_WEBHOOK_URL` | 钉钉 Webhook URL | 使用钉钉时 |
| `DINGTALK_SECRET` | 钉钉加签密钥 | 开启加签时 |
| `FEISHU_WEBHOOK_URL` | 飞书 Webhook URL | 使用飞书时 |
| `FEISHU_SECRET` | 飞书签名密钥 | 开启签名时 |

#### 🌍 国际渠道

| 变量名 | 用途 | 必需 |
|--------|------|------|
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL | 使用 Slack 时 |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL | 使用 Discord 时 |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | 使用 Telegram 时 |
| `TELEGRAM_CHAT_ID` | Telegram Chat/Channel ID | 使用 Telegram 时 |
| `TEAMS_WEBHOOK_URL` | Teams Incoming Webhook URL | 使用 Teams 时 |

#### 📧 通用渠道

| 变量名 | 用途 | 必需 |
|--------|------|------|
| `SMTP_HOST` | SMTP 服务器地址 | 使用邮件时 |
| `SMTP_USER` | SMTP 用户名 | 使用邮件时 |
| `SMTP_PASSWORD` | SMTP 密码 | 使用邮件时 |
| `EMAIL_TO` | 收件人（逗号分隔） | 使用邮件时 |
| `GITHUB_TOKEN` | GitHub Personal Access Token | 使用 GitHub 时 |
| `GITHUB_USER` | GitHub 用户名 | 使用 GitHub 时 |

## 🔌 各渠道快速配置指南

<details>
<summary><b>🇨🇳 钉钉 (DingTalk)</b></summary>

1. **创建机器人**：目标群 → 群设置 → 智能群助手 → 添加机器人 → 自定义
2. **安全设置**（三选一）：
   - ✅ **自定义关键词**（推荐）：设置 `日报`、`Data` 等关键词
   - 🔐 **加签**：记下 Secret → 配置到 `DINGTALK_SECRET`
   - 🌐 **IP 白名单**：填入服务器出口 IP
3. **复制 Webhook URL** → 配置到 `DINGTALK_WEBHOOK_URL`
</details>

<details>
<summary><b>🇨🇳 飞书 (Feishu / Lark)</b></summary>

1. **创建机器人**：目标群 → 设置 → 群机器人 → 添加机器人 → 自定义机器人
2. **安全设置**（可选）：启用签名校验 → 配置 `FEISHU_SECRET`
3. **复制 Webhook URL** → 配置到 `FEISHU_WEBHOOK_URL`
4. **交互卡片模式**：`python scripts/send_feishu.py --card --link-url https://...`
5. ⚠️ 限制：每分钟 5 条，每小时 100 条
</details>

<details>
<summary><b>🌍 Slack</b></summary>

1. 访问 https://api.slack.com/apps → Create New App
2. Features → Incoming Webhooks → 开启
3. "Add New Webhook to Workspace" → 选择目标频道
4. **复制 Webhook URL** → 配置到 `SLACK_WEBHOOK_URL`
</details>

<details>
<summary><b>🌍 Discord</b></summary>

1. 频道 → 编辑频道 (⚙️) → 整合 → Webhooks → 新建 Webhook
2. 自定义名称和头像
3. **复制 Webhook URL** → 配置到 `DISCORD_WEBHOOK_URL`
4. ⚠️ 限制：Embed 描述 4096 字符，每秒 5 次请求
</details>

<details>
<summary><b>🌍 Telegram</b></summary>

1. 搜索 `@BotFather` → `/newbot` → 获取 **Bot Token**
2. **获取 Chat ID**：将 `@userinfobot` 添加到群，或使用 `@频道用户名`
3. 配置 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID`
4. ⚠️ 限制：每秒 30 条，群组每分钟 20 条
</details>

<details>
<summary><b>🌍 Microsoft Teams</b></summary>

1. 频道 → `···` → Workflows → "Post to a channel when a webhook request is received"
2. **复制 Webhook URL** → 配置到 `TEAMS_WEBHOOK_URL`
3. 旧版兼容模式：`python scripts/send_teams.py --legacy`
4. ⚠️ 限制：Adaptive Card 约 28KB，每秒约 4 次
</details>

## 🎨 自定义

### 切换到你的行业

默认配置以 Data+AI 为例，但适配到你的行业只需两步：

**第一步：修改 `daily-brief-config.json`** — 更改 `focus_areas`：

```json
{
  "customization": {
    "focus_areas": ["金融科技", "数字银行", "支付基础设施", "监管科技"]
  }
}
```

**第二步：编辑 `SKILL.md`** — 更新 Prompt 指令：

- 更改行业范围和厂商关注列表
- 调整信源要求（适配你的行业）
- 修改输出板块（如为金融加上"监管动态"）
- 设置输出语言

**示例：金融科技日报**
```
将 "数据平台" 替换为 → "金融科技"
将厂商列表替换为 → Stripe, Plaid, Adyen, 蚂蚁集团, etc.
将开源项目替换为 → Hyperledger, OpenBanking APIs, etc.
```

### 自定义 HTML 模板

编辑 `assets/report-template.html`，修改颜色、布局和品牌标识。

## 📋 默认覆盖范围（Data+AI）

内置配置覆盖以下 Data+AI 领域：

- **行业领域**：大数据 · 数据平台 · 数据基础设施 · 数据治理 · 数据工程 · 湖仓架构 · 查询引擎 · 流批处理 · 向量检索 · 开源数据生态
- **头部厂商**：AWS · Google Cloud · Azure · Databricks · Snowflake · 阿里云 · 腾讯云 · 华为云 · 火山引擎 · Confluent · MongoDB · ClickHouse · dbt Labs
- **开源项目**：Iceberg · Hudi · Paimon · Delta Lake · Trino · Spark · Flink · Kafka · DuckDB · StarRocks · Doris
- **分析师机构**：Gartner · Forrester · IDC · a16z · Sequoia · 信通院 · 赛迪研究院 · 艾瑞咨询 · 头部券商研报

## ❤️ 支持本项目

如果这个项目对你有帮助，欢迎 [成为 Sponsor](https://github.com/sponsors/haiyangchenbj)，你的支持是持续维护和改进的动力。

## 🤝 参与贡献

欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献指南。

## 📄 开源协议

[MIT License](LICENSE) — 自由使用、修改和分发。

---

**为每一个需要行业情报的人而构建 ❤️**
