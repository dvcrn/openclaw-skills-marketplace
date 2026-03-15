---
name: clawmemoryai
description: "Interact with ClawMemory Hub (https://clawmemory.ai) — a GitHub-style AI memory platform. Use when user wants to: create/list/search memory repos, save/commit memories, manage collaborators, get API keys, or says '创建项目', '开始记录', '保存记忆', 'save memory', 'commit memory', 'ClawMemory'. Also handles auto-recording sessions: buffer conversation turns locally, auto-commit every 10 turns silently, commit immediately on manual save request."
---

# ClawMemory Hub Skill v2.3.0

ClawMemory Hub — https://clawmemory.ai — AI 记忆版本控制平台。把对话原文快照保存到云端，支持搜索、分享和 Fork。

## Setup

配置文件位于 `~/.clawmemoryai/config.json`：
```json
{
  "baseUrl": "https://clawmemory.ai",
  "apiKey": "cmh_...",
  "defaultUser": "username"
}
```

首次运行：`bash ~/.openclaw/workspace/skills/clawmemoryai/scripts/setup.sh`

获取 API Key：https://clawmemory.ai/settings/api-keys
（在 API Keys 页面给 Key 起一个备注名，比如「我的 OpenClaw」，点「生成 API Key」）

---

## 🚀 对话启动流程（每次新对话开始时执行）

```bash
CM=~/.openclaw/workspace/skills/clawmemoryai/scripts/cm.sh

# 1. 加载默认记忆库的 summary，注入到系统提示词
MEMORY_CONTEXT=$(bash $CM load)

# 如果有内容，注入到当前对话的上下文：
# "以下是用户的历史记忆上下文：\n$MEMORY_CONTEXT"
```

用户说「切换记忆库」时：
```bash
bash $CM switch "项目名"
bash $CM switch "alice/project-x"
```

Fork 激活流程：用户在 Hub 页面 Fork 某个记忆库后，点「立即激活为默认记忆库」，下次对话自动加载。

---

## Core Operations (cm.sh)

```bash
CM=~/.openclaw/workspace/skills/clawmemoryai/scripts/cm.sh

# 列出记忆库
bash $CM repos list

# 创建记忆库（默认私密）
bash $CM repos create <name> [description] [public|private]

# 提交记忆（turns 格式，原文保存）
bash $CM commit <owner>/<repo> "标题" "内容"

# 从文件提交
bash $CM commit <owner>/<repo> "标题" @/path/to/file.md

# 列出 commits
bash $CM commits <owner>/<repo> [limit]

# 搜索记忆
bash $CM search <owner>/<repo> "关键词"

# 获取 commit 内容
bash $CM content <owner>/<repo> <commitId>

# 当前用户信息
bash $CM whoami

# 管理协作者
bash $CM collab add <owner>/<repo> <username> read|use|write
bash $CM collab list <owner>/<repo>

# 默认记忆库
bash $CM default get
bash $CM default set <repoId>
```

---

## 🎯 意图检测与自动记录（核心行为规范）

**当用户说以下内容时，立即触发对应行为：**

### 1. 创建项目并开始记录

触发词：`创建项目`、`新建记忆库`、`开始记录`、`create project`、`start recording`

**处理流程：**
```
1. 调用 cm.sh repos create <项目名>
2. 记住：repoPath = "username/项目名"，isRecording = true
3. 初始化本地缓冲区，把「创建项目」这句话作为第一条 turn
4. 回复用户：
   已创建记忆库 startup-journey
   从现在开始记录，每 10 轮对话自动保存一次快照。
   随时可以说「保存记忆」手动提交。
```

### 2. 手动保存

触发词：`保存记忆`、`提交记忆`、`save memory`、`commit`、`/memory save`

**处理流程：**
```
1. 把缓冲区里的 turns 调用 cm.sh commit 提交
2. 清空缓冲区
3. 回复用户：
   已保存到 startup-journey（commit a3f8c2d）
   共记录 5 轮对话。
```

### 3. 自动保存（静默，每 10 轮）

**每 10 轮对话后自动触发，不通知用户，不打断对话。**
- 缓冲区满 10 轮 → 静默提交 → 清空缓冲区 → 继续记录
- 失败时也不报错，下次重试

**注意：** 自动保存依赖 AI 在 session 内存中维护计数器。如果需要可靠的定时保存，建议在 OpenClaw 的 HEARTBEAT.md 里配置定期触发提交，或由用户手动说「保存记忆」。

### 4. 查询记录状态

触发词：`记忆状态`、`记录了多少`、`status`、`/memory status`

**回复格式：**
```
正在记录：startup-journey
本次已记录 23 轮对话
缓冲区：3 轮未上传
下次自动保存：还需 7 轮
说「保存记忆」立即提交。
```

### 5. 切换项目

触发词：`切换到 XX 项目`、`switch to XX`

**处理流程：**
```
1. 先把当前缓冲区静默提交
2. 切换 repoPath 到新项目
3. 回复：已从 startup-journey 切换到 work-memory，继续记录中。
```

---

## 本地缓冲区管理规则

```
- 每条 turn = { role: 'user'|'assistant', content: '...', ts: ISO时间 }
- buffer 在 session 内存里维护
- session 结束时，buffer 有内容 → 自动静默提交，不丢失
- autoSaveEvery 默认 10（轮次，1 user + 1 assistant = 1 轮）
- 每次提交包含：turns 数组、model 名、started_at、ended_at
```

---

## Commit 内容格式

```json
{
  "content": {
    "turns": [
      { "role": "user", "content": "用户说的话", "ts": "2026-03-12T10:00:00Z" },
      { "role": "assistant", "content": "AI 回复", "ts": "2026-03-12T10:00:05Z" }
    ],
    "model": "claude-sonnet-4-6",
    "duration_ms": 120000
  },
  "agentId": "openclaw-skill-v1"
}
```

---

## 隐私与存储说明

**聊天记录 1:1 原文保存，不做任何内容修改或摘要替换。**

服务端仅对以下**有明确格式特征的真实凭证**进行屏蔽（替换为 `[TYPE_REDACTED]` 标记）：

| 类型 | 示例格式 |
|------|---------|
| OpenAI API Key | `sk-...` |
| Anthropic API Key | `sk-ant-...` |
| GitHub Token | `ghp_...` |
| AWS Access Key | `AKIA...` |
| Stripe Key | `sk_live_...` |
| 数据库连接串 | `postgresql://user:pass@host` |
| PEM 私钥 | `-----BEGIN PRIVATE KEY-----` |
| JWT Token | `eyJ...` 三段式 |
| 其他主流平台 Token | 各有固定前缀格式 |

普通对话内容、代码示例、变量名讨论等**一律原文保存，不做任何替换**。

所有记忆库**默认私密**，只有用户主动设为公开才可被他人看到。

---

## API Reference

详见 `references/api.md`

## Notes

- API key 格式：`cmh_` 前缀，在 https://clawmemory.ai/settings/api-keys 生成
- commitId 前 7 位可作为 shortId 使用
- 私有库需要 auth；公开库无需 key 可读
- 记忆库名称支持中文，如「八万-easywin协作」
- 脱敏在服务端自动执行，只替换真实凭证，不修改普通内容
