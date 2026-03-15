# AI 会话 - 完整接口说明

## 接口路径

- 流式 / 非流式均使用同一路径：`/linkfox-ai/chat/v1/stream/completion/create`
- 请求方式：POST
- 请求体：application/json
- 流式响应：text/event-stream（SSE）
- 非流式响应：JSON（包裹在开放平台标准响应结构中）

---

## 请求参数

| 参数 | 说明 | 必填 | 类型 |
|------|------|------|------|
| content | 聊天内容 | 是 | string |
| chatId | 会话 ID，第二次及以后的会话需传入（首次对话不传，接口会返回 chatId） | 否 | number |
| modelParam | 模型选择：1=gpt-3.5-turbo，2=gpt-3.5-turbo-16k，3=gpt-4，4=gpt-4-32k，9=gpt-4o。默认 1 | 否 | number |
| promptSystem | 系统预设模板（详见下方「模板用法」） | 否 | string |
| imageUrls | 图片 URL 数组，仅 modelParam=9（gpt-4o）时生效，最多 3 张 | 否 | array |
| checkSensitiveWord | 是否检测敏感词，默认 false | 否 | boolean |
| maxTokens | 回答最大 tokens，达到后会被截断 | 否 | number |
| temperature | 温度 [0, 2]。越低越确定性，越高越创造性。默认约 0.7 | 否 | number |
| topP | 控制随机性 [0, 1]。与 temperature 类似但使用不同方法，降低 topP 缩小 token 选择范围 | 否 | number |
| stop | 停止序列。模型响应将在指定序列之前结束（不包含该序列）。最多 4 个停止序列 | 否 | string |
| frequencyPenalty | 频率惩罚。根据 token 已出现频率按比例降低重复概率，减少逐字重复 | 否 | number |
| presencePenalty | 存在惩罚。降低已出现 token 再次出现的概率，促进引入新主题 | 否 | number |

### 请求示例

```json
{
  "content": "你好",
  "modelParam": 1,
  "checkSensitiveWord": false,
  "maxTokens": 2000,
  "temperature": 0.7
}
```

多轮对话（传入上一次返回的 chatId）：

```json
{
  "content": "继续上面的话题",
  "chatId": 1347,
  "modelParam": 9
}
```

带图片的对话（gpt-4o）：

```json
{
  "content": "描述这张图片的内容",
  "modelParam": 9,
  "imageUrls": ["https://example.com/photo.jpg"]
}
```

---

## 流式响应

响应类型为 `text/event-stream`（SSE）。每行以 `data:` 开头，最终以 `[DONE]` 标记结束。

**响应事件结构：**

| 事件 | 说明 |
|------|------|
| `{"role":2,"chatId":1347,"replyId":15399,"id":15400}` | 首条事件：角色标识(2=助手)、会话 ID、回复 ID、消息 ID |
| `{"delta":{"content":"你"}}` | 增量内容，逐 token 推送 |
| `{"tokens":140}` | 总 tokens |
| `{"promptTokens":112}` | 历史会话+当前问题消耗的 tokens |
| `{"completionTokens":28}` | 本次回答消耗的 tokens |
| `[DONE]` | 流结束标记 |

**流式响应示例：**

```
data:{"role":2,"chatId":1347,"replyId":15399,"id":15400}
data:{"delta":{"content":"你"}}
data:{"delta":{"content":"好"}}
data:{"delta":{"content":"！"}}
data:{"tokens":140}
data:{"promptTokens":112}
data:{"completionTokens":28}
[DONE]
```

---

## 非流式响应

**响应体（对应开放平台响应 data）：**

