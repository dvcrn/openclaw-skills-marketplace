# Web3 Investor Skill - Signer Service Integration Guide

> **Audience**: Intelligent agents, signer service implementers  
> **Purpose**: Understand how to configure and verify signer service

---

## Overview

web3-investor skill **does NOT hold private keys**. All transaction execution is delegated to external signer services via REST API.

```
┌──────────────────┐      REST API      ┌──────────────────┐
│  web3-investor   │ ─────────────────→ │  Signer Service  │
│  (Skill)         │                    │  (Holds Keys)    │
└──────────────────┘ ←───────────────── └──────────────────┘
                         Transaction Result
```

---

## Prerequisites

Before executing any transaction, ensure:

1. **Signer service is running**: Running at `localhost:3000` or other address
2. **API is reachable**: Skill can call signer service via HTTP
3. **Wallet is configured**: Signer service has available accounts

---

## Configuration Steps

### 1. Check/Modify Configuration File

Configuration file is located at `config/config.json`:

```json
{
  "api": {
    "base_url": "http://localhost:3000/api",
    "timeout_seconds": 30,
    "endpoints": {
      "balances": "/wallet/balances",
      "preview": "/trades/preview",
      "approve": "/trades/approve",
      "execute": "/trades/execute",
      "status": "/transactions/{tx_hash}",
      "allowances": "/allowances",
      "revoke_preview": "/allowances/revoke-preview"
    }
  }
}
```

**Modifiable Items**:
- `base_url`: If signer service runs at different address/port
- `endpoints`: If signer service API paths differ from this specification

### 2. Environment Variable Override (Optional)

```bash
# Override API address
export WEB3_INVESTOR_API_URL="http://localhost:8080/api"
```

---

## Verify Signer Service

### Method 1: Command Line Check

```bash
# Check if balance endpoint is available
curl http://localhost:3000/api/wallet/balances

# Expected response
{"success": true, "balances": [...]}
```

### Method 2: Using trade_executor.py

```bash
# Query balances (automatically checks API availability)
python3 scripts/trading/trade_executor.py balances --network base

# If successful, returns balance list
# If failed, returns error message and diagnostics
```

---

## API Specification Reference

For detailed API specification, see: [SIGNER_API_SPEC.md](SIGNER_API_SPEC.md)

**Core Endpoints**:

| Endpoint | Purpose | State Machine Stage |
|----------|---------|---------------------|
| `/wallet/balances` | Query balances | Pre-check |
| `/trades/preview` | Preview transaction | preview |
| `/trades/approve` | Approve transaction | approve |
| `/trades/execute` | Execute transaction | execute |

---

## Execution Flow

All transactions must follow the `preview → approve → execute` state machine:

```
1. preview:  Simulate transaction, returns preview_id
     ↓
2. approve:  Manual confirmation, returns approval_id
     ↓
3. execute:  Sign and broadcast, returns tx_hash
```

**Example**:

```bash
# Step 1: Preview swap
python3 scripts/trading/trade_executor.py preview \
  --type swap \
  --from-token USDC \
  --to-token WETH \
  --amount 5 \
  --network base

# Record the returned preview_id

# Step 2: Approve
python3 scripts/trading/trade_executor.py approve \
  --preview-id <preview_id>

# Record the returned approval_id

# Step 3: Execute
python3 scripts/trading/trade_executor.py execute \
  --approval-id <approval_id>
```

---

## FAQ

### Q: What if signer service API paths are different?

Modify the `endpoints` field in `config/config.json` to map to your actual API paths.

### Q: What if signer service response format is different?

You have two options:
1. Implement an adapter layer in your signer service to convert to specification format
2. Modify the response parsing logic in `scripts/trading/trade_executor.py`

### Q: How to debug?

Use Safe Vault module for offline debugging:

```bash
# Only generate calldata, no API calls
python3 scripts/trading/safe_vault.py preview-deposit \
  --protocol aave \
  --asset USDC \
  --amount 1000
```

### Q: What is the approve step?

The `approve` step is a confirmation step in the state machine for:
- Preventing unconfirmed transactions from being executed
- Allowing time window for manual/external system confirmation

Signer service implementers can customize the approve confirmation mechanism (console confirmation, hardware wallet, multi-signature, etc.).

---

## Security Checklist

Before executing a transaction, the agent should check:

- [ ] Is API reachable?
- [ ] Is balance sufficient?
- [ ] Does token need approval first?
- [ ] Are target chain/protocol/token in whitelist?
- [ ] Is transaction amount within limit?

---

**Next Step**: Read [SIGNER_API_SPEC.md](SIGNER_API_SPEC.md) for complete API specification.