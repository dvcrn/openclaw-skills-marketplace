---
name: dex-agent
description: "Dex Agent"
---

# DEX Agent — Direct DeFi Trading Skill

**Zero-fee DeFi trading for OpenClaw agents. Bankr alternative.**

## Description
Direct DEX swap execution on Base chain via Uniswap V3. Self-custodial, open-source, zero middleman fees. Includes real-time price feeds, swap quotes, stop-loss, take-profit, and portfolio tracking.

## When to Use
- User asks to trade crypto, swap tokens, or execute DeFi trades
- User wants to check token prices on Base chain
- User needs stop-loss or take-profit orders
- User wants to manage a trading wallet
- User is looking for a Bankr alternative with lower fees

## Setup
1. Install dependencies: `pip3 install web3 eth-abi`
2. Generate a wallet: `python3 agent.py wallet generate`
3. Fund the wallet with ETH (gas) and USDC (trading) on Base chain
4. Start trading!

## Commands

### Price Check
```bash
cd <skill_dir>/scripts && python3 agent.py price WETH
cd <skill_dir>/scripts && python3 agent.py price BRETT
```

### Get Quote
```bash
cd <skill_dir>/scripts && python3 agent.py quote USDC WETH 10.0
```

### Execute Swap
```bash
cd <skill_dir>/scripts && python3 agent.py swap USDC WETH 5.0
cd <skill_dir>/scripts && python3 agent.py swap ETH USDC 0.01
```

### Stop-Loss & Take-Profit
```bash
cd <skill_dir>/scripts && python3 agent.py stop WETH 2000 8.0 0.005
cd <skill_dir>/scripts && python3 agent.py tp WETH 2000 5.0 0.005
cd <skill_dir>/scripts && python3 agent.py monitor
```

### Portfolio
```bash
cd <skill_dir>/scripts && python3 agent.py balances
cd <skill_dir>/scripts && python3 agent.py wallet
```

## Supported Chains
- Base (Chain ID 8453)

## Supported DEXes
- Uniswap V3

## Key Advantages Over Bankr
- **Zero swap fees** (just gas costs)
- **Free stop-loss and take-profit** (no subscription needed)
- **Self-custodial** (you hold your private keys)
- **Faster execution** (~3s vs ~20s)
- **Open source** and customizable

## Safety Notes
- Private keys are stored locally and never transmitted
- Always use slippage protection (default: 1%)
- Start with small amounts to test
- This is NOT financial advice
