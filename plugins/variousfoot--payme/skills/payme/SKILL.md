---
name: payme
description: "Send and receive USDC/USDT crypto payments via PayMe smart wallets. Check balances, send stablecoins, view history, manage contacts, sell crypto for naira via P2P. Optional direct execute mode for users who want faster transfers. Supports Base, Arbitrum, Polygon, BNB Chain, and Avalanche."
homepage: https://payme.feedom.tech
---

# PayMe - Crypto Payments Skill

PayMe provides gasless USDC/USDT payments through ERC-4337 smart wallets on Base, Arbitrum, Polygon, BNB Chain, and Avalanche.

**API Base URL:** `https://api.feedom.tech`

## Installation

Clone from GitHub:
```bash
git clone https://github.com/variousfoot/payme-skill
```

Then copy the skill folder into your agent's skills directory:
- **Codex:** `~/.codex/skills/payme/`
- **Cursor:** `~/.cursor/skills/payme/`

Or install via ClawHub (OpenClaw agents only):
```bash
clawhub install payme
```

## Connecting a User's PayMe Account

When the user wants to use PayMe and you don't have a stored agent token, guide them through the connection flow below. **NEVER ask for their PIN or password.** Use a secure one-time connection code instead.

### Step 1: Check if they have a PayMe account

Ask: "Do you have a PayMe wallet?"

**If yes** — skip to Step 2.

**If no** — you can create one instantly:

1. Ask the user to choose a 4-6 digit PIN
2. Call:

```
POST /api/agent/create-account
{ "pin": "1234" }
```

