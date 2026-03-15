# xhs-cover-skill

<div align="center">

**小红书封面生成器** - OpenClaw AI Agent 技能

一句话生成精美的小红书风格封面图

[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://openclaw.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## ✨ 功能特性

- 🎨 **AI 自动设计** - 输入文案，自动生成小红书风格封面
- 📐 **多种比例** - 支持 3:4、9:16、1:1、16:9 等常用比例
- 💰 **余额查询** - 随时查看剩余生成次数
- 📜 **历史记录** - 查看之前生成的封面

## 📸 效果展示

只需对 AI 说：

```
帮我生成一个小红书封面，文案是：5个习惯让你越来越自律
```

AI 会自动调用此技能生成封面图片链接。

## 🚀 快速开始

### 前置要求

1. **获取 API Key**
   
   访问 [xhscover.cn/dashboard](https://xhscover.cn/dashboard) 注册并获取 API Key

2. **安装依赖**
   ```bash
   # 安装 mcporter (MCP 客户端)
   npm install -g mcporter

   # 确保有 jq (macOS 自带，其他系统可能需要安装)
   ```

### 安装技能

#### 方法 1：从 GitHub 安装（手动）

```bash
# 进入 OpenClaw workspace
cd ~/.openclaw/workspace

# 下载技能
git clone https://github.com/xwchris/xhs-cover-skill.git skills/xhs-cover

# 重启 OpenClaw 或开启新会话即可使用
```

#### 方法 2：通过 ClawHub 安装（推荐）

```bash
clawhub install xhs-cover
```

### 配置环境变量

在 `~/.openclaw/.env` 中添加：

```bash
XHS_COVER_API_URL=https://api.xhscover.cn
XHS_COVER_API_KEY=xhs_your_api_key_here
```

或者每次会话前设置：

```bash
export XHS_COVER_API_URL="https://api.xhscover.cn"
export XHS_COVER_API_KEY="xhs_your_api_key_here"
```

## 💡 使用示例

### 在 OpenClaw 中使用

安装技能后，直接用自然语言与 AI 对话：

| 你说 | AI 会做的 |
|------|-----------|
| "帮我生成一个小红书封面：5个习惯让你越来越自律" | 生成默认 3:4 竖版封面 |
| "生成一张 1:1 的封面，文案是今日份好心情" | 生成正方形封面 |
| "查询我的 xhscover 余额" | 显示剩余生成次数 |
| "看看我最近生成的封面" | 显示历史记录 |

### 命令行直接使用

```bash
cd ~/.openclaw/workspace/skills/xhs-cover

# 生成封面（默认 3:4 竖版）
./scripts/xhs-cover.sh generate "5个习惯让你越来越自律"

# 指定宽高比
./scripts/xhs-cover.sh generate "今日份好心情" 1:1
./scripts/xhs-cover.sh generate "长图笔记" 9:16

# 查询余额
./scripts/xhs-cover.sh balance

# 查看帮助
./scripts/xhs-cover.sh help
```

## 📐 支持的尺寸

| 比例 | 用途 | 效果 |
|------|------|------|
| `3:4` | 小红书标准竖版（默认） | 📱 适合图文笔记 |
| `9:16` | 超长竖版 | 📱 适合长图笔记 |
| `1:1` | 正方形 | 📱 适合 Instagram/微博 |
| `16:9` | 横版 | 💻 适合 B站/视频封面 |

## 🔒 数据安全

> ⚠️ **重要提示**：本技能需要将您的 API Key 和封面文案发送到 xhscover.cn 服务进行处理。

- 仅在使用时发送必要数据
- 不会存储或分享您的 API Key
- 请确保您信任 xhscover.cn 服务后再使用

## 📦 项目结构

```
xhs-cover-skill/
├── SKILL.md              # 技能定义文件
├── README.md             # 本文件
└── scripts/
    └── xhs-cover.sh      # 核心脚本
```

## 🔗 相关链接

- 🌐 官网：[xhscover.cn](https://xhscover.cn)
- 📖 API 文档：[xhscover.cn/docs](https://xhscover.cn/docs)
- 📦 MCP Server：[npmjs.com/package/@emit/xhs-cover-mcp-server](https://npmjs.com/package/@emit/xhs-cover-mcp-server)
- 🤖 OpenClaw：[openclaw.ai](https://openclaw.ai)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT © [xwchris](https://github.com/xwchris)

---

<div align="center">

如果这个技能对你有帮助，欢迎 ⭐ Star 支持一下！

</div>
