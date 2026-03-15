---
name: x402-layer
description: "x402-layer helps agents pay for APIs with USDC, deploy monetized endpoints,\n manage credits/webhooks/marketplace listings, and handle wallet-first ERC-8004 registration/discovery/management/reputation on Base, Ethereum, Polygon, BSC, Monad, and Solana.\n Use this skill when the user asks to \"create x402 endpoint\",\n \"deploy monetized API\", \"pay for API with USDC\", \"check x402 credits\",\n \"consume API credits\", \"list endpoint on marketplace\", \"buy API credits\",\n \"topup endpoint\", \"browse x402 marketplace\", \"set up webhook\",\n \"receive payment notifications\", \"manage endpoint webhook\",\n \"verify webhook payment\", \"verify payment genuineness\",\n \"register ERC-8004 agent\", \"register Solana 8004 agent\",\n \"submit on-chain reputation feedback\", \"rate ERC-8004 agent\",\n use \"Coinbase Agentic Wallet (AWAL)\", or manage x402 Singularity Layer\n operations on Base, Ethereum, Polygon, BSC, Monad, or Solana networks."
homepage: https://studio.x402layer.cc/docs/agentic-access/openclaw-skill
---

# x402 Singularity Layer

x402 is a Web3 payment layer where humans and agents can sell/consume APIs and products.
This skill covers the full Singularity Layer lifecycle:
- pay/consume services
- create/manage/list endpoints
- receive and verify webhook payment events
- register agents and submit on-chain reputation feedback

Networks: Base, Ethereum, Polygon, BSC, Monad, Solana  
Currency: USDC  
Protocol: HTTP 402 Payment Required

---

## Intent Router

Use this routing first, then load the relevant reference doc.

| User intent | Primary scripts | Reference |
|---|---|---|
| Pay/consume endpoint or product | `pay_base.py`, `pay_solana.py`, `consume_credits.py`, `consume_product.py` | `references/pay-per-request.md`, `references/credit-based.md` |
| Discover/search marketplace | `discover_marketplace.py` | `references/marketplace.md` |
| Create/edit/list endpoint | `create_endpoint.py`, `manage_endpoint.py`, `list_on_marketplace.py`, `topup_endpoint.py` | `references/agentic-endpoints.md`, `references/marketplace.md` |
| Configure/verify webhooks | `manage_webhook.py`, `verify_webhook_payment.py` | `references/webhooks-verification.md` |
| Register/discover/manage/rate agents (ERC-8004/Solana-8004) | `register_agent.py`, `list_agents.py`, `list_my_endpoints.py`, `update_agent.py`, `submit_feedback.py` | `references/agent-registry-reputation.md` |

---

## Quick Start

### 1) Install Skill Dependencies
```bash
pip install -r {baseDir}/requirements.txt
```

### 2) Choose Wallet Mode

Option A: private keys
```bash
export PRIVATE_KEY="0x..."
export WALLET_ADDRESS="0x..."
# Solana optional
export SOLANA_SECRET_KEY="base58-or-[1,2,3,...]"
```

Option B: Coinbase AWAL
```bash
# Install Coinbase AWAL skill (shortcut)
npx skills add coinbase/agentic-wallet-skills
export X402_USE_AWAL=1
```

Use private-key mode for ERC-8004 wallet-first registration. AWAL remains useful for x402 payment flows.

Security note: scripts read only explicit process environment variables. `.env` files are not auto-loaded.

---

## Script Inventory

### Consumer
| Script | Purpose |
|---|---|
| `pay_base.py` | Pay endpoint on Base |
| `pay_solana.py` | Pay endpoint on Solana |
| `consume_credits.py` | Consume using credits |
| `consume_product.py` | Purchase digital products/files |
| `check_credits.py` | Check credit balance |
| `recharge_credits.py` | Buy endpoint credit packs |
| `discover_marketplace.py` | Browse/search marketplace |
| `awal_cli.py` | Run AWAL auth/pay/discover commands |

### Provider
| Script | Purpose |
|---|---|
| `create_endpoint.py` | Deploy endpoint ($1 one-time, includes 4,000 credits) |
| `manage_endpoint.py` | List/update endpoint settings |
| `topup_endpoint.py` | Recharge provider endpoint credits |
| `list_on_marketplace.py` | List/unlist/update marketplace listing |
| `manage_webhook.py` | Set/remove/check endpoint webhook URL |
| `verify_webhook_payment.py` | Verify webhook signature + receipt genuineness (PyJWT/JWKS) |

### Agent Registry + Reputation
| Script | Purpose |
|---|---|
| `register_agent.py` | Register ERC-8004/Solana-8004 agent with image/version/tags and endpoint binding support |
| `list_agents.py` | List ERC-8004 agents owned by the configured wallet or linked dashboard user |
| `list_my_endpoints.py` | List platform endpoints that can be linked to ERC-8004 agents |
| `update_agent.py` | Update existing ERC-8004/Solana-8004 agent metadata, visibility, and endpoint bindings |
| `submit_feedback.py` | Submit on-chain reputation feedback |

---

## Core Security Requirements

### API Key Verification at Origin (mandatory)
When x402 proxies traffic to your origin, verify:
```http
x-api-key: <YOUR_API_KEY>
```
Reject requests when missing/invalid.

