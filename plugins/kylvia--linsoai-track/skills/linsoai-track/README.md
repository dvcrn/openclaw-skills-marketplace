# linsoai-track

定时任务管理 OpenClaw Skill。用自然语言创建和管理定时任务，AI 自动执行并通知结果。

## 安装

```bash
openclaw skills install linsoai-track
```

## 快速开始

安装后，直接用自然语言描述你的需求：

```
"帮我创建一个每天早上9点的任务，查看BTC价格变化，如果波动超过5%就通知我"
```

Skill 会自动将你的描述转化为定时任务：

```bash
openclaw cron add \
  --name "BTC价格监控" \
  --cron "0 9 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "查看当前BTC价格变化，如果波动超过5%，用 openclaw message send 通知我。"
```

### 更多示例

**每3小时检查一次服务器状态：**
```
"每3小时检查一下我的服务器 api.example.com 是否正常，异常就通知我"
```

**每周一生成周报：**
```
"每周一上午10点帮我汇总上周AI领域新闻，生成周报发到我的飞书"
```

**一次性提醒：**
```
"3月15号下午2点提醒我域名要到期了"
```

## 管理任务

```
"看看我有哪些定时任务"
"暂停BTC价格监控"
"删除服务器状态检查任务"
"手动跑一次每周报告"
```

## 通知配置

### IM 通知（推荐）

开箱即用，支持 Telegram、飞书、Discord、Slack 等 18 个渠道：

```bash
# 先配置渠道
openclaw channels add telegram --token <BotToken> --chat <ChatID>
```

### 邮件通知

需要安装 send-email skill 并配置 SMTP：

```bash
openclaw skills install send-email
```

详见 [通知配置指南](references/NOTIFICATIONS.md)。

## 从 Linso Task 迁移

如果你是 Linso Task 用户，可以快速将现有任务迁移过来：

### 方式一：自然语言重建（推荐）

直接告诉 Skill 你想要什么任务，它会帮你创建。你不需要记命令。

### 方式二：批量导入

1. 登录 Linso Task → 设置 → 导出到 OpenClaw
2. 复制导出的命令
3. 使用导入脚本：

```bash
# 从剪贴板导入
pbpaste | openclaw run node ./skills/linsoai-track/scripts/import-tasks.js

# 从文件导入
openclaw run node ./skills/linsoai-track/scripts/import-tasks.js exported-commands.txt
```

4. 检查导入结果：
```
"看看我的定时任务列表"
```

## 依赖

- **Node.js** — 导入脚本需要（OpenClaw 环境已内置）
- **send-email skill**（可选）— 邮件通知功能需要

## 参考文档

- [任务模板库](references/TEMPLATES.md) — 常用任务模板
- [调度频率速查](references/SCHEDULING.md) — cron 表达式和时区
- [通知配置指南](references/NOTIFICATIONS.md) — 邮件、IM、Webhook 配置
