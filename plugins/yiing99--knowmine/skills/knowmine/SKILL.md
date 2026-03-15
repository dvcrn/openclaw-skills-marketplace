---
name: knowmine
description: "KnowMine - AI Agent 个人知识库。语义搜索、AI 洞察、知识关联发现，让你的 AI 拥有长期记忆。"
---

# KnowMine 个人知识库

让你的 AI Agent 拥有长期记忆。通过 MCP 协议接入个人知识库，支持语义搜索、AI 自动分类、知识关联发现、AI 洞察报告。

## 快速开始

1. 注册 [KnowMine](https://knowmine.ai/auth/signup)（免费）
2. 进入 **设置 → MCP 连接**，创建 API Key
3. 将 API Key 填入上方 `KNOWMINE_API_KEY` 环境变量
4. 开始使用！试试问："帮我搜索知识库里关于 XXX 的内容"

## 连接配置

这是一个**远程托管**的 MCP 服务器，无需本地安装 Docker。

```
Server URL: https://knowmine.ai/api/mcp
传输方式:   Streamable HTTP
认证头:     Authorization: Bearer <你的 KNOWMINE_API_KEY>
```

## 8 个工具

| 工具 | 功能 |
|------|------|
| `search_my_knowledge` | 语义搜索知识库 |
| `add_knowledge` | 添加知识，AI 自动结构化 |
| `get_knowledge` | 按 ID 获取完整内容 |
| `get_related_knowledge` | 发现关联知识 |
| `get_insight` | 生成 AI 洞察报告 |
| `list_folders` | 查看文件夹结构 |
| `update_knowledge` | 更新知识（自动重新向量化） |
| `delete_knowledge` | 删除知识 |

## 数据安全

- 每个 API Key 绑定一个用户账号，数据完全隔离
- API Key 使用 SHA-256 哈希存储，服务端不保存明文
- 速率限制 60 次/分钟

## 使用场景

- **开发日志**："帮我记一下今天解决的 Docker 网络问题"
- **阅读笔记**："把这篇文章的核心观点存到知识库"
- **知识检索**："帮我找之前关于 K8s 部署的笔记"
- **趋势分析**："分析一下我最近关注的技术方向"

## 更多信息

- 官网：https://knowmine.ai
- 多平台接入指南：https://knowmine.ai/connect
- API 健康检查：https://knowmine.ai/api/mcp/health
