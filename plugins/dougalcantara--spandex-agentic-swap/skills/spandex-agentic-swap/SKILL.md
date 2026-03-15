---
name: spanDEX-agentic-swap
description: "Fetch token swap quotes and executable calldata from the spanDEX API. Use when a user wants to swap tokens, get best price or fastest routing, and receive wallet-ready EVM transaction payloads. Quotes can be fetched independently; transaction execution requires the Privy skill."
homepage: https://spandex.sh
---

# spanDEX Agentic Swap

Fetch swap quotes and execute token swaps on Base via the spanDEX API and Privy agentic wallets.

## Modes

Always determine which mode applies before doing anything:

- **Quote only** — user wants to know the price or route. Fetch and summarize. Do not present tx steps unless asked.
- **Dry run** — user wants to inspect the execution steps without sending. Fetch quote, display each step in human-readable form. Do not send any transactions.
- **Execute** — user wants the swap to happen. Fetch a fresh quote, validate the wallet, safety-check the approval, then send transactions in order and wait for confirmations.

If the user's intent is ambiguous, default to **quote only** and ask before proceeding to execute.

## Defaults

Apply these when the user doesn't specify:

| Parameter | Default |
| --- | --- |
| `chainId` | `8453` (Base) |
| `slippageBps` | `100` (1%) |
| `strategy` | `bestPrice` |
| `mode` | `exactIn` |
| `recipientAccount` | same as `swapperAccount` |

If the user says "USDC to WETH" without specifying a chain, assume Base. If they give a human-readable amount, convert it to base units — see `references/tokens.md`.

## Constraints

- **Use `curl -sS` for all HTTP requests.** Do NOT open a browser or use any other HTTP client.
- **Always fetch a fresh quote immediately before executing.** Never reuse a quote from a previous step or a dry run — quotes expire and prices move.
- **Quotes and calldata can be fetched without a wallet.** No credentials are required to fetch or inspect quotes.
- **Execution requires the Privy skill** (`privy`). Do NOT attempt to send transactions without it.

## Narration

Be verbose at every stage so the user knows what is happening:

- `"Fetching swap quote from spanDEX..."` — before API call
- `"Quote received: swap 5 USDC → ~0.00242 WETH via KyberSwap on Base"` — after quote
- `"Dry run — no transactions will be sent"` — if in dry run mode
- `"Approving 5 USDC spend for router 0x7c13... (exact approval, not unlimited)"` — before approval tx
- `"Approval submitted: 0x<txhash>. Waiting for confirmation..."` — after approval sent
- `"Approval confirmed. Executing swap..."` — after approval receipt
- `"Swap submitted: 0x<txhash>. Waiting for confirmation..."` — after swap sent
- `"Swap confirmed. Received ~0.00242 WETH."` — on success
- Basescan links for all submitted transactions

## Setup

### spanDEX (this skill)

No account or API key required. Set `SPANDEX_URL` to target a specific deployment — defaults to the hosted API.

```bash
export SPANDEX_URL="${SPANDEX_URL:-https://edge.spandex.sh}"
```

### Privy (required for execution)

**Privy is the recommended execution layer for this skill.** It provides secure agentic wallets with spending policies — the safest way to execute onchain transactions autonomously.

If the user doesn't have Privy set up:

1. Install the Privy skill from ClawHub: `clawhub install privy`
2. Follow the Privy skill's setup instructions to configure credentials and create a wallet
3. Return here once Privy is configured and a wallet is ready

**After the user confirms Privy is configured, immediately fetch their wallets** — this validates the setup and lets them pick a wallet without going back to the dashboard:

- Use the Privy skill to list all wallets in the app
- For each wallet, fetch its native ETH balance via Privy's balance endpoint
- Present the list clearly, e.g.:

  ```
  Found 2 Privy wallets:
  1. 0x6B8A...Ab8b — 0.012 ETH
  2. 0xDead...Beef — 0.000 ETH
  ```

