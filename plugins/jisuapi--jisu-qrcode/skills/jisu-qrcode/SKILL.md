---
name: jisu-qrcode
description: "使用极速数据二维码生成识别 API，按文本内容生成带模板的二维码图片（base64），或识别二维码中的文本内容，并获取模板样例列表。"
---

## 极速数据二维码生成识别（Jisu QRCode）

基于 [二维码生成识别 API](https://www.jisuapi.com/api/qrcode/) 的 OpenClaw 技能，支持：

- 根据文本/URL 生成二维码图片（base64），可选颜色、纠错等级、模板、LOGO 等参数；
- 识别二维码内容（支持二维码图片 URL 或 base64）；
- 获取官方提供的二维码模板样例列表。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/qrcode/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skill/qrcode/qrcode.py`

## 使用方式

当前脚本提供 3 个子命令：

- `generate`：二维码生成（/qrcode/generate）
- `read`：二维码识别（/qrcode/read）
- `template`：获取二维码模板样例（/qrcode/template）

### 1. 二维码生成（/qrcode/generate）

```bash
python3 skill/qrcode/qrcode.py generate '{
  "text": "https://www.jisuapi.com/api/sms",
  "width": 300,
  "tempid": 1,
  "margin": 10,
  "bgcolor": "FFFFFF",
  "fgcolor": "000000",
  "oxlevel": "L",
  "logo": "https://www.jisuapi.com/static/images/icon/qrcode.png"
}'
```

请求字段：

| 字段名  | 类型   | 必填 | 说明 |
|---------|--------|------|------|
| text    | string | 是   | 二维码内容（文本或 URL） |
| bgcolor | string | 否   | 背景色，默认 `FFFFFF`（白色） |
| fgcolor | string | 否   | 前景色，默认 `000000`（黑色） |
| oxlevel | string | 否   | 纠错等级 `L/M/Q/H`，默认 `L` |
| width   | int    | 否   | 宽度（像素），默认 `300` |
| margin  | int    | 否   | 边距（包含在宽度内），默认 `0` |
| logo    | string | 否   | LOGO 地址（HTTP 链接） |
| tempid  | int    | 否   | 模板 ID（参考模板接口返回） |

返回字段（`result`）：

| 字段名 | 类型     | 说明 |
|--------|----------|------|
| qrcode | string   | 二维码图片 base64 内容（可直接用作 `img` 的 data URI） |

### 2. 二维码识别（/qrcode/read）

```bash
python3 skill/qrcode/qrcode.py read '{
  "qrcode": "https://api.jisuapi.com/qrcode/static/images/sample/1.png"
}'
```

请求字段：

| 字段名 | 类型   | 必填 | 说明 |
|--------|--------|------|------|
| qrcode | string | 是   | 支持 base64 或可访问的二维码图片 URL |

返回字段：

| 字段名 | 类型   | 说明       |
|--------|--------|------------|
| text   | string | 解码后的内容 |

### 3. 获取二维码模板样例（/qrcode/template）

```bash
python3 skill/qrcode/qrcode.py template '{}'
```

返回字段：

`result` 为字符串数组，每个元素为一个模板样例图片 URL。

## 常见错误码

业务错误码（来源于官网文档）：

| 代号 | 说明         |
|------|--------------|
| 201  | 二维码内容为空 |
| 202  | 背景颜色不正确 |
| 203  | 前景颜色不正确 |
| 204  | 纠错等级不正确 |
| 205  | logo 地址不正确 |
| 206  | 模板 ID 不正确 |
| 209  | 二维码地址不正确 |

系统错误码：

| 代号 | 说明             |
|------|------------------|
| 101  | APPKEY 为空或不存在 |
| 102  | APPKEY 已过期    |
| 103  | APPKEY 无请求此数据权限 |
| 104  | 请求超过次数限制   |
| 105  | IP 被禁止       |
| 106  | IP 请求超过限制   |
| 107  | 接口维护中       |
| 108  | 接口已停用       |

## 在 OpenClaw 中的推荐用法

1. 用户提问：「帮我给这个活动页生成一个二维码图片」「帮我识别这个二维码里是什么链接」。  
2. 对于生成需求：构造包含活动页 URL 的 `text` 字段，调用 `generate` 获取 `qrcode` base64，并在回答中提示用户可直接嵌入到前端页面或转存为图片；  
3. 对于识别需求：将二维码图片 URL 或 base64 作为 `qrcode` 参数调用 `read`，从返回的 `text` 字段中读取内容，并结合其它技能（如 `jisu` 统一入口或 `qrcode2` 本地生成/识别）进行后续处理或安全检查。  

