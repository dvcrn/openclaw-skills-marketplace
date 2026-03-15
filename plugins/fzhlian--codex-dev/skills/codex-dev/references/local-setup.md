# Local setup | 本地配置

This package publishes a skill, not a full OpenClaw runtime state.

这个包发布的是 skill，不是你本机完整的 OpenClaw 运行状态。

It is best suited for local async development workflows where you want:

- an immediate job receipt
- saved logs and patch artifacts
- optional Telegram completion messages
- a user-selectable working directory

它特别适合这样的本地异步开发场景：

- 先拿到作业回执
- 保留日志和补丁产物
- 可选地把完成结果发到 Telegram
- 允许用户指定工作目录

## What you still configure locally | 仍需本地配置的内容

- your Telegram bot token
- your Telegram chat id
- your preferred default work directory
- your OpenClaw agent binding and routing

你仍然需要在本地自行配置：

- Telegram bot token
- Telegram chat id
- 默认工作目录
- OpenClaw agent 绑定和路由

## Suggested local environment | 建议的本地环境变量

```bash
export CODEX_DEV_DEFAULT_WORKDIR="/absolute/path/to/your/repo"
export CODEX_DEV_CHAT_ID="123456789"
export TELEGRAM_BOT_TOKEN="your-bot-token"
```

## Optional wrapper install | 可选的包装命令安装

From the installed skill folder:
从已安装的 skill 目录执行：

```bash
./scripts/install-local.sh "$HOME/bin"
```

That creates:
它会创建：

- `codex-dev`
- `codex-help`
- `codex-dev-status`
- `codex-dev-show`
- `codex-dev-dispatch`

## Suggested OpenClaw agent binding | 建议的 OpenClaw agent 绑定

Create or update a dedicated Telegram-bound agent that knows:
创建或更新一个专用于 Telegram 的 agent，并确保它知道：

- write requests should use `codex-dev`
- read-only requests can answer directly
- `/codex-dev ...` is a forced async request
- `/codex-help` and `/codex-dev help` should return usage guidance

Recommended user-facing examples:

- `/codex-dev fix one bug and summarize the change`
- `/codex-dev --workdir /absolute/path fix the issue only here`
- `/codex-help`
- `/codex-dev 修一个 bug 并总结修改`
- `/codex-dev --workdir /absolute/path 只在这个目录里修复问题`
- `/codex-help`

## Suggested publish metadata | 建议的发布元数据

- slug: `codex-dev`
- version: start with `0.1.0`
- tags: `latest,codex,async,telegram`
