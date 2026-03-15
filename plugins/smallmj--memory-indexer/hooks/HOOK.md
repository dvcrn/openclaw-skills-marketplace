---
name: memory-indexer-on-new
description: "新对话开始时自动调用 memory-indexer 搜索相关记忆"
metadata:
  openclaw:
    emoji: "🔍"
    events: ["command:new"]
    requires:
      bins: ["node"]
---

# Memory Indexer On New

当用户开始新对话时，自动调用 memory-indexer 搜索与用户相关的记忆。

## 功能

- 监听 `/new` 命令
- 在 workspace 目录执行 memory-indexer 搜索
- 搜索关键词：用户名称、偏好、项目、任务等
