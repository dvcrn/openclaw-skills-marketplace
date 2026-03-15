# Spraay Payments — OpenClaw Skill 💧

Multi-chain batch crypto payments, payroll, swaps, invoices, price feeds, and AI inference for your OpenClaw agent.

## What This Skill Does

Spraay Payments gives your OpenClaw agent the ability to:

- **Batch payments** — Send tokens to dozens of wallets in one transaction (save 60-80% on gas)
- **Payroll** — Pay your team with one command, ENS/Basename resolution included
- **Token swaps** — Get quotes and execute swaps on Base, Ethereum, Arbitrum, and more
- **Price feeds** — Real-time token prices (free, no payment needed)
- **Invoicing** — Create and track crypto invoices
- **AI inference** — Pay-per-query AI chat via OpenRouter
- **Email/XMTP messaging** — Send payment confirmations and notifications
- **IPFS storage** — Pin files to IPFS via Pinata
- **RPC relay** — Access 7 chains via Alchemy
- **Compliance** — Audit trails, tax reports, KYC verification

57 paid endpoints + 5 free endpoints across 11 chains.

## Install

Tell your OpenClaw agent:

> "Install the spraay-payments skill"

Or manually:

```bash
# From ClawHub
clawhub install spraay-payments

# Or copy to your skills directory
cp -r spraay-payments ~/.openclaw/skills/
```

## Requirements

- `curl` and `jq` (installed on most systems)
- An x402-compatible wallet (Coinbase CDP or similar) for paid endpoints
- No API key needed — Spraay uses x402 micropayments

## Quick Start

Once installed, just ask your agent:

- "Send 1000 USDC to alice.eth and 500 USDC to bob.base on Base"
- "What's the price of ETH?"
- "Create an invoice for 5000 USDC"
- "Check my USDC balance on Arbitrum"
- "Swap 2 ETH to USDC on Base"

## Links

- **App**: https://spraay.app
- **Gateway**: https://gateway.spraay.app
- **Docs**: https://docs.spraay.app
- **GitHub**: https://github.com/plagtech
- **Twitter**: [@Spraay_app](https://twitter.com/Spraay_app)
- **MCP Server**: https://smithery.ai/server/@plagtech/spraay-x402-mcp

## Revenue

This skill is also available on [LarryBrain](https://www.larrybrain.com) as a premium skill.

Built by [@plag](https://warpcast.com/plag) | [@lostpoet](https://twitter.com/lostpoet)
