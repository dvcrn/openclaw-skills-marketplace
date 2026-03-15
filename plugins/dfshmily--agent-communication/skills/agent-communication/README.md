# Agent Communication Skill

<div align="center">

一个通用的 **Agent间沟通技能**，基于 **WebSocket** 实现实时双向通信

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://clawhub.ai/skills/agent-communication)
[![WebSocket](https://img.shields.io/badge/WebSocket-实时通信-green.svg)](#websocket架构)
[![Test](https://img.shields.io/badge/test-passing-brightgreen.svg)](#测试报告)

</div>

---

## 🚀 核心技术：WebSocket 实时通信

### WebSocket 架构

```
┌─────────────────────────────────────────────────────┐
│            WebSocket 消息代理架构                     │
├─────────────────────────────────────────────────────┤
│                                                     │
│   Agent A  ◄────►  WebSocket  ◄────►  Agent B      │
│                     Server                          │
│   Agent C  ◄──────────────────────►  Agent D       │
│                                                     │
│   ✅ 实时双向通信                                    │
│   ✅ 无需轮询                                        │
│   ✅ 延迟 <1ms                                       │
│   ✅ 离线消息队列                                    │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 解决的问题

| 问题 | 解决方案 |
|------|---------|
| `sessions_send` 超时 | **WebSocket 实时通信** |
| Agent 无法直接沟通 | 消息代理转发 |
| 团队协作效率低 | 即时消息传递 |

---

## ✨ 核心功能

- 🚀 **WebSocket 实时通信** - 高性能双向通信（延迟 <1ms）
- 📨 **消息传递** - Agent 之间快速发送消息
- 📢 **广播消息** - 一次发送给多个 Agent
- 🗂️ **共享工作空间** - 文件驱动的协作
- 🟢 **状态同步** - Agent 在线状态检测
- 💾 **离线消息队列** - 离线 Agent 自动排队

---

## 📦 安装

```bash
# 安装依赖
pip install websockets

# 通过 ClawHub 安装
openclaw skill install agent-communication

# 或手动安装
git clone https://github.com/DFshmily/agent-communication.git
```

---

## 🚀 快速开始

### 1. 启动 WebSocket 消息代理

```bash
python3 scripts/broker.py
```

服务器将在 `ws://localhost:8765` 启动

---

### 2. 发送消息

```bash
# WebSocket 模式（优先，延迟 <1ms）
python3 scripts/send.py --from pm --to dev --message "开始开发任务"

# 文件模式（回退，延迟 ~500ms）
python3 scripts/send.py --from pm --to dev --message "开始" --file
```

---

### 3. 广播消息

```bash
python3 scripts/broadcast.py --from main --message "项目启动" --agents pm,dev,test
```

---

### 4. Agent 客户端连接

```python
import asyncio
import websockets
import json

async def agent_client():
    async with websockets.connect('ws://localhost:8765') as ws:
        # 注册
        await ws.send(json.dumps({'type': 'register', 'agent_id': 'pm'}))
        
        # 发送消息
        await ws.send(json.dumps({
            'type': 'send',
            'from': 'pm',
            'to': 'dev',
            'message': '开始开发'
        }))
        
        # 接收消息
        async for msg in ws:
            data = json.loads(msg)
            if data.get('type') == 'message':
                print(f"收到: {data['from']} -> {data['message']}")

asyncio.run(agent_client())
```

---

## 📊 性能测试结果

### 广播消息测试

| Agent | 延迟 | 状态 |
|-------|------|------|
| PM | 0.81ms | ✅ |
| Dev | 1.05ms | ✅ |
| Test | 0.61ms | ✅ |

**平均延迟：0.82ms** ⭐

---

### 实时双向通信测试

| 方向 | 延迟 |
|------|------|
| PM → Dev | 0.81ms |
| Dev → Test | 1.05ms |
| Test → PM | 0.61ms |

---

## 📁 文件结构

```
agent-communication/
├── scripts/
│   ├── broker.py           # WebSocket 消息代理服务器
│   ├── websocket_client.py # Agent 客户端
│   ├── send.py             # 发送消息（智能选择 WebSocket/文件）
│   ├── broadcast.py        # 广播消息
│   ├── status.py           # 状态管理
│   └── workspace.py        # 共享工作空间
├── data/
│   ├── messages/           # 消息存储
│   ├── status/             # Agent 状态
│   └── workspace/          # 共享数据
└── templates/
    └── config.json         # 配置文件
```

---

## 📋 API 文档

### WebSocket 消息类型

#### 注册
```json
{"type": "register", "agent_id": "pm"}
```

#### 发送消息
```json
{
  "type": "send",
  "from": "pm",
  "to": "dev",
  "message": "开始开发",
  "priority": "normal"
}
```

#### 广播消息
```json
{
  "type": "broadcast",
  "from": "main",
  "message": "项目启动",
  "agents": ["pm", "dev", "test"]
}
```

#### 状态查询
```json
{"type": "status"}
```

---

## 🔧 配置

编辑 `templates/config.json`：

```json
{
  "websocket": {
    "host": "0.0.0.0",
    "port": 8765
  },
  "agents": ["pm", "dev", "test", "main"],
  "retry": 3,
  "timeout": 300
}
```

---

## 版本历史

### v2.0.0 (2026-02-28)
- 🚀 升级到 WebSocket 实时通信
- ⚡ 延迟从 500ms 降低到 <1ms
- ✅ 支持离线消息队列
- ✅ 广播消息功能
- ✅ 实时双向通信

### v1.0.0 (2026-02-27)
- 初始版本
- 文件驱动消息队列

---

<div align="center">

**Made with ❤️ for OpenClaw Agents**

</div>