---
name: bijie-express
description: "Free package tracking for 2000+ couriers (SF, YTO, ZTO, Yunda, STO, JT, JD, EMS). Returns logistics status, location, transit nodes & ETA. 必捷免费快递查询，支持国内外2000+快递公司，自动识别单号，返回包裹状态、物流轨迹、预计到达时间。Use when user asks 查快递, 快递查询, 物流轨迹, 查物流, 快递到哪了, 跟踪包裹, track package, courier tracking, 圆通查询, 顺丰查询, 中通查询, 韵达查询, 申通查询, 极兔查询, 京东物流查询, EMS查询."
---

# 必捷免费快递查询

基于必捷物流平台的免费快递查询服务，支持2000+国内外快递公司。

## 快速开始

### 方式1：Python调用（推荐）

```python
from scripts.express import quick_query

# 查询快递
result = quick_query(
    company="圆通",  # 快递公司名称或编码
    num="YT25569986666541"  # 快递单号
)
print(result)
```

### 方式2：命令行

```bash
python3 scripts/express.py 圆通 YT25569986666541
```

## 支持的快递公司

| 名称 | 编码 | 名称 | 编码 |
|------|------|------|------|
| 圆通速递 | yuantong | 中通快递 | zhongtong |
| 顺丰速运 | shunfeng | 韵达快递 | yunda |
| 申通快递 | shentong | 京东物流 | jd |
| 极兔速递 | jtexpress | EMS | ems |
| 德邦快递 | debangkuaidi | 菜鸟速递 | danniao |
| DHL | dhl | FedEx | fedex |

完整编码表见 [references/company-codes.md](references/company-codes.md)

## 物流状态说明

| 状态码 | 状态 | 说明 |
|:---:|:---|:---|
| 0 | 在途 | 快件在运输途中 |
| 1 | 已揽收 | 快递公司已揽收 |
| 2 | 疑难 | 快件存在异常情况 |
| 3 | 已签收 | 快件已签收 |
| 4 | 退签 | 快件已退签 |
| 5 | 派送中 | 快件正在派件中 |
| 6 | 退回 | 快件正在返回发货人途中 |

## ⚠️ 使用限制

- **单号限流**：同一单号查询间隔必须保持在 **30分钟** 以上
- **用户限流**：每个用户每 **10分钟** 仅允许查询一次
- **严禁**用于系统后台高频自动轮询

## 隐私保护

查询结果自动脱敏：手机号 13586691386 → 135****1386

## API信息

- **端点**: `POST http://skill.bijieserv.com/api/method/express_app.open.v1.query.exec`
- **官网**: http://www.bijieserv.com