### Credit Economics (provider side)
- Endpoint creation: $1 one-time
- Starting credits: 4,000
- Top-up rate: 500 credits per $1
- Consumption: 1 credit per request
- If credits hit 0, endpoint stops serving until recharged

---

## Fast Runbooks

### A) Pay and Consume
```bash
python {baseDir}/scripts/pay_base.py https://api.x402layer.cc/e/weather-data
python {baseDir}/scripts/pay_solana.py https://api.x402layer.cc/e/weather-data
python {baseDir}/scripts/consume_credits.py https://api.x402layer.cc/e/weather-data
```

### B) Discover/Search Marketplace
```bash
python {baseDir}/scripts/discover_marketplace.py
python {baseDir}/scripts/discover_marketplace.py search weather
```

### C) Create and Manage Endpoint
```bash
python {baseDir}/scripts/create_endpoint.py my-api "My API" https://api.example.com 0.01
python {baseDir}/scripts/manage_endpoint.py list
python {baseDir}/scripts/manage_endpoint.py update my-api --price 0.02
python {baseDir}/scripts/topup_endpoint.py my-api 10
```

### D) List/Update in Marketplace
```bash
python {baseDir}/scripts/list_on_marketplace.py my-api \
  --category ai \
  --description "AI-powered analysis" \
  --logo https://example.com/logo.png \
  --banner https://example.com/banner.jpg
```

### E) Webhook Setup and Genuineness Verification
```bash
python {baseDir}/scripts/manage_webhook.py set my-api https://my-server.com/webhook
python {baseDir}/scripts/manage_webhook.py info my-api
python {baseDir}/scripts/manage_webhook.py remove my-api
```

Webhook verification helper:
```bash
python {baseDir}/scripts/verify_webhook_payment.py \
  --body-file ./webhook.json \
  --signature 't=1700000000,v1=<hex>' \
  --secret '<YOUR_SIGNING_SECRET>' \
  --required-source-slug my-api \
  --require-receipt
```

### F) Agent Registration + Reputation
```bash
python {baseDir}/scripts/list_my_endpoints.py

python {baseDir}/scripts/register_agent.py \
  "My Agent" \
  "Autonomous service agent" \
  --network baseSepolia \
  --image https://example.com/agent.png \
  --version 1.4.0 \
  --tag finance \
  --tag automation \
  --endpoint-id <ENDPOINT_UUID> \
  --custom-endpoint https://api.example.com/agent

python {baseDir}/scripts/list_agents.py --network baseSepolia

python {baseDir}/scripts/update_agent.py \
  --network baseSepolia \
  --agent-id 123 \
  --version 1.4.1 \
  --tag finance \
  --tag automation \
  --endpoint-id <ENDPOINT_UUID> \
  --public

# The same EVM flow also supports:
#   --network ethereum
#   --network polygon
#   --network bsc
#   --network monad

python {baseDir}/scripts/submit_feedback.py \
  --network base \
  --agent-id 123 \
  --rating 5 \
  --comment "High quality responses"
```

---

## References

Load only what is needed for the user task:

- `references/pay-per-request.md`:
  EIP-712/Solana payment flow and low-level signing details.
- `references/credit-based.md`:
  credit purchase + consumption behavior and examples.
- `references/marketplace.md`:
  search/list/unlist marketplace endpoints.
- `references/agentic-endpoints.md`:
  endpoint creation/top-up/status API behavior.
- `references/webhooks-verification.md`:
  webhook events, signature verification, and receipt cross-checks.
- `references/agent-registry-reputation.md`:
  ERC-8004/Solana-8004 registration, discovery, management, and feedback rules.
- `references/payment-signing.md`:
  exact signing domains/types/header payload details.

---

## Environment Reference

| Variable | Required for | Notes |
|---|---|---|
| `PRIVATE_KEY` | Base private-key mode | EVM signing key |
| `WALLET_ADDRESS` | Most operations | Primary wallet |
| `SOLANA_SECRET_KEY` | Solana private-key mode | base58 secret or JSON array bytes |
| `SOLANA_WALLET_ADDRESS` | Solana override | optional |
| `WALLET_ADDRESS_SECONDARY` | dual-chain endpoint mode | optional |
| `X402_USE_AWAL` | AWAL mode | set `1` |
| `X402_AUTH_MODE` | auth selection | `auto`, `private-key`, `awal` |
| `X402_PREFER_NETWORK` | network selection | `base`, `solana` |
| `X402_API_BASE` | API override | default `https://api.x402layer.cc` |
| `X_API_KEY` / `API_KEY` | provider endpoint/webhook management | endpoint key |
| `WORKER_FEEDBACK_API_KEY` | reputation feedback | worker auth key |

---

## API Base Paths

- Endpoints: `https://api.x402layer.cc/e/{slug}`
- Marketplace: `https://api.x402layer.cc/api/marketplace`
- Credits: `https://api.x402layer.cc/api/credits/*`
- Agent routes: `https://api.x402layer.cc/agent/*`

---

## Resources

- Docs: https://studio.x402layer.cc/docs/agentic-access/openclaw-skill
- SDK docs: https://studio.x402layer.cc/docs/developer/sdk-receipts
- GitHub docs repo: https://github.com/ivaavimusic/SGL_DOCS_2025
- x402 Studio: https://studio.x402layer.cc

---

## Known Issue

Solana payments currently have lower reliability than Base due to facilitator-side fee payer infra. Use retry logic in `pay_solana.py`, and prefer Base for production-critical flows.
