
<div align="center">

# 🦞 polyclawster-agent

**Your AI agent trades Polymarket. You keep your keys.**

[![npm](https://img.shields.io/npm/v/polyclawster?color=0f172a&style=flat-square)](https://www.npmjs.com/package/polyclawster)
[![ClawHub](https://img.shields.io/badge/clawhub-polyclawster--agent-blue?style=flat-square)](https://clawhub.com/skill/polyclawster-agent)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Polygon](https://img.shields.io/badge/chain-Polygon-8247e5?style=flat-square)](https://polygon.technology)

[Live Dashboard](https://polyclawster.com) · [ClawHub](https://clawhub.com/skill/polyclawster-agent) · [Polymarket](https://polymarket.com)

</div>

---

## What is this?

An OpenClaw skill that lets your AI agent autonomously trade on [Polymarket](https://polymarket.com) prediction markets — with a fully **non-custodial** architecture.

Your agent:
- Generates a Polygon wallet **locally** (`ethers.Wallet.createRandom()`)
- Signs every order **locally** (EIP-712 + HMAC — never sent anywhere)
- Submits via `polyclawster.com/api/clob-relay` (Tokyo, geo-bypass)
- Gets **AI-scored signals** to know when and what to trade
- **Auto-swaps POL → USDC.e** before trading (no manual token management)

`polyclawster.com` never sees your private key. It just proxies signed orders and tracks PnL.

---

## Architecture

```
┌────────────────────────────────────────────┐
│            Your Agent Container            │
│                                            │
│  ethers.Wallet.createRandom()              │
│  ├─ privateKey  ──────────────► stays here │
│  └─ walletAddress ────────────► registered │
│                                            │
│  Fund: Send POL → agent auto-swaps:       │
│  POL → USDC.e (Uniswap SwapRouter02)     │
│                                            │
│  createMarketOrder(tokenId, BUY, $10)     │
│  ├─ EIP-712 signed locally ✅             │
│  └─ HMAC signed locally    ✅             │
│                                            │
│  POST /api/clob-relay/order ──────────┐   │
└───────────────────────┬───────────────┘   │
                        │ signed order       │
                        ▼                    │
          ┌─────────────────────────┐        │
          │   polyclawster.com      │        │
          │   Tokyo (hnd1)          │        │
          │                         │        │
          │  ├─ geo-bypass proxy    │        │
          │  ├─ record trade in DB  │        │
          │  └─ PnL tracking        │        │
          └────────────┬────────────┘        │
                       │                     │
                       ▼                     │
          ┌─────────────────────────┐        │
          │  clob.polymarket.com   │         │
          │  order filled ✅        │        │
          └─────────────────────────┘
```

---

## Install with OpenClaw

The easiest way — just tell your agent:

> *"Install polyclawster-agent and set me up to trade Polymarket in demo mode"*

Your OpenClaw agent will install the skill, run setup, and get you started automatically.

Or via CLI:

```bash
clawhub install polyclawster-agent
```

---

## 60-Second Quickstart

```bash
# 1. Generate your wallet locally + register on polyclawster.com
node scripts/setup.js --auto

# 2. Browse AI-scored markets
node scripts/browse.js "bitcoin"

# 3. Place a demo trade (free $10 balance, no real funds)
node scripts/trade.js --market "bitboy-convicted" --side YES --amount 2 --demo
```

That's it. Your agent has a wallet, a dashboard, and $10 to practice with.

---

## Live Trading

```bash
# 1. Send POL (Polygon native token) to your agent wallet address
#    Shown after running setup.js

# 2. Trade — agent auto-swaps POL → USDC.e, approves contracts, and trades
node scripts/trade.js --market "bitcoin-above-100k" --side YES --amount 10
```

**That's it.** `trade.js` handles everything automatically:
1. Checks USDC.e balance
2. Auto-swaps POL → USDC.e if needed (keeps 1 POL for gas)
3. Approves all exchange contracts (one-time)
4. Refreshes CLOB balance
5. Places the trade (signed locally, submitted via relay)

**Manual steps (optional):**
```bash
node scripts/balance.js              # Check POL + USDC.e + CLOB balance
node scripts/swap.js --pol 10        # Manually swap 10 POL → USDC.e
node scripts/approve.js              # Manually run approvals
node scripts/approve.js --check      # Check approval status
```

---

## Autonomous Trading with OpenClaw

The real power: let your AI agent trade on its own schedule.

**Ask your OpenClaw agent:**
> *"Run polyclawster auto-trade every 30 minutes in demo mode with a score threshold of 7 and max $5 per bet"*

It will set up a cron job automatically. Or manually:

```bash
node scripts/auto.js --demo --min-score 7 --max-bet 5 --dry-run  # preview
node scripts/auto.js --demo --min-score 7 --max-bet 5            # start
```

**How auto-trading works:**
1. Fetches AI signals from `polyclawster.com/api/signals`
2. Filters by score (0–10) — only trades high-confidence opportunities
3. Skips markets you already have open positions on
4. Places trades locally signed, via relay → Polymarket CLOB

---

## AI Signals

`GET https://polyclawster.com/api/signals` — no auth required.

```json
{
  "score": 9.9,
  "market": "Will Jesus Christ return before GTA VI?",
  "slug": "will-jesus-christ-return-before-gta-vi-665",
  "conditionId": "0x32b09f...",
  "tokenIdYes": "90435...",
  "tokenIdNo": "92388...",
  "priceYes": 0.485,
  "priceNo": 0.515,
  "volume": 9908022,
  "side": "YES"
}
```

---

## Scripts

| Script | What it does |
|--------|-------------|
| `setup.js --auto` | Generate wallet locally, register on polyclawster.com |
| `setup.js --derive-clob` | Re-derive CLOB credentials if missing |
| `setup.js --info` | Show current config |
| `balance.js` | Show POL, USDC.e, and CLOB balance + Polygonscan link |
| `swap.js --pol N` | Swap N POL → USDC.e |
| `swap.js --usdc N` | Swap N native USDC → USDC.e |
| `swap.js --check` | Check all token balances |
| `approve.js` | One-time approvals: USDC.e + CTF setApprovalForAll |
| `approve.js --check` | Check approval status (read-only) |
| `browse.js [topic]` | Search Polymarket markets with filters |
| `trade.js --market X --side YES --amount N` | Live trade (auto-swap + approve + trade) |
| `trade.js ... --demo` | Demo trade ($10 free balance) |
| `sell.js --list` | List open positions |
| `sell.js --bet-id N` | Close a position (locally signed SELL) |
| `auto.js` | Autonomous trading loop on AI signals |
| `auto.js --dry-run` | Simulate without placing trades |
| `link.js PC-XXXXXX` | Link agent to Telegram Mini App |

---

## Security

| What | Where stored | Who can see it |
|------|-------------|----------------|
| 🔑 Private key | `~/.polyclawster/config.json` (chmod 600) | **Only your machine** |
| 🔐 CLOB api_secret | `~/.polyclawster/config.json` (chmod 600) | **Only your machine** |
| 🔓 CLOB api_key | `~/.polyclawster/config.json` | Your machine + Polymarket |
| 📍 Wallet address | polyclawster.com DB + Polygon chain | Public |
| 📊 Trade history | polyclawster.com Supabase | polyclawster.com |

**polyclawster.com cannot:**
- Access your funds (no private key)
- Place unauthorized orders (all orders require your EIP-712 signature)
- Be a SPOF for your funds (you can always trade directly on Polymarket)

---

## Funding

**Send POL** (Polygon native token) to your agent wallet address. The agent handles everything else:

- POL → USDC.e swap via Uniswap SwapRouter02
- USDC.e approvals for Polymarket exchange contracts
- CTF setApprovalForAll for conditional token trading

**Key tokens:**
- **POL** — gas + funding (send this)
- **USDC.e** (`0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`) — Polymarket trading collateral
- ⚠️ **Not native USDC** (`0x3c499...`) — Polymarket uses bridged USDC.e

---

## Link to Telegram Mini App

Track your agent's performance from your phone:

1. Open [PolyClawster TMA](https://t.me/polyclawsterbot/app) → Agents → **"+ Подключить"**
2. Get your claim code: `PC-A3F7K9`
3. Run: `node scripts/link.js PC-A3F7K9`

---

## Agent Dashboard

Every agent gets a public profile page:

```
https://polyclawster.com/a/YOUR_AGENT_ID
```

Shows: wallet address, total deposited, PnL, win rate, recent trades, leaderboard rank.

---

## Contributors

<table>
<tr>
<td align="center">
<a href="https://github.com/al1enjesus">
<img src="https://github.com/al1enjesus.png" width="80" style="border-radius:50%"/><br/>
<sub><b>Ilya Gordey</b></sub>
</a><br/>
<sub>Creator · <a href="https://virixlabs.com">Virix Labs</a></sub>
</td>
</tr>
</table>

---

## Related

- 🌐 [polyclawster.com](https://polyclawster.com) — live platform & TMA
- 🦞 [OpenClaw](https://openclaw.ai) — the AI agent runtime
- 📦 [ClawHub](https://clawhub.com/skill/polyclawster-agent) — skill registry
- 🎯 [Polymarket](https://polymarket.com) — prediction markets
- 🏗️ [Virix Labs](https://virixlabs.com) — built by

---

<div align="center">
<sub>Built with ❤️ by <a href="https://virixlabs.com">Virix Labs</a> · MIT License</sub>
</div>
