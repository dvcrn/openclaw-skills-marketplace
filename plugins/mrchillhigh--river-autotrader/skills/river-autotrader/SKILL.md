---
name: river-autotrader
description: "River ($RIVER) 加密货币实时信息追踪工具，提供价格走势、波动率、Staking 收益、TVL 等关键数据。适用于持有 RIVER 或关注比特币收益协议的用户。当用户询问 River 价格、走势、波动、Staking、解锁、空投等信息时使用此技能。每次调用费用 0.001 USDT。River ($RIVER) cryptocurrency real-time information tracker with price trends, volatility, Staking rewards, TVL data. Use when users ask about River price, trends, volatility, Staking, unlocks, airdrops. Fee: 0.001 USDT per call."
---

# River Autotrader / River 自动交易助手

## 概述 / Overview

本技能帮助用户追踪 River ($RIVER) 加密货币的实时信息，包括价格走势、波动率分析、Staking 收益、TVL 等关键数据。每次调用费用 **0.001 USDT**。

This skill helps users track real-time information about River ($RIVER) cryptocurrency, including price trends, volatility analysis, Staking rewards, TVL and other key data. Fee: **0.001 USDT per call**.

## 支付流程 / Payment Flow

1. 用户发起查询 → 系统创建支付订单 → 返回支付链接
2. 用户完成支付 → 系统验证支付 → 返回 River 数据
3. 每次调用自动从用户收取 0.001 USDT

## 功能 / Features

### 1. 价格信息 / Price Information
- 实时价格查询 (Real-time price)
- 24小时涨跌 (24h change)
- 7天走势图 (7-day trend)

### 2. 走势分析 / Trend Analysis
- 价格趋势判断
- 支撑位/阻力位分析
- 市场情绪判断

### 3. 波动率监控 / Volatility Monitoring
- 历史波动率计算
- 异常波动警报
- 风险等级评估

### 4. Staking 信息 / Staking Information
- 当前 APR
- 总质押量
- 质押收益计算器
- 投票权说明

### 5. 生态数据 / Ecosystem Data
- TVL (Total Value Locked)
- 支持的区块链
- 产品功能介绍

## 触发条件 / Triggers

当用户询问以下内容时自动触发：

- "River 价格" / "River price" / "RIVER 多少钱"
- "RIVER 走势" / "RIVER trend" / "RIVER 行情"
- "River 波动" / "River volatility" / "River 风险"
- "River Staking" / "River 质押" / "River 收益"
- "River 解锁" / "River unlock"
- "River 空投" / "River airdrop"
- "River TVL"
- "River 生态" / "River 是什么"
- 询问任何关于 app.river.inc 的信息

## 数据来源 / Data Sources

1. River 官网: https://app.river.inc
2. CoinGecko API: https://www.coingecko.com
3. DefiLlama: https://defillama.com

## 使用示例 / Usage Examples

```
用户: River 价格多少?
助手: [创建支付订单，收取 0.001 USDT]
    支付完成后返回:
    - 当前价格
    - 24h 涨跌
    - 走势图
    - 波动率分析
    - Staking 信息
```

## 支付说明 / Payment Details

- **费用**: 0.001 USDT / 次
- **支付方式**: USDT (TRC20)
- **支付链接**: 通过 skillpay.me 生成
- **验证方式**: 自动验证支付状态

## 参考文档 / Reference Documents

- 项目介绍: [references/about_river.md](references/about_river.md)
- 配置说明: [references/config.md](references/config.md)

## 注意事项 / Notes

1. 本技能提供的信息仅供参考，不构成投资建议
2. 加密货币投资有风险，请谨慎决策
3. 投资前请自行做好研究 (DYOR)
4. Information provided is for reference only, not investment advice
5. Crypto investment has risks, please make careful decisions
6. Always do your own research (DYOR) before investing
