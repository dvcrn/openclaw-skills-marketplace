---
name: jisu-barcode2
description: "使用极速数据商品条码查询 API，通过商品条形码查询商品名称、品牌、规格、产地、包装信息等基础资料。"
---

# 极速数据商品条码查询（Barcode2）

基于 [商品条码查询 API](https://www.jisuapi.com/api/barcode2/) 的 OpenClaw 技能，
通过商品条形码（EAN8/EAN13，69 开头）查询商品基础信息。

使用技能前需要申请数据，申请地址：https://www.jisuapi.com/api/barcode2/

## 环境变量配置

```bash
# Linux / macOS
export JISU_API_KEY="your_appkey_here"

# Windows PowerShell
$env:JISU_API_KEY="your_appkey_here"
```

## 脚本路径

脚本文件：`skills/barcode/barcode.py`

## 使用方式

### 按条形码查询商品信息

```bash
python3 skills/barcode/barcode.py '{"barcode":"06917878036526"}'
```

请求参数以 JSON 形式传入，仅需一个字段：

```json
{
  "barcode": "06917878036526"
}
```

## 请求参数

| 字段名   | 类型   | 必填 | 说明    |
|---------|--------|------|---------|
| barcode | string | 是   | 商品条码 |

## 返回结果示例

脚本直接输出接口 `result` 字段，典型结构与官网示例一致（简化版）：

```json
{
  "barcode": "06917878036526",
  "name": "雀巢咖啡臻享白咖啡",
  "ename": "NESCAFE White Coffee",
  "unspsc": "50201708 (食品、饮料和烟草>>饮料>>咖啡和茶>>咖啡饮料)",
  "brand": "NESCAFE",
  "type": "29g",
  "width": "70毫米",
  "height": "160毫米",
  "depth": "55毫米",
  "origincountry": "中国",
  "originplace": "",
  "assemblycountry": "中国",
  "barcodetype": "",
  "catena": ",",
  "isbasicunit": "0",
  "packagetype": "",
  "grossweight": "",
  "netcontent": "5条",
  "netweight": "145克",
  "description": "",
  "keyword": "雀巢咖啡臻享白咖啡",
  "pic": "",
  "price": "",
  "licensenum": "QS3117 0601 0440",
  "healthpermitnum": ""
}
```

当出现错误（如条码不正确或无数据）时，脚本会输出：

```json
{
  "error": "api_error",
  "code": 202,
  "message": "条码不正确"
}
```

## 常见错误码

基于 [极速数据条码文档](https://www.jisuapi.com/api/barcode2/)：

| 代号 | 说明                               |
|------|------------------------------------|
| 201  | 条码为空                           |
| 202  | 条码不正确                         |
| 203  | 该条码已下市（扣次数）             |
| 204  | 该条码已注册，但编码信息未通报（扣次） |
| 205  | 该条码异常（扣次数）               |
| 210  | 没有信息                           |

系统错误码：

| 代号 | 说明                 |
|------|----------------------|
| 101  | APPKEY 为空或不存在  |
| 102  | APPKEY 已过期        |
| 103  | APPKEY 无请求权限    |
| 104  | 请求超过次数限制     |
| 105  | IP 被禁止            |

## 在 OpenClaw 中的推荐用法

1. 用户拍照/输入条码号：「帮我查一下条码 `06917878036526` 是什么商品」。  
2. 代理构造 JSON：`{"barcode":"06917878036526"}` 并调用：  
   `python3 skills/barcode/barcode.py '{"barcode":"06917878036526"}'`  
3. 从结果中读取 `name/brand/type/netcontent/netweight/origincountry` 等字段，为用户总结商品名称、品牌、规格和产地信息。  

