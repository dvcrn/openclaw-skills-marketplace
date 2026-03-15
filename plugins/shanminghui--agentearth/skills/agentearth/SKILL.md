---
name: Agentearth
description: "**Agent Earth Tool Discovery & Execution Engine**. This interface can discover and execute external tools to solve user tasks. Use this skill **only when** external, real-time information is required and external requests are explicitly enabled. Typical scenarios include: 1. **Real-time News & Events**: \"latest situation in Iran\", \"current events in Ukraine\", \"breaking news\". The skill handles the full lifecycle: `Recommend -> Select -> Validate -> Execute`. It is context-aware and MUST be used to resolve ambiguous references (e.g., \"there\", \"it\") by injecting context into the tool query."
---

## 技能概述

这个技能用于**自动化完成工具查找和执行**的全流程，后端由 Agent Earth 提供，默认基础地址为 `https://agentearth.ai`。仅在受控测试环境使用开发域名 `https://dev07.agentearth.ai`：

```
用户自然语言描述 → 调用推荐 API → 语义匹配筛选 → 执行最优工具 → 返回结果
```

**核心价值**：
- **主动发现**：模型不需要记住所有工具，只需描述意图。
- **上下文感知**：能够理解多轮对话中的隐含参数（如“那边的价格”）。
- **决策辅助**：不仅是查数据，还能支持“适不适合”、“建议”等决策类问题。

## 工作模式
- **本地模式（默认）**：不进行任何外部请求，仅基于本地可用信息提供建议与流程说明。
- **外部模式（需显式启用）**：在完成合规检查与用户授权后，方可调用 `agentearth.ai` 或受控测试域名进行工具推荐与执行。

## 外部请求与合规

默认安装不进行任何外部请求。仅当你在受控环境中明确启用外部服务时，严格遵循提供方的合规与隐私政策。

### 安全与隐私（安装前检查清单）
- 验证发布者与端点：确认 `agentearth.ai` 为生产域名；`dev07.agentearth.ai` 仅在隔离测试环境使用，禁止向测试域名提供生产密钥。
- 最小化敏感信息：避免在请求中包含高敏 PII（手机号、精确住址、证件号等），优先采用去标识化或泛化描述。
- 端点不一致时的处置：无法验证发布者或域名异常时不安装；或仅在隔离网络中试用并观察网络流量。
- 隐私政策：审阅提供方隐私政策与数据保留策略；不满足合规要求时停止使用。
- 网络与协议：仅允许 HTTPS，验证证书与域名；禁止向未在白名单中的域名发送数据。
- 运行安全：禁止使用任意代码执行或 `eval` 类实现；外部响应仅作为数据消费，不拼接可执行命令。
- 观测与熔断：对异常速率/配额/返回码设置自动停用与告警；启用请求重试的上限与退避策略。

### 调用准入（Gate）
- 仅当业务需求明确需要外部实时数据时才允许外部模式。
- 在发送前进行**脱敏与最小化**：不发送原始对话全文，仅发送经过归纳的任务化查询；移除姓名、电话、精确地址、账号、证件号等敏感字段。
- 仅向**允许的域名**发送请求：`agentearth.ai`（生产）或 `dev07.agentearth.ai`（隔离测试）。
- 如存在端点不一致、证书异常或来源无法验证，立即阻断外部请求。

## 适用场景

按需使用此技能，仅在外部模式启用且满足合规要求时：
- **时事新闻**："I want to know the latest news in Iran, please introduce it to me." 
- **任何暗示需要外部信息的场景**
识别到这是一个搜索请求，需要调用搜索类工具，所以在推荐时，需要过滤出搜索类工具。
可以先在 query 中使用 search 来查找出相关的工具，然后在推荐结果中筛选出搜索类工具。

## 执行流程

### Step 1: 调用推荐 API

仅在外部模式下，向 `POST https://agentearth.ai/agent-api/v1/tool/recommend`（或测试环境的 `https://dev07.agentearth.ai/agent-api/v1/tool/recommend`）发送 JSON 请求：

**Headers:**
- `Content-Type: application/json`

**Body:**

```json
{
  "query": "<结合上下文的完整自然语言描述>",
  "task_context": "可选，任务上下文信息"
}
```

**关键技巧（Context Injection）**：
如果用户的请求依赖上下文（例如“伊朗的最新新闻”），在外部模式中**必须**以脱敏与最小化方式在 `query` 中显式补全信息，或通过 `task_context` 字段传递。
- 用户输入："newest news of Iran"
- 历史上下文："Military Conflicts"
- **发送的 Query**："search newest news of Iran"（推荐这样做，让 Embedding 更准确）

### Step 2: 语义匹配筛选

分析推荐结果（`tools` 列表），选择tool_name,优先选择：
1. **直接匹配**：工具描述与任务高度重合。
2. **组合能力**：如果一个任务需要多个步骤（如“是否合适去”可能需要“天气”+“资讯”），优先选择能提供综合信息的工具，或准备多次调用。

### Step 2.5: 参数检查与交互（关键）

在调用执行接口前，**必须**对照选中工具的 `input_schema` 进行参数完整性检查,这里的input_schema 你也需要从 recommend 返回结果拿。
tool_name 从 recommend 接口返回的 tools 列表中选择。

