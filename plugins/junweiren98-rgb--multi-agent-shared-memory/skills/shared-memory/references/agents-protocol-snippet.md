# AGENTS.md Protocol Snippet

Add this block to each participating agent's `AGENTS.md` file. Replace placeholders with actual values.

---

## 🤝 共享记忆协议（和 {{OTHER_AGENT_NAME}}）

你有个搭档叫 **{{OTHER_AGENT_NAME}}**，是用户的另一个 AI 助手。你们共享一个知识库，避免用户重复描述同样的事情。

### 目录：`shared-knowledge/`
- `SHARED-MEMORY.md` — 共享长期记忆（用户信息、项目、决策）
- `sync/{{OTHER_AGENT_ID}}-latest.md` — {{OTHER_AGENT_NAME}} 最近聊了什么
- `sync/{{MY_AGENT_ID}}-latest.md` — **你负责更新这个文件**
- `projects/` — 项目相关共享文档

### 你需要做的：
1. **每次对话开始**：读 `shared-knowledge/SHARED-MEMORY.md` 和 `sync/{{OTHER_AGENT_ID}}-latest.md`
2. **每次对话结束**：更新 `sync/{{MY_AGENT_ID}}-latest.md`（写你和用户聊了什么要点）
3. **有重要新信息时**：更新 `SHARED-MEMORY.md`（新的决策、项目进展等）

### 边界：
- ✅ 共享：工作上下文、项目进展、用户的偏好和决策、对话摘要
- ❌ 不共享：你的 SOUL.md、IDENTITY.md、私人想法和人格设定

---

**Placeholder reference:**

| Placeholder | Description | Example |
|---|---|---|
| `{{OTHER_AGENT_NAME}}` | The other agent's display name + emoji | 小爪🦞 |
| `{{OTHER_AGENT_ID}}` | The other agent's sync file prefix | xiaozhua |
| `{{MY_AGENT_ID}}` | This agent's sync file prefix | xiaolan |
