# Spraay Payments — Example Workflows

## Example 1: Monthly Payroll

User: "Pay my team for March. Alice gets 3000 USDC, Bob gets 2500, Carol gets 4000. Use Base."

Agent steps:
1. Resolve any ENS/Basename addresses via `/api/resolve`
2. Get current USDC price via `/api/price?symbol=USDC` (confirm peg)
3. Send batch payment via `/api/batch-payment`
4. Check tx status via `/api/tx-status`
5. Send confirmation emails via `/api/email/send`

```bash
# Step 1: Resolve names
curl "$SPRAAY_GATEWAY_URL/api/resolve?name=alice.eth"
curl "$SPRAAY_GATEWAY_URL/api/resolve?name=bob.base"

# Step 2: Send batch
curl -X POST "$SPRAAY_GATEWAY_URL/api/batch-payment" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": [
      {"address": "0xAlice...", "amount": "3000"},
      {"address": "0xBob...", "amount": "2500"},
      {"address": "0xCarol...", "amount": "4000"}
    ],
    "token": "USDC",
    "chain": "base",
    "memo": "March 2026 payroll"
  }'
```

## Example 2: Price Check Before Swap

User: "What's ETH worth right now? I want to swap 2 ETH for USDC on Base."

```bash
# Check price (free)
curl "$SPRAAY_GATEWAY_URL/api/price?symbol=ETH"

# Get swap quote (paid)
curl -X POST "$SPRAAY_GATEWAY_URL/api/swap-quote" \
  -H "Content-Type: application/json" \
  -d '{
    "tokenIn": "ETH",
    "tokenOut": "USDC",
    "amount": "2.0",
    "chain": "base"
  }'
```

## Example 3: Invoice + Payment

User: "Create an invoice for 1500 USDC from client 0xABC..."

```bash
curl -X POST "$SPRAAY_GATEWAY_URL/api/create-invoice" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "0xABC...",
    "amount": "1500",
    "token": "USDC",
    "chain": "base",
    "memo": "Q1 2026 consulting services"
  }'
```

## Example 4: Cross-Chain Balance Check

User: "Check my USDC balance on Base, Arbitrum, and Polygon."

```bash
curl "$SPRAAY_GATEWAY_URL/api/balance?address=0xMyWallet...&chain=base&token=USDC"
curl "$SPRAAY_GATEWAY_URL/api/balance?address=0xMyWallet...&chain=arbitrum&token=USDC"
curl "$SPRAAY_GATEWAY_URL/api/balance?address=0xMyWallet...&chain=polygon&token=USDC"
```

## Example 5: Airdrop / Community Distribution

User: "Airdrop 100 USDC each to these 50 community members."

Best practice: Split into batches of 10-20 recipients per call for reliability.

```bash
# Batch 1 of 5
curl -X POST "$SPRAAY_GATEWAY_URL/api/batch-payment" \
  -H "Content-Type: application/json" \
  -d '{
    "recipients": [
      {"address": "0x001...", "amount": "100"},
      {"address": "0x002...", "amount": "100"},
      ...
    ],
    "token": "USDC",
    "chain": "base",
    "memo": "Community airdrop March 2026"
  }'
```

## Example 6: IPFS Upload + Share

User: "Upload this report to IPFS and send the link to the team."

```bash
# Pin to IPFS
curl -X POST "$SPRAAY_GATEWAY_URL/api/ipfs/pin" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "<base64 or text content>",
    "name": "q1-report.pdf"
  }'

# Send XMTP message with IPFS link
curl -X POST "$SPRAAY_GATEWAY_URL/api/xmtp/send" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "0xTeamLead...",
    "message": "Q1 report uploaded: ipfs://Qm..."
  }'
```

## Example 7: Automated Compliance

User: "Log this payment for audit and generate a tax summary."

```bash
# Log the audit entry
curl -X POST "$SPRAAY_GATEWAY_URL/api/audit/log" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "batch_payment",
    "amount": "9500",
    "token": "USDC",
    "chain": "base",
    "recipients": 3,
    "txHash": "0x...",
    "timestamp": "2026-03-07T12:00:00Z"
  }'

# Get tax summary
curl "$SPRAAY_GATEWAY_URL/api/tax/summary?year=2026&quarter=Q1"
```
