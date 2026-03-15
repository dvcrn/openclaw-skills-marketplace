---
name: keyue-call
description: "通过百度 AIOB 的获取 Token 与实时任务接口创建外呼任务。适用于：立即拨打电话、定时提醒电话（例如 5 分钟后拨打）、以及通过脚本自动化创建外呼任务并结合 OpenClaw cron 调度。"
---

# AIOB 外呼技能

用于稳定地创建“立即外呼”与“延时外呼”任务。

## 工作流

1. 在 `config.json` 中配置默认参数（可参考 `config.json.example`），包括：`accessKey`、`secretKey`、`robotId`、`mobile`、`callerNum`。
2. 按 `references/aiob-auth.md` 获取 `accessToken`。
3. 按 `references/aiob-realtime-task.md` 组织实时外呼请求体。
4. 使用 `scripts/create_realtime_call.py` 发起请求（命令行参数可覆盖配置文件中的默认值）。
5. 对“5 分钟后提醒我打电话”这类需求，使用 OpenClaw `cron` 做精确定时触发。

## 典型场景

### 1）立即外呼
采用配置优先模式。

示例（拨打配置文件中的默认手机号）：
```bash
cp config.json.example config.json
python3 scripts/create_realtime_call.py --config config.json
```

示例（仅覆盖被叫手机号）：
```bash
python3 scripts/create_realtime_call.py --config config.json --mobile "13333333333"
```

### 2）延时提醒外呼（例如 5 分钟后）
使用 OpenClaw `cron` 进行一次性调度。

实现模式：
1. 创建 one-shot cron 任务（`schedule.kind = "at"`），触发时间为当前时间 + 5 分钟。
2. 任务使用 isolated `agentTurn` 执行本技能流程。
3. cron 文案中写明“这是提醒电话”，并带上必要上下文。

### 3）带截止时间的排队外呼
设置 `--stop-date "yyyy-MM-dd HH:mm:ss"`，超过截止时间后 AIOB 不再继续拨打。

## 约束与防护

- 不要在用户可见回复中暴露 AK/SK 或 accessToken。
- 若接口业务码非成功，返回简洁错误原因与可执行修复建议。
- `dialogVar`、`promptVar` 必须是合法 JSON 对象。
- 单次实时外呼请求仅传一个被叫号码（`mobile`）。

## 资源说明

- `config.json.example`：默认配置模板（AK/SK/robotId/mobile/callerNum 等）。
- `references/aiob-auth.md`：Token 获取接口与认证约束。
- `references/aiob-realtime-task.md`：实时任务字段、请求和响应要点。
- `scripts/create_realtime_call.py`：配置优先、支持参数覆盖的外呼脚本。
