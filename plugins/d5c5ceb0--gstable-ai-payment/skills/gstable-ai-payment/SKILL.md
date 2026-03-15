---
name: gstable-ai-payment
description: "GStable AI Payment Protocol - enables AI Agents to discover, negotiate, and execute cryptocurrency payments on behalf of users"
---

# GStable AI Payment Skill

An OpenClaw skill that enables AI Agents to discover, negotiate, and execute cryptocurrency payments on behalf of users.

## Features

- 🔗 Retrieve payment link details and supported tokens
- 📝 Create payment sessions (EIP-712 signatures)
- 🔍 Query payment session status
- 💰 Check native and ERC20 balances
- 💳 Prepare payments and generate on-chain transaction calldata
- ✅ Check and automatically approve tokens
- ⚡ Execute on-chain payment transactions
- 🚀 One-command payment (`pay`) with automatic approval handling
- 🔐 Secure EIP-712 signing (private key stored in environment variables)
- ⛓️ Multi-chain support (Polygon, Ethereum, Arbitrum, Base)

## Installation

```bash
clawhub install gstable-ai-payment
cd ~/.openclaw/workspace/skills/gstable-ai-payment
uv sync
```

## Configuration

Set environment variables:

```bash
# Required: wallet private key used to sign EIP-712 messages and send transactions
export WALLET_PRIVATE_KEY=0x...your_private_key_here...

# Optional: GStable API base URL (default: https://aipay.gstable.io/api/v1)
export GSTABLE_API_BASE_URL=https://aipay.gstable.io/api/v1

# Optional: default payer email
export DEFAULT_PAYER_EMAIL=user@example.com
```

⚠️ **Security note**: Never commit private keys to version control.

## Quick Start

### 1. Get payment link details

```bash
# Payment link formats:
# - https://pay.gstable.io/link/<link_id>
# - https://aipay.gstable.io/api/v1/payment/link/<link_id>

# Example 1
uv run scripts/gstable-ai-payment.py get_link lnk_BUDBgiGTWejFs8v0FbdpR3iJ83CG1tua

# Example 2
uv run scripts/gstable-ai-payment.py get_link lnk_QTAfGfyqAZHGSm9NKLhtjNYu8dNHRpGh
```

### 2. Create payment session

```bash
uv run scripts/gstable-ai-payment.py create_session lnk_BUDBgiGTWejFs8v0FbdpR3iJ83CG1tua 137 USDC
```

### 3. One-command payment (recommended)

```bash
uv run scripts/gstable-ai-payment.py pay lnk_BUDBgiGTWejFs8v0FbdpR3iJ83CG1tua 137 USDC user@example.com
```

## All Commands

```bash
# Get payment link details
uv run scripts/gstable-ai-payment.py get_link <link_id>

# Create payment session
uv run scripts/gstable-ai-payment.py create_session <link_id> <chain_id> <token> [payer]
uv run scripts/gstable-ai-payment.py create_session lnk_xxx 137 USDC
uv run scripts/gstable-ai-payment.py create_session lnk_xxx 137 0x3c499c542cef5e3811e1192ce70d8cc03d5c3359

# Get session status
uv run scripts/gstable-ai-payment.py get_session <session_id>

# Check native/ERC20 balance
uv run scripts/gstable-ai-payment.py balance <chain_id> [token_address] [wallet]

# Prepare payment (generate calldata)
uv run scripts/gstable-ai-payment.py prepare <session_id> <chain_id> <token_address> [email]

# Execute on-chain transaction
uv run scripts/gstable-ai-payment.py execute <chain_id> <to_address> <calldata>

# Check token allowance
uv run scripts/gstable-ai-payment.py allowance <chain_id> <token_address> <spender>

# Approve token for payment contract
uv run scripts/gstable-ai-payment.py approve <chain_id> <token_address> <spender> [amount]

# One-command payment (full flow, automatic approval)
uv run scripts/gstable-ai-payment.py pay <link_id> <chain_id> <token> [email]

# Show wallet address
uv run scripts/gstable-ai-payment.py wallet
```

## Supported Chains

| Chain | Chain ID | Tokens |
|-------|----------|------|
| Polygon | 137 | USDC, USDT |
| Ethereum | 1 | USDC, USDT |
| Arbitrum | 42161 | USDC |
| Base | 8453 | USDC |

Use `uv run scripts/gstable-ai-payment.py get_link <link-id>` to see exactly which chains and tokens are supported for a specific payment link.

## Usage Examples

### Complete payment flow

