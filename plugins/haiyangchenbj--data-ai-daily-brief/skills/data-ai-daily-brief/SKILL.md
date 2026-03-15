---
name: data-ai-daily-brief
description: "AI-powered industry intelligence daily brief generator. This skill automatically searches,\n filters, writes, and delivers structured daily briefings for any industry.\n Default configuration covers Data+AI (data platforms, lakehouse, streaming, governance, etc.),\n but can be customized for FinTech, HealthTech, Cybersecurity, DevTools, or any domain.\n Trigger keywords: daily brief, 日报, industry report, 行业日报, data+ai report, 数据平台日报,\n 全球日报, industry newsletter, intelligence brief, 情报简报."
---

# AI 行业情报日报生成器

一个 AI 驱动的行业情报日报生成技能，自动搜集、过滤、编写并推送高质量的行业日报。默认以 Data+AI 行业为例，可通过配置文件切换至任何行业。

## 工作流程

当用户请求生成日报时，按以下步骤执行：

### Step 1: 确认配置

1. 读取工作区中的 `daily-brief-config.json` 配置文件（如果存在）
2. 如不存在，使用 `scripts/init_config.py` 初始化默认配置
3. 确认目标日期（默认当天）和输出渠道

### Step 2: 信息采集与过滤

使用 web_search 工具，按以下优先级和过滤规则采集信息：

#### 核心原则

**数据平台优先，严格过滤。** 每条信息必须能明确回答：这会影响企业数据平台的产品路线、架构设计、成本结构、治理方式、运维效率或 Agent 在数据场景的落地吗？如果不能明确回答"是"，一律不纳入。

**信息宁缺毋滥。** 绝不因为某个板块条目过少而降低准入标准放入低相关性内容。如果某个板块（如 B. Product & Tech）当日没有合格信息，该板块留空，在总判断中简要说明即可。日报的价值在于精准，不在于条数多。

#### 覆盖范围

**严格只覆盖过去24小时内首次公开发布的信息。** 聚焦：
- 大数据、数据平台、数据基础设施
- 数据治理、数据工程、数据智能平台
- 湖仓架构、查询引擎、流批处理
- 向量检索基础设施、开源数据生态

AI 相关信息**仅在明确影响数据平台**时才纳入。

#### 严格排除

- 纯 AI 新闻（纯模型发布、纯 benchmark、纯消费级 AI 产品）
- 财经媒体、大众媒体的二手报道和分析
- 搬运号、标题党、无来源转述

#### 厂商关注优先级

**第一优先级（全球+中国头部）：**
AWS、Google Cloud、Microsoft Azure、Databricks、Snowflake、阿里云、腾讯云、华为云、字节跳动火山引擎

**第二优先级（重要厂商）：**
Confluent、MongoDB、Elastic、ClickHouse、Cloudera、Starburst/Trino、dbt Labs、Fivetran、Airbyte、Dataiku、Palantir、百度智能云、京东云

#### 开源项目与社区

Iceberg、Hudi、Paimon、Delta Lake、Trino、Spark、Flink、Ray、Airflow、Kafka、dbt、ClickHouse、DuckDB、Milvus、Weaviate、Lance/LanceDB、StarRocks、Doris、SeaTunnel、Amoro 等。

#### 分析师机构与行业研报

**全球头部分析师机构：** Gartner、Forrester、IDC、a16z、Sequoia、Bessemer 等。

**国内知名研究机构：** 中国信息通信研究院（信通院）、赛迪研究院（CCID）、中国电子技术标准化研究院（电子标准院）、艾瑞咨询、亿欧智库等。

**头部券商研报：** 国内外头部券商研报中与数据平台直接相关的核心论点和数据。券商研报与财经证券分析一律归入 D. Analyst Insights，不得放入 B 类或其他类别。

每条需注明：机构名称、报告来源、核心数据/预测、对数据平台的直接映射。

#### 信源要求

