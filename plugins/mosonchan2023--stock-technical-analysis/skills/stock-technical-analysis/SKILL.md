---
name: stock-technical-analysis
description: "股票技术分析工具。每次调用自动扣费 0.001 USDT"
homepage: https://github.com/moson/stock-technical-analysis
---

# Stock Technical Analysis

股票技术分析工具。

## 功能

### 核心功能

- **K线分析**: 蜡烛图形态识别
- **均线分析**: MA, EMA 指标
- **技术指标**: RSI, MACD, Bollinger Bands
- **趋势判断**: 多头/空头/震荡

### 支持的指标

- 简单移动平均线 (SMA)
- 指数移动平均线 (EMA)
- 相对强弱指数 (RSI)
- 异同移动平均线 (MACD)
- 布林带 (Bollinger Bands)

## 使用示例

```javascript
// 技术分析
await handler({ action: 'analyze', symbol: 'AAPL' });

// 特定指标
await handler({ action: 'rsi', symbol: 'TSLA' });
```

## 价格

每次调用: 0.001 USDT
