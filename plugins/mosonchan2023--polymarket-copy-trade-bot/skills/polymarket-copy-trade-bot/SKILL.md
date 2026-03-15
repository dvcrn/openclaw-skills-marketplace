---
name: polymarket-copy-trade-bot
description: "自动跟随成功交易者的交易策略，复制鲸鱼仓位。每次调用自动扣费 0.001 USDT"
homepage: https://github.com/moson/polymarket-copy-trade-bot
---

# Polymarket Copy Trade Bot

## 功能
- 追踪成功交易者（鲸鱼）
- 自动复制高胜率交易
- 智能仓位管理
- 止盈止损设置

## 使用
```js
{ action: 'follow', trader: '0x...' }
{ action: 'status' }
{ action: 'execute', market: '...', side: 'YES', size: 100 }
```
