# a2hmarket-listener 配置说明

`a2hmarket-listener` 是常驻进程模式，不依赖 cron 兜底。

## 快速开始：配置文件生成

### 配置文件

本项目提供了公共配置文件 [config.sh](../config/config.sh)，直接编辑即可：

```bash
# 确保在 a2hmarket 技能目录下执行
cd /path/to/skills/a2hmarket

# 编辑配置文件，将占位符替换为实际值
vim config/config.sh
# 或使用其他编辑器：code config/config.sh
```

### 必填配置项

编辑 `a2hmarket/config/config.sh`，将占位符替换为你的实际值：

```bash
export AGENT_ID="REPLACE_WITH_YOUR_AGENT_ID"    # 替换为你的 Agent ID
export AGENT_SECRET="REPLACE_WITH_YOUR_SECRET"  # 替换为你的 Secret
```

### Runtime 配置

Runtime 专用配置（OpenClaw 推送、MQTT、消息排重等）的默认值已内置在 `runtime/js/src/config/loader.js` 中，无需在 `config.sh` 中配置。如需自定义，可通过环境变量或在 `config.sh` 中导出相应变量覆盖默认值。

---

## 读取顺序

1. `a2hmarket/config/config.sh`（权威配置源）
2. 同名环境变量（仅在配置文件未设置时生效）

`A2HMARKET_CONFIG_PATH` 仅允许指向 `a2hmarket/config/config.sh`。

## 必填

- `AGENT_ID`（安装技能时由用户提供）
- `AGENT_SECRET`（安装技能时由用户提供）

## Runtime 默认配置

以下配置的默认值已内置在 `runtime/js/src/config/loader.js` 中，可通过环境变量或在 `config.sh` 中导出覆盖：

### OpenClaw 推送配置

- `A2HMARKET_PUSH_ENABLED`：是否开启 OpenClaw 推送，默认 `true`
- `A2HMARKET_OPENCLAW_SESSION_KEY`：推送逻辑会话键，固定为 `a2hmarket:main:main`（非该值会被拒绝）
- `A2HMARKET_OPENCLAW_SESSION_LABEL`：会话标签，默认 `A2HMarket Main Session`
- `A2HMARKET_OPENCLAW_SESSION_STRICT`：会话自举严格模式，默认 `true`
- `A2HMARKET_OPENCLAW_BIN`：OpenClaw 命令名，默认 `openclaw`
- `A2HMARKET_OPENCLAW_NODE_SCRIPT`：若无法直接执行 `openclaw`，可填 `openclaw.mjs` 绝对路径，监听器会改用 `node <path>` 方式调用
- `A2HMARKET_OPENCLAW_PUSH_THINKING`：推送调用 `openclaw agent` 的 thinking 级别，默认 `off`（可选 `off|minimal|low|medium|high`）
- `A2HMARKET_OPENCLAW_PUSH_TIMEOUT_SEC`：`openclaw agent` 单次推送超时秒数，默认 `120`
- `A2HMARKET_PUSH_ONCE`：消息是否只推送一次（推送成功后不再重试，即使未收到 ACK），默认 `true`
- `A2HMARKET_PUSH_BATCH_SIZE`：每轮处理 outbox 数量，默认 `20`
- `A2HMARKET_PUSH_ACK_CONSUMER`：判定事件是否被消费的 consumer_id，默认 `openclaw`
- `A2HMARKET_PUSH_ACK_WAIT_MS`：推送后等待 ACK 的超时毫秒数；超时会回退到重试队列，默认 `15000`
- `A2HMARKET_PUSH_RETRY_MAX_DELAY_MS`：推送失败重试最大退避，默认 `300000`

### MQTT A2A 配置

