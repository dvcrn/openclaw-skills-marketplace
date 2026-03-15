---
name: codebox-qrcode
description: "智能二维码生成平台 CodeBox（码盒）的 Agent Skill。免费生成二维码图片（无需 API Key），也可生成带追踪的动态二维码、智能模板匹配、短链追踪分析、动态链接更新。支持品牌/节日/行业等 150+ 风格模板，零设计门槛生成专业级二维码。"
---

# CodeBox 码盒 — 智能二维码 Skill

CodeBox（码盒）是专业的智能二维码生成平台，支持动态二维码、带 Logo 二维码、彩色渐变二维码等多种样式，提供 UTM 参数追踪、扫码统计分析等功能。

本 Skill 提供两类能力：
- **免费能力**（无需 API Key）：直接生成二维码图片
- **高级能力**（需要 API Key）：带追踪的动态二维码、扫码统计、动态链接更新、模板浏览

## Setup

Base URL: `https://www.codebox.club`

### 免费使用（generate_image）

无需任何配置，直接调用即可。限制：10 次/分钟，最大 1000px。

### 高级功能（需要 API Key）

设置环境变量：
```
export CODEBOX_API_KEY=cb_sk_your_key_here
```

获取 API Key：https://www.codebox.club/dashboard/settings/api-keys

高级功能的请求需要 Header：
```
Authorization: Bearer $CODEBOX_API_KEY
Content-Type: application/json
```

---

## Actions

### 1. generate_image — 生成二维码图片（免费，无需 API Key）

直接生成二维码图片，支持 URL、文本、WiFi、名片等多种内容类型，支持自定义颜色、渐变、Logo、背景图、模板等丰富样式。返回二维码图片（PNG/SVG）。

**When to use**: 用户想快速生成一个二维码图片，不需要追踪和统计功能。

```bash
curl -s -X POST https://www.codebox.club/api/v1/qrcode/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "https://example.com",
    "size": 300,
    "format": "png",
    "dotsStyle": "rounded",
    "dotsColor": "#f59e0b",
    "backgroundColor": "#FFFFFF",
    "cornersSquareStyle": "dot",
    "cornersDotStyle": "dot",
    "errorCorrectionLevel": "M"
  }' \
  -o qrcode.png
```

**Parameters**:
| Parameter | Type | Required | Description |
|---|---|---|---|
| content | string | Yes | 要编码的 URL 或文本内容（最大 4000 字符） |
| type | string | No | 内容类型：`URL`、`TEXT`、`WIFI`、`VCARD`、`EMAIL`、`PHONE` |
| size | number | No | 图片尺寸 50-1000px（默认 300，有 API Key 时最大 2000） |
| format | string | No | 输出格式：`png`（默认）或 `svg` |
| margin | number | No | 边距 0-100（默认 10） |
| errorCorrectionLevel | string | No | 容错级别：`L`、`M`（默认）、`Q`、`H` |
| styleMode | string | No | `normal`（默认）或 `image`（带背景图模式） |
| templateId | string | No | 风格模板 ID（通过 `list_templates` 获取） |
| dotsStyle | string | No | 模块形状：`square`、`rounded`、`classy`、`classy-rounded`、`extra-rounded`、`dots` |
| dotsColor | string | No | 模块颜色（十六进制，如 `#000000`） |
| dotsGradient | object | No | 模块渐变：`{ type, rotation, colorStops }` |
| backgroundColor | string | No | 背景色（十六进制） |
| backgroundGradient | object | No | 背景渐变 |
| backgroundImage | string | No | 背景图片 URL |
| backgroundImageSize | number | No | 背景图缩放 0.1-2.0（默认 1.0） |
| backgroundImageOpacity | number | No | 背景图透明度 0.1-1.0（默认 1.0） |
| cornersSquareStyle | string | No | 定位点外框形状：`square`、`extra-rounded`、`dot` |
| cornersSquareColor | string | No | 定位点外框颜色 |
| cornersSquareGradient | object | No | 定位点外框渐变 |
| cornersDotStyle | string | No | 定位点内框形状：`square`、`dot`、`extra-rounded` |
| cornersDotColor | string | No | 定位点内框颜色 |
| cornersDotGradient | object | No | 定位点内框渐变 |
| logoUrl | string | No | Logo 图片 URL |
| logoSize | number | No | Logo 大小比例 0.1-0.5（默认 0.2） |
| logoMargin | number | No | Logo 边距 0-50（默认 5） |
| logoX | number | No | Logo X 位置 0-1（默认 0.5 居中） |
| logoY | number | No | Logo Y 位置 0-1（默认 0.5 居中） |
| responseFormat | string | No | 设为 `json` 返回 base64 JSON 而非图片二进制 |

