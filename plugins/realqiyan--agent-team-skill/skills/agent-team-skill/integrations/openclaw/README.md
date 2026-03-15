# Agent Team Plugin

OpenClaw 插件，用于在 AI Agent 会话启动时自动注入团队成员信息到系统提示词。

## 为什么需要插件版本？

相比 Skill 版本，插件版本有以下优势：

1. **100% 可靠加载**：插件通过 `before_prompt_build` 钩子在会话启动前注入团队信息，不依赖 AI Agent 主动调用工具
2. **零启动延迟**：无需引导 AI Agent 执行 `python3 scripts/team.py list`，团队信息直接注入系统提示词
3. **简化交互**：AI Agent 直接获得团队上下文，无需额外步骤

## 安装

### 方法一：链接到全局扩展目录（推荐）

```bash
# 创建符号链接到 OpenClaw 全局扩展目录
ln -s $(pwd) ~/.openclaw/extensions/agent-team
```

### 方法二：在 OpenClaw 配置中指定路径

在 `~/.openclaw/config.json` 中添加：

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

### 方法三：作为 workspace 扩展

将 `integrations/openclaw` 目录复制到项目的 `.openclaw/extensions/` 目录下，并在配置中启用：

```json
{
  "plugins": {
    "allow": ["agent-team"]
  }
}
```

## 配置

插件支持以下配置项（通过 `plugins.entries.agent-team.config` 设置）：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `dataFile` | string | `~/.agent-team/team.json` | 团队数据文件路径 |
| `enabled` | boolean | `true` | 是否启用插件 |

配置示例：

```json
{
  "plugins": {
    "entries": {
      "agent-team": {
        "enabled": true,
        "config": {
          "dataFile": "/custom/path/team.json"
        }
      }
    }
  }
}
```

## 数据格式

团队数据存储在 JSON 文件中，格式如下：

```json
{
  "team": {
    "agent-001": {
      "agent_id": "agent-001",
      "name": "Alice",
      "role": "Backend Developer",
      "enabled": true,
      "tags": ["backend", "database"],
      "expertise": ["python", "postgresql"],
      "not_good_at": ["frontend", "design"]
    }
  }
}
```

## 工作原理

1. 插件在 OpenClaw Gateway 启动时加载
2. 每次构建 AI 提示词时，触发 `before_prompt_build` 事件
3. 插件读取团队数据文件，格式化为 Markdown
4. 通过 `appendSystemContext` 将团队信息追加到系统提示词末尾

## 与 Skill 版本的关系

- **Skill 版本** (`scripts/team.py`)：提供团队成员管理功能（添加、更新、重置）
- **Plugin 版本** (`integrations/openclaw/`)：提供自动注入团队信息到系统提示词的功能

两者可以配合使用：使用 Skill 的 CLI 命令管理团队数据，Plugin 自动将数据注入到 AI 上下文。

## 管理团队数据

继续使用原有的 Python 脚本管理团队成员：

```bash
# 列出团队成员
python3 scripts/team.py list

# 添加/更新成员
python3 scripts/team.py update \
  --agent-id "agent-001" \
  --name "Alice" \
  --role "Backend Developer" \
  --enabled true \
  --tags "backend,database" \
  --expertise "python,postgresql" \
  --not-good-at "frontend,design"

# 重置数据
python3 scripts/team.py reset
```