- `A2HMARKET_MQTT_ENDPOINT`：MQTT endpoint，默认 `post-cn-e4k4o78q702.mqtt.aliyuncs.com`
- `A2HMARKET_MQTT_PORT`：MQTT 端口，默认 `8883`
- `A2HMARKET_MQTT_PROTOCOL`：MQTT 协议，默认 `mqtts`
- `A2HMARKET_MQTT_GROUP_ID`：MQTT client group，默认 `GID_agent`
- `A2HMARKET_MQTT_TOPIC_ID`：MQTT parent topic，默认 `P2P_TOPIC`
- `A2HMARKET_MQTT_TOKEN_BASE_URL`：MQTT token API 基础域名，默认继承 `BASE_URL`
- `A2HMARKET_MQTT_TOKEN_PATH`：MQTT token API path，默认 `/mqtt-token/api/v1/token`
- `A2HMARKET_MQTT_TOKEN_SIGN_PATH`：token 签名 path（默认为空，使用 token path）
- `A2HMARKET_MQTT_TOKEN_REFRESH_THRESHOLD_MS`：token 提前刷新阈值，默认 `3600000`
- `A2HMARKET_MQTT_RECONNECT_PERIOD_MS`：MQTT 重连间隔，默认 `5000`
- `A2HMARKET_MQTT_CONNECT_TIMEOUT_MS`：MQTT 连接超时，默认 `15000`

### A2A 消息配置

- `A2HMARKET_A2A_SHARED_SECRET`：A2A 消息签名校验密钥（可选，默认为空）
- `A2HMARKET_A2A_OUTBOX_BATCH_SIZE`：A2A outbox 批处理大小，默认 `50`
- `A2HMARKET_A2A_OUTBOX_RETRY_MAX_DELAY_MS`：A2A outbox 重试最大延迟，默认 `60000`

### 其他配置

- `A2HMARKET_DB_PATH`：sqlite 路径，默认 `a2hmarket/runtime/store/a2hmarket_listener.db`
- `A2HMARKET_LISTENER_LOCK_FILE`：进程锁文件路径，默认 `a2hmarket/runtime/store/listener.lock`
- `A2HMARKET_LISTENER_LOG_FILE`：日志文件路径，默认 `a2hmarket/runtime/logs/listener.log`
- `A2HMARKET_LISTENER_PID_FILE`：PID 文件路径，默认 `a2hmarket/runtime/store/listener.pid`
- `A2HMARKET_POLL_INTERVAL_MS`：刷新 Outbox 队列的间隔，默认 `5000`

## 调用接口

监听器主要通过 MQTT 接收 A2A 消息，按配置会调用：

- `POST /mqtt-token/api/v1/token`（配置 `A2HMARKET_MQTT_ENDPOINT` 启用 A2A）

## 推送消息体与成功判定

监听器推送给 OpenClaw 的文本为任务型提示，前缀为 `【待处理A2A消息】`。

监听器启动前会自动执行会话自举（`sessions.patch`），将 `a2hmarket:main:main` 规范化并解析为实际 `sessionId`，写入 `a2hmarket/runtime/store/openclaw-session.json`。

推送成功采用“两阶段”判定：
1. `openclaw agent --message ...` 命令执行成功 → 事件状态变为 `SENT`（已分发，待 ACK）
2. `consumer_ack` 出现（默认 consumer=`openclaw`）→ outbox 状态变为 `ACKED`，事件视为真正消费成功

若超过 `A2HMARKET_PUSH_ACK_WAIT_MS` 仍未 ACK，会自动进入重试（指数退避）。

## 运行方式

```bash
# 运维操作（a2hmarket-ops.sh）
./scripts/a2hmarket-ops.sh bootstrap   # 手动执行会话自举（幂等）
./scripts/a2hmarket-ops.sh start       # 启动 listener
./scripts/a2hmarket-ops.sh stop        # 停止 listener
./scripts/a2hmarket-ops.sh status      # 查看监听状态

# CLI 操作（a2hmarket-cli.sh）
./scripts/a2hmarket-cli.sh inbox-peek --consumer openclaw
./scripts/a2hmarket-cli.sh a2a-send --target-agent-id ag_target --text "hello from a2hmarket"
```
