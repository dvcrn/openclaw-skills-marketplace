---
name: spraay-payments
description: "Send batch crypto payments, payroll, invoices, token swaps, price feeds, and AI inference using the Spraay Protocol x402 gateway. Use when the user asks to 'send payments', 'batch transfer', 'pay multiple wallets', 'crypto payroll', 'swap tokens', 'get token price', 'create invoice', 'check balance', 'resolve ENS', 'resolve basename', or mentions Spraay, x402 payments, or multi-chain batch transactions. Supports 11 chains: Base, Ethereum, Arbitrum, Polygon, BNB, Avalanche, Solana, Unichain, Plasma, BOB, Bittensor."
homepage: https://spraay.app
---

# Spraay Payments 💧

Multi-chain batch crypto payments, payroll, swaps, price feeds, invoices, and AI inference — all through one API.

Spraay is a protocol for sending crypto to multiple wallets in a single transaction. The x402 gateway exposes 57 paid endpoints and 5 free endpoints. Every paid call costs a micropayment via the x402 HTTP payment protocol. Free endpoints require no payment.

## Setup

The gateway is live at `https://gateway.spraay.app`. Set your env:

```bash
export SPRAAY_GATEWAY_URL="https://gateway.spraay.app"
```

No API key needed. Payments are made per-request via x402 (HTTP 402 → pay → retry). Your agent's wallet handles this automatically if you have a Coinbase CDP wallet or any x402-compatible facilitator.

## Supported Chains

Base, Ethereum, Arbitrum, Polygon, BNB Chain, Avalanche, Solana, Unichain, Plasma, BOB, Bittensor.

Payment contract (Base): `0x1646452F98E36A3c9Cfc3eDD8868221E207B5eEC`

## Core Workflows

### 1. Batch Payments (the main use case)

Send tokens to multiple wallets in one transaction.

```bash
curl -X POST "$SPRAAY_GATEWAY_URL/api/batch-payment" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": [
      {"address": "0xABC...123", "amount": "10"},
      {"address": "0xDEF...456", "amount": "25"},
      {"address": "0xGHI...789", "amount": "15"}
    ],
    "token": "USDC",
    "chain": "base"
  }'
```

If you get HTTP 402, the response contains payment instructions. Pay the facilitator, then retry with the payment proof header.

### 2. Token Prices

```bash
# Free endpoint — no x402 payment needed
curl "$SPRAAY_GATEWAY_URL/api/price?symbol=ETH"
```

Returns current USD price. Works for any major token symbol.

### 3. Token Balances

```bash
curl "$SPRAAY_GATEWAY_URL/api/balance?address=0xABC...&chain=base"
```

### 4. Token Swaps

```bash
curl -X POST "$SPRAAY_GATEWAY_URL/api/swap-quote" \
  -H "Content-Type: application/json" \
  -d '{
    "tokenIn": "ETH",
    "tokenOut": "USDC",
    "amount": "1.0",
    "chain": "base"
  }'
```

### 5. ENS / Basename Resolution

```bash
# Free endpoint
curl "$SPRAAY_GATEWAY_URL/api/resolve?name=vitalik.eth"
```

Resolves ENS names and Base names to addresses.

### 6. Invoices

```bash
curl -X POST "$SPRAAY_GATEWAY_URL/api/create-invoice" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "0xABC...123",
    "amount": "500",
    "token": "USDC",
    "chain": "base",
    "memo": "March consulting invoice"
  }'
```

### 7. AI Chat Inference

```bash
curl -X POST "$SPRAAY_GATEWAY_URL/api/ai/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain DeFi yield farming",
    "model": "openrouter/auto"
  }'
```

Powered by OpenRouter. Pay-per-query via x402.

### 8. Payroll

```bash
curl -X POST "$SPRAAY_GATEWAY_URL/api/batch-payment" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": [
      {"address": "alice.eth", "amount": "3000"},
      {"address": "bob.base", "amount": "2500"},
      {"address": "0xCCC...999", "amount": "4000"}
    ],
    "token": "USDC",
    "chain": "base",
    "memo": "March 2026 payroll"
  }'
```

ENS and Basename addresses resolve automatically.

## Communication Endpoints (Paid)

### Email
```bash
curl -X POST "$SPRAAY_GATEWAY_URL/api/email/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "team@company.com",
    "subject": "Payment Confirmation",
    "body": "Batch payment of 50,000 USDC sent to 12 recipients on Base."
  }'
```

### XMTP Messaging
```bash
curl -X POST "$SPRAAY_GATEWAY_URL/api/xmtp/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "0xRecipient...",
    "message": "Your payment of 500 USDC has been sent via Spraay."
  }'
```

### Webhooks
```bash
curl -X POST "$SPRAAY_GATEWAY_URL/api/webhook/send" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhook",
    "payload": {"event": "payment_complete", "txHash": "0x..."}
  }'
```

## Infrastructure Endpoints (Paid)

### RPC Relay (7 chains via Alchemy)
```bash
curl -X POST "$SPRAAY_GATEWAY_URL/api/rpc/relay" \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "base",
    "method": "eth_blockNumber",
    "params": []
  }'
```

### IPFS Upload (via Pinata)
```bash
curl -X POST "$SPRAAY_GATEWAY_URL/api/ipfs/pin" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello from Spraay!",
    "name": "my-file.txt"
  }'
```

## Free Endpoints (No Payment Required)

These 5 endpoints work without x402 payment:
- `GET /api/price?symbol=ETH` — Token prices
- `GET /api/resolve?name=vitalik.eth` — ENS/Basename resolution
- `GET /api/health` — Gateway health check
- `GET /api/chains` — List supported chains
- `GET /api/endpoints` — List all available endpoints

## x402 Payment Flow

1. Call any paid endpoint
2. Receive HTTP 402 with payment details (amount, facilitator address, token)
3. Send micropayment to the facilitator
4. Retry the original request with the `X-PAYMENT` header containing payment proof
5. Receive your response

Typical cost per call: fractions of a cent in USDC on Base.

## Error Handling

- `402` — Payment required. Follow the payment instructions in the response body.
- `400` — Bad request. Check your parameters.
- `404` — Endpoint not found.
- `500` — Server error. Retry after a moment.

Always check the HTTP status code before processing the response body.

## Tips

- Batch payments save 60-80% on gas vs individual transfers.
- Use the free `/api/price` endpoint to calculate USD values before sending.
- Resolve ENS/Basenames before batching to validate all addresses.
- Chain defaults to "base" if not specified.
- Token defaults to "USDC" if not specified.
- The gateway supports any ERC-20 token plus native ETH.

## Links

- App: https://spraay.app
- Gateway: https://gateway.spraay.app
- Docs: https://docs.spraay.app
- GitHub: https://github.com/plagtech
- Twitter: https://twitter.com/Spraay_app
- MCP Server: https://smithery.ai/server/@plagtech/spraay-x402-mcp
