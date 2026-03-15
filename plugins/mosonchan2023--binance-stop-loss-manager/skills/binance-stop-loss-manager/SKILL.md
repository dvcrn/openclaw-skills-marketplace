---
name: binance-stop-loss-manager
description: "Stop loss and take profit manager for Binance trades. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/moson/binance-stop-loss-manager
---

# Binance Stop Loss Manager

## 功能

Professional stop loss and take profit manager for Binance trades.

### 核心功能

- **Stop Loss Orders**: Set automatic stop loss to limit losses
- **Take Profit Orders**: Set take profit levels to secure gains
- **Trailing Stop**: Dynamic stop loss that follows price
- **Order Management**: View and manage all open orders
- **Risk Calculator**: Calculate position size based on risk
- **Multi-Pair Support**: Manage multiple trading pairs

## 使用方法

```json
{
  "action": "set",
  "pair": "BTC/USDT",
  "entryPrice": 42000,
  "stopLoss": 41000,
  "takeProfit": 45000,
  "riskPercent": 2
}
```

## 输出示例

```json
{
  "success": true,
  "orderId": "123456789",
  "stopLoss": 41000,
  "takeProfit": 45000,
  "riskReward": "1:2",
  "message": "Stop loss and take profit orders placed successfully"
}
```

## 价格

每次调用: 0.001 USDT

## 风险管理技巧

1. **Risk/Reward Ratio**: Always aim for at least 1:2 risk/reward
2. **Position Sizing**: Never risk more than 2% per trade
3. **Stop Loss Placement**: Place stop loss below support (long) or above resistance (short)
4. **Trail Stop**: Use trailing stop to lock in profits as price moves

## 常见问题

**Q: 止损和止盈有什么区别？**
A: 止损是当价格不利时自动卖出限制损失，止盈是当价格达到目标时自动卖出锁定利润。

**Q: 建议设置多大的止损？**
A: 建议每笔交易风险不超过账户的 2%。

**Q: 支持合约交易吗？**
A: 是的，支持现货和合约交易。
