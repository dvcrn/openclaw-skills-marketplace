---
name: jisu-stockindex
description: "使用极速数据上证股票指数 API，获取上证指数、深证成指、创业板指、中小板指、沪深300、上证50、科创50、B股指数等品种的实时行情，数据粒度为分钟。"
---

# 极速数据上证股票指数（Jisu Stock Index）

基于 [上证股票指数 API](https://www.jisuapi.com/api/stockindex/) 的 OpenClaw 技能，支持：

- **股票指数**（`/stockindex/sh`）：一次性获取上证指数、深证成指、创业板指、中小板指、沪深300、上证50、科创50、B股指数等品种的最新价、昨收盘价、数据量、更新时间及分钟级趋势（`trend` / `trend_standard`），数据粒度为分钟。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/stockindex/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skill/stockindex/stockindex.py`

## 使用方式

### 股票指数（/stockindex/sh）

无需请求参数，直接调用即可获取各指数品种的实时行情及分钟趋势。

```bash
python3 skill/stockindex/stockindex.py sh
```

## 返回结果示例（节选）

```json
[
  {
    "name": "上证指数",
    "code": "000001",
    "price": "3416.08",
    "lastclosingprice": 3410.18,
    "trendnum": "241",
    "updatetime": 1607509662,
    "openningprice": "3410.18",
    "trend": [
      "2020-12-09 09:30,3416.08,2081381,2544235056.00,3411.749",
      "2020-12-09 09:31,3417.53,4931922,5994410752.00,3411.554"
    ],
    "trend_standard": []
  }
]
```

| 字段名            | 类型   | 说明                                                                 |
|-------------------|--------|----------------------------------------------------------------------|
| name              | string | 品种名称（如上证指数、深证成指）                                       |
| code              | string | 品种代码                                                             |
| price             | string | 最新价                                                               |
| lastclosingprice  | string | 昨收盘价                                                             |
| trendnum          | string | 数据量                                                               |
| updatetime        | string | 更新时间                                                             |
| openningprice     | string | 开盘价                                                               |
| trend             | array  | 趋势：时间、价格、成交量、成交总额、平均价                             |
| trend_standard    | array  | 标准趋势：时间、开盘价、收盘价、最高价、最低价、成交量、成交总额、平均价 |

当接口返回业务错误时，脚本会输出：

```json
{
  "error": "api_error",
  "code": 210,
  "message": "没有信息"
}
```

## 常见错误码

来源于 [极速数据股票指数文档](https://www.jisuapi.com/api/stockindex/)：

| 代号 | 说明     |
|------|----------|
| 210  | 没有信息 |

系统错误码：101～108（与其它极速数据接口一致）。

## 在 OpenClaw 中的推荐用法

1. 用户提问：「今天大盘指数怎么样？上证、深证、创业板都多少？」  
2. 代理调用：`python3 skill/stockindex/stockindex.py sh`  
3. 从返回数组中按 `name` 筛选「上证指数」「深证成指」「创业板指」等，提取 `price`、`lastclosingprice`、`openningprice`，用自然语言汇总涨跌与点位；若用户需要分钟走势，可说明 `trend` / `trend_standard` 可用于绘图。
