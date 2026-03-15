# Spraay x402 Gateway — Full Endpoint Reference

## Free Endpoints (5)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/price` | GET | Token price lookup (param: `symbol`) |
| `/api/resolve` | GET | ENS/Basename resolution (param: `name`) |
| `/api/health` | GET | Gateway health status |
| `/api/chains` | GET | List supported chains |
| `/api/endpoints` | GET | List all endpoints |

## Paid Endpoints — Payments (Core)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/batch-payment` | POST | Batch send tokens to multiple wallets |
| `/api/swap-quote` | POST | Get token swap quote |
| `/api/balance` | GET | Check token balance |
| `/api/create-invoice` | POST | Create payment invoice |
| `/api/tx-status` | GET | Check transaction status |
| `/api/gas-estimate` | POST | Estimate gas for transaction |
| `/api/token-info` | GET | Get token metadata |
| `/api/allowance` | GET | Check token allowance |
| `/api/approve` | POST | Approve token spending |
| `/api/transfer` | POST | Single token transfer |

## Paid Endpoints — AI & Inference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ai/chat` | POST | AI chat completion (OpenRouter) |
| `/api/ai/summarize` | POST | Summarize text |
| `/api/ai/analyze` | POST | Analyze data/text |

## Paid Endpoints — Communication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/email/send` | POST | Send email (AgentMail) |
| `/api/email/inbox` | GET | Check inbox |
| `/api/sms/send` | POST | Send SMS |
| `/api/xmtp/send` | POST | Send XMTP message |
| `/api/xmtp/inbox` | GET | Check XMTP inbox |
| `/api/webhook/send` | POST | Fire webhook |
| `/api/webhook/register` | POST | Register webhook listener |
| `/api/notification/send` | POST | Send notification |

## Paid Endpoints — Infrastructure

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/rpc/relay` | POST | RPC relay (Alchemy, 7 chains) |
| `/api/ipfs/pin` | POST | Pin to IPFS (Pinata) |
| `/api/ipfs/get` | GET | Retrieve from IPFS |
| `/api/cron/create` | POST | Create scheduled job |
| `/api/cron/list` | GET | List cron jobs |
| `/api/cron/delete` | DELETE | Delete cron job |
| `/api/log/write` | POST | Write to log |
| `/api/log/read` | GET | Read logs |
| `/api/storage/set` | POST | Key-value storage set |
| `/api/storage/get` | GET | Key-value storage get |

## Paid Endpoints — Identity & Access

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/kyc/verify` | POST | KYC verification |
| `/api/kyc/status` | GET | Check KYC status |
| `/api/auth/token` | POST | Generate auth token |
| `/api/auth/verify` | POST | Verify auth token |
| `/api/sso/initiate` | POST | Initiate SSO flow |
| `/api/sso/callback` | POST | SSO callback handler |
| `/api/access/grant` | POST | Grant access |
| `/api/access/revoke` | POST | Revoke access |
| `/api/access/check` | GET | Check access permission |

## Paid Endpoints — Compliance

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/audit/log` | POST | Write audit entry |
| `/api/audit/trail` | GET | Get audit trail |
| `/api/tax/report` | POST | Generate tax report |
| `/api/tax/summary` | GET | Get tax summary |
| `/api/compliance/check` | POST | Run compliance check |
| `/api/compliance/report` | GET | Get compliance report |

## Paid Endpoints — Analytics & Reporting

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analytics/payments` | GET | Payment analytics |
| `/api/analytics/volume` | GET | Volume analytics |
| `/api/report/generate` | POST | Generate report |
| `/api/report/download` | GET | Download report |

## Paid Endpoints — Advanced

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/multisig/create` | POST | Create multisig |
| `/api/multisig/sign` | POST | Sign multisig tx |
| `/api/schedule/payment` | POST | Schedule future payment |
| `/api/schedule/list` | GET | List scheduled payments |
| `/api/template/create` | POST | Create payment template |
| `/api/template/list` | GET | List templates |
| `/api/template/execute` | POST | Execute template |

---

**Total: 57 paid + 5 free = 62 endpoints**

Gateway: https://gateway.spraay.app
Contract (Base): `0x1646452F98E36A3c9Cfc3eDD8868221E207B5eEC`
Payments to: `0xAd62f03C7514bb8c51f1eA70C2b75C37404695c8`
Gateway version: v3.0.0
