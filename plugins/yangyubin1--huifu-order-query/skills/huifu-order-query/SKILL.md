---
name: huifu-order-query
description: "[后端项目使用]汇付托管交易订单查询接口技能。用于查询订单支付状态和详细信息。当用户提到订单查询、支付查询、/hfpay/queryorderinfo时触发。"
---

# 汇付订单查询接口

## 引导词

当开发者提到以下关键词时，本技能将被触发：

- 订单查询、支付查询、查询订单
- /hfpay/queryorderinfo
- 汇付订单状态、支付状态查询
- 托管支付查询

## 前置检查（重要）

在开始编写代码之前，必须先检查项目是否已安装汇付SDK依赖。

### 步骤1：检查依赖

检查项目的 pom.xml 文件中是否包含 `dg-java-sdk` 依赖：

```xml
<dependency>
    <groupId>com.huifu.bspay.sdk</groupId>
    <artifactId>dg-java-sdk</artifactId>
    <version>${dg-java-sdk.version}</version>
</dependency>
```

### 步骤2：安装依赖（如未安装）

如果项目中没有该依赖，需要先在 pom.xml 中添加上述依赖，然后执行 Maven 安装：

```bash
mvn clean install
```

或在 IDE 中刷新 Maven 项目。

### 步骤3：验证依赖

确认以下类可以正常导入：
- `com.huifu.bspay.sdk.opps.core.BasePay`
- `com.huifu.bspay.sdk.opps.core.config.MerConfig`
- `com.huifu.bspay.sdk.opps.core.net.BasePayRequest`
- `com.huifu.bspay.sdk.opps.core.utils.DateTools`
- `com.huifu.bspay.sdk.opps.core.utils.SequenceTools`

**只有完成以上前置检查后，才能继续按照 reference 目录中的示例代码进行开发。**

## 接口说明

| 属性 | 值 |
|-----|-----|
| 接口路径 | `/hfpay/queryorderinfo` |
| 请求方式 | POST |
| Content-Type | application/json |
| 汇付API端点 | `v2/trade/hosting/payment/queryorderinfo` |

## 功能说明

查询订单支付状态和详细信息，包括交易状态、金额、时间等。

## 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|-------|------|-----|------|
| huifuId | String | 是 | 商户号 |
| org_req_date | String | 是 | 原交易请求日期（格式：yyyyMMdd） |
| org_req_seq_id | String | 是 | 原交易请求流水号 |

## 实现步骤

1. 初始化商户配置（MerConfig）
2. 组装请求参数（包含原交易信息）
3. 调用汇付API
4. 返回结果


## 注意事项

1. 需要传入原交易的请求日期和请求流水号
2. 可用于确认支付状态后再进行业务处理
3. 建议在异步通知处理时同步调用查询接口进行二次确认