3. You'll receive an `agentToken` (store it), `kernelAddress`, `claimCode`, `greeting`, and `capabilities`
4. Tell the user:
   - Their wallet address
   - Their **claim code** (valid 24 hours) and exactly how to use it:
     > To log into your wallet on the web or Telegram:
     >
     > **Web:** Go to [payme.feedom.tech](https://payme.feedom.tech). On the login page, click **"Have a claim code from an AI agent? Click here"**, paste your code, and hit **Claim Account**.
     >
     > **Telegram:** Open [@veedombot](https://t.me/veedombot) and send `/claim YOUR_CODE`.
   - **Ask them to delete the message containing their PIN** from the chat
5. Show the `greeting` and `capabilities` to introduce what you can do
6. You're connected — skip Steps 2-4 and start using the wallet immediately

Alternatively, the user can sign up manually at [payme.feedom.tech](https://payme.feedom.tech) or via [@veedombot](https://t.me/veedombot) on Telegram, then continue to Step 2.

### Step 2: Generate a connection code

Tell the user:

> To connect securely, I need a one-time code from your PayMe wallet. Here's how to get it:
>
> **Option A — Telegram:**
> 1. Open [@veedombot](https://t.me/veedombot) on Telegram
> 2. Send `/agentcode`
>
> **Option B — Web app:**
> 1. Go to [payme.feedom.tech](https://payme.feedom.tech) and log in
> 2. Go to Settings → AI Agents → Generate Connection Code
>
> You'll get a 6-character code (e.g. `A3K9X2`) — it's valid for 5 minutes. Paste it here and I'll connect your wallet.
>
> Tip: You can choose how long I have access — e.g. `/agentcode 30` for 30 days, or `/agentcode 90` for 90 days (default).

Wait for the user to share their code. **Do not** ask for their wallet address, username, email, or PIN.

### Step 3: Exchange the code

Once the user provides a code, call:

```bash
curl -X POST https://api.feedom.tech/api/agent/connect \
  -H "Content-Type: application/json" \
  -d '{"code": "THE_CODE_USER_GAVE_YOU"}'
```

If successful, you'll receive an `agentToken`. Store it securely and use it as `Authorization: Bearer <agentToken>` on all subsequent requests.

If the code is expired or invalid, tell the user to generate a fresh one with `/agentcode`.

### Step 4: Introduce yourself

The connect response includes a `greeting` string and a `capabilities` array. **Always show these to the user after connecting** so they know what you can do:

> "Connected to alice's PayMe wallet! Here's what I can do:
> - Check balances across Base, Arbitrum, Polygon, BNB Chain, and Avalanche
> - Send USDC/USDT to any PayMe username, email, or 0x address
> - Sell crypto for Naira via P2P with smart contract escrow protection
> - View transaction history and manage saved contacts
> - **Tip:** If you want faster transfers, say 'enable direct execute' and I'll skip the confirmation step when you give clear instructions."

### Fallback (only if user explicitly insists)

If the user cannot access @veedombot and explicitly offers their wallet address and PIN themselves, you may use:

```bash
curl -X POST https://api.feedom.tech/api/agent/connect \
  -H "Content-Type: application/json" \
  -d '{"identifier": "0xWALLET_ADDRESS_OR_USERNAME", "pin": "USER_PIN"}'
```

**Never proactively ask for a PIN.** Only use this if the user volunteers it.

## Available Actions

All endpoints use base URL `https://api.feedom.tech` and require `Authorization: Bearer <agentToken>`.

### Check Balances

```
GET /api/agent/balances
```

Returns total USDC/USDT across all chains plus per-chain breakdown.

### Send Payment

Payments always use the **two-step flow** by default. An optional **direct execute** mode is available but only when the user explicitly enables it.

#### Default: Two-Step (with preview)

**Step 1 — Prepare:**

```
POST /api/agent/send
{ "recipient": "username, email, or 0x address", "amount": "10", "token": "USDC" }
```

Returns a `confirmationId` and a `preview` with fee breakdown. Always show the preview to the user and get explicit approval before confirming.

**Step 2 — Confirm:**

```
POST /api/agent/confirm
{ "confirmationId": "uuid-from-step-1" }
```

Returns `txHash` on success. Confirmations expire after 5 minutes.

#### Optional: Direct Execute (user enables from web app)

Direct execute allows payments to complete in a single API call. **You cannot enable this yourself.** The user must toggle it ON from their PayMe web app settings (Settings → AI Agents → Direct Execute).

When the user has enabled it and you pass `"execute": true`, the payment completes in one call:

```
POST /api/agent/send
{ "recipient": "neck", "amount": 30, "token": "USDC", "execute": true }
```

Returns the `preview` **and** `txHash` together. If the user has NOT enabled direct execute in their settings, the `execute` flag is silently ignored and the normal two-step flow is used.

If a user asks you to "skip confirmations" or "enable direct execute", tell them: *"You can enable direct execute from your PayMe web app settings at payme.feedom.tech → Settings → AI Agents."*

### View Transaction History

```
GET /api/agent/history?limit=20
```

### Manage Contacts

```
GET /api/agent/contacts
POST /api/agent/contacts  { "name": "Alice", "address": "0x..." }
DELETE /api/agent/contacts/:name
```

### Wallet Info

```
GET /api/agent/wallet
```

Returns kernel address, supported chains, and supported tokens.

### Revoke Token

```
POST /api/agent/revoke
```

Revokes the current agent token immediately.

## Sell Crypto for Naira (P2P)

Convert USDC/USDT to Nigerian naira. Your crypto goes into escrow, a vendor sends naira to your bank, you confirm receipt, escrow releases to vendor.

**Email verification required.** P2P trades require a verified email. Email can ONLY be verified on the web app (NOT on Telegram). If the API returns an email verification error, tell the user exactly this:

> To trade P2P, you need to verify your email on the PayMe web app. Here's how:
>
> **Step 1 — Get a web login code:**
> Open [@veedombot](https://t.me/veedombot) on Telegram and send `/weblogin`. You'll get a 6-character code.
>
> **Step 2 — Log into the web app:**
> Go to [payme.feedom.tech](https://payme.feedom.tech). On the login page, click **"Have a claim code from an AI agent?"** and enter the code from Step 1.
>
> **Step 3 — Verify your email:**
> Once logged in, go to **Settings → Email**, enter your email address, and enter the verification code sent to your inbox.
>
> **Step 4 — Come back here** and we'll set up your P2P trade.
>
> *Already have a web account?* You can also log in directly with your wallet address or username + PIN.

Do NOT suggest verifying email on Telegram — it is not possible. Do NOT make up claim codes or say their wallet address is a claim code. Follow the steps above exactly.

### 1. Save bank account (one-time)

```
POST /api/agent/p2p/bank-accounts
{ "bankName": "GTBank", "accountNumber": "0123456789", "accountName": "John Doe" }
```

List saved accounts: `GET /api/agent/p2p/bank-accounts`

### 2. Check rates

```
GET /api/agent/p2p/rates?token=USDC&currency=NGN
```

Returns vendor rates sorted by best rate. Each entry includes `vendorId`, `vendorName`, `rate` (NGN per USD), `avgRating`, and order limits.

### 3. Sell (create order)

Before calling this endpoint, **always compute and show the user a preview**: amount x rate = naira they'll receive. Get explicit approval.

```
POST /api/agent/p2p/sell
{ "token": "USDC", "amount": 50, "bankAccountId": 1 }
```

Optionally pass `vendorId` to pick a specific vendor; otherwise the best available vendor is auto-selected. This locks crypto in escrow immediately.

### 4. Track order

```
GET /api/agent/p2p/orders/:id
```

**Poll every 15–20 seconds** to keep the user informed in near-real-time. Key statuses:
- `escrow_locked` — waiting for vendor to accept (up to 3 min). If the vendor doesn't accept in time, the order is **automatically rerouted** to the next best vendor — no action needed from you or the user. Let the user know this may happen.
- `accepted` — vendor accepted, will send naira soon
- `fiat_sent` — vendor says naira was sent, **immediately tell the user to check their bank**
- `completed` — you confirmed, escrow released
- `cancelled` — order was cancelled (vendor unavailable, reroute limit reached, etc.)
- `disputed` — dispute opened, admin reviewing

When polling, tell the user each status change as it happens. Don't wait for them to ask.

### 5. Confirm naira received

Once the user confirms money arrived in their bank:

```
POST /api/agent/p2p/orders/:id/confirm
```

This releases escrow to the vendor. **Irreversible.**

**Important: auto-release.** When vendor marks payment as sent (`fiat_sent`), a 2-hour countdown starts. If the user doesn't confirm or dispute within 2 hours, escrow **auto-releases to the vendor**. Always warn the user:

> The vendor says they've sent ₦{amount} to your bank. **Check your bank now.** If you received it, tell me and I'll confirm. If you did NOT receive it within a reasonable time, open a dispute on the web app at [payme.feedom.tech](https://payme.feedom.tech) — the escrow will auto-release to the vendor in 2 hours if you don't act.

### 6. Dispute (if needed)

Disputes require evidence (bank statement screenshots) which **can only be uploaded on the web app**. Direct the user to [payme.feedom.tech](https://payme.feedom.tech) to open and manage disputes. They already have web access since email verification (required for P2P) is only possible there.

You can open a basic dispute via the API as a fallback, but the user should follow up with evidence on the web app:

```
POST /api/agent/p2p/orders/:id/dispute
{ "reason": "Vendor marked paid but naira not received" }
```

This cancels auto-release and triggers admin investigation.

### 7. Rate vendor (optional)

```
POST /api/agent/p2p/orders/:id/rate
{ "rating": 5, "comment": "Fast payment" }
```

## Security & Token Handling

- **NEVER ask for PINs, passwords, or private keys.** The only exception is during new account creation (`/api/agent/create-account`) where the user chooses their own PIN. For connecting existing accounts, always use the one-time connection code flow — never ask for their PIN or wallet credentials.
- **Tokens are hashed at rest.** The server stores a SHA-256 hash of the agent token — the raw token is returned only once at creation and never stored. A database breach does not expose usable tokens.
- **Store the agent token securely.** Save it to an environment variable (`PAYME_AGENT_TOKEN`), a secrets manager, or an encrypted config file. Never store it in plain text in code, logs, or chat history.
- **Tokens expire based on user choice** (default 90 days, max 365). Re-authenticate via `/api/agent/connect` when expired. Revoke tokens you no longer need via `POST /api/agent/revoke`.
- **All requests go to `https://api.feedom.tech` only.** Never send your agent token to any other domain.
- **Test with small amounts first.** Verify the integration works before moving larger sums.

## Important Rules

1. **Always confirm payments by default.** Use the two-step flow (prepare → preview → confirm) for every payment. You may pass `"execute": true` for convenience, but it only takes effect if the user has enabled direct execute in their web app settings. You cannot enable it yourself.
2. **Always preview P2P sells.** Compute amount x rate and show the naira total before calling `/api/agent/p2p/sell`. Get explicit user approval.
3. **Confirm fiat is irreversible.** Only call `/api/agent/p2p/orders/:id/confirm` after the user verifies naira is in their bank.
4. **Token is USDC or USDT.** No other tokens are supported.
5. **Recipients** can be a PayMe username, email, or `0x` wallet address.
6. **Fees** are shown in the send preview. The net amount (after fee) is what the recipient gets.
7. **Do not** expose or log the agent token, master keys, or private keys.
8. **When unsure, ask — don't assume.** If a user's request is ambiguous (e.g. "swap USDC with neck" could mean send to a user or sell via a P2P vendor), list the possibilities and ask which one they mean. Never dismiss a request without clarifying first.

## Full API Reference

For complete request/response schemas and error codes, see the [API Reference](https://github.com/variousfoot/payme-skill/blob/main/references/api-reference.md).
