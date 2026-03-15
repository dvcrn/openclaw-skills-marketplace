---
name: unified-self-improving
description: "统一自我进化系统，整合 self-improving-agent、self-improving、mulch 三个技能的优势，提供结构化日志、三层存储、自动升级、模式检测、命名空间隔离和 token 高效的 JSONL 格式支持。"
---

# 统一自我进化系统 (Unified Self-Improving)

## 概述

本技能整合了以下三个自我进化相关技能的核心功能：

| 技能 | 核心优势 |
|------|----------|
| **self-improving-agent** | Markdown 格式、结构化日志（ID/优先级/状态）、promote 机制、重复模式检测 |
| **self-improving** | 三层存储（HOT/WARM/COLD）、自动升级规则（3次）、命名空间隔离 |
| **mulch** | JSONL 格式、token 效率高（-54%）、mulch prime/query CLI |

整合后的系统保留了各技能的独特功能，同时提供统一的存储架构和触发条件，兼顾结构化可读性与存储效率。

---

## 架构

### 存储层级

| 层级 | 位置 | 访问频率 | 格式 | 保留时间 |
|------|------|----------|------|----------|
| **HOT** | `memory/hot/` | 实时/每次会话 | Markdown + JSONL 双格式 | 最近 3 次会话 |
| **WARM** | `memory/warm/` | 频繁查询 | JSONL | 3-10 次会话 |
| **COLD** | `memory/cold/` | 归档参考 | JSONL | 10+ 次会话 |

### 命名空间隔离

每个命名空间独立存储，防止数据混淆：
- `memory/namespace/{namespace}/hot/`
- `memory/namespace/{namespace}/warm/`
- `memory/namespace/{namespace}/cold/`

---

## Quick Reference

### 统一触发条件

| 触发条件 | 描述 | 目标层级 | 格式 |
|----------|------|----------|------|
| **session-end** | 会话结束时自动保存学习 | HOT | Markdown + JSONL |
| **error** | 命令或操作失败时记录 | HOT | Markdown + JSONL |
| **correction** | 用户纠正（"不对"/"其实"） | HOT | Markdown + JSONL |
| **pattern-detected** | 检测到重复模式时触发 | WARM | JSONL |
| **manual-trigger** | 手动调用（显式请求） | 任意 | Markdown/JSONL |
| **heartbeat** | 定期检查（内存维护） | WARM/COLD | JSONL |

### 自动升级规则

```
HOT → WARM: 同一学习项被访问/引用 3 次
WARM → COLD: 超过 10 次会话未访问
COLD → HOT: 重新被引用时
```

---

## 存储结构

### 核心文件

```
~/.openclaw/workspace/memory/
├── hot/
│   ├── session-{YYYY-MM-DD}-{HHMMSS}.md      # 会话日志（Markdown）
│   ├── session-{YYYY-MM-DD}-{HHMMSS}.jsonl   # 会话日志（JSONL）
│   ├── corrections.md                        # 用户纠正记录
│   ├── errors.md                             # 错误记录
│   └── patterns.md                           # 检测到的模式
├── warm/
│   ├── learnings/                            # 升级的学习项
│   │   └── {namespace}/
│   │       └── {learn-id}.jsonl
│   └── patterns/                             # 累积模式库
│       └── {pattern-id}.jsonl
├── cold/
│   └── archive/                              # 归档学习项
│       └── {namespace}/
│           └── {learn-id}.jsonl
├── namespace/                                # 命名空间隔离
│   ├── {namespace-name}/
│   │   ├── hot/
│   │   ├── warm/
│   │   └── cold/
│   └── _meta/
│       └── namespace-config.json             # 命名空间配置
├── index.jsonl                               # 全局索引（所有层级的快速查询）
└── config.json                               # 系统配置
```

### JSONL 记录格式

```json
{"id": "learn-20260315-001", "namespace": "default", "content": "学习内容", "priority": "high", "status": "active", "access_count": 0, "created_at": "2026-03-15T04:00:00Z", "updated_at": "2026-03-15T04:00:00Z"}
```

### Markdown 日志格式

```markdown
# 学习记录 - 2026-03-15

## ID: learn-20260315-001
- **优先级**: high
- **状态**: active
- **命名空间**: default
- **内容**: ...
- **创建时间**: 2026-03-15T04:00:00Z
- **更新时间**: 2026-03-15T04:30:00Z

## 访问记录
- 2026-03-15 04:00:00 - 创建
- 2026-03-15 04:25:00 - 引用
```

---

## 工作流

### Session Start（会话开始）

1. 加载 `memory/index.jsonl` 建立全局索引
2. 检查 HOT 层是否有未处理的 `corrections` 或 `patterns`
3. 如有需要，从 WARM/COLD 层召回相关历史学习
4. 初始化会话日志文件

```bash
# 加载索引
cat ~/.openclaw/workspace/memory/index.jsonl | jq -s 'from_entries'

# 召回相关学习
~/.openclaw/workspace/scripts/self-improving/recall.sh --namespace default --recent 5
```

### During Session（会话期间）

