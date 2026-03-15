# MoltsPay Client Skill

Let your AI agent pay for services using USDC. Multi-chain support (Base + Polygon). No gas needed.

## Features

- 🔐 **One wallet, all chains** — same address works on Base & Polygon
- 💸 **Pay for services** with USDC/USDT (gasless via x402)
- 🔍 **Discover services** from marketplace or individual providers
- 🛡️ **Spending limits** built-in ($2/tx, $10/day default)

## Quick Start

After installing, your agent can:

1. **Generate videos:**
   > "Generate a video of a cat dancing"
   
2. **Check balance:**
   > "What's my wallet balance?"

3. **Discover services:**
   > "What services can I pay for?"

## Supported Chains

| Chain | Tokens | Notes |
|-------|--------|-------|
| Base | USDC, USDT | Recommended, lowest fees |
| Polygon | USDC | Alternative option |

## Example Services

| Service | Price | Command |
|---------|-------|---------|
| Zen7 Text-to-Video | $0.99 | `npx moltspay pay https://juai8.com/zen7 text-to-video --prompt "..." --chain base` |
| Zen7 Image-to-Video | $1.49 | `npx moltspay pay https://juai8.com/zen7 image-to-video --image /path/to/img --chain base` |

## Discover Services

List all services on marketplace:
```bash
npx moltspay services https://moltspay.com
```

List services from a specific provider:
```bash
npx moltspay services https://juai8.com/zen7
```

## Funding Your Wallet

1. Get your address: `npx moltspay status`
2. Send USDC on **Base** or **Polygon** to that address
3. No ETH/MATIC needed (gasless transactions)

⚠️ Balance on each chain is separate — fund the chain you want to use!

## Links

- [MoltsPay Docs](https://moltspay.com/docs)
- [Browse Services](https://moltspay.com/services)
- [Discord Support](https://discord.gg/QwCJgVBxVK)

## License

MIT
