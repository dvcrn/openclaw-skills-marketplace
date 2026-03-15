---
name: binance-rsi-bot
description: "RSI indicator trading bot for Binance - generate buy/sell signals based on RSI technical analysis. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/moson/binance-rsi-bot
---

# Binance RSI Bot

## 功能

RSI (Relative Strength Index) indicator trading bot for Binance - generates buy/sell signals based on RSI technical analysis.

### 核心功能

- **RSI Calculation**: Calculate RSI values for any trading pair
- **Overbought/Oversold Signals**: Detect overbought (>70) and oversold (<30) conditions
- **Divergence Detection**: Identify RSI divergences from price
- **Trading Suggestions**: Generate actionable buy/sell recommendations
- **Historical RSI**: View historical RSI trends
- **Multiple Timeframes**: Support for 1m, 5m, 15m, 1h, 4h, 1d timeframes

## RSI 策略说明

- **RSI > 70**: 超买区域，考虑卖出
- **RSI < 30**: 超卖区域，考虑买入
- **RSI > 80**: 极端超买，强烈建议卖出
- **RSI < 20**: 极端超卖，强烈建议买入
- **RSI 50**: 中性区域

## 使用方法

```json
{
  "action": "rsi",
  "pair": "BTC/USDT",
  " timeframe": "1h",
  "period": 14
}
```

## 输出示例

```json
{
  "success": true,
  "pair": "BTC/USDT",
  "rsi": 65.5,
  "signal": "NEUTRAL",
  "interpretation": "RSI in neutral zone, no clear signal",
  "recommendation": "Wait for RSI to reach oversold or overbought zones"
}
```

## 价格

每次调用: 0.001 USDT

## 常见问题

**Q: 什么是 RSI？**
A: RSI (Relative Strength Index) 是相对强弱指标，用于判断价格是否超买或超卖。

**Q: RSI 策略有效吗？**
A: RSI 是经典技术指标，配合其他指标使用效果更好。

**Q: 支持哪些时间框架？**
A: 支持 1m, 5m, 15m, 1h, 4h, 1d 等时间框架。
