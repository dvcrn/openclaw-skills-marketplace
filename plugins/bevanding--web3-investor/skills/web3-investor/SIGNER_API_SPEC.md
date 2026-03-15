# Web3 Signer API Specification (Reference Implementation)

> **Version**: v1.0.0  
> **Purpose**: Define the expected signer service API interface for web3-investor skill  
> **Audience**: Signer service implementers, intelligent agents

---

## Design Philosophy

### Agent-First Design

This specification is designed to be **understood by intelligent agents**, not auto-adapted by programs.

- Agents have LLM and programming capabilities
- Agents can read documentation, understand design intent, and modify code
- We provide a **reference specification**, not a mandatory standard

### Core Principles

| Principle | Description |
|-----------|-------------|
| **No Private Keys** | Signer service holds private keys, skill does NOT hold any |
| **State Machine** | All transactions must go through `preview → approve → execute` |
| **Security Checks** | Sufficient balance, sufficient allowance, valid route |
| **Configurable** | API endpoints can be mapped via configuration file |

---

## Execution Model

```
┌─────────────────────────────────────────────────────────────┐
│                        Web3 Investor Skill                   │
│                     (Running in Agent Environment)           │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ REST API Call
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Local Keystore Signer Service             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│  │  Keystore   │   │   Signing   │   │   Broadcast │       │
│  │ (Key Store) │ → │   Engine    │ → │   Service   │       │
│  └─────────────┘   └─────────────┘   └─────────────┘       │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Broadcast Transaction
                              ▼
                       ┌─────────────┐
                       │  Blockchain │
                       │ (Base/ETH)  │
                       └─────────────┘
```

**Key Points**:
- Skill only generates transaction requests, does NOT hold private keys
- Signer service handles signing and broadcasting
- Both communicate via REST API

---

## State Machine

```
preview ──→ approve ──→ execute
   │           │            │
   │           │            └──→ tx_hash (success) or error (failure)
   │           │
   │           └──→ Requires manual confirmation
   │
   └──→ simulation_ok: true/false
        risk: { balance, allowance, route }
```

**Enforced Rules**:
- ❌ Cannot skip `approve` step
- ✅ Must `preview` first to validate transaction feasibility
- ✅ `approve` requires manual/external confirmation

---

## API Endpoint Specification

### 1. Query Balances

```
GET /api/wallet/balances
```

**Query Parameters**:
- `chain` (optional): Chain name, e.g., `base`, `ethereum`
- `tokens` (optional): Token list, e.g., `USDC,WETH`

**Response**:
```json
{
  "success": true,
  "balances": [
    {
      "symbol": "USDC",
      "address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "balance": "1000.50",
      "chain": "base"
    },
    {
      "symbol": "ETH",
      "balance": "0.5",
      "chain": "base"
    }
  ]
}
```

---

### 2. Preview Transaction

```
POST /api/trades/preview
```

**Request**:
```json
{
  "type": "swap",
  "from_token": "USDC",
  "to_token": "WETH",
  "amount": "5",
  "network": "base",
  "slippage_percent": 0.5
}
```

**Response**:
```json
{
  "success": true,
  "preview_id": "550e8400-e29b-41d4-a716-446655440000",
  "simulation_ok": true,
  "rate": "0.00035",
  "estimated_output": "0.00175",
  "gas_estimate": 150000,
  "risk": {
    "balance_sufficient": true,
    "allowance_sufficient": true,
    "route_valid": true,
    "warnings": []
  },
  "transaction": {
    "to": "0x...",
    "value": "0x0",
    "data": "0x..."
  },
  "next_step": "approve"
}
```

**Field Descriptions**:
| Field | Type | Description |
|-------|------|-------------|
| `preview_id` | string | Preview ID for subsequent approve |
| `simulation_ok` | boolean | Whether simulation succeeded |
| `risk` | object | Risk assessment result |
| `next_step` | string | Next action: `approve` or `clarification` |

