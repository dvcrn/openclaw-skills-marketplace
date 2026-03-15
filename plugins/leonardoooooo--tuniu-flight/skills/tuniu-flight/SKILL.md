---
name: tuniu-flight
description: "途牛机票助手 - 通过 exec + curl 调用 MCP 实现国内航班搜索、舱位查询、预订下单。适用于用户询问航班、查询机票价格或提交机票订单时使用。"
---

# 途牛机票助手

当用户询问航班搜索、舱位查询或机票预订时，使用此 skill 通过 exec 执行 curl 调用途牛机票 MCP 服务。

## 运行环境要求

本 skill 通过 **shell exec** 执行 **curl** 向 MCP endpoint 发起 HTTP POST 请求，使用 JSON-RPC 2.0 / `tools/call` 协议。**运行环境必须提供 curl 或等效的 HTTP 调用能力**（如 wget、fetch 等可发起 POST 的客户端），否则无法调用 MCP 服务。

## 隐私与个人信息（PII）说明

预订功能会将用户提供的**个人信息**（联系人姓名、手机号、乘机人姓名、证件号等）通过 HTTP POST 发送至途牛机票 MCP 远端服务（`https://openapi.tuniu.cn/mcp/flight`），以完成机票预订。使用本 skill 即表示用户知晓并同意上述 PII 被发送到外部服务。请勿在日志或回复中暴露用户个人信息。

## 适用场景

- 按出发/到达城市、日期搜索航班（第一页、翻页）
- 查看指定航班的舱位价格详情
- 用户确认后创建机票预订订单

## 配置要求

### 必需配置

- **TUNIU_API_KEY**：途牛开放平台 API key，用于 `apiKey` 请求头