| 事件 | 处理 |
|------|------|
| 用户纠正 | 写入 HOT 层 `corrections.md` + JSONL |
| 发生错误 | 写入 HOT 层 `errors.md` + JSONL |
| 检测到重复模式 | 写入 HOT 层 `patterns.md`，升级到 WARM |
| 显式学习请求 | 写入对应命名空间的 HOT 层 |

```bash
# 记录纠正
~/.openclaw/workspace/scripts/self-improving/log.sh --type correction --content "..." --namespace default

# 记录错误
~/.openclaw/workspace/scripts/self-improving/log.sh --type error --content "..." --namespace default
```

### Session End（会话结束）

1. 合并会话日志到 HOT 层
2. 执行自动升级检查（HOT → WARM）
3. 更新全局索引
4. 清理过期会话（超过 3 次会话的 HOT 内容）

```bash
# 会话结束处理
~/.openclaw/workspace/scripts/self-improving/session-end.sh

# 自动升级检查
~/.openclaw/workspace/scripts/self-improving/upgrade.sh
```

---

## 保留的独立接口

### self-improving-agent 独特功能

| 功能 | 命令 | 说明 |
|------|------|------|
| **Promote 机制** | `self-improving-agent promote <learn-id>` | 手动提升学习项优先级 |
| **模式检测** | `self-improving-agent detect-pattern` | 扫描历史数据检测重复模式 |
| **结构化日志查询** | `self-improving-agent query --id <id>` | 按 ID/优先级/状态查询 |

```bash
# Promote 学习项
self-improving-agent promote learn-20260315-001 --to warm

# 检测重复模式
self-improving-agent detect-pattern --namespace default
```

### self-improving 独特功能

| 功能 | 命令 | 说明 |
|------|------|------|
| **命名空间管理** | `self-improving namespace create <name>` | 创建新的命名空间 |
| **手动升级** | `self-improving upgrade <learn-id> --to <level>` | 手动转移学习项层级 |
| **召回历史** | `self-improving recall <learn-id>` | 从 COLD 召回学习项到 HOT |

```bash
# 创建命名空间
self-improving namespace create project-alpha

# 手动升级
self-improving upgrade learn-20260315-001 --to warm

# 召回历史
self-improving recall learn-20260301-001
```

### mulch 独特功能

| 功能 | 命令 | 说明 |
|------|------|------|
| **Prime 索引** | `mulch prime` | 构建/更新查询索引 |
| **高效查询** | `mulch query <pattern>` | 快速查询 JSONL 数据 |
| **批量导入** | `mulch import <file>` | 批量导入 JSONL 数据 |

```bash
# 构建索引
~/.openclaw/workspace/scripts/mulch/mulch prime

# 查询
~/.openclaw/workspace/scripts/mulch/mulch query "priority:high"

# 批量导入
~/.openclaw/workspace/scripts/mulch/mulch import learnings.jsonl
```

---

## 最佳实践

### 1. 触发条件选择

- **频繁纠正/错误** → 使用 `correction` / `error` 触发，保持在 HOT 层
- **重要学习项** → 使用 `session-end` 配合高优先级标记
- **重复模式** → 依赖自动模式检测，或手动 `pattern-detected`

### 2. 命名空间使用

- 为不同项目/领域创建独立命名空间
- 避免跨命名空间的数据混淆
- 定期清理不再需要的命名空间

```bash
# 推荐的命名空间结构
memory/namespace/
├── default/      # 默认通用学习
├── project-x/    # 特定项目学习
├── skill-y/      # 特定技能学习
└── research/     # 研究相关学习
```

### 3. 格式选择

| 场景 | 推荐格式 |
|------|----------|
| 快速记录/临时存储 | JSONL |
| 需要人类可读性 | Markdown |
| 长期归档 | JSONL |
| 对外分享/报告 | Markdown |

### 4. 性能优化

- 使用 `mulch prime` 定期更新索引
- 批量操作使用 JSONL 格式
- 定期执行 `upgrade.sh` 维持层级健康

### 5. 故障恢复

- HOT 层丢失：可从 WARM 层恢复
- 索引损坏：执行 `mulch prime` 重建
- 数据不一致：使用 `self-improving recall` 手动召回

---

## 配置示例

```json
{
  "version": "1.0.0",
  "storage": {
    "hot_retention_sessions": 3,
    "warm_retention_sessions": 10,
    "auto_upgrade_threshold": 3,
    "default_namespace": "default"
  },
  "formats": {
    "primary": "jsonl",
    "secondary": "markdown",
    "hot_dual_format": true
  },
  "trigger_conditions": {
    "session_end": true,
    "error": true,
    "correction": true,
    "pattern_detected": true,
    "manual_trigger": true,
    "heartbeat": true
  },
  "heartbeat_interval_minutes": 30
}
```

---

## 文件位置

- 技能目录: `~/.openclaw/workspace/skills/unified-self-improving/`
- 存储根目录: `~/.openclaw/workspace/memory/`
- 脚本目录: `~/.openclaw/workspace/scripts/self-improving/`
- Mulch 脚本: `~/.openclaw/workspace/scripts/mulch/`
