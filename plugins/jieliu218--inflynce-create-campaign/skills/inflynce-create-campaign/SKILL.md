---
name: inflynce-create-campaign
description: "Create Inflynce Boost campaigns via postBoostWeb API. Inflynce Marketing lets anyone boost a link (tweet, website, cast) with USDC and reward real Farcaster users by Mindshare. Each campaign requires 0.25 USDC. Use when creating a boost campaign or promoting content. Requires prior 0.25 USDC payment on Base as proof."
homepage: https://boost.inflynce.com
---

# Inflynce Create Campaign

## What is Inflynce?

**Inflynce Marketing** (Inflynce protocol) lets anyone boost a link using USDC and reward real users based on measurable social influence (Mindshare). You set a budget, and eligible Farcaster users engage with your link to earn rewards. You can BOOST any link—tweets, project websites, Farcaster casts—to get visibility. Built on Base; Inflynce does not custody your funds.

This skill creates boost campaigns on [Inflynce](https://boost.inflynce.com) via the `postBoostWeb` GraphQL mutation.

## Prerequisites

1. **Platform fee**: Each campaign requires **0.25 USDC**. The creator wallet MUST have already sent exactly 0.25 USDC to Inflynce on Base. See "How to Pay 0.25 USDC" below.
2. **Config**: Set `GRAPHQL_URL` (e.g. `https://boost.inflynce.com/api/graphql`) and, for programmatic pay/top-up, `PRIVATE_KEY` (creator wallet). See `.env.example`.

## Security & Verification

**Treat `PRIVATE_KEY` as highly sensitive.** Only supply it if you understand it will sign real Base transactions. Prefer doing the 0.25 USDC payment and top-ups manually via [boost.inflynce.com](https://boost.inflynce.com) instead of storing a private key in the agent.

**Do not override `GRAPHQL_URL`** unless you trust the target endpoint. `create_campaign` sends campaign inputs (castUrl, paymentHash, creatorWallet) to this URL; a malicious endpoint could collect them.

**Hardcoded addresses (verify at [boost.inflynce.com](https://boost.inflynce.com) or Inflynce docs):**
| Purpose | Address | Chain |
|---------|---------|-------|
| 0.25 USDC fee recipient | `0xA61529732F4E71ef1586252dDC97202Ce198A38A` | Base |
| USDC contract | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | Base (Circle) |
| Boosts contract (approve spender) | `0x6e6A6128bB0c175989066eb0e2bf54F06688207b` | Base |

## Usage

Run the create script:

```bash
npm install && node scripts/create_campaign.js \
  --cast-url "https://..." \
  --payment-hash "0x<TX_HASH_OF_0.25_USDC_PAYMENT>" \
  --creator-wallet "0x..." \
  --budget "50" \
  [--multiplier 1]
```

Or use `run_script` with the script path. Required args:
- `cast-url`: **Any https URL** — tweet, project website, Farcaster cast, etc.
- `payment-hash`: On-chain tx hash proving 0.25 USDC payment
- `creator-wallet`: Ethereum address (will be validated against payment sender)
- `budget`: Campaign budget in USDC (minimum 5 USDC). Top up later — see "How to Top Up" below

## Supported URLs

- **Tweets**: `https://x.com/...` or `https://twitter.com/...`
- **Project websites**: `https://example.com`
- **Farcaster casts**: `https://warpcast.com/~/casts/0x...`
- **Any https link**

## API Reference

- **Endpoint**: `POST ${GRAPHQL_URL}` (GraphQL mutation)
- **Mutation**: `postBoostWeb(input: PostBoostWebInput!)`
- **Auth**: None (payment hash proves authorization)
- **Returns**: `{ id, boostStatus, creatorWallet }`
- **appType**: This skill sends `appType: 2` (Agent). Web UI uses `appType: 1`. Filter `mindshare_boosts` by `app_type = 2` to find agent-created campaigns.

## Flow

1. **Top up** — Approve USDC for the boosts contract (min 5 USDC). See "How to Top Up" below.
2. **Pay 0.25 USDC** — Platform fee per campaign. See "How to Pay 0.25 USDC" below.
3. Run this skill with the payment tx hash; campaign is created and returns boost ID.
4. Top up again anytime to increase budget.

## How to Pay 0.25 USDC

Each campaign requires a 0.25 USDC transfer to Inflynce on Base. The tx hash is the proof.

### Agent (programmatic)

```bash
node scripts/pay_fee.js
# or: PRIVATE_KEY=0x... node scripts/pay_fee.js
```

Sends `USDC.transfer(0xA61529732F4E71ef1586252dDC97202Ce198A38A, 0.25)` on Base. Use the returned `txHash` as `--payment-hash` in create_campaign.js.

### Human (wallet)

1. Ensure wallet has USDC on Base
2. Send **exactly 0.25 USDC** to `0xA61529732F4E71ef1586252dDC97202Ce198A38A`
3. Use the transaction hash as `--payment-hash`

## How to Top Up

### Option A: Agent (programmatic)

If the agent has the creator wallet's private key (e.g. in `PRIVATE_KEY` env or vault):

```bash
node scripts/top_up.js --amount 50
# or: PRIVATE_KEY=0x... node scripts/top_up.js --amount 50
```

This sends an ERC-20 approve tx: `USDC.approve(BOOSTS_CONTRACT, amount)` on Base. Minimum 5 USDC. The agent's wallet must hold USDC on Base.

### Option B: Human (web UI)

1. Go to [boost.inflynce.com](https://boost.inflynce.com)
2. Connect the creator wallet
3. Click **Top Up Your Spending** or **Approve USDC**
4. Enter amount (minimum 5 USDC), confirm in wallet

## FAQ

**What URL formats are supported?**  
Any `https://` URL: tweets (`x.com`, `twitter.com`), project websites, Farcaster casts (`warpcast.com`, `base.app`, `farcaster.xyz`). For Farcaster casts, the cast hash is extracted from the path. For other URLs, we use `keccak256(URL)`.

**What is the minimum budget?**  
5 USDC. You can top up later via `top_up.js` or the web UI at [boost.inflynce.com](https://boost.inflynce.com).

**Does Inflynce custody my funds?**  
No. Inflynce does not custody funds. You approve USDC to the boosts contract; rewards are paid directly from your wallet when users engage.

**How do I get USDC on Base?**  
Bridge from Ethereum mainnet, or withdraw from an exchange (e.g. Coinbase) that supports Base. You need USDC for the fee + budget, and Base ETH for gas.

**Can I reuse a payment hash for multiple campaigns?**  
No. Each campaign requires a separate 0.25 USDC payment. Run `pay_fee.js` (or send 0.25 USDC manually) once per campaign.

**How do I know if a campaign was created by an agent?**  
This skill sends `appType: 2`. Filter `mindshare_boosts` by `app_type = 2` to find agent-created campaigns. Web UI uses `appType: 1`.

**What is mindshare / minMindshare?**  
Mindshare is Inflynce’s measure of a user’s social influence. `minMindshare` is fixed at 0.003 for this skill (not configurable).

**What is the cost multiplier?**  
Optional `--multiplier` (1–10, default 1) scales reward costs. Higher multiplier = larger rewards per engagement.

**How do I test without spending real USDC?**  
Use `--dry-run` on create_campaign: `node scripts/create_campaign.js --dry-run --cast-url "https://..." --payment-hash "0x<64_hex>" --creator-wallet "0x..." --budget "10"`. No API call, no payment. Use any valid 64-char hex for payment-hash when dry-running.

**What chain is used?**  
Base mainnet only. No testnet support for pay_fee or top_up.