```bash
# Payment link: https://pay.gstable.io/link/lnk_BUDBgiGTWejFs8v0FbdpR3iJ83CG1tua

# Option 1: one-command payment (recommended)
uv run scripts/gstable-ai-payment.py pay lnk_BUDBgiGTWejFs8v0FbdpR3iJ83CG1tua 137 USDC user@example.com

# Output:
# Step 1/5: Getting payment link details...
# Step 2/5: Creating payment session...
# Step 3/5: Preparing payment...
# Step 4/5: Checking token allowance...
# Step 5/5: Executing on-chain payment transaction...
# ✅ Payment completed!
# { "linkId": "lnk_BUDBgiGTWejFs8v0FbdpR3iJ83CG1tua", "sessionId": "sess_xxx", "txHash": "0x..." }

# Option 2: run step by step
# 1) Get payment link details
uv run scripts/gstable-ai-payment.py get_link lnk_BUDBgiGTWejFs8v0FbdpR3iJ83CG1tua
# Returns payment link details in JSON format

# 2) Create payment session
uv run scripts/gstable-ai-payment.py create_session lnk_BUDBgiGTWejFs8v0FbdpR3iJ83CG1tua 137 USDC
# Output: { "sessionId": "sess_abc123", ... }

# 3) Prepare payment
uv run scripts/gstable-ai-payment.py prepare sess_abc123 137 0x3c499c542cef5e3811e1192ce70d8cc03d5c3359 user@example.com
# Output: { "executionChainId": "137", "executorContract": "0x...", "calldata": "0x..." }

# 4) Check and approve allowance (if needed)
uv run scripts/gstable-ai-payment.py allowance 137 0x3c499c542cef5e3811e1192ce70d8cc03d5c3359 0x...
uv run scripts/gstable-ai-payment.py approve 137 0x3c499c542cef5e3811e1192ce70d8cc03d5c3359 0x...

# 5) Execute on-chain transaction
uv run scripts/gstable-ai-payment.py execute 137 0x... 0x...
# Output: { "status": "submitted", "txHash": "0x..." }
```

### Agent interaction example

```
User: "I want to pay this: https://pay.gstable.io/link/lnk_BUDBgiGTWejFs8v0FbdpR3iJ83CG1tua"

Agent: [uv run scripts/gstable-ai-payment.py get_link lnk_BUDBgiGTWejFs8v0FbdpR3iJ83CG1tua]
       "This is a payment link. You can pay with USDC on Polygon. Which network would you like to use?"

User: "Use Polygon"

Agent: [uv run scripts/gstable-ai-payment.py pay lnk_BUDBgiGTWejFs8v0FbdpR3iJ83CG1tua 137 USDC]
       "✅ Payment completed! Transaction hash: 0x..."
```

## Payment Flow

```
┌─────────────────┐
│ User shares link│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    get_link     │ ──► Get product and payment options
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User picks token│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ create_session  │ ──► Create session (EIP-712 signature)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    prepare      │ ──► Get transaction calldata (EIP-712 signature)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   allowance     │ ──► Check token allowance
└────────┬────────┘
         │
         ▼ (if insufficient)
┌─────────────────┐
│    approve      │ ──► Approve token for payment contract
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    execute      │ ──► Send on-chain transaction
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ✅ Payment done │
└─────────────────┘

Or use the `pay` command to complete everything in one step.
```

## Environment Variables

| Variable | Required | Description |
|------|------|------|
| `WALLET_PRIVATE_KEY` | ✅ | Wallet private key used to sign EIP-712 messages and execute transactions (`0x` prefix) |
| `GSTABLE_API_BASE_URL` | ❌ | GStable API base URL (default: https://aipay.gstable.io/api/v1) |
| `DEFAULT_PAYER_EMAIL` | ❌ | Default payer email |
| `RPC_URL_POLYGON` | ❌ | Polygon RPC URL (default: https://polygon-rpc.com) |
| `RPC_URL_ETHEREUM` | ❌ | Ethereum RPC URL (default: https://eth.llamarpc.com) |
| `RPC_URL_ARBITRUM` | ❌ | Arbitrum RPC URL (default: https://arb1.arbitrum.io/rpc) |
| `RPC_URL_BASE` | ❌ | Base RPC URL (default: https://mainnet.base.org) |

## Troubleshooting

**"WALLET_PRIVATE_KEY not set"**
```bash
export WALLET_PRIVATE_KEY=0x...
```

**"Token not supported"**
```bash
# Check supported tokens first
uv run scripts/gstable-ai-payment.py get_link <link_id>
```

**"Session expired"**
```bash
# Recreate session
uv run scripts/gstable-ai-payment.py create_session <link_id> <chain_id> <token>
```

**"No RPC URL configured for chain"**
```bash
# Set RPC URL for the corresponding chain
export RPC_URL_POLYGON=https://polygon-rpc.com
```

**"Gas estimation failed" or "Transaction failed"**
- Ensure the wallet has enough native token (e.g., MATIC) to pay gas fees
- Ensure the wallet has enough token balance to complete the payment
- Check whether the token has been approved for the payment contract

## Resources

- GStable AI Payment Protocol: https://docs.gstable.io/zh-Hans/docs/category/ai-payment-protocol
- GStable AI Agent Integration: https://docs.gstable.io/zh-Hans/docs/category/ai-agent-integration
- GitHub: https://github.com/gstable/gstable-ai-payment-skill

## License

MIT
