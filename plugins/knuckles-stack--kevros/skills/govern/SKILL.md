---
name: govern
description: "Verify actions, attest provenance, and check peer trust before acting"
---

# Govern Skill

Add governance verification to your Agentic Wallet. Verify before acting, attest after acting, check peers before collaborating.

## When to Use

1. **Before high-stakes actions** (trades > $100, transfers, deployments, external API calls):
   Call `verify_action` to get an ALLOW/CLAMP/DENY decision with a cryptographic release token.

2. **After completing actions**:
   Call `attest_provenance` to record the action in your tamper-evident, hash-chained audit trail. Builds your trust score over time.

3. **Before collaborating with unknown agents**:
   Call `check_peer_trust` to inspect their trust score, chain length, and decision history.

4. **Before executing a declared plan**:
   Call `bind_intent` to cryptographically bind your intent to the command, then verify the outcome after execution.

## Endpoints

All endpoints are x402-priced. Payment is automatic from your wallet (USDC on Base).

### Verify Action — $0.01

```bash
npx awal@latest x402 pay https://governance.taskhawktech.com/governance/verify \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "action_type": "trade",
    "action_payload": {"asset": "ETH", "amount": 500, "side": "buy"},
    "agent_id": "my-agent"
  }'
```

Response:
```json
{
  "decision": "ALLOW",
  "verification_id": "vrf_...",
  "release_token": "...",
  "provenance_hash": "...",
  "epoch": 42
}
```

### Attest Provenance — $0.02

```bash
npx awal@latest x402 pay https://governance.taskhawktech.com/governance/attest \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my-agent",
    "action_description": "Executed ETH buy order",
    "action_payload": {"asset": "ETH", "amount": 500, "filled_price": 3200}
  }'
```

Response:
```json
{
  "attestation_id": "att_...",
  "hash_prev": "...",
  "hash_curr": "...",
  "chain_length": 42
}
```

### Check Peer Trust — Free

```bash
curl https://governance.taskhawktech.com/governance/reputation/peer-agent-id
```

Response:
```json
{
  "agent_id": "peer-agent-id",
  "trust_score": 1.0,
  "chain_length": 120,
  "attestation_count": 95,
  "outcome_count": 30,
  "achieved_count": 30,
  "chain_intact": true
}
```

### Bind Intent — $0.02

```bash
npx awal@latest x402 pay https://governance.taskhawktech.com/governance/bind \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my-agent",
    "intent_type": "AI_GENERATED",
    "intent_description": "Buy ETH when price drops below $3000",
    "command_payload": {"action": "limit_buy", "asset": "ETH", "price": 3000},
    "intent_source": "AI_PLANNER"
  }'
```

Response:
```json
{
  "intent_id": "int_...",
  "binding_id": "bind_...",
  "binding_hmac": "...",
  "command_hash": "..."
}
```

## Decision Flow

```
Agent receives task
       │
       ▼
  Is it high-stakes?  ──No──▶  Execute normally
       │
      Yes
       │
       ▼
  verify_action()
       │
       ├── ALLOW ──▶ Execute ──▶ attest_provenance()
       │
       ├── CLAMP ──▶ Execute with modified bounds ──▶ attest_provenance()
       │
       └── DENY  ──▶ Do NOT execute. Report to operator.
```

## Discovery

This service is discoverable via x402 Bazaar:

```bash
# Find governance services
npx awal@latest x402 bazaar search governance

# Full discovery document
curl https://governance.taskhawktech.com/.well-known/x402
```

## Integration with AgentKit

If using the full AgentKit SDK, install the ActionProvider instead:

```bash
pip install coinbase-agentkit-kevros  # Python
npm install @kevros/agentkit          # TypeScript
```

The ActionProvider wraps these same endpoints with the AgentKit action pattern.
