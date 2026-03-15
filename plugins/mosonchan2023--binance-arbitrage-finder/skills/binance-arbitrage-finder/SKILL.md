---
name: binance-arbitrage-finder
description: "Find arbitrage opportunities between Binance and other exchanges. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/moson/binance-arbitrage-finder
---

# Binance Arbitrage Finder

## 功能

Find profitable arbitrage opportunities between Binance and other major cryptocurrency exchanges.

### 核心功能

- **Cross-Exchange Price Scanning**: Compare prices across exchanges
- **Profit Calculation**: Calculate theoretical arbitrage profit
- **Real-Time Monitoring**: Monitor arbitrage opportunities
- **Risk Assessment**: Evaluate execution risks
- **Multi-Pair Analysis**: Scan multiple trading pairs
- **Historical Analysis**: Track arbitrage historical data

## 使用方法

```json
{
  "action": "scan",
  "minProfit": 0.5,
  "pairs": ["BTC/USDT", "ETH/USDT"],
  "exchanges": ["binance", "bybit", "okx"]
}
```

## 输出示例

```json
{
  "success": true,
  "opportunities": [
    {
      "pair": "BTC/USDT",
      "buyExchange": "binance",
      "sellExchange": "bybit",
      "priceDiff": "0.8%",
      "potentialProfit": "0.6%",
      "volume": "10000 USDT"
    }
  ]
}
```

## 价格

每次调用: 0.001 USDT

## 风险提示

- 套利存在执行风险
- 市场波动可能导致机会消失
- 需要考虑交易手续费
- 建议先小额测试

## 常见问题

**Q: 套利真的能赚钱吗？**
A: 理论上有利润，但需要快速执行并考虑手续费、滑点等成本。

**Q: 支持哪些交易所？**
A: Binance, Bybit, OKX, Huobi, Gate.io 等主流交易所。
