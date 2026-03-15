---
name: xhs-cover
description: "生成小红书风格封面图片。使用场景：(1) 用户要求生成小红书封面 (2) 用户要求生成社交媒体封面图 (3) 用户为笔记/文章生成配图 (4) 用户询问 credit 余额或生成历史。"
---

# 小红书封面生成器

通过 MCP 协议生成小红书风格封面图片。

> ⚠️ **注意**：本技能需要将您的 API Key 发送到 xhscover.cn 服务。请确保您信任该服务后再使用。

## 环境要求

- `mcporter` - MCP 客户端

## 快速配置

```bash
# 1. 安装 mcporter
npm i -g mcporter

# 2. 设置 API Key
export XHS_COVER_API_KEY="xhs_your_api_key"  # 在 xhscover.cn/dashboard 获取
```

## 快速使用

```bash
# 生成封面（默认 3:4 竖版）
./scripts/xhs-cover.sh generate "5个习惯让你越来越自律"

# 指定宽高比
./scripts/xhs-cover.sh generate "今日份好心情" 1:1

# 查询余额
./scripts/xhs-cover.sh balance

# 查看历史
./scripts/xhs-cover.sh history

# 查看帮助
./scripts/xhs-cover.sh help
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `XHS_COVER_API_URL` | API 地址 | https://api.xhscover.cn |
| `XHS_COVER_API_KEY` | API 密钥 | 无（必填） |

在 [xhscover.cn/dashboard](https://xhscover.cn/dashboard) 获取您的 API Key。

## 宽高比选项

| 比例 | 说明 |
|------|------|
| `3:4` | 小红书标准竖版（默认） |
| `9:16` | 超长竖版 |
| `1:1` | 正方形 |
| `16:9` | 横版 |

## 数据流向

本技能通过 mcporter ad-hoc 模式调用 `@emit/xhs-cover-mcp-server` MCP 服务，该服务会将您的：
- 封面文案
- API Key

发送到 `api.xhscover.cn` 进行处理。

## 相关链接

- 官网：https://xhscover.cn
- API 文档：https://xhscover.cn/docs
- MCP Server：https://npmjs.com/package/@emit/xhs-cover-mcp-server
