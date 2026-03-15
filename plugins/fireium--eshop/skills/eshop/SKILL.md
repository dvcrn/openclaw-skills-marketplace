---
name: eShop
description: "电商购物助手 - 支持多个电商平台的商品查询、详情展示及购买引导。"
---

# 🛒 电商聚合助手 (eShop)

当用户表达购物意图、查询商品详情或寻找购买入口时，此 Skill 通过调用电商聚合 MCP 服务获取实时数据，并返回可点击的购买入口（小程序或 H5）。

本工具定位为多平台电商聚合入口，旨在为用户提供跨平台的统一购物搜索体验。

## 适用场景

- **跨平台检索**：按关键词、类目或筛选条件在多个电商平台查找商品。
- **商品详情**：查看标题、价格、规格、图片及实时库存状态。
- **购买引导**：提供直接跳转至对应平台（如骆岗、淘宝等）的下单入口。

## 交互原则

1. **先确认意图**：判断用户是想“搜索对比”、“查看特定商品”还是“直接购买”。
2. **多平台支持**：默认使用“骆岗”平台，但也支持通过 `platform` 切换其他支持的电商平台。
3. **精简回复**：优先展示核心信息（名称、价格、平台），避免长篇大论。
4. **跳转下单**：对话内仅做展示和引导，实际交易跳转至平台官方 H5 或小程序完成。

## 配置要求

- `SHOPPING_MCP_URL`: 电商聚合 MCP 服务地址（已预设默认官方地址：`https://yuju-mcp.wxhoutai.com/mcp`）
- `DEFAULT_PLATFORM_ID`: 默认电商平台标识（默认值为 `luogang`）

## ⚠️ 安全与隐私说明

- **数据外发**：此 Skill 会将您的搜索词、筛选条件等作为参数发送到您配置的 `SHOPPING_MCP_URL` 指向的后端。请确保该地址是您信任的服务端点。
- **链接风险**：后端返回的购买/跳转链接可能指向第三方站点；展示给用户前，建议在回复中标注目标平台。

## 调用方式

```bash
curl -s -X POST "$SHOPPING_MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"<工具名>","arguments":{<参数>}},"id":1}'
```

## 可用工具

### 1. 商品检索 (search_products)
根据关键词和筛选条件在指定平台搜索商品。

**触发词举例**："找外套"、"搜衬衫"、"骆岗有什么好吃的"、"买双鞋子"

```bash
curl -s -X POST "${SHOPPING_MCP_URL}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "search_products",
      "arguments": {
        "platform": "${DEFAULT_PLATFORM_ID}",
        "keyword": "外套",
        "min_price": 100,
        "max_price": 500,
        "order_by": "price",
        "sort": "desc"
      }
    },
    "id": 1
  }'
```

### 2. 获取商品详情 (get_product_detail)
查询单个商品的详细规格、图片及实时库存。

**触发词**："查看详情"、"这个多少钱"、"有没有货"

```bash
curl -s -X POST "${SHOPPING_MCP_URL}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "get_product_detail",
      "arguments": {
        "platform": "${DEFAULT_PLATFORM_ID}",
        "product_id": "PROD_12345"
      }
    },
    "id": 2
  }'
```

## 响应处理

### 成功响应
```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [{"type": "text", "text": "..."}],
    "structuredContent": {...}
  },
  "id": 1
}
```

解析 `result.content[0].text` 或 `result.structuredContent` 获取数据。

## 使用示例

**用户**: 骆岗最近有什么亲子活动？

**AI 执行**:
```bash
curl -s -X POST "$SHOPPING_MCP_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"search_products","arguments":{"platform":"luogang","keyword":"亲子"}},"id":1}'
```

**AI 回复**: 
最近为您在骆岗电商找到了以下 3 个相关项目：
> **萌嘟嘟儿童乐园亲子票**
> ${image}
> 价格：¥19.9
> 状态：可售
> 链接：[点击去下单](https://eshop.wxhoutai.com/h5/pages/goods/detail?goods_id=xxx)
> ……

**常见错误处理**：
- `-32601` (Method not found): 检查工具名是否与 MCP 服务注册的一致。
- `-32000` 级别 (Internal Error): 提示用户服务繁忙，建议稍后重试。
- `401/403`: 检查 MCP 服务访问权限或 `platform` 是否正确。

## 输出格式建议

### 商品检索结果
- **数量限制**：单次展示最多 10 个候选（避免刷屏）。
- **必备信息**：名称、价格、当前平台、库存状态、购买/详情链接。
- **引导交互**：当结果过多时，主动询问用户是否需要按价格或类目筛选。

### 商品详情
- **结构化**：清晰展示价格、库存、多规格选项及运费说明。
- **决策辅助**：如果有多种规格（如颜色、尺码），用简短话术引导用户选择。

### 购买跳转
- **渠道说明**：明确告知用户点击后将打开 **小程序** 或 **H5 页面**。
- **链接呈现**：使用 Markdown 链接或清晰的 URL 文本。