**WiFi 类型示例**：
```bash
curl -s -X POST https://www.codebox.club/api/v1/qrcode/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "MyWiFi",
    "type": "WIFI",
    "wifi": { "ssid": "MyWiFi", "password": "12345678", "security": "WPA" },
    "dotsStyle": "rounded",
    "dotsColor": "#3b82f6"
  }' \
  -o wifi-qrcode.png
```

**名片类型示例**：
```bash
curl -s -X POST https://www.codebox.club/api/v1/qrcode/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "vcard",
    "type": "VCARD",
    "vcard": { "firstName": "张", "lastName": "三", "phone": "13800138000", "email": "zhang@example.com", "organization": "码盒科技" },
    "dotsColor": "#10b981"
  }' \
  -o vcard-qrcode.png
```

**JSON 格式返回（获取 base64）**：
```bash
curl -s -X POST https://www.codebox.club/api/v1/qrcode/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "https://example.com",
    "responseFormat": "json"
  }'
```

Response:
```json
{
  "success": true,
  "data": {
    "image": "data:image/png;base64,iVBORw0KGgo...",
    "format": "png",
    "size": 300,
    "mimeType": "image/png"
  }
}
```

**Tips**:
- 默认返回二进制图片，用 `-o file.png` 保存到文件
- 设 `responseFormat: "json"` 获取 base64 编码的图片数据
- 有 API Key 时尺寸上限提升到 2000px，频率提升到 60 次/分钟
- 使用 `templateId` 可一键应用预设风格

---

### 2. generate — 生成带追踪的动态二维码（需要 API Key）

创建带短链追踪的动态二维码，可事后更新目标 URL，可查看扫码统计。

**When to use**: 用户想创建可追踪、可动态更新的二维码，用于营销活动、线下物料等。

```bash
curl -s -X POST https://www.codebox.club/api/v1/plugin/generate \
  -H "Authorization: Bearer $CODEBOX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "https://example.com",
    "mode": "DYNAMIC",
    "name": "夏季促销活动",
    "keywords": ["科技", "现代"],
    "errorCorrectionLevel": "M"
  }'
```

**Parameters**:
| Parameter | Type | Required | Description |
|---|---|---|---|
| content | string | Yes | 要编码的 URL 或文本内容 |
| mode | string | No | `DYNAMIC`（默认，可追踪）或 `STATIC` |
| name | string | No | 二维码显示名称 |
| templateId | string | No | 风格模板 ID（通过 `list_templates` 获取） |
| keywords | string[] | No | 自动匹配模板的关键词（如 `["春节", "喜庆"]`） |
| errorCorrectionLevel | string | No | 容错级别：`L`、`M`（默认）、`Q`、`H` |

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "clxxx...",
    "shortLink": "https://www.codebox.club/s/AbCdEf",
    "templateUsed": "tech-modern-01",
    "matchedKeywords": ["科技"],
    "styles": { ... }
  }
}
```

**Tips**:
- 使用 `DYNAMIC` 模式可在不重新印刷的情况下更新目标 URL
- 使用 `keywords` 自动匹配视觉相关的风格模板
- 使用 `templateId` 精确指定模板（先用 `list_templates` 浏览）

---

### 3. get_stats — 获取二维码扫码统计（需要 API Key）

获取扫描统计数据，包括总扫描量、设备分布、浏览器/操作系统统计、地理位置数据和每日趋势。

**When to use**: 用户想查看二维码效果、分析扫码数据、对比不同活动、或获取地域洞察。

```bash
curl -s -X GET "https://www.codebox.club/api/v1/plugin/analytics?id=QR_CODE_ID&startDate=2026-01-01&endDate=2026-03-09" \
  -H "Authorization: Bearer $CODEBOX_API_KEY"
