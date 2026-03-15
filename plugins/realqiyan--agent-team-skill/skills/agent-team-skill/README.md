# Agent Team Skill

Agent 团队管理工具，用于管理团队成员信息，包括技能、角色和工作分配。

提供两种使用方式：

- **Skill 版本** (`scripts/team.py`) - 通过 ClawHub/ClawDBot 使用，需要 AI Agent 主动调用
- **Plugin 版本** (`integrations/openclaw/`) - OpenClaw 原生插件，自动注入团队信息到系统提示词

## 功能特性

- 👥 **成员管理** - 管理团队成员信息，包括技能、角色和工作分配
- 🔍 **智能路由** - 根据成员专长匹配任务
- 📊 **能力评估** - 了解每个成员的优势和弱点
- ⚡ **自动注入** - 插件版本可在会话启动时自动加载团队信息
- 🌐 **全局共享** - 团队数据全局共享，跨会话可用

## 安装方法

### Skill 版本 (ClawHub/ClawDBot)

```bash
# 通过 ClawHub 安装
clawhub install agent-team-skill

# 或克隆仓库
git clone https://github.com/realqiyan/agent-team-skill.git
cd agent-team-skill

# 确保安装了 Python 3.10+
python3 --version
```

### Plugin 版本 (OpenClaw)

插件版本可在 OpenClaw 启动时自动注入团队信息到系统提示词，无需 AI Agent 主动调用工具。

```bash
# 方法一：链接到全局扩展目录
ln -s $(pwd)/integrations/openclaw ~/.openclaw/extensions/agent-team

# 方法二：在配置中指定路径
# 编辑 ~/.openclaw/config.json
```

配置示例：
```json
{
  "plugins": {
    "load": {
      "paths": ["/path/to/agent-team-skill/integrations/openclaw"]
    },
    "entries": {
      "agent-team": {
        "enabled": true
      }
    }
  }
}
```

详细配置请参考 [integrations/openclaw/README.md](./integrations/openclaw/README.md)。

## 使用方法

### Plugin 版本（推荐）

安装插件后，团队信息会在会话启动时自动注入到系统提示词，AI Agent 无需执行任何命令即可获得团队上下文。

### Skill 版本

```bash
python3 scripts/team.py <command> [options]
```

| 命令 | 说明 |
|------|------|
| `list` | 列出所有成员 |
| `update` | 添加/更新成员 |
| `reset` | 重置成员数据 |

### 团队协作规则

核心流程：**接到任务时** → 查团队 → 找专家 → 转交执行。所有任务必须交给最擅长的伙伴执行。

### 列出成员

列出所有团队成员（YAML 格式）：

```bash
python3 scripts/team.py list
```

输出示例：
```yaml
team:
  - agent_id: alice
    name: Alice
    role: Backend Developer
    enabled: true
    tags:
      - backend
      - api
      - database
    expertise:
      - python
      - go
      - postgresql
    not_good_at:
      - frontend
      - design
  - agent_id: bob
    name: Bob
    role: Designer
    enabled: true
    tags:
      - ui
      - ux
    expertise:
      - figma
      - css
    not_good_at:
      - backend
# Total: 2 member(s)
```

### 添加/更新成员

添加新成员或更新现有成员：

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

### 重置数据

清除所有团队数据，重置为空状态：

```bash
python3 scripts/team.py reset
```

## 自定义数据文件

使用 `--data-file` 参数指定自定义数据文件路径：

```bash
python3 scripts/team.py --data-file /path/to/team.json list
```

默认数据存储位置：`~/.agent-team/team.json`

## 数据文件说明

数据文件使用 JSON 格式存储，结构如下：

```json
{
  "team": {
    "agent-001": {
      "agent_id": "agent-001",
      "name": "Alice",
      "role": "Backend Developer",
      "enabled": true,
      "tags": ["backend", "api", "database"],
      "expertise": ["python", "go", "postgresql"],
      "not_good_at": ["frontend", "design"]
    }
  }
}
```

## 用例场景

- Team Building: 记录所有团队成员及其技能信息
- Task Assignment: 根据成员专长和标签分配任务
- Capability Assessment: 了解每个成员的优势和弱点
- Team Collaboration: 快速找到具有特定技能的成员

---

## 测试

运行测试：

```bash
python3 -m pytest tests/
```

测试覆盖：
- `test_team.py` - 成员管理测试 (14 个测试)