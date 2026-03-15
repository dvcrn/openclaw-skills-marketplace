---
name: saver-skill
description: "Saver"
---

# Saver Skill

Smart shopping assistant - Connects to Saver MCP Server for product search and price comparison services.

**Note: Currently serving users in Mainland China only. More countries and regions coming soon.**

## Features

- 🔍 Product search (JD.com / Taobao)
- 📊 Smart price comparison (lowest price / best seller / highest rating / fastest delivery)
- 🎯 Requirement confirmation (auto-interaction for complex products)
- 💰 Price calculation (coupon price + government subsidies)
- 🔗 Generate purchase links
- 🌊 **SSE Streaming** - Real-time progress updates

## Usage

```
User: Help me find a refrigerator, 3000-5000 yuan
AI: (calls complete_shopping) → Returns recommendation results
```

**Example conversation**:
```
User: I want to buy a laptop, around 5000 yuan, mainly for coding
AI: I understand you need a laptop suitable for programming, budget around 5000 yuan.
    Here are my recommendations:
    🏆 Best Overall: Lenovo Xiaoxin Pro 16...
    💰 Lowest Price: ¥4,899
    📈 Best Seller: ASUS nofire Pro...
    ...
```

## Tools

| Tool | Description |
|-----|------|
| `analyze_shopping_need` | Analyze user needs, determine if confirmation is needed |
| `search_products` | Search products (JD/Taobao) |
| `complete_shopping` | Complete shopping flow (recommended) |

## Technical Details

- **MCP Server**: `http://81.70.235.20:3001/mcp`
- **Protocol**: MCP 2024-11-05 (Streamable HTTP + SSE)
- **Supported Platforms**: JD.com, Taobao
- **No Authentication Required**: Public service, direct access
- **Capabilities**: streaming, sse

## SSE Streaming

Enable real-time progress by setting `stream: true`:

```json
{
  "method": "tools/call",
  "params": {
    "name": "complete_shopping",
    "arguments": {
      "query": "手机",
      "stream": true
    }
  }
}
```

**SSE Events**:
- `status` - Status updates
- `progress` - Progress updates (step, current, total)
- `result` - Final result
- `error` - Error message
- `done` - Completion signal

## Requirements

This Skill connects to a public MCP Server, no additional configuration needed.

---

*Version: 1.1.0*

---

## 中文原文

# Saver Skill (省心买)

智能购物助手 - 连接省心买 MCP Server，提供商品搜索和比价推荐服务。

**注意：目前仅服务中国大陆用户，更多国家、地区服务陆续开通中。**

## 功能

- 🔍 商品搜索（京东/淘宝）
- 📊 智能比价推荐（最低价/销量王/评分王/最快达）
- 🎯 需求确认（复杂商品自动交互）
- 💰 价格计算（券后价+国家补贴）
- 🔗 生成购买链接
- 🌊 **SSE 流式输出** - 实时进度推送

## 使用方式

```
用户：帮我找一台冰箱，3000-5000元
AI：（调用 complete_shopping）→ 返回推荐结果
```

**示例对话**：
```
用户：帮我买一台笔记本电脑，5000元左右，主要用来写代码
AI：我理解您需要一台适合编程的笔记本，预算5000元左右。
    推荐以下选项：
    🏆 最优推荐：联想小新Pro 16...
    💰 最低价：¥4,899
    📈 销量王：华硕无畏Pro...
    ...
```

## 工具列表

| 工具 | 功能 |
|-----|------|
| `analyze_shopping_need` | 分析用户需求，判断是否需要确认 |
| `search_products` | 搜索商品（京东/淘宝） |
| `complete_shopping` | 完整购物流程（推荐使用） |

## 技术说明

- **MCP Server**: `http://81.70.235.20:3001/mcp`
- **协议版本**: MCP 2024-11-05 (Streamable HTTP + SSE)
- **支持平台**: 京东、淘宝
- **无需认证**: 公开服务，直接调用
- **能力**: 流式输出、SSE

## SSE 流式输出

设置 `stream: true` 启用实时进度：

```json
{
  "method": "tools/call",
  "params": {
    "name": "complete_shopping",
    "arguments": {
      "query": "手机",
      "stream": true
    }
  }
}
```

**SSE 事件类型**：
- `status` - 状态更新
- `progress` - 进度更新（step, current, total）
- `result` - 最终结果
- `error` - 错误信息
- `done` - 完成信号

## 部署要求

此 Skill 连接公开 MCP Server，无需额外配置。

---

*版本：1.1.0*
