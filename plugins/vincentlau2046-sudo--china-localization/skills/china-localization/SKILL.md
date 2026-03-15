---
name: china-localization
description: "中国本地化工具包：中文搜索、天气查询、飞书/微信/钉钉集成。让中国用户零门槛使用 OpenClaw。"
homepage: https://github.com/vincentlau2046-sudo/china-localization
---

# China Localization Pack - 中国本地化包

为中国用户提供的本地化工具，支持中文搜索、天气查询、飞书/微信/钉钉等本地服务集成。

## 配置

在 `~/.config/china-localization/` 目录下存储 API Key：

```bash
mkdir -p ~/.config/china-localization

# Tavily API Key（必需，用于中文搜索和天气）
echo "tvly-YOUR_KEY" > ~/.config/china-localization/tavily_key

# 飞书配置（可选）
echo "cli_xxx" > ~/.config/china-localization/feishu_app_id
echo "your_secret" > ~/.config/china-localization/feishu_app_secret
echo "your_token" > ~/.config/china-localization/feishu_user_token

# 微信公众号配置（可选）
echo "wx_xxx" > ~/.config/china-localization/wechat_app_id
echo "your_secret" > ~/.config/china-localization/wechat_app_secret

# 钉钉机器人 Webhook（可选）
echo "https://oapi.dingtalk.com/robot/send?access_token=xxx" > ~/.config/china-localization/dingtalk_webhook
```

---

## 中文搜索（Tavily）

使用 Tavily 搜索中文内容，优先返回中文结果。

### 基础搜索

```bash
TAVILY_KEY=$(cat ~/.config/china-localization/tavily_key)

curl -s "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d "{
    \"api_key\": \"$TAVILY_KEY\",
    \"query\": \"AI 最新动态\",
    \"search_depth\": \"basic\",
    \"max_results\": 5
  }" | jq '.results[] | {title: .title, url: .url, content: .content[:200]}'
```

### 搜索并提取全文

```bash
curl -s "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d "{
    \"api_key\": \"$TAVILY_KEY\",
    \"query\": \"大模型技术进展\",
    \"search_depth\": \"advanced\",
    \"max_results\": 5,
    \"include_raw_content\": true
  }" | jq '.results[] | {title: .title, url: .url, raw_content: .raw_content[:500]}'
```

### 按时间范围搜索

```bash
curl -s "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d "{
    \"api_key\": \"$TAVILY_KEY\",
    \"query\": \"GPT-5 发布\",
    \"search_depth\": \"basic\",
    \"max_results\": 5,
    \"include_domains\": [\"openai.com\", \"techcrunch.com\"]
  }"
```

---

## 天气查询

### 方式 1：wttr.in（免费，无需 API Key）

```bash
# 简洁格式
curl -s "wttr.in/深圳?format=3"
# 输出：深圳: 🌤 +25°C

# 详细格式
curl -s "wttr.in/深圳?lang=zh"
# 输出中文详细天气预报

# 仅温度
curl -s "wttr.in/深圳?format=%t"
# 输出：+25°C

# 仅天气状况
curl -s "wttr.in/深圳?format=%C"
# 输出：多云
```

### 方式 2：Tavily 搜索天气

```bash
curl -s "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d "{
    \"api_key\": \"$TAVILY_KEY\",
    \"query\": \"深圳 天气 今天 温度\",
    \"search_depth\": \"basic\",
    \"max_results\": 3
  }"
```

---

## 飞书集成

### 获取 Access Token

```bash
APP_ID=$(cat ~/.config/china-localization/feishu_app_id)
APP_SECRET=$(cat ~/.config/china-localization/feishu_app_secret)

# 获取 tenant_access_token
curl -s "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"$APP_ID\",
    \"app_secret\": \"$APP_SECRET\"
  }" | jq '.tenant_access_token'
```

### 获取日历事件

```bash
TOKEN=$(cat ~/.config/china-localization/feishu_user_token)

curl -s "https://open.feishu.cn/open-apis/calendar/v4/calendars/primary/events?start_time=$(date -d 'today 00:00' +%s)000&end_time=$(date -d 'today 23:59' +%s)000" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.data.events[] | {summary: .summary, start: .start_time, end: .end_time}'
```

### 获取任务列表

```bash
TOKEN=$(cat ~/.config/china-localization/feishu_user_token)

curl -s "https://open.feishu.cn/open-apis/task/v2/tasks?page_size=50" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq '.data.items[] | {name: .name, due: .due, status: .status}'
```

### 发送消息

