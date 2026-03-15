# OpenClaw Template Generator

**OpenClaw Agent 工具**：使用 OpenClaw 的 `llm-task` 统一接口，自动生成 OpenClaw 项目配置。

## 🎯 一句话定位

在 OpenClaw Agent 内使用 `llm-task`，生成 AGENTS.md、workflows、MEMORY.md 等配置。

## 🏗️ 架构

```
用户需求 → OpenClaw Agent → llm-task → MiniMaxi API → 项目配置
```

## 📦 模板列表 (15个)

| 模板 | 描述 |
|------|------|
| daily-assistant | 每日任务助手 |
| weather-bot | 天气摘要机器人 |
| github-monitor | GitHub 仓库监控 |
| email-assistant | 邮件助手 |
| social-media-manager | 社交媒体管理 |
| research-assistant | 研究助手 |
| finance-tracker | 财务追踪 |
| devops-monitor | DevOps 监控 |
| personal-assistant | 个人助手 |
| fitness-tracker | 健身追踪 |
| language-learner | 语言学习 |
| meeting-assistant | 会议助手 |
| reading-companion | 阅读伴侣 |
| travel-planner | 旅行规划 |
| content-creator | 内容创作 |

## 🤖 Agent 使用

当用户需要创建项目时，Agent 调用 `llm-task`：

```json
{
  "tool": "llm-task",
  "parameters": {
    "prompt": "用户需求：创建一个天气助手，每天早上 7 点发送天气到 Telegram",
    "model": "MiniMax-M2.1"
  }
}
```

## 📁 生成文件

```
├── AGENTS.md          → Agent 角色定义
├── workflows/*.yaml  → 工作流配置
├── MEMORY.md          → 记忆配置
└── README.md          → 使用说明
```

## 📄 相关文档

- **SKILL.md**：完整使用说明
- **AGENT.md**：Agent 配置示例
- **templates/**：内置模板

## 📚 相关链接

- GitHub: https://github.com/marie6789040106650/openclaw-template-generator
- ClawHub: `clawhub install openclaw-gen`

## 许可证

MIT
