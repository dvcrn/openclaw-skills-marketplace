# Git 项目监控技能

自动监控 Git 项目更新（支持 GitHub、GitLab、Gitee 等所有 Git 平台），当有新的 commit 时自动拉取代码并生成变更摘要。

## ⚙️ 首次配置

### 飞书通知配置（可选）

1. 打开 `config.json` 文件
2. 替换以下占位符：

```json
"feishu": {
  "appId": "你的飞书应用ID",
  "appSecret": "你的飞书应用密钥",
  "chatId": "你的群聊ID"
}
```

获取飞书配置：
- 访问 https://open.feishu.cn/ 创建企业自建应用
- 获取 App ID 和 App Secret
- 开启权限 `im:chat:read:chat_id` 和 `im:message:send_as_bot`

## ✨ 特性

- 🌐 **多平台支持** - GitHub、GitLab、Gitee 及任何 Git 仓库
- 📦 **灵活管理** - 轻松添加、删除、查看监控项目
- 🔄 **自动更新** - 定期检查并拉取最新代码
- 📊 **智能摘要** - 自动生成可读的变更摘要
- 🔔 **即时通知** - 通过 Feishu 推送更新通知

## 🚀 快速开始

### 添加监控项目

支持多种格式：

```bash
# GitHub 项目（简写）
node helper.js add anthropics/skills

# 完整 URL
node helper.js add https://github.com/openai/openai-python

# GitLab 项目
node helper.js add gitlab:gitlab-org/gitlab
node helper.js add https://gitlab.com/gitlab-org/gitlab-runner

# Gitee 项目
node helper.js add gitee:mindspore/mindspore
node helper.js add https://gitee.com/openharmony/docs

# 自定义 Git 服务器
node helper.js add https://git.example.com/my-org/my-project

# 指定分支（默认 main）
node helper.js add owner/repo develop
```

### 查看监控列表

```bash
node helper.js list
```

### 检查更新

```bash
# 检查所有仓库（静默模式）
node helper.js check

# 检查所有仓库（详细模式，显示调试信息）
node helper.js check --verbose

# 检查特定仓库
node helper.js check anthropics-skills
node helper.js check anthropics/skills
```

### 删除监控

```bash
node helper.js remove anthropics-skills
node helper.js remove anthropics/skills
```

## 💬 对话式使用

你也可以直接通过对话来管理：

```
监控 GitHub 项目 anthropics/skills
监控 https://gitlab.com/gitlab-org/gitlab
添加仓库 gitee:mindspore/mindspore

查看监控列表
列出所有仓库

检查所有更新
检查 anthropics/skills 的更新

删除 anthropics/skills 的监控
停止监控 gitlab-org/gitlab
```

## 📋 当前配置

### 已监控项目
运行 `node helper.js list` 查看当前监控的所有项目。

### 定时任务
已创建定时任务，每 6 小时自动检查一次所有仓库的更新：
- 任务 ID: `157acdca-a8c1-43bb-9421-cbd809c21375`
- 检查间隔: 6 小时
- 通知方式: Feishu

## 📊 更新摘要示例

当检测到更新时，你会收到类似这样的通知：

```
📦 anthropics-skills 有新更新！

🔖 最新提交 (3 个):
- [abc123d] Add new PDF extraction skill (2 hours ago)
- [def456e] Fix bug in document generation (5 hours ago)
- [ghi789f] Update README with new examples (1 day ago)

📝 主要变更:
- 新增: 2 个文件
  • skills/pdf-extract/SKILL.md
  • skills/pdf-extract/extract.py
- 修改: 3 个文件
  • skills/docx/SKILL.md
  • README.md
  • spec/skill-format.md

📊 统计:
 5 files changed, 234 insertions(+), 67 deletions(-)

🔗 查看详情: https://github.com/anthropics/skills/compare/abc123d...ghi789f
```

## 🗂️ 文件结构

```
skills/github-monitor/
├── SKILL.md          # 技能定义和说明
├── README.md         # 本文档
├── config.json       # 监控配置（自动生成）
├── monitor.sh        # Bash 脚本（git 操作）
└── helper.js         # Node.js 工具（仓库管理）
```

## ⚙️ 配置说明

### config.json

```json
{
  "repositories": [
    {
      "url": "https://github.com/anthropics/skills.git",
      "name": "anthropics-skills",
      "platform": "github",
      "owner": "anthropics",
      "repo": "skills",
      "localPath": "/Users/xxx/.openclaw/workspace/repos/anthropics-skills",
      "branch": "main",
      "lastChecked": "2026-03-12T02:52:32.415Z",
      "lastCommit": "b0cbd3d...",
      "addedAt": "2026-03-12T02:50:00.000Z"
    }
  ],
  "checkInterval": "6h",
  "notifyChannel": "feishu",
  "maxCommitsToShow": 10,
  "includeDiffSummary": true
}
```

### 支持的平台

- **GitHub** - github.com
- **GitLab** - gitlab.com 或自托管实例
- **Gitee** - gitee.com
- **其他** - 任何支持 Git 协议的服务器

## 🔧 高级功能

### 监控私有仓库

1. 生成访问令牌（GitHub Personal Access Token / GitLab Access Token）
2. 修改 `monitor.sh`，在 git 命令中使用令牌：
   ```bash
   git clone https://TOKEN@github.com/owner/repo.git
   ```

### 自定义通知格式

编辑 `helper.js` 中的 `generateSummary()` 函数来自定义摘要格式。

### 过滤特定文件

在 `helper.js` 中添加文件过滤逻辑，只关注特定目录或文件类型的变更。

### 修改检查间隔

编辑定时任务或在 `config.json` 中修改 `checkInterval`。

## 🛠️ 管理定时任务

### 查看所有定时任务
```
列出所有定时任务
```

### 暂停/恢复监控
```
暂停 Git 监控任务
启用 Git 监控任务
```

### 删除定时任务
```
删除 Git 监控任务
```

## ❓ 故障排查

### 问题：克隆失败
- 检查网络连接
- 确认仓库 URL 正确
- 如果是私有仓库，检查访问令牌

### 问题：定时任务未运行
- 运行 `cron list` 查看任务状态
- 检查 OpenClaw Gateway 是否正常运行

### 问题：通知未收到
- 确认 Feishu 配置正确
- 检查 `config.json` 中的 `notifyChannel` 设置

### 问题：本地仓库冲突
- 手动进入本地路径，运行 `git status` 检查状态
- 如有冲突，可以删除本地仓库重新克隆

## 📝 使用技巧

1. **批量添加** - 可以连续添加多个仓库
2. **分支监控** - 可以为同一仓库的不同分支创建多个监控
3. **定期清理** - 删除不再需要的监控项目，节省存储空间
4. **手动检查** - 在添加新仓库后，建议先手动检查一次

## 🔄 更新日志

- **2026-03-12 v2.0**: 重大更新
  - ✨ 支持多平台（GitHub、GitLab、Gitee 等）
  - ✨ 通用仓库管理（添加、删除、列表）
  - ✨ 灵活的输入格式（URL、简写、平台前缀）
  - 🔧 重构代码结构，提高可维护性

- **2026-03-12 v1.0**: 初始版本
  - 基础 GitHub 监控功能
  - 自动生成变更摘要
  - Feishu 通知集成

## 📚 相关资源

- [OpenClaw 文档](https://docs.openclaw.ai)
- [Git 文档](https://git-scm.com/doc)
- [Anthropic Skills 仓库](https://github.com/anthropics/skills)

## 🤝 贡献

欢迎提出建议和改进！这是一个开放的技能，可以根据需求自由修改。
