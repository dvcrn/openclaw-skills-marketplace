---
name: whale-watcher
description: "Monitor crypto whale wallets for large transactions.\n Track big moves on Ethereum, BSC, and other chains.\n Get alerts when whales move significant amounts."
---

# 🐋 Whale Watcher - 巨鲸钱包监控

Monitor crypto whale wallets and get alerts for large transactions.

## Features

- 🔍 Track specific whale wallets
- 💰 Set minimum transaction threshold
- ⛓️ Support multiple chains (ETH, BSC, etc.)
- 📱 Telegram alerts
- 📊 Transaction history

## Usage

```bash
# Monitor a wallet
/whale-watcher monitor 0x123...abc --threshold 1000000

# Check recent transactions
/whale-watcher txs 0x123...abc

# Set alert threshold
/whale-watcher alert --min 5000000
```

## API Sources

- Etherscan API
- BscScan API
- On-chain data

## Setup

Add to environment:
```bash
export ETHERSCAN_API_KEY="your_key"
export BSCSCAN_API_KEY="your_key"
```

