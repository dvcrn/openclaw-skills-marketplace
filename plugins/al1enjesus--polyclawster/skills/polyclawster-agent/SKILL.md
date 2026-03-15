---
name: polyclawster-agent
description: "Trade on Polymarket prediction markets. Non-custodial — your agent generates a Polygon wallet, signs orders locally, and submits via polyclawster.com relay (geo-bypass). Private key never leaves your machine. Fund with POL — agent auto-swaps to USDC.e."
---

# polyclawster-agent

Trade on [Polymarket](https://polymarket.com) prediction markets with your OpenClaw agent.

## Quick Start

```
"Set me up to trade Polymarket"
→ runs: node scripts/setup.js --auto
→ shows wallet address — send POL to fund it
```

## How It Works

1. **Setup** → generates Polygon wallet + registers agent on polyclawster.com
2. **Fund** → send POL (Polygon native token) to agent wallet address
3. **Trade** → agent auto-swaps POL → USDC.e, approves contracts, places orders

All signing happens locally. Private key never leaves the machine.
Orders go through polyclawster.com relay (Tokyo) for Polymarket geo-bypass.

## Scripts

### `setup.js --auto`
Generate wallet, register agent, derive CLOB API credentials.
```bash
node scripts/setup.js --auto
```

### `balance.js`
Check all balances: POL, USDC.e, CLOB available.
```bash
node scripts/balance.js
```

### `swap.js`
Convert POL or native USDC to USDC.e (Polymarket's trading token).
```bash
node scripts/swap.js              # auto-detect and swap
node scripts/swap.js --pol 10     # swap 10 POL → USDC.e
node scripts/swap.js --check      # check balances only
```

### `approve.js`
One-time on-chain approvals for Polymarket contracts.
Called automatically by `trade.js` when needed.
```bash
node scripts/approve.js           # approve all
node scripts/approve.js --check   # check status only
```

### `browse.js`
Search Polymarket markets.
```bash
node scripts/browse.js "bitcoin"
node scripts/browse.js "politics"
```

### `trade.js`
Place a trade. Live by default — add `--demo` for paper trading.
Before live trades, auto-checks: USDC.e balance, swaps if needed, approves if needed.
```bash
node scripts/trade.js --market "bitcoin-100k" --side YES --amount 5
node scripts/trade.js --market "trump-win" --side NO --amount 2 --demo
```

### `sell.js`
Close/sell an existing position.
```bash
node scripts/sell.js --bet-id 123
```

## Architecture

```
Agent (your machine)          polyclawster.com           Polymarket
─────────────────           ─────────────────          ──────────────
Private key (local)    →    /api/clob-relay (Tokyo)  → CLOB order book
Signs orders locally        Geo-bypass proxy            Matches + settles
                            Records in Supabase
                            Leaderboard / dashboard
```

- **Wallet**: Polygon EOA, generated locally
- **Trading token**: USDC.e (bridged USDC on Polygon) — `0x2791Bca1...`
- **Funding**: send POL → agent swaps to USDC.e via Uniswap
- **Relay**: polyclawster.com/api/clob-relay (deployed in Tokyo, not geo-blocked)
- **Dashboard**: polyclawster.com/a/{wallet_address}

## Funding

Send **POL** (Polygon native token) to your agent's wallet address.
The agent automatically converts POL → USDC.e when placing live trades.

You can also send USDC.e directly if you prefer — no swap needed.

**Do NOT send native USDC** — Polymarket uses USDC.e (bridged). If you accidentally send native USDC, run `node scripts/swap.js` to convert it.