```

**Parameters**:
| Parameter | Type | Required | Description |
|---|---|---|---|
| id | string | Yes | 二维码 ID（来自 `generate` 的响应） |
| startDate | string | No | 起始日期 `YYYY-MM-DD`（默认：30 天前） |
| endDate | string | No | 结束日期 `YYYY-MM-DD`（默认：今天） |

**Response**:
```json
{
  "success": true,
  "data": {
    "totalScans": 1234,
    "uniqueUsers": 890,
    "deviceBreakdown": { "mobile": 72.5, "desktop": 22.3, "tablet": 5.2 },
    "dailyScans": [{ "date": "2026-03-01", "count": 45 }],
    "topBrowsers": [{ "browser": "Chrome", "count": 500 }],
    "topOS": [{ "os": "iOS", "count": 400 }],
    "geoData": [{ "country": "CN", "region": "Shanghai", "city": "Shanghai", "count": 200 }]
  }
}
```

---

### 4. update_link — 更新动态二维码（需要 API Key）

修改已有动态二维码的目标 URL、名称或状态，无需重新印刷。

**When to use**: 用户想将现有二维码重定向到新 URL、重命名、或禁用/过期处理。

```bash
curl -s -X PATCH https://www.codebox.club/api/v1/plugin/update \
  -H "Authorization: Bearer $CODEBOX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "QR_CODE_ID",
    "targetUrl": "https://example.com/new-page",
    "name": "秋季活动"
  }'
```

**Parameters**:
| Parameter | Type | Required | Description |
|---|---|---|---|
| id | string | Yes | 二维码 ID |
| targetUrl | string | No | 新的目标 URL |
| name | string | No | 新的显示名称 |
| status | string | No | `READY`、`EXPIRED` 或 `DELETED` |

至少需要提供 `targetUrl`、`name`、`status` 中的一个。

**Response**:
```json
{
  "success": true,
  "data": {
    "id": "clxxx...",
    "targetUrl": "https://example.com/new-page",
    "name": "秋季活动",
    "status": "READY",
    "updatedAt": "2026-03-09T10:30:00.000Z"
  }
}
```

---

### 5. list_templates — 浏览风格模板（需要 API Key）

列出所有可用的二维码风格模板，包括品牌、行业、场景、艺术、平台、节日、名片等类别。返回的模板 ID 可用于 `generate` 或 `generate_image` 的 `templateId` 参数。

**When to use**: 用户想查看可用风格、找到主题模板、或在生成前按类别浏览。

```bash
curl -s -X GET https://www.codebox.club/api/v1/plugin/catalog \
  -H "Authorization: Bearer $CODEBOX_API_KEY"
```

**Response**:
```json
{
  "success": true,
  "data": {
    "totalTemplates": 150,
    "tags": ["科技", "春节", "商务", "餐饮"],
    "categories": [
      {
        "source": "style",
        "count": 80,
        "templates": [{ "id": "tech-01", "name": "科技蓝", "category": "technology", "tags": [] }]
      },
      {
        "source": "festival",
        "count": 40,
        "templates": []
      },
      {
        "source": "business",
        "count": 30,
        "templates": []
      }
    ]
  }
}
```

---

### 6. check_quota — 查询 API 配额（需要 API Key）

查询当前计费周期的 API 调用剩余配额。

```bash
curl -s -X GET https://www.codebox.club/api/v1/quota \
  -H "Authorization: Bearer $CODEBOX_API_KEY"
```

---

## Workflow Examples

### 快速生成二维码（免费）

1. 调用 `generate_image` 生成二维码图片，自定义颜色和样式
2. 保存图片用于分享或打印

### 营销活动二维码（需要 API Key）

1. 浏览模板：调用 `list_templates` 找到合适的风格
2. 生成二维码：调用 `generate`，传入 `templateId` 和活动 URL
3. 分享 `shortLink` 或嵌入二维码图片到物料中
4. 投放后，调用 `get_stats` 监控扫码效果
5. 需要时，调用 `update_link` 重定向到新 URL

### A/B 测试

1. 生成两个二维码，分别指向不同的目标 URL（方案 A 和 B）
2. 在相似位置部署两个二维码
3. 积累足够数据后，调用 `get_stats` 对比两者效果
4. 使用 `update_link` 将效果差的二维码重定向到效果好的 URL

### 季节活动轮换

1. 生成一个 `DYNAMIC` 二维码用于固定展示位
2. 每个季度调用 `update_link` 指向新的季节页面
3. 通过 `get_stats` 的日期范围参数对比各季度效果