```bash
TOKEN=$(cat ~/.config/china-localization/feishu_user_token)
RECEIVE_ID="ou_xxx"  # 用户 Open ID

curl -s "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"$RECEIVE_ID\",
    \"msg_type\": \"text\",
    \"content\": \"{\\\"text\\\":\\\"你好，这是测试消息\\\"}\"
  }"
```

### 读取文档

```bash
TOKEN=$(cat ~/.config/china-localization/feishu_user_token)
DOC_TOKEN="docx_xxx"  # 从 URL 提取

curl -s "https://open.feishu.cn/open-apis/docx/v1/documents/$DOC_TOKEN/blocks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

---

## 微信集成

### 获取 Access Token

```bash
APP_ID=$(cat ~/.config/china-localization/wechat_app_id)
APP_SECRET=$(cat ~/.config/china-localization/wechat_app_secret)

curl -s "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=$APP_ID&secret=$APP_SECRET" | jq '.access_token'
```

### 发送模板消息

```bash
ACCESS_TOKEN="xxx"
OPENID="oxxx"  # 用户 OpenID

curl -s "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token=$ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"touser\": \"$OPENID\",
    \"template_id\": \"TEMPLATE_ID\",
    \"data\": {
      \"title\": {\"value\": \"通知标题\"},
      \"content\": {\"value\": \"通知内容\"}
    }
  }"
```

---

## 钉钉集成

### 发送机器人消息

```bash
WEBHOOK=$(cat ~/.config/china-localization/dingtalk_webhook)

# 文本消息
curl -s "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "msgtype": "text",
    "text": {"content": "这是一条测试消息"}
  }'

# Markdown 消息
curl -s "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "msgtype": "markdown",
    "markdown": {
      "title": "通知标题",
      "text": "## 标题\n内容正文\n- 项目 1\n- 项目 2"
    }
  }'

# @所有人
curl -s "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "msgtype": "text",
    "text": {"content": "紧急通知！"},
    "at": {"isAtAll": true}
  }'
```

---

## 高德地图集成

### 地理编码（地址转坐标）

```bash
AMAP_KEY="your_amap_key"
ADDRESS="深圳市南山区"

curl -s "https://restapi.amap.com/v3/geocode/geo?key=$AMAP_KEY&address=$ADDRESS" | jq '.geocodes[0] | {address: .formatted_address, location: .location}'
```

### 路径规划

```bash
ORIGIN="116.481028,39.989643"
DESTINATION="116.465302,40.004717"

curl -s "https://restapi.amap.com/v3/direction/driving?key=$AMAP_KEY&origin=$ORIGIN&destination=$DESTINATION" | jq '.route.paths[0] | {distance: .distance, duration: .duration, steps: (.steps | length)}'
```

---

## 常用组合场景

### 晨间简报

```bash
# 1. 获取天气
WEATHER=$(curl -s "wttr.in/深圳?format=3")
echo "🌤️ 天气: $WEATHER"

# 2. 搜索 AI 新闻
curl -s "https://api.tavily.com/search" \
  -H "Content-Type: application/json" \
  -d "{\"api_key\": \"$TAVILY_KEY\", \"query\": \"AI 新闻 今日\", \"max_results\": 3}" | jq '.results[].title'

# 3. 获取飞书日历（如果有配置）
# ...

# 4. 推送到钉钉（如果有配置）
# ...
```

### 消息推送

```bash
# 构建消息内容
MESSAGE="## 每日简报\n\n天气: $WEATHER\n\n热点新闻:\n1. $NEWS1\n2. $NEWS2"

# 推送到钉钉
curl -s "$WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "{\"msgtype\": \"markdown\", \"markdown\": {\"title\": \"每日简报\", \"text\": \"$MESSAGE\"}}"
```

---

## 错误处理

所有 API 调用应该检查错误：

```bash
# 检查 Tavily 错误
RESPONSE=$(curl -s "https://api.tavily.com/search" ...)
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
  echo "❌ 搜索失败: $(echo $RESPONSE | jq -r '.error')"
  exit 1
fi

# 检查飞书错误
if echo "$RESPONSE" | jq -e '.code != 0' > /dev/null 2>&1; then
  echo "❌ 飞书 API 错误: $(echo $RESPONSE | jq -r '.msg')"
  exit 1
fi
```

---

## 依赖

- **必需**: `curl`, `jq`, Tavily API Key
- **可选**: 飞书/微信/钉钉/高德账号

无需安装 npm 包，所有功能通过 curl 调用 API 实现。