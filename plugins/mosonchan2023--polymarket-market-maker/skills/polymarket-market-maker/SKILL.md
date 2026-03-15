---
name: polymarket-market-maker
description: "为 Polymarket 市场提供流动性，自动做市。每次调用自动扣费 0.001 USDT"
homepage: https://github.com/moson/polymarket-market-maker
---

# Polymarket Market Maker

## 功能

- 自动化做市策略
- 双边挂单
- 价差管理
- 仓位对冲

## 详细说明

此技能为 Polymarket 预测市场提供专业做市服务。通过智能算法自动在 markets 中提供流动性，赚取交易费用。

### 核心功能

1. **自动挂单**: 根据市场波动性自动设置买卖价差
2. **仓位管理**: 实时监控和对冲已开仓位
3. **风险控制**: 设置最大持仓限制和自动平仓条件
4. **收益追踪**: 记录做市收益和费用

### 使用方法

调用时指定市场条件参数:
```json
{
  "market": "BTC price prediction market",
  "spread": 0.02,
  "maxPosition": 100
}
```

### 注意事项

- 需要钱包私钥进行交易
- 建议初始资金不低于 100 USDT
- 做市有风险，请谨慎设置参数
