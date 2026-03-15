---
name: binance-scalping-bot
description: "快速小额交易剥头皮策略。每次调用自动扣费 0.001 USDT"
homepage: https://github.com/moson/binance-scalping-bot
---

# Binance Scalping Bot

高频小额交易策略，适合日内交易者。

## 功能

剥头皮交易是一种通过捕捉微小价格波动获利的策略。

### 核心功能

- **快速入场**: 毫秒级订单执行
- **小额利润**: 每次交易目标 0.1-0.5%
- **日内平仓**: 不过夜持仓
- **风险控制**: 自动止损

### 策略参数

- 交易对: 主流币种 (BTC, ETH, BNB)
- 利润目标: 0.1-0.5%
- 止损: 0.2%
- 持仓时间: 分钟级

## 使用示例

```javascript
// 查看 bot 状态
await handler({ action: 'status' });

// 启动 bot
await handler({ action: 'start', pair: 'BTC/USDT' });

// 停止 bot
await handler({ action: 'stop' });
```

## 价格

每次调用: 0.001 USDT

## 风险提示

1. 高频交易风险高
2. 需要充足流动性
3. 市场波动可能导致快速亏损
4. 建议先用模拟账户测试
5. 需要稳定的网络连接

## 配置说明

如需自动交易，需要配置 Binance API：

```javascript
{
  API_KEY: "your_binance_api_key",
  API_SECRET: "your_binance_api_secret"
}
```

## 剥头皮技巧

1. 选择高流动性交易对
2. 关注交易量峰值时段
3. 设置严格的止损点
4. 保持低杠杆或不使用杠杆
5. 持续监控市场状态
