# Inflynce Create Campaign — OpenClaw Skill

Create Inflynce Boost campaigns for **any link** — tweets, project websites, Farcaster casts, etc.

## What is Inflynce?

**Inflynce Marketing** (Inflynce protocol) lets anyone boost a link using USDC and reward real users based on measurable social influence (Mindshare). You set a budget, and eligible Farcaster users engage with your link to earn rewards. BOOST any link—tweets, websites, casts—to get visibility. Built on Base; Inflynce does not custody your funds.

## Prerequisites

1. **Platform fee**: Each campaign requires **0.25 USDC**. See [How to Pay 0.25 USDC](#how-to-pay-025-usdc).
2. **Budget**: Minimum budget is 5 USDC to launch. Agent can top up anytime (see [How to Top Up](#how-to-top-up))
3. **Config**: Set `GRAPHQL_URL` (e.g. `https://boost.inflynce.com/api/graphql`)

## Environment Variables

| Variable     | Required | Description                                                                 |
|-------------|----------|-----------------------------------------------------------------------------|
| `PRIVATE_KEY` | For pay_fee + top_up | Creator wallet private key (0x...). Required for `pay_fee.js` and `top_up.js`. Store securely; never commit. |
| `GRAPHQL_URL` | No      | Inflynce GraphQL endpoint. Default: `https://boost.inflynce.com/api/graphql` |

Copy `.env.example` to `.env` and fill in. Load before running: `export $(cat .env | xargs)` or use OpenClaw's secrets/vault.

## Installation

```bash
/skills install @inflynce/inflynce-create-campaign
```

## Usage

### From OpenClaw

Ask your agent to create a campaign, e.g.:
- "Create an Inflynce boost campaign for this tweet: https://x.com/..."
- "BOOST this project website: https://example.com with minimum budget $50 (top up later if needed)"
- "Start boosting this cast: https://warpcast.com/~/casts/0x..."

The agent will use the `run_script` tool to execute:

```bash
node scripts/create_campaign.js \
  --cast-url "https://warpcast.com/~/casts/0x..." \
  --payment-hash "0x<TX_HASH>" \
  --creator-wallet "0x..." \
  --budget "50"
```

### Manual / CLI

```bash
cd openclaw-skill/inflynce-create-campaign
npm install
GRAPHQL_URL=https://boost.inflynce.com/api/graphql node scripts/create_campaign.js \
  --cast-url "https://x.com/user/status/123" \
  --payment-hash "0x..." \
  --creator-wallet "0x..." \
  --budget "50"
```

### Arguments

| Argument        | Required | Description                                  |
|----------------|----------|----------------------------------------------|
| `--cast-url`   | Yes      | **Any https URL** — tweet, website, cast     |
| `--payment-hash` | Yes    | Tx hash of 0.25 USDC (required per campaign) |
| `--creator-wallet` | Yes  | Wallet that made the payment                 |
| `--budget`     | Yes      | Campaign budget in USDC (minimum 5 USDC). Top up via [boost.inflynce.com](https://boost.inflynce.com) (see below) |
| `--multiplier` | No       | Cost multiplier 1–10 (default 1)             |
| `--graphql-url` | No      | Override (default: GRAPHQL_URL env)          |
| `--dry-run`     | No      | Validate inputs only, no API call            |

## How to Pay 0.25 USDC

Each campaign requires a 0.25 USDC transfer to Inflynce on Base. Use the tx hash as `--payment-hash`.

### Agent (programmatic)

```bash
node scripts/pay_fee.js
# or: PRIVATE_KEY=0x... node scripts/pay_fee.js
```

Sends `USDC.transfer(0xA61529732F4E71ef1586252dDC97202Ce198A38A, 0.25)` on Base. Copy the returned `txHash` for create_campaign.js.

### Human (wallet)

Send **exactly 0.25 USDC** to `0xA61529732F4E71ef1586252dDC97202Ce198A38A` on Base. Use any wallet (MetaMask, Coinbase Wallet, etc.).

## How to Top Up

### Agent (programmatic)

If the agent has the creator wallet's private key:

```bash
node scripts/top_up.js --amount 50
# or: PRIVATE_KEY=0x... node scripts/top_up.js --amount 50
```

This sends `USDC.approve(BOOSTS_CONTRACT, amount)` on Base. Minimum 5 USDC. Requires viem (included in package.json).

| Argument       | Required | Description                        |
|----------------|----------|------------------------------------|
| `--amount`     | Yes      | Amount in USDC (minimum 5)         |
| `--private-key`| No       | Wallet private key (or `PRIVATE_KEY` env) |

### Human (web UI)

1. Go to [boost.inflynce.com](https://boost.inflynce.com)
2. Connect the creator wallet
3. Click **Top Up Your Spending** or **Approve USDC**
4. Enter amount (minimum 5 USDC), confirm in wallet

## How to Test

### 1. Validate inputs (no API call, no real payment)

```bash
node scripts/create_campaign.js --dry-run \
  --cast-url "https://x.com/user/status/123" \
  --payment-hash "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef" \
  --creator-wallet "0x0000000000000000000000000000000000000001" \
  --budget "10"
```

Prints the parsed input. Use any 64-char hex for payment-hash when dry-running.

### 2. Script error handling

```bash
node scripts/create_campaign.js
# → "Required: --cast-url, --payment-hash, --creator-wallet"

node scripts/create_campaign.js --cast-url "https://x.com/1" --payment-hash "0x" --creator-wallet "0x0" --budget "1"
# → "Minimum budget is 5 USDC"

node scripts/pay_fee.js
# → "Private key required"

node scripts/top_up.js --amount 2
# → "Amount must be at least 5 USDC"
```

### 3. Full end-to-end (real USDC on Base)

1. Ensure wallet has USDC on Base (bridge or buy from an exchange)
2. `cp .env.example .env` and set `PRIVATE_KEY`
3. Pay fee: `node scripts/pay_fee.js` → copy `txHash`
4. Create campaign: `GRAPHQL_URL=https://boost.inflynce.com/api/graphql node scripts/create_campaign.js --cast-url "https://x.com/user/1" --payment-hash "<txHash>" --creator-wallet "<your_address>" --budget "10"`

### 4. Testing pay_fee and top_up (real Base mainnet)

Both scripts send real transactions. No dry-run; no testnet support.

**Pay 0.25 USDC fee:**

1. Wallet needs: **0.25 USDC** + enough Base ETH for gas (~0.0001 ETH)
2. Get USDC on Base: bridge from Ethereum, or withdraw from Coinbase/CEX
3. Set `PRIVATE_KEY` in `.env`, then: `node scripts/pay_fee.js`
4. Copy the printed `txHash` for create_campaign `--payment-hash`

**Top up (approve USDC for campaigns):**

1. Wallet needs: Base ETH for gas only (approve does not transfer USDC)
2. Run: `node scripts/top_up.js --amount 5` (min 5 USDC)
3. This sets `USDC.approve(BOOSTS_CONTRACT, amount)` — the actual spend happens when the campaign rewards users

## Publishing to ClawHub

ClawHub accepts **text files only** (no node_modules, LICENSE, \*.map). Create a clean folder first:

```bash
npm run prepare:publish
```

Then either:

**CLI:**
```bash
clawhub login
clawhub publish .clawhub-publish --version 1.0.0
```

**Web:** Go to [clawhub.ai/upload](https://clawhub.ai/upload), choose the `.clawhub-publish` folder (not the root).

Use semantic versioning (e.g. `1.0.1`, `1.1.0`) when publishing updates. Requires a ClawHub developer account at [clawhub.ai](https://clawhub.ai).


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

**ClawHub publish: "acceptLicenseTerms: invalid value"?**  
Accept the developer/publisher license terms on [clawhub.ai](https://clawhub.ai) (sign in → settings or developer section), then try again.

**ClawHub publish: GitHub API rate limit exceeded?**  
Set `GITHUB_TOKEN` (GitHub Personal Access Token) when publishing: `GITHUB_TOKEN=ghp_... clawhub publish . --version 1.0.0`.

**ClawHub publish: version must be valid semver?**  
Pass version explicitly: `clawhub publish . --version 1.0.0`. Use semver (e.g. `1.0.1`, `1.1.0`) for updates.
