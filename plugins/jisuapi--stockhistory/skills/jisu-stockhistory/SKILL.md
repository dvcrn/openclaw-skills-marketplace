---
name: jisu-stockhistory
description: "使用极速数据股票历史行情查询 API，按股票代码与时间范围获取历史日线数据，或查列表与单只详情，可用于 K 线及走势分析。"
---

# 极速数据股票历史行情查询（Jisu Stock History）

基于 [股票历史行情查询 API](https://www.jisuapi.com/api/stockhistory/) 的 OpenClaw 技能，支持：

- **股票历史查询**（`/stockhistory/query`）：根据股票代码、开始时间、结束时间获取历史数据，数据粒度为天，返回日期、开盘价、收盘价、最高价、最低价、成交量、成交额、换手率、涨跌幅等，可用于绘制 K 线及走势分析
- **股票列表**（`/stockhistory/list`）：按分类（沪深股市）分页获取股票列表
- **股票详情**（`/stockhistory/detail`）：根据股票代码获取单只股票详情（最新价、涨跌幅、成交量、市盈率等）

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/stockhistory/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skill/stockhistory/stockhistory.py`

## 使用方式

### 1. 股票历史查询（/stockhistory/query）

根据股票代码与可选的时间范围获取历史日线数据。

```bash
# 指定时间范围
python3 skill/stockhistory/stockhistory.py query '{"code":"300917","startdate":"2020-12-24","enddate":"2020-12-25"}'

# 仅股票代码（startdate/enddate 可选，不传由接口默认）
python3 skill/stockhistory/stockhistory.py query '{"code":"300917"}'
```

请求 JSON：

```json
{
  "code": "300917",
  "startdate": "2020-12-24",
  "enddate": "2020-12-25"
}
```

| 字段名     | 类型   | 必填 | 说明     |
|------------|--------|------|----------|
| code       | string | 是   | 股票代码 |
| startdate  | string | 否   | 开始日期 |
| enddate    | string | 否   | 结束日期 |

### 2. 股票列表（/stockhistory/list）

按分类分页获取股票列表，当前文档中 classid 为 1（沪深股市）。

```bash
python3 skill/stockhistory/stockhistory.py list '{"classid":1,"pagenum":1,"pagesize":10}'
```

请求 JSON：

```json
{
  "classid": 1,
  "pagenum": 1,
  "pagesize": 10
}
```

| 字段名   | 类型   | 必填 | 说明               |
|----------|--------|------|--------------------|
| classid  | int    | 是   | 1 沪深股市         |
| pagenum  | int    | 否   | 当前页，默认 1     |
| pagesize | int    | 否   | 每页数量，默认 30  |

### 3. 股票详情（/stockhistory/detail）

根据股票代码获取单只股票详情。

```bash
python3 skill/stockhistory/stockhistory.py detail '{"code":"300917"}'
```

请求 JSON：

```json
{
  "code": "300917"
}
```

| 字段名 | 类型   | 必填 | 说明     |
|--------|--------|------|----------|
| code   | string | 是   | 股票代码 |

## 返回结果示例（节选）

### 股票历史查询（query）

```json
{
  "code": "300917",
  "name": "C特发",
  "startdate": "2020-12-24",
  "enddate": "2020-12-25",
  "list": [
    {
      "stockid": 6769,
      "date": "2020-12-24",
      "openningprice": "40.10",
      "closingprice": "53.92",
      "maxprice": "54.20",
      "minprice": "40.10",
      "tradenum": 166623,
      "tradeamount": "756991472.00",
      "turnoverrate": "78.110",
      "changepercent": "32.48",
      "changeamount": "13.22",
      "amplitude": "34.64",
      "per": null,
      "pbr": null,
      "totalmarket": null,
      "circulationmarket": null
    }
  ]
}
```

### 股票列表（list）

```json
{
  "pagesize": 10,
  "pagenum": 1,
  "total": 4486,
  "classid": 1,
  "list": [
    { "name": "信达增利", "code": "166105" },
    { "name": "R003", "code": "201000" }
  ]
}
```

### 股票详情（detail）

与实时股票接口类似，包含 name、code、price、maxprice、minprice、tradenum、tradeamount、turnoverrate、openningprice、lastclosingprice、changepercent、changeamount、amplitude、quantityratio、per、pbr、totalmarket、circulationmarket、updatetime 等字段。

当接口返回业务错误时，脚本会输出：

```json
{
  "error": "api_error",
  "code": 201,
  "message": "股票代码为空"
}
```

## 常见错误码

来源于 [极速数据股票历史行情文档](https://www.jisuapi.com/api/stockhistory/)：

| 代号 | 说明           |
|------|----------------|
| 201  | 股票代码为空   |
| 202  | 股票代码不存在 |
| 210  | 没有信息       |

系统错误码：101～108（与其它极速数据接口一致）。

## 在 OpenClaw 中的推荐用法

1. 用户提问：「300917 最近一周的历史走势 / K 线数据有吗？」  
2. 代理根据当前日期计算 startdate/enddate，调用：  
   `python3 skill/stockhistory/stockhistory.py query '{"code":"300917","startdate":"2025-02-24","enddate":"2025-03-02"}'`  
3. 从返回的 `list` 中提取 date、openningprice、closingprice、maxprice、minprice、tradenum、changepercent 等，用文字或建议用户用图表绘制 K 线、涨跌幅走势。  
4. 需要先选股票时，可调用 `list` 获取沪深列表，或结合 `skill/stock` 的实时接口做「历史 + 实时」组合查询。
