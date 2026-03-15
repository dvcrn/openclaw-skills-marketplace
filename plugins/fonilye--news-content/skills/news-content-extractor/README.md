# 新闻内容提取 Skill (News Content Extractor)

这是一个专为 [OpenClaw](https://openclaw.ai) 打造的高性能新闻内容提取工具。它能精准识别网页中的新闻标题、作者、发布日期以及正文内容，并过滤掉广告和无关侧边栏。

## 🌟 特点

- **极速安装**: 客户端基于 Node.js，无需安装任何 Python 依赖库，即插即用。
- **高精准度**: 核心解析逻辑由云端专为新闻优化的 `trafilatura` 引擎驱动。
- **隐私保护**: 仅需提供 API Key 即可进行远程解析。

## 🚀 安装步骤

1. **从 ClawHub 安装**:
   在您的 OpenClaw 项目目录下运行：
   ```bash
   npx clawhub@latest install news-content-extractor
   ```

2. **配置环境变量**:
   使用此 Skill 需要设置 API Key。请在您的 `.env` 文件或系统环境变量中添加以下项：
   ```bash
   # 您的身份验证 Token
   EASYALPHA_API_KEY=您的_API_KEY
   
   # 后端地址 (可选，通常使用默认地址)
   NEWS_EXTRACTOR_SERVER_URL=https://your-api-endpoint.com/extract
   ```

## 📝 使用方法

安装并配置完成后，您可以直接在聊天中发送新闻 URL：

**用户**: "把这个新闻的内容抓取给我：https://finance.sina.com.cn/xxxx"

**Agent**: (自动调用本 Skill 并返回如下结果)
> **标题**: xxxx  
> **日期**: 2024-xx-xx  
> **正文**: ......

---

## 🛠️ 技术支持
如果您在安装或使用过程中遇到问题，请联系 [ClawHub.ai](https://clawhub.ai) 或查看项目主页故障排除。