**仅接受一手来源：**
- 官网、官方博客、官方文档、release notes、GitHub 官方仓库
- 论文原文、官方 keynote
- 创始人/CEO/CTO/Chief Architect 的原始发言
- earnings call 原始记录
- 分析师机构官方报告、头部券商研报
- 通过 PR Newswire/Business Wire/GlobeNewswire 发布的官方新闻稿

### Step 3: 编写日报

#### 搜索策略

对以下关键词分别进行 web_search（使用英文和中文各一轮）：

**英文搜索：**
1. `"data platform" OR "data infrastructure" release announcement {date_range}`
2. `Databricks OR Snowflake OR "data lakehouse" announcement {date_range}`
3. `Apache Iceberg OR Hudi OR Paimon OR "Delta Lake" release {date_range}`
4. `"data governance" OR "data catalog" OR "data quality" announcement {date_range}`
5. `Gartner OR Forrester OR IDC "data platform" OR "data analytics" {date_range}`
6. `ClickHouse OR DuckDB OR StarRocks OR Doris release update {date_range}`

**中文搜索：**
1. `数据平台 OR 数据基础设施 发布 公告`
2. `湖仓一体 OR 数据湖 OR 数据治理 新品`
3. `阿里云 OR 腾讯云 OR 华为云 数据 发布`

对搜索结果进行交叉验证，每条信息追溯到一手来源。

#### 输出格式

标题：`《Data+AI 全球日报 | YYYY-MM-DD》`

**开头：**
- 今日最重要的3个变化（一句话概括）
- 一句总判断：今天行业信号更偏向平台整合、成本优化、治理强化、Agent落地或开源加速中的哪一类

**正文板块：**

**A. Top Signals（3条）**
每条包含：事件标题、来源（具体出处+链接）、摘要（2-3句）、为什么对数据平台重要

**B. Product & Tech（0-6条，宁缺毋滥）**
严格限定为数据平台相关的产品与技术动态，仅包括：云厂商数据产品发布/功能更新/版本升级、开源数据项目版本发布/重大PR合并、数据平台技术框架组件升级、数据工具链新版本。
以下内容不属于 B 类：政策文件、股市行情、券商研报、行业分析、基础设施（电力/散热/芯片）动态、AI模型发布（除非直接集成到数据平台产品中）。
如果当日确实没有合格的产品/技术发布，B 类留空并在总判断中说明，不得为了填充而放入不相关内容。
每条包含：事件标题、来源、摘要（1-2句）、对数据平台的影响判断

**C. People & Views（1-3条）**
每条包含：人物及职位、原始来源、核心观点、映射到数据平台的判断

**D. Analyst Insights（1-3条）**
统一归集全球分析师机构（Gartner/Forrester/IDC）、国内研究机构（信通院/赛迪/艾瑞等）、头部券商研报（国内外）以及顶级投资机构的行业分析。
券商研报与财经证券分析一律归入此类，不得放入 B 类或其他类别。
每条包含：机构名称、报告/来源、核心论点和数据、对数据平台的映射。
筛选标准：仅纳入与数据平台成本、架构、市场格局直接相关的研报论点。

**E. Watchlist（1-3条）**
值得继续跟踪但尚未定论的信息

**要求：**
- 输出中文，专业、简洁、克制
- 每条信息必须有：来源（具体链接或出处）、摘要、影响判断
- 总量控制在 8-12 条，宁少勿滥
- 不杜撰数据

### Step 4: 生成输出文件

1. **生成 Markdown 文件**：`Data+AI全球日报_{date}.md`
2. **生成 HTML 文件**：使用 `assets/report-template.html` 模板，生成美观的 HTML 版本 `Data+AI全球日报_{date}.html`
   - HTML 中每条信息的来源带有可点击的超链接
   - 使用现代化的卡片式布局

### Step 5: 推送（按配置）

根据 `daily-brief-config.json` 中的配置，执行推送。支持以下 **9 大渠道**：

#### 国内渠道

