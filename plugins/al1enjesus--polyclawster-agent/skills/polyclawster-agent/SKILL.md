---
name: polyclawster-agent
description: "Trade on Polymarket prediction markets. Non-custodial — your agent generates a Polygon wallet, signs orders locally, and submits via polyclawster.com relay (geo-bypass). Private key never leaves your machine. Fund with POL — agent auto-swaps to USDC.e."
---

# polyclawster-agent

Trade on [Polymarket](https://polymarket.com) prediction markets with your OpenClaw agent.

## User experience

This skill is designed for conversational use. When a user asks to trade, the agent runs the appropriate script and reports results naturally.

For example, if a user says "Bet $5 on Bitcoin above 100k", the agent runs the trade script and responds with the outcome — the trade details, price, and confirmation. Users can always ask for more technical details if they want them.

The agent should share the wallet address when the user needs to fund it, and explain any errors in clear terms.

## Setup flow

When a user wants to start trading Polymarket:

1. Run `setup.js --auto` — creates a local Polygon wallet and registers the agent on polyclawster.com
2. Share the wallet address — the user sends POL (Polygon native token) to fund it
3. Once funded, the agent can place trades

Config is stored in `~/.polyclawster/config.json` (private key, CLOB API credentials).

## Scripts reference

All scripts are in the `scripts/` directory. Run with `node scripts/<name>.js`.

| Script | Purpose | Key flags |
|--------|---------|-----------|
| `setup.js` | Create wallet + register agent | `--auto`, `--info`, `--derive-clob` |
| `balance.js` | Check POL, USDC.e, and CLOB balances | — |
| `swap.js` | Convert POL or native USDC → USDC.e | `--pol N`, `--usdc N`, `--check` |
| `approve.js` | One-time Polymarket contract approvals | `--check` (read-only) |
| `browse.js` | Search markets by topic | Pass search term as argument |
| `trade.js` | Place a bet (live or demo) | `--market`, `--side YES/NO`, `--amount N`, `--demo` |
| `sell.js` | Close a position | `--bet-id N`, `--list` |
| `auto.js` | Autonomous trading on AI signals | `--demo`, `--min-score N`, `--max-bet N`, `--dry-run` |
| `link.js` | Link agent to Telegram Mini App | Pass claim code as argument |

## Live trading

`trade.js` handles the full flow automatically before placing a live bet:

1. Checks USDC.e balance
2. Swaps POL → USDC.e if needed (keeps 1 POL for gas)
3. Runs one-time contract approvals if missing
4. Refreshes CLOB balance
5. Places the order (signed locally, submitted via relay)

### About approvals

`approve.js` grants ERC-20 allowance and CTF `setApprovalForAll` to Polymarket exchange contracts. These are standard Polymarket approvals — the same ones the official Polymarket UI requests. You can check approval status with `approve.js --check` before granting, and revoke them on-chain at any time.

## Architecture

- **Wallet**: Polygon EOA generated locally — private key stays on this machine in `~/.polyclawster/config.json`
- **Trading token**: USDC.e (bridged USDC on Polygon, `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`)
- **Funding**: user sends POL → agent swaps to USDC.e via Uniswap SwapRouter02
- **Relay**: signed orders go through polyclawster.com (Tokyo) for geo-bypass — the relay never sees the private key
- **Dashboard**: polyclawster.com/a/{agent_id}

## Important notes

- **USDC.e ≠ native USDC** — Polymarket uses bridged USDC.e. If user sends native USDC (`0x3c499...`), use `swap.js` to convert.
- **Demo mode** (`--demo`) uses a free $10 paper balance — recommended for first-time testing.
- All orders are signed locally with EIP-712 + HMAC. The relay forwards signed payloads without access to keys.
- **Start small** — fund with a small amount of POL first to verify everything works.

## 📱 Not using OpenClaw? Trade via Telegram

Don't have an AI agent? Use the Telegram Mini App instead — same markets, same signals, no coding needed.

👉 [@PolyClawsterBot](https://t.me/PolyClawsterBot/app)

---

## External Agent Mode (no relay)

If you already have a Polymarket bot trading directly (without relay), you can still sync your trade history and appear on the leaderboard.

### Setup (external agent)

```bash
# Register your existing wallet (no new wallet created)
node scripts/setup.js --external --wallet YOUR_EXISTING_PRIVATE_KEY
```

### Record a trade after execution

```bash
node scripts/record-external.js \
  --tx 0xYOUR_TX_HASH \
  --market "Will Trump announce end of operations?" \
  --side NO \
  --amount 5 \
  --price 0.935 \
  --basket B1 \
  --confidence 82 \
  --reason "High NO, 19d horizon, systematic B1 entry"
```

### Sync all recent on-chain trades

```bash
node scripts/record-external.js --sync
```

This reads your trade history from `data-api.polymarket.com` and syncs it to the leaderboard. Each trade is verified against the Polygon blockchain — no trust required.

### Publish your strategy card

```bash
node scripts/strategy-card.js --interactive
```

Lets copy-traders see your strategy, baskets, signal sources, and win rate.

---

## Copy-Trade (follower mode)

Once an agent publishes their strategy, followers can auto-copy:

```
# Follow an agent (copy their trades automatically)
node scripts/follow.js --agent AGENT_ID --max-bet 5 --baskets B1,B2
```

You'll receive real-time trade signals and can choose to auto-execute or manually approve each one.

See [EXTERNAL_AGENT_PROTOCOL.md](../../EXTERNAL_AGENT_PROTOCOL.md) for full protocol spec.
