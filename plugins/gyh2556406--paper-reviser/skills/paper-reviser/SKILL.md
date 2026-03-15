---
name: paper-reviser
description: "论文改稿平台 - 根据审稿意见生成 AI 修改建议。上传 PDF/LaTeX 论文和审稿人意见（优点/缺点），自动调用 LLM 逐条分析并生成修改方案。支持 Google OAuth 登录、多审稿人、结构化结果展示、Markdown 导出。使用此技能当用户需要：搭建论文改稿平台、分析审稿意见生成修改建议、处理被拒论文的修改工作。"
---

# PaperReviser 论文改稿助手

根据审稿意见，AI 自动生成逐条修改建议的 Web 平台。

## 功能

1. Google OAuth 登录
2. 上传 PDF 或 LaTeX (.tex) 论文，自动提取文本
3. 多审稿人意见录入（优点 + 缺点，动态增删）
4. LLM 逐条分析，生成修改建议并引用原文
5. 结构化结果展示 + Markdown 导出

## 技术栈

- 前端：React 18 + Vite + TailwindCSS
- 后端：Node.js + Express
- 数据库：SQLite (sql.js)
- 认证：Google OAuth 2.0 (Passport.js)
- LLM：支持 Anthropic Claude / OpenAI GPT / Google Gemini / Kimi

## 快速启动

```bash
# 进入项目目录
cd paper-revision-platform

# 配置环境变量
cp .env.example .env
# 编辑 .env，填入 Google OAuth 凭据和 LLM API Key

# 安装依赖
cd server && npm install && cd ../client && npm install && cd ..

# 启动（两个终端）
cd server && npm run dev   # 后端 :3001
cd client && npm run dev   # 前端 :5173
```

## 环境变量

| 变量 | 说明 |
|---|---|
| GOOGLE_CLIENT_ID | Google OAuth Client ID |
| GOOGLE_CLIENT_SECRET | Google OAuth Client Secret |
| LLM_PROVIDER | `anthropic` / `openai` / `gemini` / `kimi` |
| ANTHROPIC_API_KEY | Anthropic API Key |
| OPENAI_API_KEY | OpenAI API Key |
| GEMINI_API_KEY | Gemini API Key |
| KIMI_API_KEY | Kimi API Key |
| SESSION_SECRET | Session 加密密钥 |

## Google OAuth 配置

1. 访问 [Google Cloud Console](https://console.cloud.google.com/) 创建 OAuth 2.0 凭据
2. 授权重定向 URI：`http://localhost:3001/api/auth/google/callback`
3. 将 Client ID 和 Secret 填入 `.env`

## 源码

GitHub: https://github.com/gyh2556406/paper-revision-platform
