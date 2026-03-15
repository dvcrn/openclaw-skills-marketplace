# 定时调度说明

本技能更适合拆成两个独立部分：

1. **词库同步**：按需手动触发，尤其是在涉及登录状态与浏览器交互时
2. **每日推送**：在词库已经准备好的前提下，由调度器自动触发

不建议把每日调度设计成每天重新打开浏览器、检查登录并重新抓词。
更稳定的方式是：

- 需要时再同步收藏词
- 调度器只负责从现有词库中选择并发送今日单词

## 推荐方案：OpenClaw cron

推荐的定时执行命令：

```bash
cd /Users/zhonghanwen/.openclaw/workspace/skills/word-vault-revival && npm run send
```

## 推荐顺序

1. 先确认至少完成过一次词库同步
2. 运行 `npm run test-message` 检查输出
3. 再配置循环任务，例如每天 09:00 执行一次

## 为什么这样更合理

登录状态与页面抓取属于浏览器交互问题，通常需要人工介入。
每日推送则不同：它只依赖已有的本地词库和推送目标，因此更适合自动化。

## 可选调度器

以下几种方式都可以：

- OpenClaw cron
- OpenClaw heartbeat
- 系统级调度器，如 `launchd` 或 `cron`

## 最小验证

```bash
cd /Users/zhonghanwen/.openclaw/workspace/skills/word-vault-revival
npm run send
```

## 建议自动化的范围

建议自动化的仅是：

```bash
npm run send
```

而不是整段：

```text
打开浏览器 → 登录 → 抓取页面 → 同步 → 发送
```