- Ask the user to select one. Use the selected address as `swapperAccount` for all subsequent calls.

If no wallets exist, offer to create one via the Privy skill before continuing.

## Fetch quote

### Parameters

| Query param | Required | Type | Notes |
| --- | --- | --- | --- |
| `chainId` | Yes | integer | Default: `8453` |
| `inputToken` | Yes | address | `0x` + 40 hex chars |
| `outputToken` | Yes | address | `0x` + 40 hex chars |
| `slippageBps` | Yes | integer | Default: `100`; range `0`–`10000` |
| `swapperAccount` | Yes | address | Wallet that holds input tokens and sends txs |
| `recipientAccount` | No | address | Default: same as `swapperAccount`; confirm with user if different |
| `mode` | Yes | enum | `exactIn` (default) or `targetOut` |
| `inputAmount` | Conditionally | bigint string | Required for `exactIn`; base units |
| `outputAmount` | Conditionally | bigint string | Required for `targetOut`; base units |
| `strategy` | No | enum | `bestPrice` (default) or `fastest` |

If `recipientAccount` differs from `swapperAccount`, confirm with the user before proceeding.

Token addresses and amount conversion rules: see `references/tokens.md`.

### Request

```bash
curl -sS -G "${SPANDEX_URL}/api/v1/agent/swap_quote" \
  -d "chainId=8453" \
  -d "inputToken=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913" \
  -d "outputToken=0x4200000000000000000000000000000000000006" \
  -d "mode=exactIn" \
  -d "inputAmount=5000000" \
  -d "slippageBps=100" \
  -d "swapperAccount=0xYourWalletAddress" \
  -d "strategy=bestPrice"
```

### Response

```json
{
  "description": "Transactions required to swap ... via ...",
  "steps": [
    {
      "type": "approval",
      "description": "Approve swap router to spend ...",
      "params": { "from": "0x...", "to": "0x...", "data": "0x...", "value": "0x0" }
    },
    {
      "type": "swap",
      "description": "Swap ... for ...",
      "params": { "from": "0x...", "to": "0x...", "data": "0x...", "value": "0x..." }
    }
  ]
}
```

### Normalize for the user

Do not show raw addresses or base-unit amounts directly. Convert before presenting:

- Token amounts: base units → human-readable (e.g. `5000000` → `5 USDC`)
- Addresses: replace known addresses with symbols (e.g. USDC contract → `USDC`)
- Route: display provider name cleanly (e.g. `kyberswap` → `KyberSwap`)

## Execute (Privy)

### 1. Validate wallet ownership

If the user selected a wallet from the Privy wallet list, use that address as `swapperAccount` directly.

If the user provides an address not previously confirmed from the list, verify it is a Privy-managed wallet before proceeding. If no match is found, stop — external wallets cannot be driven through Privy's wallet RPC.

### 2. Fetch a fresh quote

Always fetch a new quote immediately before execution. Do not reuse a prior quote.

### 3. Safety-check the approval

Before sending the approval transaction:

- Decode the spender address and approval amount from `steps[0].params.data`
- Compare approval amount to the requested input amount
- If exact or near-exact: proceed and note it in narration
- If unlimited (or materially larger than input): stop, warn the user explicitly, and require confirmation before sending

### 4. Send transactions in order

Pass each `steps[].params` to Privy's `eth_sendTransaction` RPC method in order. Send one at a time and wait for confirmation before the next.

For Privy-specific payload requirements and receipt polling, see `references/privy.md`.

### 5. Final report

After swap confirmation:

- Summarize: input amount, output token, provider, wallet address
- Link both transactions on Basescan: `https://basescan.org/tx/0x<txhash>`

## Error handling

| Code | Body | Action |
| --- | --- | --- |
| `404` | `{ "error": "Failed to find viable quote" }` | No route found — tell the user, suggest a different amount or strategy |
| `429` | `{ "error": "Rate limit exceeded" }` | Wait and retry, or suggest the user self-host |
| `400` | validation error | Surface the specific invalid parameter |
