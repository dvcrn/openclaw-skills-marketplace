---
name: arbitrage-scanner
description: "扫描DEX套利机会，发现不同交易所价差。触发词：套利、arbitrage、价差、搬砖。"
---

# 套利扫描器

每次调用收费 0.001 USDT。

## 功能

- 多DEX价格对比
- 实时套利机会发现
- 考虑Gas成本后的净利润
- 支持ETH/BSC/Arbitrum

## 输出示例

⚡ **套利机会**
━━━━━━━━━━━━━━━━
💱 ETH/USDC
📍 Uniswap: $2,350
📍 SushiSwap: $2,365
📈 价差: 0.64%
💰 预估利润: +$125 (扣除Gas)
⚠️ 窗口: ~30秒
