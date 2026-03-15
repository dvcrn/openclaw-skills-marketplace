---
name: options-chain
description: "Options chain data and analysis - strike prices, premiums, Greeks, implied volatility. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/moson/options-chain
---

# Options Chain

## 功能

Options chain data and analysis for traders - get strike prices, premiums, Greeks, and implied volatility.

### 核心功能

- **Options Chain Data**: Full options chain with all strikes
- **Premium Calculation**: Calculate option premiums
- **Greeks Analysis**: Delta, Gamma, Theta, Vega, Rho
- **Implied Volatility**: IV analysis and comparisons
- **Strategy Suggestions**: Recommend optimal strategies
- **Risk Analysis**: Assess risk of options positions

## 使用方法

```json
{
  "symbol": "AAPL",
  "expiration": "2026-04-15",
  "type": "call"
}
```

## 输出示例

```json
{
  "success": true,
  "symbol": "AAPL",
  "expiration": "2026-04-15",
  "chain": [
    {
      "strike": 180,
      "call": { "bid": 5.2, "ask": 5.5, "iv": "28%" },
      "put": { "bid": 3.1, "ask": 3.3, "iv": "27%" }
    }
  ],
  "greeks": {
    "delta": 0.65,
    "gamma": 0.03,
    "theta": -0.05,
    "vega": 0.12
  }
}
```

## 价格

每次调用: 0.001 USDT

## 常见问题

**Q: 支持哪些标的？**
A: 股票、ETF、加密货币等。

**Q: 什么是 Greeks？**
A: Greeks 是期权定价模型中的风险指标，包括 Delta、Gamma、Theta、Vega 等。

**Q: 如何使用 IV？**
A: IV (隐含波动率) 越高，期权价格越贵。
