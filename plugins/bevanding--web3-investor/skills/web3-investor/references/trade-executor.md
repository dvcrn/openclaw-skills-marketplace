# Trade Executor Module (REST API Adapter)

> **Purpose**: Generate executable transaction requests via REST API to local keystore signer.

---

## What It Does

Generates executable transaction requests via REST API to local keystore signer. **This module does NOT hold private keys** — all transactions require explicit approval.

## Execution Model

| Property | Value |
|----------|-------|
| **Wallet Type** | Local keystore signer |
| **Supported Chains** | `base`, `ethereum` |
| **Entry Point** | REST API |
| **State Machine** | `preview` → `approve` → `execute` |

## Security Constraints (MUST FOLLOW)

- ❌ **Cannot skip `approve` step** — every transaction requires manual confirmation
- ✅ **Must simulate before execution** — uses `eth_call` for validation
- ⚠️ **Must return risk warnings** — insufficient balance, missing allowance, invalid route
- 🔒 **Default minimum permissions**:
  - Whitelist chains/protocols/tokens
  - Transaction value limits
  - Max slippage caps

## Payment Methods

### Option A: Keystore Signer (Production)

Requires local signer service running. Best for automated agents with dedicated signing infrastructure.

```bash
# Step 4a: Preview transaction
python3 scripts/trading/trade_executor.py preview \
  --type deposit \
  --protocol aave \
  --asset USDC \
  --amount 1000 \
  --network base

# Step 4b: Approve (returns approval_id)
python3 scripts/trading/trade_executor.py approve \
  --preview-id <uuid-from-preview>

# Step 4c: Execute (broadcasts signed tx)
python3 scripts/trading/trade_executor.py execute \
  --approval-id <uuid-from-approve>
```

### Option B: EIP-681 Payment Link (Mobile Recommended)

Generate a MetaMask-compatible payment link or QR code. Best for mobile users and quick investments without local signer setup.

```bash
# Generate payment link for RWA investment
python3 scripts/trading/eip681_payment.py generate \
  --token USDC \
  --to 0x1F3A9A450428BbF161C4C33f10bd7AA1b2599a3e \
  --amount 10 \
  --network base \
  --qr-output /tmp/payment_qr.png
```

**Output includes:**
- MetaMask deep link (mobile users click to open app)
- QR code PNG file (desktop users scan with phone)
- Raw transaction details (for manual verification)

**Supported tokens:** USDC, USDT, WETH, ETH on Base and Ethereum mainnet.

### Option C: WalletConnect (Roadmap)

Coming in future release. Will support complex DeFi interactions and persistent wallet connections.

## API Endpoints

| Operation | Method | Endpoint | Description |
|-----------|--------|----------|-------------|
| Query Balances | GET | `/api/wallet/balances` | Get wallet token balances |
| Preview Swap | POST | `/api/trades/preview` or `/api/uniswap/preview-swap` or `/api/zerox/preview-swap` | Generate transaction preview |
| Approve | POST | `/api/trades/approve` | Confirm transaction for execution |
| Execute | POST | `/api/trades/execute` | Broadcast signed transaction |
| Check Status | GET | `/api/transactions/{tx_hash}` | Query transaction status |
| Query Allowances | GET | `/api/allowances` | Get token allowances |
| Revoke Preview | POST | `/api/allowances/revoke-preview` | Preview allowance revoke |

## Unified Transaction Request Format

All transaction requests follow this structure:

```json
{
  "request_id": "uuid",
  "timestamp": "ISO8601",
  "network": "base",
  "chain_id": 8453,
  "type": "transfer|swap|deposit|contract_call",
  "description": "human readable",
  "transaction": {
    "to": "0x...",
    "value": "0x0",
    "data": "0x...",
    "gas_limit": 250000
  },
  "metadata": {
    "protocol": "uniswap|0x|aave|...",
    "from_token": "USDC",
    "to_token": "WETH",
    "amount": "5"
  }
}
```

## Response Specifications

### `preview` Response

```json
{
  "preview_id": "uuid",
  "simulation_ok": true|false,
  "risk": {
    "balance_sufficient": true|false,
    "allowance_sufficient": true|false,
    "route_valid": true|false,
    "warnings": ["..."]
  },
  "next_step": "approve" | "clarification"
}
```

### `approve` Response

```json
{
  "approval_id": "uuid",
  "preview_id": "...",
  "approved_at": "ISO8601",
  "expires_at": "ISO8601"
}
```

### `execute` Response

```json
{
  "tx_hash": "0x...",
  "explorer_url": "https://basescan.org/tx/0x...",
  "executed_at": "ISO8601",
  "network": "base"
}
```

### Error Format

```json
{
  "code": "E001-E999",
  "message": "human readable",
  "diagnostics": "technical details"
}
```

## CLI Usage Examples

```bash
# Step 1: Preview a swap
python3 scripts/trading/trade_executor.py preview \
  --type swap \
  --from-token USDC \
  --to-token WETH \
  --amount 5 \
  --network base

# Step 2: Approve the preview
python3 scripts/trading/trade_executor.py approve \
  --preview-id <uuid-from-step-1>

# Step 3: Execute the approved transaction
python3 scripts/trading/trade_executor.py execute \
  --approval-id <uuid-from-step-2>

# Check balances
python3 scripts/trading/trade_executor.py balances \
  --network base

# Check transaction status
python3 scripts/trading/trade_executor.py status \
  --tx-hash 0x...
```

## Health Check (MUST RUN BEFORE TRADING)

```bash
python3 scripts/trading/trade_executor.py balances --network base
# If success → signer is available
# If error E010 → signer unavailable, stop and inform user
```

## Module Usage Guide

| Module | Purpose | Production/Debug |
|--------|---------|------------------|
| `trade_executor.py` | Main execution module, connects to signer service | ✅ Production |
| `eip681_payment.py` | Generate MetaMask payment links & QR codes | ✅ Production |
| `safe_vault.py` | Calldata generation, balance check (no signing) | 🔧 Debug |
| `simulate_tx.py` | Transaction simulation (no signing) | 🔧 Debug |

## Troubleshooting

### Import Errors
If you see `ModuleNotFoundError`, ensure you're running from the workspace root:
```bash
cd /home/admin/.openclaw/workspace
python3 skills/web3-investor/scripts/trading/trade_executor.py ...
```

### Signer Unavailable
- Check if the local signer service is running
- Verify `WEB3_INVESTOR_API_URL` environment variable
- Consult SETUP.md for signer setup instructions