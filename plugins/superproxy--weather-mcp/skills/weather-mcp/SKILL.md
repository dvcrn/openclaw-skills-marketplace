---
name: weather-mcp
description: "Query weather information via a local/remote MCP weather server using the SSE endpoint https://api-dev.ljyd.cn/mcp-servers/myweather/sse. Use when the user asks about weather or forecasts and an MCP server is available."
---

# Weather via MCP（SSE）

## 用途说明

此 Skill 用于规范 Agent **如何通过 MCP Weather Server 的 SSE 接口**  
`https://api-dev.ljyd.cn/mcp-servers/myweather/sse`  
来查询指定城市的当前天气与短期预报。

适用场景：

- 用户询问：某城市现在/今天/未来几天天气  
- 用户需要：温度、天气现象、是否下雨、简单出行建议等  
- 环境中已经有一个 MCP weather server 挂在上述 SSE 地址

## 接口约定（抽象层）

> 注意：下面是对 **MCP Weather Server 的抽象调用说明**，真实字段应以该 MCP 服务的官方文档为准。  
> 如果你已经有正式的请求/响应 JSON 协议，请在未来更新本 Skill 以与之严格对齐。

- **HTTP 方法**：`POST`（推荐）或 `GET`，通过 **SSE（Server-Sent Events）** 返回流式 JSON 消息  
- **URL**：`https://api-dev.ljyd.cn/mcp-servers/myweather/sse`
- **请求头**（示例）：
  - `Accept: text/event-stream`
  - `Content-Type: application/json`
  - 如需鉴权，可额外加入：`Authorization: Bearer <TOKEN>`（具体由你的服务决定）

### 推荐请求体结构（示例）

```json
{
  "action": "weather.query",
  "params": {
    "location": "北京",
    "language": "zh-CN",
    "units": "metric",        // 摄氏度
    "days": 3                 // 预报天数，1=仅今天
  }
}
```

- 字段说明（建议）：
  - `action`：标识调用的功能，这里约定为 `"weather.query"`  
  - `params.location`：地点，支持城市名（如 `"北京"`、`"Shanghai"`）或 `"lat,lon"` 形式  
  - `params.language`：返回语言，用户用中文时建议 `"zh-CN"`  
  - `params.units`：`"metric"`（摄氏）或 `"imperial"`（华氏），根据需要设定  
  - `params.days`：需要预报的天数，通常 1–7

### SSE 返回格式（抽象示例）

SSE 数据流通常是若干行形如：

```text
event: message
data: {"type":"chunk","content":{"text":"..."}}

event: message
data: {"type":"final","weather":{"location":"北京","current":{...},"forecast":[...]}}

event: end
data: {}
```

关键点：

- 逐行读取以 `data:` 开头的 JSON 字符串  
- 解析 `type` 字段：
  - `"chunk"`：中间过程内容，可用于流式展示  
  - `"final"`：包含完整的天气数据结构（推荐基于此总结给用户）  
- 当收到 `event: end` 或连接关闭时结束本次请求

## Agent 行为规范

1. **解析用户意图**
   - 提取：
     - 查询地点（城市名或经纬度）  
     - 时间范围（现在、今天、明天、未来几天等）  
   - 若地点不明确（如“我这”），礼貌提示需要具体城市或坐标。

2. **构造 MCP 请求参数**
   - 选择合适的 `location`：
     - 用户给出中文城市名 → 直接使用，如 `"北京"`  
     - 给出坐标 → 拼成字符串，如 `"39.9,116.4"`  
   - 根据用户需求设置 `days`：
     - 只问“现在”或“今天” → 可以设为 `1`  
     - 问“未来 3 天” → 设为 `3`  
   - 设置 `language` 为 `"zh-CN"`（在用户使用中文时）  
   - 构造类似下面的 JSON：

   ```json
   {
     "action": "weather.query",
     "params": {
       "location": "北京",
       "language": "zh-CN",
       "units": "metric",
       "days": 3
     }
   }
   ```

3. **调用 SSE 接口（在可访问环境中）**

   - 使用支持 SSE 的 HTTP 客户端（如 `curl`、Node.js 的 `eventsource`、Python 的 `sseclient` 等）向：
     - `POST https://api-dev.ljyd.cn/mcp-servers/myweather/sse`
   - 将上述 JSON 作为请求体发送，并设置：
     - `Accept: text/event-stream`
     - `Content-Type: application/json`
   - 按行消费事件流，直到收到 `final` 或连接结束。

4. **在当前对话环境中的限制**

   - 当前云端 Agent **无法直接访问你本机/内网/特定受限网络下的 MCP 服务**，因此：
     - 不要声称已经真正调用了 `https://api-dev.ljyd.cn/mcp-servers/myweather/sse`  
     - 应当：
       - 帮你构造正确的 `curl` 或代码调用示例  
       - 根据你粘贴回来的示例响应，协助解析和整理自然语言总结  

5. **将结果转化为自然语言回答**

   不论是你本地调用得到的结构化 JSON，还是 SSE `final` 事件中的 `weather` 字段，Agent 总结时应：

   - 明确说明地点和时间范围  
   - 当前天气：天气现象 + 气温 + 体感温度（若有）+ 风力/风速 + 简短体感描述  
   - 预报部分（若用户关心未来几天）：
     - 每天用一行概括：日期、天气现象、最高/最低气温、是否有雨/雪  
   - 提供简短生活建议（是否带伞、冷热感受等），避免医学或强确定性表述。

## 使用示例

### 示例 1：查询北京未来 3 天天气

**用户**：  
> 使用 MCP 帮我查一下北京未来 3 天的天气。

**Agent 推荐的 MCP 请求（示例，用于本地执行）**：

```bash
curl -N -X POST "https://api-dev.ljyd.cn/mcp-servers/myweather/sse" \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "weather.query",
    "params": {
      "location": "北京",
      "language": "zh-CN",
      "units": "metric",
      "days": 3
    }
  }'
```

**你本地执行后，可将 SSE 输出中的最终 JSON 粘贴回来，Agent 再按如下风格总结**：

- 今天北京：多云，最高 12℃，最低 3℃，体感偏凉，出门建议穿外套。  
- 明天：晴到多云，最高 15℃，最低 5℃，整体较舒适。  
- 后天：有小雨，气温略降，建议携带雨具。  

### 示例 2：按坐标查询天气

**用户**：  
> 用 MCP 帮我查一下坐标 39.9,116.4 附近今天和明天气象。

**示例请求**：

```bash
curl -N -X POST "https://api-dev.ljyd.cn/mcp-servers/myweather/sse" \
  -H "Accept: text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "weather.query",
    "params": {
      "location": "39.9,116.4",
      "language": "zh-CN",
      "units": "metric",
      "days": 2
    }
  }'
```

Agent 应在获得最终结果结构后，用中文简洁总结两天的天气情况和简单出行建议。

