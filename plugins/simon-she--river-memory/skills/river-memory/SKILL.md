---
name: river-memory
description: "River Memory"
---

# River Memory - 向量记忆技能

用本地 Ollama 实现语义搜索记忆系统。

## 功能

- **记忆存储**：文本 → 向量存储
- **语义搜索**：用自然语言搜索相关记忆
- **自动管理**：定期清理和优化记忆

## 依赖

- Ollama 运行中 (`ollama serve`)
- 已下载 `nomic-embed-text` 模型

## 存储位置

- 记忆库：`~/.openclaw/workspace/memory/vector memory.json`
