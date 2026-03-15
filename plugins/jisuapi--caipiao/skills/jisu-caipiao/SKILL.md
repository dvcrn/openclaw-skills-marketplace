---
name: jisu-caipiao
description: "使用极速数据彩票开奖 API 查询彩票分类、最新开奖结果、历史开奖信息以及给定号码是否中奖。"
---

# 极速数据彩票开奖（Jisu Caipiao）

基于 [彩票开奖 API](https://www.jisuapi.com/api/caipiao/) 的 OpenClaw 技能，支持：

- **彩票开奖**（`/caipiao/query`）
- **历史开奖信息**（`/caipiao/history`）
- **彩票分类**（`/caipiao/class`）
- **查询是否中奖**（`/caipiao/winning`）

可用于对话中回答「今晚双色球开奖号码是多少」「最近 10 期大乐透号码」「有哪些彩种」「我这注彩票中没中奖」等问题。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/caipiao/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/caipiao/caipiao.py`

## 使用方式

### 1. 彩票分类（class）

```bash
python3 skills/caipiao/caipiao.py class
```

返回各彩种的 `caipiaoid`、名称、上级 ID 以及下期开奖时间等。

### 2. 最新或指定期彩票开奖（query）

```bash
# 最新一期
python3 skills/caipiao/caipiao.py query '{"caipiaoid":13}'

# 指定期号
python3 skills/caipiao/caipiao.py query '{"caipiaoid":13,"issueno":"2014127"}'
```

### 3. 历史开奖信息（history）

```bash
python3 skills/caipiao/caipiao.py history '{"caipiaoid":13,"start":0,"num":10}'
```

### 4. 查询是否中奖（winning）

```bash
python3 skills/caipiao/caipiao.py winning '{"caipiaoid":11,"number":"02 06 15 25 30 32","refernumber":"08"}'
```

## 请求参数摘要

### /caipiao/query

| 字段名    | 类型   | 必填 | 说明                             |
|-----------|--------|------|----------------------------------|
| caipiaoid | int    | 是   | 彩票 ID                          |
| issueno   | string | 否   | 期号，不传则为当前期             |

### /caipiao/history

| 字段名    | 类型   | 必填 | 说明                                  |
|-----------|--------|------|---------------------------------------|
| caipiaoid | int    | 是   | 彩票 ID                               |
| issueno   | string | 否   | 期号，不传默认当前期历史向前          |
| num       | int    | 否   | 获取数量，最大 20，默认 10            |
| start     | int    | 否   | 起始位置，默认 0                      |

### /caipiao/class

无请求参数。

### /caipiao/winning

| 字段名      | 类型   | 必填 | 说明                                  |
|-------------|--------|------|---------------------------------------|
| caipiaoid   | string | 是   | 彩票 ID                              |
| issueno     | string | 否   | 期号，默认最新一期                    |
| number      | string | 是   | 彩票号码（红球，如 `20 03 05 07 22`） |
| refernumber | string | 否   | 剩余号码（蓝球等）                    |
| type        | string | 否   | 投注类型（1 直选，2 组三，3 组六）     |

## 返回结果说明（节选）

### /caipiao/query

```json
{
  "caipiaoid": "13",
  "issueno": "2014127",
  "number": "05 07 10 18 19 21 27",
  "refernumber": "28",
  "opendate": "2014-10-29",
  "deadline": "2014-12-27",
  "saleamount": "7482530",
  "prize": [
    {
      "prizename": "二等奖",
      "require": "中6+0",
      "num": "50",
      "singlebonus": "608921"
    }
  ],
  "totalmoney": "..."
}
```

### /caipiao/history

返回对象包含 `caipiaoid` 和 `list`，`list` 中每期包含开奖日期、期号、号码、销售额及奖级列表。

### /caipiao/class

返回彩种数组，每项如：

```json
{
  "caipiaoid": 11,
  "name": "双色球",
  "parentid": 1,
  "nextopentime": "2025-03-09 21:30:00",
  "nextbuyendtime": "2025-03-09 20:00:00",
  "lastissueno": "2025024",
  "nextissueno": "2025025"
}
```

### /caipiao/winning

```json
{
  "caipiaoid": "11",
  "number": "02 06 15 25 30 32",
  "refernumber": "08",
  "issueno": "2016081",
  "winstatus": "0",
  "prizename": "二等奖",
  "require": "中6+0",
  "singlebonus": "239666",
  "winnumber": "02 06 15 25 30 32",
  "winrefernumber": "07"
}
```

## 错误返回示例

```json
{
  "error": "api_error",
  "code": 201,
  "message": "彩票ID为空"
}
```

## 常见错误码

来源于 [极速数据彩票开奖文档](https://www.jisuapi.com/api/caipiao/)：

| 代号 | 说明         |
|------|--------------|
| 201  | 彩票 ID 为空 |
| 202  | 彩票号码为空 |
| 203  | 不支持的彩种 |
| 210  | 没有信息     |

系统错误码：101 APPKEY 为空或不存在、102 已过期、103 无权限、104 超过次数限制、105 IP 被禁止、106 IP 超限、107 接口维护中、108 接口已停用。

## 在 OpenClaw 中的推荐用法

1. 用户：「今晚双色球开奖号码」→ 先用 `class` 找到双色球的 `caipiaoid`（通常为 11），再调用 `query` 并格式化展示中奖号码及奖池。  \n
2. 用户：「最近 10 期大乐透走势」→ 使用 `history` 拉取最近若干期数据，提取号码并可视化（折线/表格）。  \n
3. 用户：「帮我看看这注是否中奖」→ 使用 `winning`，将用户提供的号码和期号（可选）传入，并根据 `winstatus`、`prizename`、`singlebonus` 给出自然语言反馈。  \n
4. 用户：「支持哪些彩种」→ 调用 `class`，罗列所有 `name` 与对应 `caipiaoid`，方便后续对话使用 ID 进行精确查询。