1. **企业微信**：`scripts/send_wecom.py`
   - 先发精简摘要版（<4096字节），再发完整版 HTML 文件
   - **摘要中不带任何链接**，保持纯文本阅读体验，来源仅以文字标注
   - **所有来源链接仅在 HTML 完整版中呈现**
   - 配置：群机器人 Webhook URL → `WECOM_WEBHOOK_URL`

2. **钉钉**：`scripts/send_dingtalk.py`
   - 支持 Markdown 消息 + 链接消息，支持加签安全验证
   - 配置：群机器人 Webhook → `DINGTALK_WEBHOOK_URL`，可选加签 → `DINGTALK_SECRET`
   - 限制：每分钟最多 20 条消息

3. **飞书**：`scripts/send_feishu.py`
   - 支持富文本（post）和交互卡片（含按钮）两种模式
   - 配置：群机器人 Webhook → `FEISHU_WEBHOOK_URL`，可选签名 → `FEISHU_SECRET`
   - 卡片模式：`--card --link-url <URL>`
   - 限制：每分钟 5 条，每小时 100 条

#### 国际渠道

4. **Slack**：`scripts/send_slack.py`
   - 使用 Block Kit 富消息格式，支持按钮链接
   - 配置：Incoming Webhook URL → `SLACK_WEBHOOK_URL`

5. **Discord**：`scripts/send_discord.py`
   - 使用 Embed 消息格式，支持文件上传
   - 配置：Webhook URL → `DISCORD_WEBHOOK_URL`
   - 限制：Embed 描述 4096 字符，每秒 5 次

6. **Telegram**：`scripts/send_telegram.py`
   - 通过 Bot API 推送 HTML 格式消息，支持文件上传
   - 配置：Bot Token → `TELEGRAM_BOT_TOKEN`，Chat ID → `TELEGRAM_CHAT_ID`
   - 限制：消息 4096 字符，每秒 30 条

7. **Microsoft Teams**：`scripts/send_teams.py`
   - 支持 Adaptive Card（推荐）和旧版 MessageCard 格式
   - 配置：Incoming Webhook → `TEAMS_WEBHOOK_URL`
   - 旧版兼容：`--legacy`

#### 通用渠道

8. **邮件**：`scripts/send_email.py`
   - SMTP 邮件推送，HTML 正文 + 纯文本备选
   - 配置：`SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAIL_TO`

9. **GitHub Pages**：`scripts/deploy_github.py`
   - 部署到 GitHub Pages 作为公开访问的网页，自动归档历史版本
   - 配置：`GITHUB_TOKEN`, `GITHUB_USER`

## 自定义指南

### 修改关注领域

编辑 `daily-brief-config.json` 中的 `customization` 字段，可自定义：
- 关注的行业领域（默认 Data+AI）
- 厂商优先级列表
- 开源项目列表
- 输出语言和格式

### 添加推送渠道

在 `daily-brief-config.json` 的 `adapters` 中启用渠道并填入配置：

| 渠道 | 配置键 | 类型 | 主要环境变量 |
|------|--------|------|-------------|
| 企业微信 | `wechatwork` | Webhook | `WECOM_WEBHOOK_URL` |
| 钉钉 | `dingtalk` | Webhook | `DINGTALK_WEBHOOK_URL`, `DINGTALK_SECRET` |
| 飞书 | `feishu` | Webhook | `FEISHU_WEBHOOK_URL`, `FEISHU_SECRET` |
| Slack | `slack` | Webhook | `SLACK_WEBHOOK_URL` |
| Discord | `discord` | Webhook | `DISCORD_WEBHOOK_URL` |
| Telegram | `telegram` | Bot API | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` |
| Teams | `teams` | Webhook | `TEAMS_WEBHOOK_URL` |
| 邮件 | `email` | SMTP | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` |
| GitHub | `github` | API | `GITHUB_TOKEN`, `GITHUB_USER` |

### 调整定时任务

修改 `daily-brief-config.json` 中的 `cron` 配置：
```json
{
  "schedule": "0 8 * * 1-5",
  "timezone": "Asia/Shanghai"
}
```