| 参数 | 说明 | 类型 |
|------|------|------|
| traceId | 链路 ID | string |
| code | 状态码，200 为成功 | string |
| msg | 成功/错误描述 | string |
| msgKey | 错误码，code 非 200 时存在 | string |
| data.chatId | 会话 ID（后续多轮对话需传回） | number |
| data.status | 1=正常，4=失败 | number |
| data.errorCode | 错误码（失败时） | string |
| data.errorBody | 错误详情（失败时） | string |
| data.content | 响应内容 | string |
| data.tokens | 总使用 tokens | number |
| data.promptTokens | 历史会话+当前问题 tokens | number |
| data.completionTokens | 本次回答 tokens | number |

**非流式响应示例：**

```json
{
  "traceId": "12345678-1234-1234-1234-123456789abc",
  "code": "200",
  "msg": "成功",
  "data": {
    "chatId": 12345,
    "status": 1,
    "content": "你好！我是AI助手，很高兴为您服务。有什么我可以帮助您的吗？",
    "tokens": 50,
    "promptTokens": 20,
    "completionTokens": 30
  }
}
```

---

## promptSystem 模板用法

### 占位符

模板中使用 `{{参数名}}` 作为占位符，调用时需将占位符替换为实际值。

**示例模板：**

```
你是一位经验丰富的亚马逊Listing创作员，你拥有极丰富的商品营销经验，
请根据我以下的输入编写亚马逊的五点描述，商品名称是：{{param1}}
商品描述信息是：{{param2}}
Please answer in {{language}}
```

**调用时替换占位符后传入 content：**

```json
{
  "content": "你是一位经验丰富的亚马逊Listing创作员，你拥有极丰富的商品营销经验，请根据我以下的输入编写亚马逊的五点描述，商品名称是：iphone13pro\n商品描述信息是：苹果最新款\nPlease answer in English"
}
```

### 语言参数 `{{language}}`

| 语言 | 参数值 |
|------|--------|
| 英文 | English |
| 中文 | Chinese |
| 西班牙语 | Spanish |
| 德语 | German |
| 法语 | French |
| 意大利语 | Italian |
| 日语 | Japanese |
| 荷兰语 | Dutch |
| 波兰语 | Polish |
| 瑞典语 | Swedish |
| 韩语 | Korean |
| 葡萄牙语 | Portuguese |
| 泰语 | Thai |
| 越南语 | Vietnamese |
| 印尼语 | Indonesian |
| 土耳其语 | Turkish |

### 系统模板参数（promptSystem 中可用）

| 参数名 | 描述 | 默认值 |
|--------|------|--------|
| country | 国家 | 空 |
| region | 地区 | 空 |
| month | 月份 | 空 |
| asin | ASIN | 空 |
| price | 售价 | 空 |
| follow_sales_num | 跟卖数量 | 空 |
| follow_sales | 跟卖商家列表 | 空 |
| category | 类目 | 空 |
| sif_keyword_overide | 关键词 | 空 |
| review_rate | 商品评分 | 空 |
| key_comment | 买家评论要点 | 空 |
| title | 商品标题 | 空 |
| five_desc | 商品特性（五点描述） | 空 |
| product_desc | 商品描述 | 空 |

### 完整模板调用示例

同时使用 content（用户指令）+ promptSystem（系统预设）：

```json
{
  "content": "请仿写一个吸引眼球的Listing，用English输出",
  "promptSystem": "我会给你一段文本信息，请你明确理解以下几个词汇概念：\n国家，地区，当前月份，关键词，商品类目，评论要点，Listing（包含商品标题、商品特性、商品描述），ASIN，售价，跟卖商家，跟卖数量。\n下面是文本信息：\n当前国家为美国，当前地区为New York，当前月份为12月；\nASIN是：B08PBMTX95；\n售价是：$11.99；\n类目：Cell Phones & Accessories；\n商品标题：SOH Mingying iPhone 12 Silicone Case；\n商品特性：1、TRIPLE PROTECTION...\n",
  "modelParam": 9
}
```

---

## 错误码

错误码见本 skill 内 `references/open-platform.md`，或开放平台 https://open.ziniao.com 。
