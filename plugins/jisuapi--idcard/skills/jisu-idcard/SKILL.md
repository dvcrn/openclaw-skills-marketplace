---
name: jisu-idcard
description: "使用极速数据身份证号码归属地查询 API，根据身份证号查询发证地区、出生年月、性别及校验位是否正确，并支持根据城市查询身份证前 6 位。"
---

# 极速数据身份证号码归属地查询（Jisu Idcard）

基于 [身份证号码归属地查询 API](https://www.jisuapi.com/api/idcard/) 的 OpenClaw 技能，支持：

- **身份证查询**（`/idcard/query`）
- **城市查身份证前 6 位**（`/idcard/city2code`）

可用于对话中回答「这个身份证是哪里的」「校验位对不对」「鹿邑县对应的身份证前 6 位是多少」等问题。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/idcard/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/idcard/idcard.py`

## 使用方式

### 1. 身份证查询（query）

```bash
python3 skills/idcard/idcard.py query '{"idcard":"41272519800102067x"}'
```

### 2. 城市查身份证前 6 位（city2code）

```bash
python3 skills/idcard/idcard.py city2code '{"city":"鹿邑"}'
```

## 请求参数

### /idcard/query

| 字段名  | 类型   | 必填 | 说明             |
|---------|--------|------|------------------|
| idcard  | string | 是   | 身份证号或前 6 位 |

### /idcard/city2code

| 字段名 | 类型   | 必填 | 说明 |
|--------|--------|------|------|
| city   | string | 是   | 城市 |

## 返回结果示例

### /idcard/query

```json
{
  "province": "河南省",
  "city": "周口市",
  "town": "鹿邑县",
  "lastflag": "0",
  "sex": "男",
  "birth": "1980年01月02日",
  "area": "河南省周口市鹿邑县"
}
```

字段说明：

| 字段名   | 类型   | 说明                                             |
|----------|--------|--------------------------------------------------|
| province | string | 省                                               |
| city     | string | 市                                               |
| town     | string | 县                                               |
| lastflag | string | 最后一位校验码：`0` 正确，`1` 错误                |
| sex      | string | 性别                                             |
| birth    | string | 出生年月                                         |
| area     | string | 区域信息（由于行政区划调整，具体以该字段为准）   |

### /idcard/city2code

```json
{
  "province": "河南省",
  "city": "周口市",
  "town": "鹿邑县",
  "code": "412725"
}
```

字段说明：

| 字段名   | 类型   | 说明       |
|----------|--------|------------|
| code     | string | 身份证前 6 位 |
| province | string | 省         |
| city     | string | 市         |
| town     | string | 县         |

## 错误返回示例

```json
{
  "error": "api_error",
  "code": 201,
  "message": "身份证为空"
}
```

## 常见错误码

来源于 [极速数据身份证号码归属地文档](https://www.jisuapi.com/api/idcard/)：

| 代号 | 说明       |
|------|------------|
| 201  | 身份证为空 |
| 202  | 身份证不正确 |
| 203  | 没有信息   |

系统错误码：101 APPKEY 为空或不存在、102 已过期、103 无请求此数据权限、104 请求超过次数限制、105 IP 被禁止、106 IP 请求超过限制、107 接口维护中、108 接口已停用。

## 在 OpenClaw 中的推荐用法

1. 用户：「帮我查一下 41272519800102067x 是哪里的」→ 调用 `query`，读取 `province`、`city`、`town` 和 `lastflag`，说明地区和校验是否通过。  \n
2. 用户：「鹿邑县的身份证前 6 位是多少？」→ 使用 `city2code '{"city":"鹿邑"}'`，返回 `code`。  \n
3. 用户：「校验一下这个身份证号是否正确」→ 使用 `query`，根据 `lastflag` 和是否返回 `result` 告知是否为合法号码。  \n
4. 用户：「只知道前 6 位，想确认大概地区」→ 仍使用 `query`，传入前 6 位，结合返回的 `province/city/town/area` 做说明。  \n

