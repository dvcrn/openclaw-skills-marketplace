# Examples

## 0. `user_id` 或 `apikey` 缺失

场景：
- 用户想用量化图、行情问答或实时监控
- 但还没有提供 `user_id`、`apikey`，或只提供了其中一个

OpenClaw 应这样处理：
- 不要直接请求接口
- 先明确告诉用户缺少哪个字段
- 引导用户去鹰眼量化站点的"用户中心" -> "开发 API"获取

示例提示：

```text
继续之前需要先提供 user_id 和 apikey。

你可以在鹰眼量化网站的“用户中心” -> “开发 API”页面获取这两个值：
https://yingyan.chatface.com/
```

## 1. 用户发送自然语言选股条件

请求：

```http
POST /api/openclaw/stock/query
Content-Type: application/json

{
  "query": "涨幅超过8%的半导体股票，按换手率从高到低排序，取前20只",
  "user_id": "68b26718213929ab1d78aae5",
  "apikey": "YOUR_12_CHAR_KEY"
}
```

预期：
- 返回 `intent=stock_query`
- 最多返回 20 条股票记录
- 只返回固定字段，不返回网页端那种大字段全集
- 适合在 OpenClaw 对话中直接渲染成精简表格

## 2. 用户只发股票代码

请求：

```http
POST /api/openclaw/stock/message
Content-Type: application/json

{
  "message": "000001",
  "user_id": "68b267182139",
  "apikey": "YOUR_12_CHAR_KEY"
}
```

预期：
- 返回 `intent=chart`
- 读取 `render_markdown`
- 将量化图 markdown 直接渲染到聊天界面

## 3. 用户只发股票名称

请求：

```http
POST /api/openclaw/stock/message
Content-Type: application/json

{
  "message": "平安银行",
  "user_id": "68b26718213929",
  "apikey": "YOUR_12_CHAR_KEY"
}
```

预期：
- 返回 `intent=chart`
- 读取 `render_markdown`

## 4. 用户发送"股票+行情"

请求：

```http
POST /api/openclaw/stock/message
Content-Type: application/json

{
  "message": "平安银行行情",
  "user_id": "68b267182139",
  "apikey": "YOUR_12_CHAR_KEY"
}
```

预期：
- 返回 `intent=market_query`
- 返回 `stock_context`（TDX 截面数据结构化信息）
- 返回 `system_prompt` 和 `user_prompt`
- OpenClaw 大模型使用 `system_prompt` 作为系统角色、`user_prompt` 作为用户消息，生成趋势诊断并返回给用户

## 5. 股票匹配到多个候选

请求：

```http
POST /api/openclaw/stock/message
Content-Type: application/json

{
  "message": "平安行情",
  "user_id": "68b267182139",
  "apikey": "YOUR_12_CHAR_KEY"
}
```

预期：
- 返回 `ok=false`
- `error.code=multiple`
- 提示用户从 `error.candidates` 中选择更精确的股票

## 6. 获取实时监控接入信息

请求：

```http
GET /api/openclaw/stock/monitor/stream?user_id=68b2671
```

预期：
- 返回 `ws_url_template`
- 由客户端填入 `apikey` 与 `user_id` 后连接 WebSocket 服务

## 7. 建立 WebSocket 实时监控连接

连接地址（由 `ws_url_template` 拼接）：

```text
wss://yingyan.chatface.com/ws/monitor/open?apikey=YOUR_12_CHAR_KEY&user_id=68b2671825
```

预期：
- 连接成功后持续接收 JSON 数组格式的监控信号推送
- 每条推送包含 `ticker`、`name`、`prev_rating`、`latest_rating`、`close`、`zhangdie`、`latest_time`
- 连接断开后可自动重连

补充说明：
- 建议直接使用原生 WebSocket 客户端连接，不要默认先安装 `wscat`、`websocat`。
- 连接建立后如果暂时没有消息，属于正常现象；服务端不会先发送欢迎包。
- 只有监控信号发生有效变化时才会推送；若最新评级变为 `await`，不会推送。

## 8. OpenClaw 配置实时监控的推荐流程

步骤 1：先验证凭证

```http
POST /api/openclaw/stock/message
Content-Type: application/json

{
  "message": "000001",
  "user_id": "68b26718213929ab1d78aae5",
  "apikey": "YOUR_12_CHAR_KEY"
}
```

预期：
- 返回 `ok=true`
- 说明 `user_id` 与 `apikey` 至少对消息接口鉴权有效

如果凭证缺失：
- 不要继续走步骤 2 和步骤 3
- 先提示用户到"用户中心" -> "开发 API"补全 `user_id` 和 `apikey`

步骤 2：获取监控流模板

```http
GET /api/openclaw/stock/monitor/stream?user_id=68b26718213929ab1d78aae5
```

预期：
- 返回 `ws_url_template`
- 模板类似 `wss://yingyan.chatface.com/ws/monitor/open?apikey={apikey}&user_id={user_id}`

步骤 3：直接建立 WebSocket 连接

```text
wss://yingyan.chatface.com/ws/monitor/open?apikey=YOUR_12_CHAR_KEY&user_id=68b26718213929ab1d78aae5
```

预期：
- WebSocket 握手成功即表示连接成功
- 若连接后暂无消息，不应判定为失败
- 应向用户说明："连接正常，当前正在等待实时监控信号变化"

## 9. WebSocket 成功但没有立即收到消息

现象：
- 连接已经建立
- 一段时间内没有收到任何 JSON 消息

正确结论：
- 这是正常现象，不代表连接失败
- 服务端只在监控信号变化时推送
- 当评级变为 `await` 时不会推送

错误做法：
- 因为短时间没有消息，就反复改用 `wscat`、`websocat`、`curl` 等工具
- 把"连接后暂无消息"误判成"WebSocket 不可用"

## 10. OpenClaw 自然语言搜股与网页端选股的区别

网页端：
- 页面：`web/query/queryFundamentals.html`
- 接口：`POST /api/query/tdx`
- 返回可能较多列，偏完整分析表

OpenClaw：
- 接口：`POST /api/openclaw/stock/query`
- 最多只返回 20 只
- 只返回以下字段：
  - `代码`
  - `名称`
  - `涨幅%`
  - `现价`
  - `涨跌`
  - `换手%`
  - `细分行业`
  - `活跃度`
  - `连涨天`
  - `昨涨幅%`
  - `3日涨幅%`
  - `5日涨幅%`
  - `10日涨幅%`
  - `20日涨幅%`
  - `60日涨幅%`
  - `一年涨幅%`
  - `月初至今%`
  - `年初至今%`
  - `近日指标提示`

## 11. 健康检查

请求：

```http
GET /api/openclaw/health
```

预期：
- 返回 `service`、`endpoints`、`demo_page`
- 可用于平台接入前自检

## 12. 打开 demo 页面

地址：

```text
https://yingyan.chatface.com/web/openclaw_demo.html
```

预期：
- 可直接点按测试健康检查、消息入口、WebSocket 实时监控
