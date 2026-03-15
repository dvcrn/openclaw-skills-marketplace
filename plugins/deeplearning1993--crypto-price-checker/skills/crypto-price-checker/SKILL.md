---
name: crypto-price-checker
description: "实时加密货币价格查询。支持BTC、ETH、SOL等主流币种，返回当前价格、24h涨跌幅、交易量。每次调用收费0.001 USDT。触发词：币价、crypto price、比特币价格、以太坊价格。"
---

# 加密货币价格查询

每次调用收费 0.001 USDT。

## 功能

- 查询任意加密货币实时价格
- 显示24小时涨跌幅
- 显示24小时交易量
- 支持CoinGecko数据源

## 使用方法

```bash
python scripts/price_checker.py BTC user_id
```

## 收费集成

使用SkillPay API进行收费，收款钱包: 0x64f15739932c144b54ad12eb05a02ea64f755a53
