---
name: auto-memory
description: "自动记忆更新机制 — 提取对话、清理过期、优先级过滤、跨Agent共享、智能摘要、增量索引、定期提炼。解决 agent 跨 session 记忆丢失问题。"
---

# Auto Memory - 自动记忆更新 v1.3.0

让你的 agent 拥有完整持久记忆系统，自动管理学习经验。

## v1.3.0 完整功能

| 功能 | 说明 |
|------|------|
| 🧹 自动过期清理 | 归档 30 天前的日志 |
| 🎯 优先级过滤 | 只加载 critical/high 学习 |
| 🌐 跨 Agent 共享 | 共享错误和最佳实践 |
| 📝 智能摘要 | 自动提取关键词摘要 |
| 🔄 增量索引 | 只索引变更文件 |
| 📊 定期提炼 | 每周日提炼长期记忆 |

---

## 安装

```bash
# 创建目录
mkdir -p ~/.openclaw/scripts
mkdir -p ~/.openclaw/workspace/.learnings/shared

# 下载脚本
# 从 Gitee 克隆或下载

# 初始化所有 agent
for agent in main python-expert architect product-manager operations-assistant data-analyst; do
  dir="$HOME/.openclaw/workspaces/$agent"
  [ "$agent" = "main" ] && dir="$HOME/.openclaw/workspace"
  mkdir -p "$dir/memory" "$dir/.learnings" "$dir/.openclaw"
done
```

---

## 文件结构

```
~/.openclaw/workspaces/<agent>/
├── AGENTS.md
├── MEMORY.md
├── memory/
│   ├── YYYY-MM-DD.md     # 日常日志
│   └── archive/          # 过期归档
├── .learnings/
│   ├── LEARNINGS.md      # 学习经验
│   ├── ERRORS.md         # 错误记录
│   └── archive/          # 已解决归档
└── .openclaw/
    └── .index-state.json # 索引状态

~/.openclaw/workspace/.learnings/shared/
├── common-errors.md      # 共享错误
└── best-practices.md     # 共享最佳实践
```

---

## 工作流程

```
┌─────────────────────────────────────────────────────────┐
│                    Session 开始                          │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 1. 自动清理                                             │
│    - 归档 30 天前的 memory 日志                          │
│    - 归档已解决的错误                                    │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 2. 加载学习经验                                         │
│    - LEARNINGS.md (priority: critical/high)            │
│    - ERRORS.md (priority: critical/high)               │
│    - shared/common-errors.md                           │
│    - shared/best-practices.md                          │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 3. 提取 session 对话                                    │
│    - 检测重要对话 → memory/                             │
│    - 检测错误 → ERRORS.md                              │
│    - 检测纠正 → LEARNINGS.md                           │
│    - 检测最佳实践 → shared/best-practices.md           │
│    - 生成智能摘要（关键词提取）                          │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 4. 增量索引                                             │
│    - 检查文件变更                                       │
│    - 只在有变更时重建索引                               │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│ 5. 周报提炼（每周日）                                    │
│    - 提炼项目、关键词、决策                             │
│    - 更新 MEMORY.md                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 自动检测规则

### 错误 → ERRORS.md
关键词：`错误`、`失败`、`报错`、`error`、`failed`、`exception`、`bug`、`崩溃`

### 纠正 → LEARNINGS.md
关键词：`不对`、`错了`、`应该`、`其实`、`实际上`、`不是`

### 最佳实践 → shared/best-practices.md
关键词：`最佳`、`推荐`、`建议`、`最好`、`优化`

### 共享错误 → shared/common-errors.md
包含 `API`、`网络`、`配置`、`权限` 的错误

---

## 配置 Heartbeat

```markdown
## 1. 自动记忆更新

\`\`\`bash
~/.openclaw/scripts/extract-memory.sh AGENT_ID
\`\`\`
```

## 配置 AGENTS.md

```markdown
## 每次会话开始时

1. 读取 `MEMORY.md` — 长期记忆
2. 读取 `memory/YYYY-MM-DD.md` — 近期对话
3. 读取 `.learnings/LEARNINGS.md` — 历史学习
4. 读取 `.learnings/ERRORS.md` — 历史错误
5. 读取 `.learnings/shared/` — 共享经验
```

---

## 示例输出

```
🧹 检查过期文件...
   📦 已归档 3 个过期日志
📚 加载学习经验...
   ⚠️ 学习经验: 2 条高优先级
   🔴 错误记录: 1 条高优先级
   🌐 共享错误: 5 条
   💡 共享最佳实践: 8 条
📄 分析 session: 2c36a403-xxx.jsonl
✅ 已更新 memory: 12 条消息
   📝 摘要: 记忆系统, 优化, 提取
🔄 更新向量索引...
✅ 索引已更新
```

---

## 配置参数

```bash
DAYS_TO_KEEP=30  # 日志保留天数
```

---

## 更新日志

### v1.3.0 (2026-03-12)
- 📝 智能摘要（关键词提取）
- 🔄 增量索引（只索引变更）
- 📊 定期提炼（每周日）

### v1.2.0 (2026-03-12)
- 🧹 自动过期清理
- 🎯 优先级过滤
- 🌐 跨 Agent 共享

### v1.1.0 (2026-03-12)
- 整合 self-improvement
- 主动加载历史学习

### v1.0.0 (2026-03-12)
- 初始版本