---

### 3. Approve Transaction

```
POST /api/trades/approve
```

**Request**:
```json
{
  "preview_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response**:
```json
{
  "success": true,
  "approval_id": "660e8400-e29b-41d4-a716-446655440001",
  "preview_id": "550e8400-e29b-41d4-a716-446655440000",
  "approved_at": "2026-03-05T06:00:00Z",
  "expires_at": "2026-03-05T06:30:00Z"
}
```

---

### 4. Execute Transaction

```
POST /api/trades/execute
```

**Request**:
```json
{
  "approval_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Response**:
```json
{
  "success": true,
  "tx_hash": "0xabcdef1234567890...",
  "explorer_url": "https://basescan.org/tx/0xabcdef1234567890...",
  "network": "base",
  "executed_at": "2026-03-05T06:01:00Z"
}
```

---

### 5. Query Transaction Status

```
GET /api/transactions/{tx_hash}
```

**Response**:
```json
{
  "success": true,
  "tx_hash": "0xabcdef1234567890...",
  "status": "confirmed",
  "block_number": 12345678,
  "gas_used": 145000,
  "network": "base"
}
```

---

### 6. Query Allowances

```
GET /api/allowances?chain=base&token=USDC
```

**Response**:
```json
{
  "success": true,
  "allowances": [
    {
      "token": "USDC",
      "token_address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
      "spender": "0x...",
      "spender_name": "Uniswap Router",
      "allowance": "115792089237316195423570985008687907853269984665640564039457584007913129639935",
      "allowance_formatted": "Unlimited"
    }
  ]
}
```

---

### 7. Preview Revoke Allowance

```
POST /api/allowances/revoke-preview
```

**Request**:
```json
{
  "token": "USDC",
  "spender": "0x...",
  "chain": "base"
}
```

**Response**:
```json
{
  "success": true,
  "preview_id": "770e8400-e29b-41d4-a716-446655440002",
  "current_allowance": "115792089237316195423570985008687907853269984665640564039457584007913129639935",
  "next_step": "approve"
}
```

---

## Error Format

All error responses follow a unified format:

```json
{
  "success": false,
  "error": {
    "code": "E001",
    "message": "Insufficient balance for transaction"
  },
  "diagnostics": "Required: 10 USDC, Available: 5 USDC"
}
```

**Error Code Definitions**:

| Code | Description |
|------|-------------|
| E001 | Insufficient balance |
| E002 | Insufficient allowance, need to approve token first |
| E003 | No valid route found |
| E004 | Chain not in whitelist |
| E005 | Protocol not in whitelist |
| E006 | Token not in whitelist |
| E007 | Exceeds transaction limit |
| E008 | Simulation failed |
| E009 | Not approved, cannot execute |
| E010 | API service unavailable |
| E999 | Unknown error |

---

## Configuration Adaptation

Signer service implementers can adapt different APIs by modifying `config/config.json`:

```json
{
  "api": {
    "base_url": "http://localhost:3000/api",
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

---

## Adaptation Guide

If your signer service API differs from this specification:

### Method 1: Modify Configuration File
Update the `endpoints` mapping in `config/config.json`.

### Method 2: Modify Code
Update the `api_request()` function in `scripts/trading/trade_executor.py`.

### Method 3: Implement Adapter Layer
Implement an adapter layer in your signer service to convert your API to this specification format.

---

## Security Recommendations

1. **Signer service should run locally**, not exposed to public internet
2. **Approve step should have confirmation mechanism**, which can be:
   - Console confirmation (development environment)
   - Hardware wallet confirmation (production environment)
   - Multi-signature confirmation (team environment)
3. **Set transaction limits** to prevent single transactions that are too large
4. **Whitelist mechanism** to limit contract addresses that can be interacted with

---

**Maintainer**: Web3 Investor Skill Team  
**Last Updated**: 2026-03-05