---
name: x402-cli
description: "Pay for x402 payment-gated HTTP endpoints using USDC stablecoins"
---

# x402-cli

Pay for x402 payment-gated HTTP endpoints using USDC stablecoins.

## When to use

Use this tool when you need to access an API that returns HTTP 402 Payment Required with x402 payment requirements. The tool handles the full payment flow: probe → sign → pay → return response.

## Prerequisites

Set `EVM_PRIVATE_KEY` environment variable with a wallet private key that holds USDC on the target network (e.g., Base Sepolia for testnet).

## Usage

### Probe an endpoint (check price without paying)

```bash
x402-cli --json --skip-verify <url>
```

Returns JSON with `probe.paymentRequirements` containing the price, network, and asset.

### Pay and access an endpoint

```bash
x402-cli --json -y <url>
```

Returns JSON with `payment.body` containing the backend response and `payment.paymentResponse` containing the transaction hash.

### POST with body

```bash
x402-cli --json -y -X POST -d '{"query": "hello"}' -H 'Content-Type: application/json' <url>
```

### Self-signed TLS (local development)

```bash
x402-cli --json -y -k <url>
```

## Exit codes

- `0` — Success (payment accepted or probe completed)
- `1` — Error (network, config, or unexpected failure)
- `2` — Payment rejected by facilitator
- `3` — Route is free (no payment needed)

## JSON output structure

```json
{
  "status": "accepted",
  "probe": {
    "statusCode": 402,
    "paymentRequired": true,
    "paymentRequirements": { "...x402 requirements..." }
  },
  "payment": {
    "statusCode": 200,
    "accepted": true,
    "signer": "0x...",
    "paymentResponse": { "success": true, "transaction": "0x...", "network": "eip155:84532" },
    "body": "...backend response..."
  }
}
```

## Key fields to parse

- `.status` — `"free"`, `"payment_required"`, `"accepted"`, `"rejected"`, `"error"`
- `.probe.paymentRequirements.accepts[0].amount` — price in atomic units
- `.probe.paymentRequirements.accepts[0].network` — chain ID (e.g., `eip155:84532`)
- `.payment.body` — the actual backend response after payment
- `.payment.paymentResponse.transaction` — on-chain transaction hash
