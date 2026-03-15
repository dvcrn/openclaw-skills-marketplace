---
name: websocket-receiver
description: "WebSocket data receiver skill for learning and practice. Supports auto-reconnect, batch processing, and AI analysis."
---

# WebSocket Receiver v1.1.2

🎓 这是一个 WebSocket 对接的练手 skill，适合学习如何：
- 建立和维护 WebSocket 长连接
- 处理实时数据流
- 实现自动重连和错误恢复
- 批量处理和 AI 分析集成

可作为模板，修改后对接你自己的 WebSocket 数据源。

## 特性

- 🔌 自动重连（指数退避）
- 📦 批量数据处理
- 🤖 可选 AI 分析集成
- 📊 日志轮转
- 🛑 优雅关闭（处理完缓冲区再退出）
- 💾 JSONL 数据持久化

## 安装

```bash
# 安装依赖
pip install websockets

# 或使用 venv
~/clawd/venv/bin/pip install websockets
```

## 获取 WebSocket 地址

⚠️ 本 skill 仅供学习练手，不包含真实数据源。

配套的测试服务端每隔 10 秒推送一条模拟数据，方便你观察接收和批量处理流程。

如需测试，你可以：
1. 联系作者获取测试服务器地址
2. 自己搭建一个 WebSocket 服务器
3. 使用公开的测试 WebSocket

配置方式：
- 环境变量：`WEBSOCKET_URL=ws://your-server:port/ws`
- 配置文件：`~/.openclaw/websocket-config.json`

## 快速开始

```bash
# 前台测试（替换为你的真实地址）
WEBSOCKET_URL=ws://your-server:port/ws websocket-receiver test

# 后台运行
WEBSOCKET_URL=ws://your-server:port/ws websocket-receiver start

# 查看状态
websocket-receiver status

# 查看日志
websocket-receiver logs

# 停止
websocket-receiver stop
```

## 配置

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `WEBSOCKET_URL` | WebSocket 服务器地址 | (需配置) |
| `WEBSOCKET_BATCH` | 批次大小 | `10` |
| `WEBSOCKET_DATA_DIR` | 数据目录 | `~/clawd/data/websocket` |
| `WEBSOCKET_CONFIG` | 配置文件路径 | `~/.openclaw/websocket-config.json` |

### 配置文件

创建 `~/.openclaw/websocket-config.json`（替换为你申请到的地址）：

```json
{
  "ws_url": "ws://your-server:port/ws",
  "batch_size": 10,
  "auto_analyze": true,
  "data_dir": "~/clawd/data/websocket",
  "reconnect_delay": 2,
  "reconnect_max_delay": 60,
  "reconnect_max_attempts": 0
}
```

### 配置项说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `ws_url` | WebSocket URL | (需配置) |
| `batch_size` | 触发批量处理的消息数 | `10` |
| `auto_analyze` | 是否自动 AI 分析 | `true` |
| `data_dir` | 数据存储目录 | `~/clawd/data/websocket` |
| `reconnect_delay` | 初始重连延迟（秒） | `2` |
| `reconnect_max_delay` | 最大重连延迟（秒） | `60` |
| `reconnect_max_attempts` | 最大重连次数（0=无限） | `0` |
| `connect_timeout` | 连接超时（秒） | `30` |
| `ping_interval` | 心跳间隔（秒） | `30` |
| `ping_timeout` | 心跳超时（秒） | `10` |

## 命令

```bash
websocket-receiver start    # 后台启动
websocket-receiver stop     # 停止
websocket-receiver restart  # 重启
websocket-receiver status   # 查看状态
websocket-receiver logs     # 实时日志
websocket-receiver config   # 查看/创建配置
websocket-receiver test     # 前台测试
```

## 数据格式

接收的 JSON 消息格式：

```json
{
  "id": "unique-id",
  "title": "标题",
  "content": "内容",
  "url": "链接",
  "timestamp": "2026-03-12T12:00:00Z"
}
```

数据保存为 JSONL 格式：

```json
{"received_at": "2026-03-12T12:00:00", "data": {...}}
```

## 文件结构

```
~/clawd/data/websocket/
├── receiver.pid          # PID 文件
├── receiver.log          # 日志（自动轮转）
├── data_20260312_14.jsonl  # 按小时分割的数据
├── data_20260312_15.jsonl
└── analysis_20260312.md  # AI 分析报告
```

## 自定义处理

```python
from receiver import WebSocketReceiver

receiver = WebSocketReceiver(config)

# 自定义消息处理
def my_handler(data):
    print(f"Received: {data}")
    return True  # 返回 True 表示处理成功

receiver.on_message = my_handler

# 自定义批量处理（支持 async）
async def my_batch_handler(batch):
    # 自定义分析逻辑
    return "分析结果"

receiver.on_batch = my_batch_handler

receiver.run()
```

## 依赖

- Python 3.8+
- websockets

## 版本历史

### v1.1.2
- 强制配置 WebSocket 地址，未配置时启动报错

### v1.1.1
- 重写核心逻辑，提升稳定性
- 添加指数退避重连
- 异步 subprocess 调用
- 优雅关闭机制
- 日志轮转
- 正确的 PID 管理

### v1.0.0
- 初始版本

## License

MIT
