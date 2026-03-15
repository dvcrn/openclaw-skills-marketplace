---
name: crypto-arbitrage-scanner
description: "Cryptocurrency arbitrage scanner - detect cross-exchange price differences, triangular arbitrage opportunities, real-time alerts. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/moson/crypto-arbitrage-scanner
---

# Crypto Arbitrage Scanner

## 功能

### 1. 跨交易所价差检测
- Binance vs Bybit vs OKX vs KuCoin
- 实时价差计算
- 扣除手续费后净收益

### 2. 三角形套利
- ETH/USDC/USDT 三角循环
- 自动检测无风险利润
- Gas 成本考虑

### 3. 实时警报
- 价差 > 0.5% 时推送
- 最佳套利路径推荐

## 使用示例

```javascript
// 扫描所有交易对
{ action: "scan" }

// 扫描特定交易对
{ action: "scan", pair: "BTC/USDT" }

// 设置警报阈值
{ action: "alert", threshold: 0.5 }
```

## 输出示例

```json
{
  "success": true,
  "opportunities": [
    {
      "type": "cross-exchange",
      "pair": "BTC/USDT",
      "buyExchange": "binance",
      "sellExchange": "bybit",
      "priceDiff": "0.8%",
      "netProfit": "0.5%"
    }
  ]
}
```

## 风险提示

- 套利机会往往转瞬即逝
- 需要足够流动性
- 考虑滑点和 Gas

## 价格

每次调用: 0.001 USDT
