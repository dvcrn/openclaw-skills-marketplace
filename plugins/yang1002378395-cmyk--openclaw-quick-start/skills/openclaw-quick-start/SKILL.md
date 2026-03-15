---
name: openclaw-quick-start
description: "OpenClaw 5 分钟快速开始 - 最简化的入门教程。适合：完全新手、想快速体验的用户。"
---

# OpenClaw 5 分钟快速开始

最简化的入门教程，5 分钟上手。

## 前置要求

- 电脑（Windows/Mac/Linux）
- 网络连接
- 5 分钟时间

## 步骤 1：安装（2 分钟）

### Windows

```powershell
# 下载并安装 Node.js
# https://nodejs.org/

# 安装 OpenClaw
npm install -g openclaw
```

### Mac

```bash
# 安装 Node.js
brew install node

# 安装 OpenClaw
npm install -g openclaw
```

### Linux

```bash
# 安装 Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 安装 OpenClaw
npm install -g openclaw
```

## 步骤 2：配置（2 分钟）

### 获取免费 API Key

1. 访问：https://platform.deepseek.com/
2. 注册账号
3. 创建 API Key
4. 复制保存

### 配置 OpenClaw

```bash
# 初始化配置
openclaw config init

# 设置模型
openclaw config set model deepseek-chat

# 设置 API Key
openclaw config set api_key sk-xxxxx
```

## 步骤 3：开始使用（1 分钟）

### 命令行对话

```bash
openclaw chat

# 输入消息
你好，请介绍一下你自己
```

### Web 界面

```bash
# 启动 Web 服务
openclaw start

# 打开浏览器
# http://localhost:3000
```

## 验证安装

```bash
# 检查版本
openclaw --version

# 运行诊断
openclaw doctor

# 测试 API
openclaw test
```

## 下一步

- [连接 Telegram](/skills/openclaw-telegram-connector)
- [连接 Discord](/skills/openclaw-discord-connector)
- [使用免费模型](/skills/openclaw-free-models)
- [自定义 Skill](/skills/openclaw-custom-skill)

## 遇到问题？

- [常见错误修复](/skills/openclaw-error-fix)
- [故障排查](/skills/openclaw-troubleshoot)
- 需要帮助：微信 yang1002378395

## 需要帮助？

- 安装服务：¥99
- 配置咨询：¥99
- 技术支持：¥99/月

联系：微信 yang1002378395 或 Telegram @yangster151

---
创建：2026-03-14
