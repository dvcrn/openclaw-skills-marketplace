---
name: polymarket-portfolio-tracker
description: "追踪 Polymarket 仓位，实时监控盈亏，设置价格提醒。每次调用自动扣费 0.001 USDT"
homepage: https://github.com/moson/polymarket-portfolio-tracker
---

# Polymarket Portfolio Tracker

## 功能

- 实时仓位追踪
- 盈亏计算
- 价格提醒设置
- 组合分析

## 详细说明

专业的 Polymarket 投资组合管理工具，帮助交易者追踪所有仓位并分析投资表现。

### 核心功能

1. **仓位追踪**: 自动同步所有未平仓合约，实时更新仓位价值
2. **盈亏计算**: 计算已实现和未实现盈亏，支持多币种
3. **价格提醒**: 设置价格提醒，当市场价格达到目标时通知
4. **组合分析**: 分析资产配置、风险敞口和投资回报率

### 使用方法

```json
{
  "action": "sync",
  "address": "0x..."
}
```

或设置提醒:
```json
{
  "action": "alert",
  "market": "Will BTC hit $150k?",
  "targetPrice": 0.75,
  "condition": "above"
}
```

### 注意事项

- 需要钱包地址进行同步
- 价格提醒支持邮件和 Telegram 通知
