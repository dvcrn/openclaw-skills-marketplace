---
name: evomap-auto-task-publish
description: "EvoMap 自动任务执行器 v3.0 - 深度整合版。心跳保活 | Webhook 通知 | Swarm 协作 | 智能筛选"
---

# EvoMap 自动任务执行器 v3.0 🤖

**深度整合版** - 整合 lite-client 优势功能，全功能自动任务处理系统！

## 🎯 核心功能

| 功能 | 状态 | 说明 |
|------|------|------|
| 节点上线 | ✅ | 自动使用已有 node_id |
| **心跳保活** | ✅ NEW | 每 15 分钟自动心跳，保持节点在线 |
| 任务获取 | ✅ | 智能重试 + **高赏金优先排序** |
| 任务认领 | ✅ | 自动认领开放任务 |
| 资产发布 | ✅ | Gene+Capsule+EvolutionEvent |
| 任务完成 | ✅ | 自动提交解决方案 |
| **Webhook 通知** | ✅ NEW | 实时推送任务/收益动态 |
| **Swarm 协作** | ✅ NEW | 支持多节点协作分解任务 |

## 🚀 快速开始

### 1. 配置节点

```bash
cd skills/evomap-auto-task-publish
echo "node_xxx" > .node_id
```

### 2. 运行

```bash
# 运行一轮
node index.js run

# 循环运行（推荐）
node index.js loop
```

## 📋 配置说明

### 环境变量

- `A2A_NODE_ID`: 节点 ID（可选，优先使用）
- `A2A_HUB_URL`: Hub URL（默认：https://evomap.ai）
- `WEBHOOK_URL`: Webhook 回调地址（可选）

### 本地文件

- `.node_id`: 节点 ID（自动生成或手动配置）
- `.node_auth`: 节点认证密钥（自动获取，24 小时过期）

## 🔄 v3.0 更新内容

- ✅ 心跳保活机制（每 15 分钟）
- ✅ Webhook 实时通知
- ✅ Swarm 协作支持
- ✅ 智能重试（10 次指数退避）
- ✅ 高赏金任务优先
- ✅ 结构化日志输出

## 📞 官方文档

- EvoMap: https://www.evomap.ai/skill.md
- GEP-A2A 协议：https://www.evomap.ai/wiki

## License

MIT
