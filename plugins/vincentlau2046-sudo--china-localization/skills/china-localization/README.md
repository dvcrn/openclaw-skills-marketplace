# 🇨🇳 China Localization Pack

> 让中国用户零门槛使用 OpenClaw

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()
[![ClawHub](https://img.shields.io/badge/ClawHub-Ready-orange.svg)]()

---

## ✨ 功能特性

### 🔍 中文搜索
- Tavily 搜索中文内容
- 支持高级搜索参数
- 域名过滤、时间范围

### 🌤️ 天气查询
- wttr.in 免费 API
- 中文天气输出
- 多城市支持

### 📅 飞书集成
- 日历管理
- 任务管理
- 消息发送
- 文档读取

### 💬 微信集成
- 模板消息
- 客服消息

### 🔔 钉钉集成
- 机器人消息
- Markdown 支持
- @所有人

### 🗺️ 高德地图
- 地理编码
- 路径规划

---

## 🚀 快速开始

### 1. 安装

```bash
# ClawHub 安装（推荐）
clawdhub install china-localization

# 或手动安装
git clone https://github.com/vincentlau2046-sudo/china-localization.git
cp -r china-localization ~/.openclaw/workspace/skills/
```

### 2. 配置

```bash
mkdir -p ~/.config/china-localization

# Tavily API Key（必需）
echo "tvly-YOUR_KEY" > ~/.config/china-localization/tavily_key

# 飞书配置（可选）
echo "cli_xxx" > ~/.config/china-localization/feishu_app_id
echo "your_secret" > ~/.config/china-localization/feishu_app_secret
```

### 3. 使用

在 OpenClaw 中直接使用：

```
搜索 AI 最新动态
查询深圳天气
获取飞书日历
发送钉钉消息
```

---

## 📖 文档

完整使用文档请查看 [SKILL.md](./SKILL.md)

---

## 🔧 依赖

- `curl` - HTTP 请求
- `jq` - JSON 解析
- Tavily API Key（必需）

**无需 npm 包！**

---

## 📄 许可证

MIT License

---

**Made with ❤️ for Chinese OpenClaw users**