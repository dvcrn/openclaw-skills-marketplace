# ME News - OpenClaw Skill

> 为 OpenClaw AI 助手提供加密货币快讯和 Polymarket 预测市场数据

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Compatible](https://img.shields.io/badge/OpenClaw-Compatible-blue.svg)](https://openclaw.ai)

**🚀 无需配置，立即使用！** | **📖 [快速开始](QUICKSTART.md)**

## 📖 简介

ME News Skill 是一个为 OpenClaw 设计的技能插件，提供：

- 📰 **实时快讯** - 加密货币行业最新资讯
- 🤖 **聚合热点** - 智能聚合热点话题与热门代币
- � **完全公开** - 无需认证，开箱即用
- � **预测市场** - Polymarket 活跃预测事件
- 🌐 **双语支持** - 中英文无缝切换

## 🚀 快速安装

### 使用 ClawHub CLI（推荐）

```bash
# 安装 ClawHub CLI
npm i -g clawhub

# 搜索并安装 ME News Skill
clawhub search menews
clawhub install menews
```

### 手动安装

```bash
# 克隆到 OpenClaw skills 目录
cd ~/.openclaw/workspace/skills
git clone https://github.com/jamesmenews/menews.git
```

## 🎉 无需配置

本 Skill 使用**完全公开的 API**，无需任何认证或配置。

安装后直接使用即可！

## 💡 使用示例

安装并配置后，直接向 OpenClaw 提问：

### 查询快讯

```
你：最新的加密货币快讯有哪些？

OpenClaw：📰 为您找到最新的加密货币快讯：

1. 比特币突破 $70,000
   时间：2026-03-10 23:00
   摘要：比特币价格突破 7 万美元关口，创历史新高...
   
2. 以太坊升级即将到来
   时间：2026-03-10 22:30
   摘要：以太坊将在下周进行重大升级，预计将提升...
```

### 查询聚合热点

```
你：最近有什么热点话题？

OpenClaw：🤖 聚合热点（过去 1 小时）：

【当前热点】
1. 比特币 ETF 获批引发市场热议
   来源：OpenNews | 讨论数：1,234
   
【热门代币】
1. $BTC - 看涨情绪
   原因：ETF 获批推动价格上涨
   讨论数：2,345
   
【X 平台热议】
1. Vitalik 发布以太坊路线图更新
   讨论数：3,456
```

### 查询预测市场

```
你：Polymarket 上有什么热门预测？

OpenClaw：🎯 Polymarket 当前活跃的预测事件：

1. 2024 年美国总统大选
   市场：Politics | 流动性：$5.2M
   
2. 比特币年底价格预测
   市场：Crypto | 流动性：$2.1M
```

## 🎯 触发词

Skill 会在以下情况自动激活：

- **中文**：新闻、快讯、预测市场、加密货币、热点、摘要
- **英文**：news, flash, crypto, polymarket, prediction, digest, aggregation

## 📊 API 端点

**API 基础地址**: `https://agent.me.news`

### 快讯列表

```bash
curl 'https://agent.me.news/skill/flash/list?page=1&size=20'
```

### 聚合热点内容

```bash
curl 'https://agent.me.news/skill/aggregation/list?type=digest&window=1h&page=1&size=10'
```

### 预测事件

```bash
curl 'https://agent.me.news/skill/poly/events?page=1&size=20&active_only=true'
```

**完全公开，无需认证！**

## 🔧 开发

### 本地运行 API 服务

```bash
# 克隆项目
git clone https://github.com/jamesmenews/menews.git
cd menews

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 启动服务
python run.py
```

### 测试

```bash
# 使用 Bruno 测试
# 打开 bruno/ 目录中的测试集合

# 或使用 curl
curl 'http://localhost:8000/skill/flash/list'
```

## 📝 技术栈

- **后端框架**：FastAPI
- **限流**：SlowAPI (20次/分钟)
- **HTTP 客户端**：httpx
- **数据验证**：Pydantic

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🔗 相关链接

- [OpenClaw 官网](https://openclaw.ai)
- [ClawHub 技能市场](https://clawhub.ai)
- [ME News 官网](https://me.news)
- [问题反馈](https://github.com/jamesmenews/menews/issues)

## 📮 联系方式

- **邮箱**：aimpact@me.news
- **GitHub**：[@jamesmenews](https://github.com/jamesmenews)

---

**Made with ❤️ for the OpenClaw community**