用户需在[途牛开放平台](https://open.tuniu.com/mcp)注册并获取上述密钥。

### 可选配置

- **FLIGHT_MCP_URL**：MCP 服务地址，默认 `https://openapi.tuniu.cn/mcp/flight`

## 调用方式

**直接调用工具**：使用以下请求头调用 `tools/call` 即可：

- `apiKey: $TUNIU_API_KEY`
- `Content-Type: application/json`
- `Accept: application/json, text/event-stream`

## 可用工具

**重要**：下方示例中的参数均为占位，调用时需**根据用户当前需求**填入实际值（城市、日期、航班号、乘机人、联系方式等），勿直接照抄示例值。

### 1. 航班搜索 (searchLowestPriceFlight)

**支持 6 种查询模式**：
- **默认低价查询**：不传 searchType，查询最低价航班
- **TIME 时间范围查询**：searchType="TIME"，按出发/到达时间范围筛选
- **PRICE 价格区间查询**：searchType="PRICE"，按价格区间筛选
- **NEAR_GO 周边出发**：searchType="NEAR_GO"，查询出发地周边机场
- **NEAR_BACK 周边到达**：searchType="NEAR_BACK"，查询目的地周边机场
- **TRANSFER 中转查询**：searchType="TRANSFER"，查询中转航班

**第一页**：必填 `departureCityName`、`arrivalCityName`、`departureDate`（格式 YYYY-MM-DD）。

**翻页**：传相同的城市日期参数和 `pageNum`（2=第二页，3=第三页…）。用户说「还有吗」「翻页」「下一页」时用相同参数 + pageNum 再次调用即可。

**触发词**：某地到某地航班、查机票、搜航班、机票价格、按时间查、按价格查、周边出发、中转航班

```bash
# 第一页：出发城市、到达城市、日期按用户需求填写（日期格式 YYYY-MM-DD）
# 默认低价查询
curl -s -X POST "${FLIGHT_MCP_URL:-https://openapi.tuniu.cn/mcp/flight}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"searchLowestPriceFlight","arguments":{"departureCityName":"<用户指定的出发城市>","arrivalCityName":"<用户指定的到达城市>","departureDate":"<用户指定的出发日期 YYYY-MM-DD>"}}}'

# TIME 模式：按时间范围查询（早班机）
curl -s -X POST "${FLIGHT_MCP_URL:-https://openapi.tuniu.cn/mcp/flight}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"searchLowestPriceFlight","arguments":{"departureCityName":"北京","arrivalCityName":"上海","departureDate":"2026-03-15","searchType":"TIME","departureTime":"06:00-10:00"}}}'

# PRICE 模式：按价格区间查询
curl -s -X POST "${FLIGHT_MCP_URL:-https://openapi.tuniu.cn/mcp/flight}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"searchLowestPriceFlight","arguments":{"departureCityName":"北京","arrivalCityName":"上海","departureDate":"2026-03-15","searchType":"PRICE","priceRange":"500-800"}}}'

# NEAR_GO 模式：周边机场出发查询
curl -s -X POST "${FLIGHT_MCP_URL:-https://openapi.tuniu.cn/mcp/flight}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"searchLowestPriceFlight","arguments":{"departureCityName":"北京","arrivalCityName":"上海","departureDate":"2026-03-15","searchType":"NEAR_GO"}}}'

# NEAR_BACK 模式：周边机场到达查询
curl -s -X POST "${FLIGHT_MCP_URL:-https://openapi.tuniu.cn/mcp/flight}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"searchLowestPriceFlight","arguments":{"departureCityName":"北京","arrivalCityName":"上海","departureDate":"2026-03-15","searchType":"NEAR_BACK"}}}'

# TRANSFER 模式：中转航班查询
curl -s -X POST "${FLIGHT_MCP_URL:-https://openapi.tuniu.cn/mcp/flight}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"searchLowestPriceFlight","arguments":{"departureCityName":"北京","arrivalCityName":"上海","departureDate":"2026-03-15","searchType":"TRANSFER"}}}'
```

```bash
# 翻页：传相同的城市日期 + pageNum
curl -s -X POST "${FLIGHT_MCP_URL:-https://openapi.tuniu.cn/mcp/flight}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"searchLowestPriceFlight","arguments":{"departureCityName":"<出发城市>","arrivalCityName":"<到达城市>","departureDate":"<出发日期 YYYY-MM-DD>","pageNum":2}}}'
```

### 2. 舱位详情查询 (multiCabinDetails)

**入参**：`departureCityName`、`arrivalCityName`、`departureDate`（YYYY-MM-DD）、`flightNo`（航班号，从搜索结果获取）均为必填。

**返回**：`flightInfo`（航班详情）、`cabinInfo`（舱位列表，含 sourceId、vendorId、cabinCodes、价格、退改签规则等）。**sourceId、vendorId、cabinCodes 为下单必填，需保留供 saveOrder 使用。**

**触发词**：舱位、票价详情、看一下这个航班、这个航班有什么舱位

```bash
# departureCityName、arrivalCityName、departureDate 从搜索结果或用户需求取，flightNo 从搜索结果取
curl -s -X POST "${FLIGHT_MCP_URL:-https://openapi.tuniu.cn/mcp/flight}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"multiCabinDetails","arguments":{"departureCityName":"<出发城市>","arrivalCityName":"<到达城市>","departureDate":"<出发日期 YYYY-MM-DD>","flightNo":"<航班号>"}}}'
```

### 3. 获取预订信息 (getBookingRequiredInfo)

**功能**：获取机票预订所需填写的字段说明，下单前必须先调用此接口了解必填字段。

**触发词**：预订要填什么、下单需要什么信息

```bash
curl -s -X POST "${FLIGHT_MCP_URL:-https://openapi.tuniu.cn/mcp/flight}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"getBookingRequiredInfo","arguments":{}}}'
```

### 4. 创建订单 (saveOrder)

**前置条件**：
- 必须先调用 `searchLowestPriceFlight` 获取航班信息
- 必须调用 `multiCabinDetails` 获取舱位详情；从返回的 `cabinInfo` 中选取舱位，拿到 `sourceId`、`vendorId`、`cabinCodes`
- 建议先调用 `getBookingRequiredInfo` 了解必填字段

**必填参数**：departureCityName、arrivalCityName、departureDate（YYYY-MM-DD）、flightNo、sourceId、vendorId、cabinCodes、tourists（乘机人列表）、contactTourist（联系人信息）。

**tourists 格式**：

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 姓名 |
| firstname | string | 名（拼音/英文） |
| lastname | string | 姓（拼音/英文） |
| psptType | number | 证件类型：1身份证, 2因私护照, 3军官证, 4港澳通行证, 7台胞证, 11台湾通行证, 12驾驶证 |
| psptId | string | 证件号码 |
| sex | number | 性别：1男, 0女, 9未知 |
| psptEndDate | string | 证件过期日期 YYYY-MM-DD |
| birthday | string | 生日 YYYY-MM-DD |
| touristType | number | 乘客类型：0成人, 1儿童, 2婴儿 |
| tel | string | 手机号 |
| intlCode | string | 国际区号（默认86） |
| index | number | 出游人下标，从0开始 |

**contactTourist 格式**：

| 字段 | 类型 | 说明 |
|------|------|------|
| name | string | 联系人姓名 |
| tel | string | 联系人手机号 |
| email | string | 联系人邮箱 |

**触发词**：预订、下单、订机票、我要订、提交订单

```bash
# sourceId、vendorId、cabinCodes 从最近一次 multiCabinDetails 结果取；乘机人、联系人按用户需求填
curl -s -X POST "${FLIGHT_MCP_URL:-https://openapi.tuniu.cn/mcp/flight}" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "apiKey: $TUNIU_API_KEY" \
  -d '{
    "jsonrpc": "2.0",
    "id": 6,
    "method": "tools/call",
    "params": {
      "name": "saveOrder",
      "arguments": {
        "departureCityName": "<出发城市>",
        "arrivalCityName": "<到达城市>",
        "departureDate": "<出发日期 YYYY-MM-DD>",
        "flightNo": "<航班号>",
        "sourceId": "<multiCabinDetails 返回的 sourceId>",
        "vendorId": "<multiCabinDetails 返回的 vendorId>",
        "cabinCodes": "<multiCabinDetails 返回的 cabinCodes>",
        "tourists": [
          {
            "name": "<乘机人姓名>",
            "psptType": 1,
            "psptId": "<证件号码>",
            "sex": 1,
            "birthday": "<生日 YYYY-MM-DD>",
            "touristType": 0,
            "tel": "<手机号>",
            "index": 0
          }
        ],
        "contactTourist": {
          "name": "<联系人姓名>",
          "tel": "<联系人手机号>",
          "email": "<联系人邮箱>"
        }
      }
    }
  }'
```

（sourceId、vendorId、cabinCodes 必须来自最近一次 multiCabinDetails 的返回，不可用示例值。）

## 响应处理

### 成功响应

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [{"type": "text", "text": "..."}]
  },
  "id": 2
}
```

- **本项目中** 工具结果统一放在 **`result.content[0].text`** 中。`text` 为 **JSON 字符串**，需先 `JSON.parse(result.content[0].text)` 再使用。
- 解析后为业务对象，各工具结构不同：
  - **航班列表**（searchLowestPriceFlight）：`successCode`、`data`（航班列表，含 flightNumber、departureAirport、arrivalAirport、departureTime、arrivalTime、basePrice、cabinClass、remainingSeats 等）。
  - **舱位详情**（multiCabinDetails）：`successCode`、`flightInfo`、`cabinInfo`（含 sourceId、vendorId、cabinCodes、basePrice、refundChangeRule、baggageInfo 等）。
  - **创建订单**（saveOrder）：`successCode`、`orderId`、`orderStatus`、`payAmount`、`payUrl`、`createTime`。
- 错误时 `text` 解析后为 `{ "successCode": false, "errorMessage": "错误信息" }`，可从 `errorMessage` 字段取提示文案。

### 错误响应

本项目中错误分两类，需分别处理：

**1. 传输/会话层错误**（无 `result`，仅有顶层 `error`，通常伴随 HTTP 4xx/5xx）：

```json
{
  "jsonrpc": "2.0",
  "error": {"code": -32000, "message": "..."},
  "id": null
}
```
- **Method Not Allowed**：GET 等非 POST 请求
- **Internal server error**（code -32603）：服务内部异常

**2. 工具层错误**（HTTP 仍为 200，有 `result`）：与成功响应结构相同，但 `result.content[0].text` 解析后为 `{ "successCode": false, "errorMessage": "错误信息" }`。例如参数校验失败、舱位信息失效、下单失败等，从 `errorMessage` 字段取文案提示用户或重试。

## 输出格式建议

- **搜索列表**：以表格或清单展示航班号、出发/到达机场、时间、价格、舱位、剩余座位；可提示「可以说翻页/下一页」
- **舱位详情**：分块展示舱位、价格、退改签规则、行李额；提示用户可预订
- **预订成功**：明确写出订单号、支付金额、支付链接、航班信息、乘机人信息

## 使用示例

以下示例中，所有参数均从**用户表述或上一轮结果**中解析并填入，勿用固定值。

**用户**：3 月 15 号北京到上海的航班

**AI 执行**：按用户意图填参：departureCityName=北京、arrivalCityName=上海、departureDate=2026-03-15，调用 searchLowestPriceFlight（请求头需带 apiKey、Content-Type、Accept）。解析 result.content[0].text，整理航班列表回复。

**用户**：还有吗？/ 下一页

**AI 执行**：用相同的城市日期参数 + pageNum=2（或 3、4…）再次调用 searchLowestPriceFlight。

**用户**：看一下 MU5101 这个航班的舱位

**AI 执行**：从上一轮列表确认航班号 MU5101，连同城市和日期，调用 multiCabinDetails；解析舱位列表后展示价格、退改签规则、行李信息，并提示可预订。

**用户**：订这个，联系人张三 13800138000，乘机人李四 身份证 310101199001011234

**AI 执行**：从最近一次 multiCabinDetails 结果取 sourceId、vendorId、cabinCodes；按用户提供的乘机人信息填 tourists（name=李四、psptType=1、psptId=310101199001011234、sex=1、birthday=1990-01-01、touristType=0、tel=13800138000、index=0），contactTourist（name=张三、tel=13800138000）。成功后回复订单号、支付金额、支付链接，并提醒用户完成支付。

## 注意事项

1. **密钥安全**：不要在回复或日志中暴露 TUNIU_API_KEY
2. **PII 安全**：联系人姓名、手机号、乘机人姓名、证件号等仅在预订时发送至 MCP 服务，勿在日志或回复中暴露
3. **认证**：若遇协议或认证错误，可重试或检查 TUNIU_API_KEY
4. **日期格式**：所有日期均为 YYYY-MM-DD
5. **下单前**：saveOrder 的 sourceId、vendorId、cabinCodes 必须来自最近一次 multiCabinDetails 的返回；若间隔较长，建议重新调舱位详情刷新报价
6. **翻页**：用户要「更多」「下一页」时用相同的城市日期参数 + pageNum（≥2）调用即可
7. **支付提醒**：下单成功后必须提示用户点击 payUrl 完成支付