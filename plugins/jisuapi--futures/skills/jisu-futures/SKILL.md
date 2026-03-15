---
name: jisu-futures
description: "使用极速数据期货查询 API 获取上海、大连、郑州、中国金融、广州等交易所的期货价格行情。"
---

## 极速数据期货查询（Jisu Futures）

基于 [期货查询 API](https://www.jisuapi.com/api/futures/) 的 OpenClaw 技能，提供上海期货交易所、大连商品交易所、郑州商品交易所、中国金融期货交易所、广州期货交易所等多家交易所的期货价格查询。

每个接口返回品种代号、品种名称、最新价、涨跌幅、最高/最低价、开盘价、昨收盘价、总成交量、持仓量、买卖价量、更新时间等字段，可用于期货行情展示与简单分析。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/futures/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skill/futures/futures.py`

## 使用方式

当前脚本通过不同子命令调用不同交易所接口：

### 1. 上海期货交易所（/futures/shfutures）

```bash
python3 skill/futures/futures.py shfutures
```

### 2. 大连商品交易所（/futures/dlfutures）

```bash
python3 skill/futures/futures.py dlfutures
```

### 3. 郑州商品交易所（/futures/zzfutures）

```bash
python3 skill/futures/futures.py zzfutures
```

### 4. 中国金融期货交易所（/futures/zgjrfutures）

```bash
python3 skill/futures/futures.py zgjrfutures
```

### 5. 广州期货交易所（/futures/gzfutures）

```bash
python3 skill/futures/futures.py gzfutures
```

上述接口均无需额外 JSON 参数，脚本会直接输出接口 `result` 对象，其内部按品种名称分组，例如 `{"燃油": [...合约列表...], "铜": [...合约列表...]}`。

## 返回结果示例（节选）

```json
{
  "燃油": [
    {
      "type": "FU2309",
      "typename": "燃料油2309",
      "price": "2948.00",
      "changepercent": "+6.27%",
      "changequantity": "+174",
      "maxprice": "2975.00",
      "minprice": "2777.00",
      "openingprice": "2782.00",
      "lastclosingprice": "2774.000",
      "tradeamount": "704525",
      "holdamount": "295063",
      "buyamount": "47",
      "buyprice": "2947.000",
      "sellamount": "66",
      "sellprice": "2948.000",
      "updatetime": "2023-04-03 15:46:43"
    }
  ]
}
```

## 常见错误码

业务错误码（参考官网错误码参照）：  

| 代号 | 说明     |
|------|----------|
| 201  | 没有信息 |

系统错误码：

| 代号 | 说明                     |
|------|--------------------------|
| 101  | APPKEY 为空或不存在     |
| 102  | APPKEY 已过期           |
| 103  | APPKEY 无请求此数据权限 |
| 104  | 请求超过次数限制         |
| 105  | IP 被禁止               |
| 106  | IP 请求超过限制         |
| 107  | 接口维护中               |
| 108  | 接口已停用               |

## 在 OpenClaw 中的推荐用法

1. 用户提问：「帮我看看今天 PTA、燃油、工业硅这几个期货的价格和涨跌情况。」  
2. 代理按交易所调用对应命令，例如：`python3 skill/futures/futures.py shfutures`、`python3 skill/futures/futures.py dlfutures`、`python3 skill/futures/futures.py gzfutures`。  
3. 从返回的 `result` 中按品种名称（如 `PTA`、`燃油`、`工业硅`）筛选相关合约，读取 `price`、`changepercent`、`maxprice`、`minprice`、`tradeamount` 等字段，为用户总结当前价格区间与涨跌幅，并必要时提醒仅作行情参考。  

