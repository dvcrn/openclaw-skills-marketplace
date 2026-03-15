---
name: binance-macd-bot
description: "MACD indicator trading bot for Binance - generate buy/sell signals based on MACD technical analysis. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/moson/binance-macd-bot
---

# Binance MACD Bot

## 功能

MACD (Moving Average Convergence Divergence) indicator trading bot for Binance - generates buy/sell signals based on MACD technical analysis.

### 核心功能

- **MACD Calculation**: Calculate MACD values (MACD line, signal line, histogram)
- **Golden Cross Signals**: Detect golden cross (bullish crossover)
- **Death Cross Signals**: Detect death cross (bearish crossover)
- **Divergence Detection**: Identify MACD divergences from price
- **Trend Analysis**: Determine current market trend
- **Signal Generation**: Generate actionable buy/sell recommendations

## MACD 策略说明

- **MACD Line > Signal Line**: 看涨信号 (Golden Cross)
- **MACD Line < Signal Line**: 看跌信号 (Death Cross)
- **Histogram Positive**: 多头趋势
- **Histogram Negative**: 空头趋势
- **Zero Line Crossover**: 趋势转换信号

## 使用方法

```json
{
  "action": "macd",
  "pair": "BTC/USDT",
  " timeframe": "1h",
  "fast": 12,
  "slow": 26,
  "signal": 9
}
```

## 输出示例

```json
{
  "success": true,
  "pair": "BTC/USDT",
  "macd": 150.5,
  "signal": 145.2,
  "histogram": 5.3,
  "signal_type": "GOLDEN_CROSS",
  "interpretation": "Bullish momentum increasing",
  "recommendation": "BUY - MACD crossing above signal line"
}
```

## 价格

每次调用: 0.001 USDT

## 常见问题

**Q: 什么是 MACD？**
A: MACD (Moving Average Convergence Divergence) 是移动平均收敛发散指标，用于判断趋势方向和动量。

**Q: MACD 策略有效吗？**
A: MACD 是经典技术指标，特别适合趋势明显的市场。

**Q: 建议配合什么指标使用？**
A: 建议配合 RSI、均线一起使用，提高信号准确度。
