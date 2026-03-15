---
name: moltspay_skill
description: "Pay for and use AI services via MoltsPay protocol.\n Trigger: User asks to generate video, use a paid service, etc.\n Auto-discovers services from /.well-known/agent-services.json"
---

# MoltsPay Client Skill

Pay for AI services using USDC/USDT. Supports multiple chains. No gas needed.

## When to Use

- User asks to generate a video, image, or use any paid AI service
- User asks about wallet balance or payment history
- User wants to discover available services
- User mentions "pay", "buy", "purchase" + AI service

## Available Commands

| Command | Description |
|---------|-------------|
| `moltspay init` | Create wallet (works on all chains) |
| `moltspay fund <amount>` | Fund wallet via QR code (debit card/Apple Pay) |
| `moltspay status` | Check balance on each chain |
| `moltspay config` | Modify spending limits |
| `moltspay services <url>` | List services from a provider or marketplace |
| `moltspay pay <url> <service> --chain <chain>` | Pay for a service |

## Wallet Setup

`moltspay init` creates one wallet that works on all supported chains:

| Chain | Tokens | Notes |
|-------|--------|-------|
| Base | USDC, USDT | Recommended, lowest fees |
| Polygon | USDC | Alternative option |

Same address, same private key — works everywhere.

After setup, tell user their wallet address and that they need to fund it with USDC on their preferred chain.

## Discover Services

### Marketplace Discovery

List all services on MoltsPay marketplace:
```
moltspay services https://moltspay.com
```

### Single Provider Discovery

List services from a specific provider:
```
moltspay services https://juai8.com/zen7
```

Shows provider name, wallet, supported chains, and all services with prices.

**Present results as a table to users:**

| Service | Price | Chains |
|---------|-------|--------|
| text-to-video | $0.99 USDC | Base, Polygon |
| image-to-video | $1.49 USDC | Base, Polygon |

Never show raw JSON to users - always format nicely.

## Chain Selection (Pay Only)

When paying:
- If server accepts only one chain → auto-selected
- If server accepts multiple chains → specify with `--chain`

| Chain | Tokens | Notes |
|-------|--------|-------|
| Base | USDC, USDT | Default, lowest fees |
| Polygon | USDC | Alternative |

Examples:
```
moltspay pay https://juai8.com/zen7 text-to-video --prompt "a cat dancing" --chain base
moltspay pay https://juai8.com/zen7 text-to-video --prompt "a cat dancing" --chain polygon
```

## Paying for Services

Use the `moltspay pay` command with the provider URL and service ID.

**Parameters vary by service:**
- `--prompt` for text-based services
- `--image` for image-based services
- `--chain` to specify which chain to pay on
- `--token` to specify token (USDC or USDT, default USDC)

Example: Zen7 video generation
```
moltspay pay https://juai8.com/zen7 text-to-video --prompt "sunset over ocean" --chain base
```

## Spending Limits

Users can configure:
- **max-per-tx**: Maximum per transaction (default $2)
- **max-per-day**: Daily spending limit (default $10)

Use `moltspay config` to modify limits.

## Funding Your Wallet

### Option 1: QR Code (Easiest - No crypto needed!)

```bash
# Fund $10 on Base (recommended)
moltspay fund 10

# Fund $20 on Polygon  
moltspay fund 20 --chain polygon
```

Scan QR code → pay with US debit card or Apple Pay → USDC arrives in ~2 minutes.

**No CDP credentials or crypto knowledge needed.** Server handles everything.

### Option 2: Direct Transfer

Your wallet address works on ALL chains. Send USDC from any wallet:

| Chain | Token | How to fund |
|-------|-------|-------------|
| Base | USDC | Send from Coinbase, MetaMask, etc. |
| Polygon | USDC | Send from any Polygon-compatible wallet |

⚠️ **Important:**
- Balance on Base ≠ Balance on Polygon (they're separate!)
- Check balance per chain with `moltspay status`
- No ETH/MATIC needed (gasless transactions via x402)

## Common User Requests

### "Generate a video of X"

1. Check wallet status (`moltspay status`)
2. If not initialized → run `moltspay init`
3. If balance is 0 → tell user to fund wallet
4. If funded → pay for text-to-video service with appropriate chain
5. Return video URL to user

### "What's my balance?"

Run `moltspay status` and report:
- Wallet address
- Balance on each chain (Base, Polygon)
- Spending limits
- Today's usage

### "What services are available?"

Run `moltspay services https://moltspay.com` to list marketplace.
Format results as a clean table with service names, prices, and providers.

## Error Handling

| Error | Solution |
|-------|----------|
| Insufficient balance | Fund wallet with USDC on the chain you want to use |
| Exceeds daily limit | Wait until tomorrow, or increase limit with `moltspay config` |
| Exceeds per-tx limit | Increase limit with `moltspay config` |
| Service not found | Verify service URL and ID |
| Chain mismatch | Server doesn't accept specified chain. Check supported chains. |
| Multi-chain required | Server accepts multiple chains. Specify `--chain base` or `--chain polygon` |

## Links

- Docs: https://moltspay.com/docs
- Marketplace: https://moltspay.com/services
- GitHub: https://github.com/Yaqing2023/moltspay