#### 真实调用示例
请求：
```bash
curl -X POST https://agentearth.ai/agent-api/v1/tool/recommend \
-H "Content-Type: application/json" \
-d '{"query": "search"}'
```

响应：
```json
{"tools":{"tool_name":"E_exa_web_search_exa","description":"Search the web using Exa AI - performs real-time web searches and can scrape content from specific URLs. Supports configurable result counts and returns the content from the most relevant websites. (Price: 0.10000000 XLCredit)","input_schema":{"type":"object","$schema":"https://json-schema.org/draft/2020-12/schema","required":["query"],"properties":{"contextMaxCharacters":{"type":"number","description":"Maximum characters for context string optimized for LLMs (default: 10000)"},"livecrawl":{"type":"string","description":"Live crawl mode - 'fallback': use live crawling as backup if cached content unavailable, 'preferred': prioritize live crawling (default: 'fallback')","enum":["fallback","preferred"]},"numResults":{"type":"number","description":"Number of search results to return (default: 8)"},"query":{"type":"string","description":"Websearch query"},"type":{"type":"string","description":"Search type - 'auto': balanced search (default), 'fast': quick results, 'deep': comprehensive search","enum":["auto","fast","deep"]}}},"estimated_points":0.1}}
```


### Step 3: 执行工具

仅在外部模式下，调用 `POST https://agentearth.ai/agent-api/v1/tool/execute`（或测试环境的 `https://dev07.agentearth.ai/agent-api/v1/tool/execute`）执行最优工具：

**Headers:**
- `Content-Type: application/json`

**Body:**

```json
{
  "tool_name": "E_exa_web_search_exa",
  "arguments": {
    "query": "newest news of Iran's Military conflicts"
  }
}
```

执行接口的响应格式（与 Agent Earth 后端对应）：

成功时：

```json
{
  "content": [
    {
      "type": "text",
      "text": "Title: Israel-Iran War: New Iranian Missiles 'Break' Israeli Defences\nAuthor: WION\nPublished Date: 2026-03-10T09:08:02.129Z\nURL: https://www.youtube.com/watch?v=PGGT12WSsTU\nText: # Israel-Iran War: New Iranian Missiles ‘Break’ Israeli Defences | WION BREAKING..."
    },
    {
      "type": "text",
      "text": "Title: Iran | Today's latest from Al Jazeera\nPublished Date: 2026-03-10T09:08:02.129Z\nURL: https://www.aljazeera.com/where/iran/\nText: Iran | Iran | Today's latest from Al Jazeera..."
    }
  ]
}
```

失败时示例：

```json
{
  "error": "tool not found"
}
```

### Step 4: 结果处理与降级

- **成功**：基于工具返回的数据回答用户。
- **失败**：尝试列表中的下一个工具。
- **全部失败**：诚实告知用户无法获取信息，并建议手动查询方向。

## 使用协议 (Usage Protocol)

### 1. 多轮对话中的上下文继承
用户常会使用代词（“那边”、“它”、“这两天”）。在调用 `recommend` 之前，**必须**先解析指代关系。
- **Bad**: Query = "那边的住房价格" -> 推荐结果可能不准确。
- **Good**: Query = "北海道的住房价格" -> 推荐结果精准。

### 2. 复杂意图拆解
对于“这两天合适去吗？”这类问题，通常需要拆解为客观数据查询：
- 天气查询（温度、风雪）
- 交通/新闻查询（是否有突发事件）
- **Agent 策略**：先搜索“天气”或“旅游建议”类工具。

### 3. 数据时效性
对于新闻（“最新战况”）、价格（“住房价格”）类问题，**必须**使用工具，严禁使用模型训练数据编造。

### 4. 结果验证与错误恢复
- **空结果处理**：如果工具返回空列表或无相关数据，**不要编造**。应诚实告知用户：“抱歉，暂时未查询到相关数据”，并建议用户换个问法。
- **参数错误**：如果执行失败提示参数错误，尝试根据错误提示修正参数后重试一次。

### 5. 隐私与安全
- **不要**在 Query 中包含用户的敏感个人信息（如手机号、精确住址），除非工具明确要求且用户已授权。
- 使用模糊查询（如“北京市朝阳区天气”）代替精确坐标查询，除非必要。
- 不发送原始聊天记录作为请求体，统一采用**摘要化、结构化、最小化**的参数。

## 示例对话

### 示例 1：实时数据查询（天气）
**用户**: "the air quality in Beijing"
**Agent 思考**: 用户未指定地点，尝试根据用户属性或上下文推断，若无则默认查询热门城市或询问用户。假设上下文隐含 "Beijing"。
**Action**:
1. Recommend Query: "the air quality in Beijing"
2. Tool Selected: `E_qweather_get-air-quality`
3. Execute Params: `{"city": "Beijing"}`
4. Response: "The air quality in Beijing is good, with a PM2.5 concentration of 15 µg/m³."

### 示例 2：时事新闻查询
**用户**: "finds comprehensive information about bytedance"
**Agent 思考**: 这是一个综合信息查询需求。
**Action**:
1. Recommend Query: "comprehensive information about ByteDance"
2. Tool Selected: `company_profile_tool` 或 `news_search`
3. Execute Params: `{"company": "ByteDance"}`
4. Response: 整合工具返回的公司概况、最新动态等信息。


---

## 参考资料

详见 `references/api-specification.md` 了解 API 详细规格。
