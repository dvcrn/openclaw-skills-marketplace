---
name: cognitive-brain
description: "Cognitive Brain"
---

# 🧠 Cognitive Brain

> **跨会话记忆与认知系统** | Cross-Session Memory & Cognition System
> 
> 让 AI 拥有像人类一样的记忆、思考和预测能力

**Version: 2.7.2** | **License: MIT**

---

## ✨ 功能特性 | Features

| 功能 | Feature | 描述 |
|------|---------|------|
| 🔄 实时共享 | Real-time Sharing | 跨会话毫秒级记忆同步 |
| 🧠 四层记忆 | Four-Layer Memory | 感官/工作/情景/语义记忆架构 |
| 💭 自由思考 | Free Thinking | 非任务驱动的意识流思考 |
| 🔮 智能预测 | Prediction | 预测用户需求，预加载记忆 |
| 📊 可视化 | Visualization | 知识图谱、时间线、摘要 |
| 🔗 联想网络 | Association Network | 概念关联，激活扩散算法 |

---

## 🚀 快速开始 | Quick Start

### 安装 | Installation

```bash
# ClawHub 安装（推荐）
clawhub install cognitive-brain

# 手动安装
cd ~/.openclaw/workspace/skills
git clone <repository> cognitive-brain
cd cognitive-brain && npm install
```

### 基础使用 | Basic Usage

```bash
# 存储记忆
node scripts/brain.cjs encode "用户的项目叫 Alpha"

# 检索记忆
node scripts/brain.cjs recall "项目"

# 健康检查
node scripts/brain.cjs health_check
```

---

## 🏗️ 架构概览 | Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      应用层 | Application                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  心跳反思  │  │  自由思考  │  │  预测预加载 │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                实时层 | Real-time (Redis)                    │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Pub/Sub   │  │  工作记忆  │  │ 共享上下文  │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              持久层 | Persistence (PostgreSQL)               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  系统记忆  │  │  情景记忆  │  │  语义记忆   │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 四层记忆模型 | Four-Layer Memory

| 层级 | Layer | 持续时间 | 用途 |
|------|-------|---------|------|
| 感官记忆 | Sensory | 毫秒级 | 瞬时感知缓冲 |
| 工作记忆 | Working | 分钟~小时 | 活跃处理工作区 |
| 情景记忆 | Episodic | 长期 | 个人经历、事件 |
| 语义记忆 | Semantic | 长期 | 事实、概念、知识 |

---

## 🔄 共享工作区 | Shared Workspace

### 核心表 | Core Tables

| 表名 | Table | 说明 |
|------|-------|------|
| `system_memory` | System Memory | 替代 MEMORY.md，跨会话共享 |
| `shared_context` | Shared Context | 会话间临时上下文 |
| `memory_changes` | Memory Changes | 变更日志，实时追踪 |

### 使用示例 | Usage

```bash
# 设置用户档案
node scripts/shared_memory.cjs set "user_name" "master" profile

# 获取用户档案
node scripts/shared_memory.cjs user

# 获取所有教训
node scripts/shared_memory.cjs lessons
```

---

## 🔧 核心模块 | Core Modules

### 记忆操作 | Memory Operations

```bash
# 编码
node scripts/encode.cjs --content "内容" --metadata '{"type":"fact"}'

# 检索
node scripts/recall.cjs --query "关键词" --options '{"limit":5}'

# 联想
node scripts/associate.cjs spread "概念A,概念B"
```

### 思考与反思 | Thinking & Reflection

```bash
# 心跳反思
node scripts/heartbeat_reflect.cjs check

# 自由思考
node scripts/free_think.cjs think
```

### 可视化 | Visualization

```bash
# 知识图谱
node scripts/visualize.cjs mermaid > graph.md
node scripts/visualize.cjs html > graph.html

# 时间线
node scripts/timeline.cjs recent 7
```

---

## 🔗 Hook 集成 | OpenClaw Hooks

### cognitive-recall

**触发事件 | Event:** `message:preprocessed`

**功能 | Functions:**
- 并行检索记忆 + 教训 + 预测
- 注入上下文到消息
- 自动编码用户消息

**注入格式 | Injection Format:**

```
[🔮 预测]
  用户可能的下一步需求
[/预测]

[🧠 Memory Context]
  相关记忆内容
[/Memory Context]

[⚠️ 教训提醒]
  系统级别教训
[/教训提醒]
```

---

## ⚙️ 配置 | Configuration

### 系统要求 | Requirements

| 组件 | 版本 |
|------|------|
| Node.js | >= 18.0 |
| PostgreSQL | >= 14.0 (需要 pgvector) |
| Redis | >= 6.0 (可选) |
| Python | >= 3.8 (用于本地 Embedding) |

### config.json

```json
{
  "storage": {
    "primary": {
      "type": "postgresql",
      "host": "localhost",
      "port": 5432,
      "database": "cognitive_brain",
      "user": "postgres",
      "password": "cognitive123"
    },
    "cache": {
      "type": "redis",
      "host": "localhost",
      "port": 6379
    }
  },
  "embedding": {
    "provider": "local",
    "dimension": 384
  }
}
```

---

## 📚 API 参考 | API Reference

### SharedMemory 类

| 方法 | 说明 |
|------|------|
| `getSystemMemory(key)` | 获取系统记忆 |
| `setSystemMemory(key, content, category)` | 设置系统记忆 |
| `getUserProfile()` | 获取用户档案 |
| `getLessons()` | 获取所有教训 |
| `setSharedContext(sessionId, type, content)` | 设置共享上下文 |
| `onChange(callback)` | 监听变更 |

---

## 🔧 故障排除 | Troubleshooting

### 常见问题 | Common Issues

| 问题 | 解决方案 |
|------|---------|
| 数据库连接失败 | 检查 PostgreSQL 服务状态 |
| Embedding 加载慢 | 运行 `warmup_embedding.cjs serve` |
| Hook 不生效 | 复制 handler.js 到 OpenClaw hooks 目录 |
| 跨会话不同步 | 确保所有会话使用相同数据库配置 |

---

## 📝 更新日志 | Changelog

### v2.7.1 (2026-03-13)
- 优化 SKILL.md 文档结构
- 中英文双语支持

### v2.7.0 (2026-03-13)
- 共享工作区：PostgreSQL NOTIFY 实时同步
- system_memory 表替代 MEMORY.md

### v2.6.0 (2026-03-13)
- 知识图谱可视化
- 预测与预加载

### v2.5.0 (2026-03-13)
- 自由思考模块
- 分离收集与思考架构

---

## 📄 许可证 | License

MIT License

## 👤 作者 | Author

AI Self-Design

## 🔗 链接 | Links

- **ClawHub:** https://clawhub.com
- **OpenClaw:** https://github.com/openclaw/openclaw
- **文档:** https://docs.openclaw.ai
