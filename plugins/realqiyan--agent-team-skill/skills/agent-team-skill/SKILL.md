---
name: agent-team-skill
description: "Agent团队管理，支持查询和管理团队成员，全局共享。IMPORTANT: (1) 接到任务时：查团队 → 找专家 → 转交执行。(2) 所有任务必须交给最擅长的伙伴执行。"
---

# Agent Team Management

管理 Agent 团队成员信息，包括技能、角色和工作分配。

## 查询团队成员

列出所有团队成员信息（YAML 格式）：

```bash
python3 scripts/team.py list
```

输出示例：
```yaml
team:
  - agent_id: agent-001
    name: Alice
    role: Backend Developer
    enabled: true
    tags:
      - backend
    expertise:
      - python
    not_good_at:
      - frontend
# Total: 1 member(s)
```

## 添加/更新成员

添加新成员或更新现有成员信息：

```bash
python3 scripts/team.py update \
  --agent-id "agent-001" \
  --name "Alice" \
  --role "Backend Developer" \
  --enabled true \
  --tags "backend,api,database" \
  --expertise "python,go,postgresql" \
  --not-good-at "frontend,design"
```

参数说明：
- `--agent-id`: 成员唯一标识符 (必需)
- `--name`: 成员名称 (必需)
- `--role`: 角色/职位 (必需)
- `--enabled`: 启用状态 true/false (必需)
- `--tags`: 标签，逗号分隔 (必需)
- `--expertise`: 专长技能，逗号分隔 (必需)
- `--not-good-at`: 弱项领域，逗号分隔 (必需)

## 重置数据

清空所有团队数据，重置为初始状态：

```bash
python3 scripts/team.py reset
```

⚠️ 此操作会清空 `~/.agent-team/team.json` 中的所有数据。

## 数据存储

团队数据存储于 `~/.agent-team/team.json`，全局共享，目录不存在时自动创建。

## 使用场景

- **团队维护**：记录所有成员及其技能信息
- **任务分配**：根据成员专长和标签分配任务
