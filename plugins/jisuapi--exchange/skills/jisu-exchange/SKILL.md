---
name: jisu-exchange
description: "使用极速数据汇率查询 API，支持货币间汇率换算、单个货币的热门汇率、所有货币列表及十大银行外汇牌价查询。"
---

# 极速数据汇率查询（Jisu Exchange）

基于 [汇率查询 API](https://www.jisuapi.com/api/exchange/) 的 OpenClaw 技能，支持：

- **汇率换算**：任意两种货币之间的金额换算；
- **单个货币**：某一货币相对热门货币的实时汇率列表；
- **所有货币**：查询所有支持的货币代码及名称；
- **十大银行外汇牌价**：查询银行中间价、买入价、卖出价等。

> 汇率为综合汇率，仅供参考，来源详见极速数据文档 [`https://www.jisuapi.com/api/exchange/`](https://www.jisuapi.com/api/exchange/)。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/exchange/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/exchange/exchange.py`

## 使用方式

### 1. 汇率换算（/exchange/convert）

```bash
python3 skills/exchange/exchange.py '{"from":"CNY","to":"USD","amount":10}'
```

请求 JSON：

```json
{
  "from": "CNY",
  "to": "USD",
  "amount": 10
}
```

### 2. 单个货币热门汇率（/exchange/single）

```bash
python3 skills/exchange/exchange.py single CNY
```

### 3. 所有货币列表（/exchange/currency）

```bash
python3 skills/exchange/exchange.py currency
```

### 4. 十大银行外汇牌价（/exchange/bank）

```bash
# 默认中国银行 BOC
python3 skills/exchange/exchange.py bank

# 指定银行（示例：工商银行 ICBC）
python3 skills/exchange/exchange.py bank ICBC
```

支持的银行编码示例：

- `ICBC`：工商银行
- `BOC`：中国银行
- `ABCHINA`：农业银行
- `BANKCOMM`：交通银行
- `CCB`：建设银行
- `CMBCHINA`：招商银行
- `CEBBANK`：光大银行
- `SPDB`：浦发银行
- `CIB`：兴业银行
- `ECITIC`：中信银行

## 请求参数

### 汇率换算

| 字段名 | 类型   | 必填 | 说明                            |
|--------|--------|------|---------------------------------|
| from   | string | 是   | 原货币代码（如 CNY、USD）      |
| to     | string | 是   | 目标货币代码                    |
| amount | number | 否   | 数量（默认 1）                  |

### 单个货币

| 字段名   | 类型   | 必填 | 说明     |
|----------|--------|------|----------|
| currency | string | 是   | 货币代码 |

### 所有货币

无需额外参数，仅需 `appkey`。

### 银行外汇牌价

| 字段名 | 类型   | 必填 | 说明                               |
|--------|--------|------|------------------------------------|
| bank   | string | 否   | 银行编码，不传则默认为 BOC（中国银行） |

## 返回结果示例

### 汇率换算（简化）

```json
{
  "from": "CNY",
  "to": "USD",
  "fromname": "人民币",
  "toname": "美元",
  "updatetime": "2015-10-26 16:56:22",
  "rate": "0.1574",
  "camount": "1.574"
}
```

### 单个货币热门汇率（简化）

```json
{
  "currency": "CNY",
  "name": "人民币",
  "list": {
    "USD": {
      "name": "美元",
      "rate": "0.1574",
      "updatetime": "2015-10-26 16:56:22"
    },
    "EUR": {
      "name": "欧元",
      "rate": "0.1426",
      "updatetime": "2015-10-26 16:56:22"
    }
  }
}
```

### 所有货币列表（简化）

```json
[
  { "currency": "USD", "name": "美元" },
  { "currency": "EUR", "name": "欧元" },
  { "currency": "CNY", "name": "人民币" }
]
```

### 银行外汇牌价（简化）

```json
{
  "bank": "BOC",
  "list": [
    {
      "code": "USD",
      "name": "美元",
      "midprice": "717.4100",
      "cashbuyprice": "722.0800",
      "forexbuyprice": "722.0800",
      "cashsellprice": "725.1100",
      "forexsellprice": "725.1100",
      "updatetime": "2025-03-11 18:05:59"
    }
  ]
}
```

当出现参数错误（如货币代码有误、数量为空等）时，脚本会输出：

```json
{
  "error": "api_error",
  "code": 204,
  "message": "要兑换的货币有误"
}
```

## 常见错误码

来源于 [极速数据汇率文档](https://www.jisuapi.com/api/exchange/)：

| 代号 | 说明             |
|------|------------------|
| 201  | 要兑换的货币为空 |
| 202  | 兑换后的货币为空 |
| 203  | 兑换数量为空     |
| 204  | 要兑换的货币有误 |
| 205  | 兑换后的货币有误 |
| 206  | 货币为空         |
| 207  | 货币有误         |
| 208  | 没有信息         |

系统错误码：

| 代号 | 说明                 |
|------|----------------------|
| 101  | APPKEY 为空或不存在  |
| 102  | APPKEY 已过期        |
| 103  | APPKEY 无请求权限    |
| 104  | 请求超过次数限制     |
| 105  | IP 被禁止            |

## 在 OpenClaw 中的推荐用法

1. 用户输入自然语言：「帮我把 1000 人民币换算成美元，大概是多少？」  
2. 代理构造 JSON：`{"from":"CNY","to":"USD","amount":1000}` 并调用：  
   `python3 skills/exchange/exchange.py '{"from":"CNY","to":"USD","amount":1000}'`  
3. 从返回结果中读取 `rate` 和 `camount`，向用户说明当前汇率与折算后的金额；  
4. 若用户询问某货币常见汇率，可使用 `single` 或 `currency` / `bank` 子命令补充汇率表或银行牌价信息。

