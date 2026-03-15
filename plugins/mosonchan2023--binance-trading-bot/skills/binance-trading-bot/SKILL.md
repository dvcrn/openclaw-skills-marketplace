---
name: binance-trading-bot
description: "Binance 现货/合约交易机器人 - 查询余额、市价/限价下单、止盈止损。每次调用自动扣费 0.001 USDT（SkillPay 集成）"
homepage: https://github.com/moson/binance-trading-bot
---

# Binance Trading Bot

## 功能

Binance 现货/合约交易机器人，支持：

1. **查询余额** - 获取现货和合约钱包余额
2. **市价交易** - 快速市价买入/卖出
3. **限价交易** - 设置价格买入/卖出
4. **止盈止损** - 设置止盈止损单
5. **市场数据** - 查询实时价格、K线数据

## 使用示例

```
- "查询我的 binance 余额"
- "市价买入 BTC 0.01"
- "限价买入 ETH 0.1 价格 3000"
- "卖出 BNB 0.5"
```

## 配置要求

```json
{
  "skills": {
    "entries": {
      "binance-trading-bot": {
        "enabled": true,
        "env": {
          "SKILLPAY_API_KEY": "你的 SkillPay API Key",
          "BINANCE_API_KEY": "你的 Binance API Key",
          "BINANCE_SECRET_KEY": "你的 Binance Secret Key"
        }
      }
    }
  }
}
```

## 风险提示

- 交易有风险，资金自负
- 建议先使用测试网测试
