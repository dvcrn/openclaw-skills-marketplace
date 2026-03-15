# MemOS Cloud Skill

[English](README.md) | [中文](README_zh.md)

MemOS Cloud Server API 技能。该技能允许 Agent 或开发者直接调用 MemOS 云平台 API，实现记忆的检索、添加、删除以及反馈功能。

## 环境要求 (Prerequisites)

- **Python**: 3.x 及以上版本
- **Python 依赖**: `requests` 模块 (`pip3 install requests`)

## 安装与引入 (Install)

### 方式一：使用命令安装（推荐）

```bash
npx skills add https://github.com/MemTensor/MemOS-Cloud-Skill
```

### 方式二：本地克隆并手动复制安装

1. 将本仓库克隆到本地：
    ```bash
    git clone https://github.com/MemTensor/MemOS-Cloud-Skill.git
    ```
2. 手动将技能文件夹复制到你对应的 agent 技能库目录中进行引入即可。

## 配置环境变量 (Environment Variables)

这是最重要的一步！在执行任何 API 操作前，你必须确保以下环境变量已经配置。

**环境变量配置位置**

- 你可以在系统环境变量中全局配置（例如 `~/.bashrc` 或 `~/.zshrc`）。
- 或者，你可以在特定的 AI Agent 或框架的环境设置中进行配置（例如，OpenClaw/Moltbot/Clawdbot 等框架支持读取 `.env` 文件）。

### 必填配置

- `MEMOS_API_KEY` (必填；Token 鉴权) — 在 [MemOS API 控制台](https://memos-dashboard.openmem.net/cn/apikeys/) 注册并获取。
- `MEMOS_USER_ID` (必填；确定性的用户自定义个人标识符，如邮箱哈希值或员工 ID) — **请不要使用随机值或聊天会话 ID 作为用户标识符。**

```env
MEMOS_API_KEY=你的_API_KEY
MEMOS_USER_ID=你的_USER_ID
```

### 可选配置

- `MEMOS_CLOUD_URL` (默认值: `https://memos.memtensor.cn/api/openmem/v1`)

### 快速配置命令 (Shell 用户，如 Linux/macOS)

```bash
echo 'export MEMOS_API_KEY="mpg-..."' >> ~/.bashrc
echo 'export MEMOS_USER_ID="user-123"' >> ~/.bashrc
source ~/.bashrc
```

### 快速配置命令 (Windows PowerShell 用户)

```powershell
[System.Environment]::SetEnvironmentVariable("MEMOS_API_KEY", "mpg-...", "User")
[System.Environment]::SetEnvironmentVariable("MEMOS_USER_ID", "user-123", "User")
```

## 功能与使用规范 (Usage)

安装并配置成功后，您的 AI 助手（如 Trae, Cursor, OpenClaw 等）将自动获得记忆管理能力。您可以直接使用自然语言与助手交互，Agent 会根据对话上下文，智能识别意图并自主调用 MemOS 云端 API。

### 1. 添加记忆 (Add Message)

当您在对话中提及重要的事实、个人偏好或特定指令时，Agent 会自动提取高价值信息并将其存储到云端。

**交互示例：**

- **用户：** “请记住，我平时开发首选语言是 Python，喜欢用深色主题。”
- **Agent：** _(识别意图 -> 自动调用 `add_message` 技能)_ “好的，我已经记住了您关于 Python 和深色主题的偏好。”

### 2. 搜索记忆 (Search Memory)

在回答问题之前，或者当您主动询问时，Agent 会根据当前问题去云端检索相关的历史记忆，并基于这些记忆给出最符合您个性化的回答。

**交互示例：**

- **用户：** “根据我常用的技术栈写一段初始化的模板代码。”
- **Agent：** _(识别意图 -> 自动调用 `search` 技能查阅记录)_ “没问题！根据您的偏好，这里是一份 Python 的初始化模板代码……”

### 3. 删除记忆 (Delete Memory)

当某些信息已经过时或者当初记录有误时，您可以直接命令 Agent 忘掉它们。

**交互示例：**

- **用户：** “忘记我之前的居住地址，我已经搬家了。”
- **Agent：** _(识别意图 -> 自动调用 `delete` 技能)_ “明白，我已经从记忆中删除了您的旧地址信息。”

### 4. 反馈 (Add Feedback)

如果 Agent 的回答不符合期望，您可以进行纠正，Agent 会自动将这些反馈添加到记忆流中，以便在未来的交互中改进。

**交互示例：**

- **用户：** “刚才的回答不够详细，以后请记得多加一些代码注释。”
- **Agent：** _(识别意图 -> 自动调用 `add_feedback` 技能)_ “收到，今后的代码我会提供更详细的注释说明。”

