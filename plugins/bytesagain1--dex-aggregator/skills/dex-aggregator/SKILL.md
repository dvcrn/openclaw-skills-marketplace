---
name: DEX Aggregator
description: "Compare token prices across decentralized exchanges — find best rates, lowest slippage, and optimal swap routes using DexScreener and 1inch APIs."
---

# DEX Aggregator

Find the best swap rates across all DEXes.

## How It Works

1. Query multiple DEX APIs simultaneously
2. Compare prices including gas and slippage
3. Recommend optimal routing
4. Show price impact for large trades

## Commands

```bash
bash scripts/dex.sh quote <token_in> <token_out> <amount> [chain]
bash scripts/dex.sh compare <token> [chain]
bash scripts/dex.sh pools <token> [chain]
bash scripts/dex.sh trending [chain]
bash scripts/dex.sh gas [chain]
```

## Supported DEXes

- **Ethereum**: Uniswap V3, SushiSwap, Curve, Balancer
- **BSC**: PancakeSwap, BiSwap
- **Polygon**: QuickSwap, SushiSwap
- **Arbitrum**: Camelot, SushiSwap
- **Base**: Aerodrome, BaseSwap
- **Solana**: Jupiter, Raydium, Orca

Powered by BytesAgain | bytesagain.com | hello@bytesagain.com
