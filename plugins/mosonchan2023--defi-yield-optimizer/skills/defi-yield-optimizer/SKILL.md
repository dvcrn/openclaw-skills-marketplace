---
name: defi-yield-optimizer
description: "DeFi Yield optimizer - cross-protocol yield comparison, auto-rebalancing, best yield farming strategies. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/moson/defi-yield-optimizer
---

# DeFi Yield Optimizer

## 功能

### 1. 收益对比
- 跨 Aave/Compound/Curve/Yearn 收益对比
- 实时 APY 监控
- 收益排行榜

### 2. 最优策略
- 自动推荐最佳收益来源
- 风险调整后收益计算
- 流动性考虑

### 3. 再平衡
- 仓位自动再平衡
- 收益复投
- Gas 优化

## 使用示例

```javascript
// 查询最优收益
{ action: "best-yield", token: "USDC" }

// 对比协议收益
{ action: "compare", tokens: ["USDC", "USDT", "DAI"] }

// 计算收益
{ action: "calculate", principal: 10000, protocol: "aave", days: 30 }
```

## 输出示例

```json
{
  "success": true,
  "bestProtocol": "Aave",
  "apy": "4.5%",
  "alternatives": [
    { "protocol": "Compound", "apy": "3.8%" },
    { "protocol": "Yearn", "apy": "5.2%" }
  ]
}
```

## 风险提示

- DeFi 有智能合约风险
- 收益会波动
- 建议分散投资

## 价格

每次调用: 0.001 USDT
