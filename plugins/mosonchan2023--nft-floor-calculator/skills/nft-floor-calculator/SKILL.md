---
name: nft-floor-calculator
description: "Calculate NFT floor prices across multiple marketplaces - OpenSea, Blur, Magic Eden. Each call charges 0.001 USDT via SkillPay."
homepage: https://github.com/moson/nft-floor-calculator
---

# NFT Floor Calculator

## 功能

Calculate NFT floor prices across multiple marketplaces - OpenSea, Blur, Magic Eden.

### 核心功能

- **Multi-Marketplace Comparison**: Compare floor prices across platforms
- **Historical Floor Analysis**: Track floor price changes over time
- **Collection Analytics**: Get detailed collection statistics
- **Price Alerts**: Set alerts for floor price changes
- **Wash Trade Filter**: Filter out wash trades for accurate pricing

## 使用方法

```json
{
  "collection": "bored-ape-yacht-club",
  "marketplaces": ["opensea", "blur", "magic-eden"],
  "timeframe": "7d"
}
```

## 输出示例

```json
{
  "success": true,
  "collection": "bored-ape-yacht-club",
  "floor_price": "18.5 ETH",
  "marketplaces": {
    "opensea": "18.5 ETH",
    "blur": "18.2 ETH",
    "magic-eden": "18.8 ETH"
  },
  "volume_24h": "150 ETH"
}
```

## 支持的市场

- OpenSea
- Blur
- Magic Eden
- LooksRare
- X2Y2

## 价格

每次调用: 0.001 USDT
