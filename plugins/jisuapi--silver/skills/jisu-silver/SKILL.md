---
name: jisu-silver
description: "使用极速数据白银价格 API，查询上海黄金交易所白银、上海期货交易所白银及伦敦银等市场白银价格行情。"
---

# 极速数据白银价格（Jisu Silver）

基于 [白银价格 API](https://www.jisuapi.com/api/silver/) 的 OpenClaw 技能，支持：

- **上海黄金交易所白银价格**（`/silver/shgold`）
- **上海期货交易所白银价格**（`/silver/shfutures`）
- **伦敦银价格**（`/silver/london`）

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/silver/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/silver/silver.py`

## 使用方式

### 1. 上海黄金交易所白银价格（/silver/shgold）

```bash
python3 skills/silver/silver.py shgold
```

### 2. 上海期货交易所白银价格（/silver/shfutures）

```bash
python3 skills/silver/silver.py shfutures
```

### 3. 伦敦银价格（/silver/london）

```bash
python3 skills/silver/silver.py london
```

## 返回结果示例（节选）

### 上海黄金交易所白银价格

```json
[
  {
    "type": "Ag(T+D)",
    "typename": "白银延期",
    "price": "3399.00",
    "openingprice": "3402.00",
    "maxprice": "3407.00",
    "minprice": "3388.00",
    "changepercent": "0.09%",
    "lastclosingprice": "3396.00",
    "tradeamount": "1373982.0000",
    "updatetime": "2015-10-27 15:07:25"
  }
]
```

### 上海期货交易所白银价格

```json
[
  {
    "type": "AG1512",
    "typename": "白银1512",
    "price": "3438",
    "changequantity": "4",
    "buyprice": "3437",
    "buyamount": "41",
    "sellprice": "3438",
    "sellamount": "191",
    "tradeamount": "397592",
    "openingprice": "3438",
    "lastclosingprice": "3434",
    "maxprice": "3447",
    "minprice": "3424",
    "holdamount": "417466",
    "increaseamount": "2212"
  }
]
```

### 伦敦银价格

```json
[
  {
    "type": "白银美元",
    "price": "15.84",
    "changepercent": "-0.13%",
    "changequantity": "-0.02",
    "openingprice": "15.86",
    "maxprice": "15.87",
    "minprice": "15.77",
    "lastclosingprice": "15.86",
    "amplitude": "0.63",
    "buyprice": "15.92",
    "sellprice": "15.84",
    "updatetime": "2015-10-27 15:03:00"
  }
]
```

当无数据时，脚本会输出：

```json
{
  "error": "api_error",
  "code": 201,
  "message": "没有信息"
}
```

## 常见错误码

来源于 [极速数据白银文档](https://www.jisuapi.com/api/silver/)：

| 代号 | 说明     |
|------|----------|
| 201  | 没有信息 |

系统错误码：

| 代号 | 说明                 |
|------|----------------------|
| 101  | APPKEY 为空或不存在  |
| 102  | APPKEY 已过期        |
| 103  | APPKEY 无请求权限    |
| 104  | 请求超过次数限制     |
| 105  | IP 被禁止            |

## 在 OpenClaw 中的推荐用法

1. 用户提问：「现在白银价格大概多少？帮我看看国内和伦敦市场。」  
2. 代理依次调用：  
   - `python3 skills/silver/silver.py shgold`  
   - `python3 skills/silver/silver.py london`  
3. 从返回结果中选取代表性品种（如白银延期、白银9999、伦敦银），为用户总结当前价格、涨跌幅与近期波动区间。  

