---
name: nft-mint-monitor
description: "NFT铸造监控，追踪即将铸造的热门NFT项目，提醒mint时间。每次调用收费0.001 USDT。触发词：NFT铸造、mint监控、NFT提醒、白名单mint。"
---

# NFT铸造监控

每次调用收费 0.001 USDT。收款钱包: 0x64f15739932c144b54ad12eb05a02ea64f755a53

## 功能

- **即将铸造**: 显示24小时内可mint的NFT
- **价格追踪**: 预售/公售价格
- **WL状态**: 白名单是否开放
- **热度评分**: 基于Twitter/社区活跃度

## 使用方法

```bash
python scripts/nft_mint_monitor.py
```

## 输出示例

```
🎨 NFT铸造监控
━━━━━━━━━━━━━━━━
⏰ 即将铸造 (24h内):

1. Azuki Spirit 📅 今天 20:00 UTC
   💰 价格: 0.08 ETH
   📦 总量: 10,000
   🔥 热度: ⭐⭐⭐⭐⭐
   🎫 WL: 已开放

2. DeGods Genesis 📅 明天 12:00 UTC
   💰 价格: 5 SOL
   📦 总量: 5,000
   🔥 热度: ⭐⭐⭐⭐
   🎫 WL: 已满

💡 建议: Azuki Spirit热度高，建议参与

✅ 已扣费 0.001 USDT
```
