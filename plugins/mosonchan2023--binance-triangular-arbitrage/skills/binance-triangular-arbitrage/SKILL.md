---
name: binance-triangular-arbitrage
description: "Binance 三角套利检测和执行。每次调用自动扣费 0.001 USDT"
homepage: https://github.com/moson/binance-triangular-arbitrage
---

# Binance Triangular Arbitrage

检测和执行 Binance 平台内部的三角套利机会。

## 功能

三角套利是一种利用同一交易所内三个交易对价格差异获利的策略。例如：
- 用 USDT 买入 BTC
- 用 BTC 买入 ETH
- 用 ETH 卖出换 USDT

如果最终获得的 USDT 大于初始金额，则盈利。

### 核心功能

- **路径识别**: 自动发现有利可图的三角套利路径
- **利润计算**: 计算包含手续费的净利润
- **实时扫描**: 持续监控市场寻找机会
- **自动执行**: 支持设置自动交易（需配置 API Key）

### 支持的交易对类型

- 主流币种: BTC, ETH, BNB
- 稳定币: USDT, USDC, BUSD
- 山寨币: 多种可选交易对

## 使用示例

```javascript
// 扫描三角套利机会
await handler({ action: 'scan' });

// 按最小利润过滤
await handler({ action: 'scan', minProfit: 0.01 });

// 查看特定路径
await handler({ action: 'scan', path: ['BTC', 'ETH', 'USDT'] });
```

## 返回数据

- 套利路径 (A→B→C→A)
- 每条边的价格
- 理论利润（扣除手续费）
- 风险评估
- 执行建议

## 策略说明

### 何时使用

三角套利适合以下情况：
1. 市场波动较大时
2. 交易所流动性充足时
3. 有高速网络和 API 接口时

### 风险提示

- 三角套利需要快速执行
- 网络延迟可能影响利润
- 建议使用 API 自动执行
- 手续费可能侵蚀利润

## 价格

每次调用: 0.001 USDT

## 配置说明

此技能无需配置 API Key 即可扫描机会。如需自动执行，需要配置 Binance API Key 和 Secret。

```javascript
{
  API_KEY: "your_binance_api_key",
  API_SECRET: "your_binance_api_secret"
}
```

## 常见问题

**Q: 三角套利真的能赚钱吗？**
A: 理论上可以，但机会稍纵即逝，需要高速执行能力。

**Q: 需要多少资金？**
A: 建议至少 1000 USDT 开始，太小难以覆盖手续费。

**Q: 会被交易所封吗？**
A: 正常套利不会违规，但高频API可能被限制，请遵守交易所规则。
