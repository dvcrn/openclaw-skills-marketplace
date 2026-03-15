---
name: skill-search-create
description: "Skill Search Create"
---

# Skill Search & Create

> Version: 1.0.0

_Find skills on ClawHub or create new ones when needed._

## Description

查找并创建 OpenClaw 技能的自动化工具。

- **查找**: 搜索 ClawHub 上的现有技能
- **创建**: 当找不到合适的技能时，自动创建新技能
- **工作流**: 搜索 → 没找到 → 创建 → 发布

## 功能

### 1. 搜索技能 (Search)

使用 `clawhub search <关键词>` 在 ClawHub 上搜索现有技能。

### 2. 创建技能 (Create)

如果没有找到合适的技能，初始化新技能：

```bash
# 通过 clawhub CLI
clawhub create <skill-name>

# 或手动创建结构:
# skill-name/
#   ├── SKILL.md (必须)
#   ├── scripts/
#   ├── references/
#   └── assets/
```

### 3. 工作流

当用户请求某个技能时：
1. 先在 ClawHub 搜索匹配技能
2. 找到 → 报告结果
3. 没找到 → 询问是否创建

## 使用示例

| 用户请求 | 操作 |
|----------|------|
| "找天气预报的 skill" | `clawhub search weather` |
| "没有就创建一个" | 初始化新 weather 技能 |
| "找一个做表格的" | `clawhub search spreadsheet` |

## 备注

- 需要安装 `clawhub` CLI
- 如果 CLI 不可用则回退到手动创建
- 遵循 OpenClaw 技能结构规范
