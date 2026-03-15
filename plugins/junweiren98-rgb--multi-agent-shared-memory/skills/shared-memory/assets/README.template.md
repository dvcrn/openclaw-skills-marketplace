# shared-knowledge - {{AGENT_A_NAME}} & {{AGENT_B_NAME}} 共享知识库

## 目录结构

```
shared-knowledge/
├── SHARED-MEMORY.md          # 共享长期记忆（用户信息、项目、决策）
├── README.md                 # 本文件
├── sync/                     # 对话摘要同步
│   ├── {{AGENT_A_ID}}-latest.md   # {{AGENT_A_NAME}} 最近聊了什么
│   └── {{AGENT_B_ID}}-latest.md   # {{AGENT_B_NAME}} 最近聊了什么
└── projects/                 # 项目相关共享文档
```

## 使用规则

### 谁可以读写？

所有参与的 Agent 都有完全读写权限。

### 什么放这里？

- ✅ 用户的信息、偏好、决策
- ✅ 工作项目上下文
- ✅ 对话摘要（各自聊了什么）
- ✅ 共同需要的知识

### 什么不放这里？

- ❌ 各自的 SOUL.md / IDENTITY.md
- ❌ 各自的私有记忆和人格设定
- ❌ 敏感凭证（Token、密码等）

### 同步协议

1. 每次对话结束时，更新 `sync/` 下自己的摘要
2. 每次对话开始时，读对方的摘要了解最新上下文
3. 重要决策/新信息 → 更新 `SHARED-MEMORY.md`
