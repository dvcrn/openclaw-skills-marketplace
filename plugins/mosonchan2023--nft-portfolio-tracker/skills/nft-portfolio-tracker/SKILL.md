---
name: nft-portfolio-tracker
description: "NFT 组合追踪器 - 追踪 NFT 持仓，计算地板价，总价值，收益分析。每次调用自动扣费 0.001 USDT"
---

# NFT Portfolio Tracker

## 功能

1. **持仓追踪** - 追踪多个钱包 NFT 持仓
2. **地板价计算** - 实时地板价，总价值
3. **收益分析** - ROI 计算，盈亏追踪
4. **巨鲸监控** - 监控大户持仓变化

## 使用

```js
{ action: "portfolio", address: "0x..." }
{ action: "floor", collection: "bored-ape" }
{ action: "profit", address: "0x..." }
```
