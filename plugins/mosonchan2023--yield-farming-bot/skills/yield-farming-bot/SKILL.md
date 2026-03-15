---
name: yield-farming-bot
description: "DeFi yield farming bot - auto-compound, optimize yields, track positions across protocols. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/moson/yield-farming-bot
---

# Yield Farming Bot

## 功能

DeFi yield farming bot - auto-compound, optimize yields, track positions across protocols.

### 核心功能

- **Auto-Compound**: Automatically compound yields
- **Yield Optimization**: Find best yield opportunities
- **Position Tracking**: Track all farming positions
- **Reward Collection**: Auto-claim rewards
- **Gas Optimization**: Optimize gas fees
- **Multi-Protocol Support**: Support for major DeFi protocols

## 使用方法

```json
{
  "action": "optimize",
  "protocol": "uniswap",
  "pool": "ETH-USDC",
  "auto_compound": true
}
```

## 输出示例

```json
{
  "success": true,
  "action": "optimize",
  "current_yield": "12.5%",
  "optimized_yield": "15.2%",
  "improvement": "+21.6%",
  "gas_saved": "0.002 ETH"
}
```

## 支持的协议

- Uniswap
- SushiSwap
- Curve
- Aave
- Compound
- Yearn

## 价格

每次调用: 0.001 USDT

## 常见问题

**Q: 安全吗？**
A: 使用官方合约，只授权必要权限。

**Q: 如何优化收益？**
A: 自动复投、选择高收益池、优化 Gas 费用。

**Q: 支持哪些链？**
A: Ethereum, Polygon, Arbitrum, Optimism 等。
