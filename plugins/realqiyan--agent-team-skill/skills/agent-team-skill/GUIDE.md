# Agent Team Skill - 完整指南

本文档包含 `agent-team-skill` 的所有功能说明。核心的「查询团队成员」功能请参考 [SKILL.md](./SKILL.md)。

## 更新人员信息

添加新成员或更新现有成员信息：

```bash
python3 scripts/team.py update \
  --agent-id "agent-001" \
  --name "Alice" \
  --role "Backend Developer" \
  --enabled true \
  --tags "backend,database" \
  --expertise "python,postgresql" \
  --not-good-at "frontend,design"
```

### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| `--agent-id` | 是 | 成员唯一标识符 |
| `--name` | 是 | 成员名称 |
| `--role` | 是 | 角色/职位 |
| `--enabled` | 是 | 启用状态 (true/false) |
| `--tags` | 是 | 标签（逗号分隔） |
| `--expertise` | 是 | 擅长领域（逗号分隔） |
| `--not-good-at` | 是 | 不擅长领域（逗号分隔） |

### 使用场景

- 新成员加入团队时添加信息
- 成员技能更新时修改信息
- 调整成员的启用状态

## 重置数据

清空所有团队数据，重置为初始状态：

```bash
python3 scripts/team.py reset
```

⚠️ **警告**：此操作会清空 `~/.agent-team/team.json` 中的所有数据，重置为 `{"team": {}}`。

### 使用场景

- 需要重新初始化团队数据
- 数据损坏需要重新开始

---

如需查询团队成员，请参考 [SKILL.md](./SKILL.md)。