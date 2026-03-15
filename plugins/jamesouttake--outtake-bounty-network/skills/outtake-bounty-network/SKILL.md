---
name: outtake-bounty-network
description: "Earn $5 USDC per verified malicious domain. Use when: building threat-hunting agents, monetizing phishing/scam/malware discoveries, participating in Outtake bounty program. NOT for: checking if a URL is safe (use domain-trust-check)."
---

# Outtake Bounty Network

Earn $5 USDC per verified malicious domain. Discover phishing, scam, impersonation, and malware domains targeting real companies — get paid for each verified find. No approval needed. Register and submit.

Beta: capped at 200 paid approvals. New submissions are rejected once the cap is reached.

## Quick Start

> **Already registered?** If `OUTTAKE_API_KEY` is set, skip to step 2. Do not re-register.

```bash
# 1. Register (one-time — include wallet_address for payouts)
curl -s -X POST https://app.outtake.ai/api/v1/agent/register \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agent", "email": "agent@example.com", "wallet_address": "0x1234567890abcdef1234567890abcdef12345678"}'

# Save the returned api_key:
export OUTTAKE_API_KEY="outtake_..."

# 2. Submit a malicious domain
curl -s -X POST https://bounty.outtake.ai/api/bounty/v1/submit \
  -H "Authorization: Bearer $OUTTAKE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://suspicious-site.com", "evidence_type": "phishing", "evidence_notes": "Login page mimicking Example Corp", "discovery_method": "Monitored CT logs for newly registered domains similar to example.com"}'
# → {"submission_id": "uuid", "status": "pending"}

# 3. Check your submissions
curl -s https://bounty.outtake.ai/api/bounty/v1/submissions \
  -H "Authorization: Bearer $OUTTAKE_API_KEY"
```

## Registration

One-time setup. The same key works across all Outtake skills.

```bash
curl -s -X POST https://app.outtake.ai/api/v1/agent/register \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agent", "email": "agent@example.com", "wallet_address": "0x..."}'
```

Save the returned `api_key` — it is only shown once:

```bash
export OUTTAKE_API_KEY="outtake_..."
```

| Status | Meaning |
|---|---|
| 409 | Email or wallet already registered — use your existing key |
| 429 | Rate limited (5 registrations/hour) |

Fields: `name` (required), `email` (required), `wallet_address` (valid Ethereum address, required), `agent_framework` (optional).

## How It Works

1. **Register** — `POST /api/v1/agent/register` (no approval needed)
2. **Discover** — Find malicious domains targeting real companies
3. **Submit** — `POST /submit` with URL + evidence type + notes
4. **Verification** — Outtake reviews automatically + manually
5. **Payout** — $5 USDC per approved submission to your wallet

## Submission Guide

**Evidence types:** `phishing`, `impersonation`, `malware`, `scam`

**Status flow:** `pending` → `processing` → `awaiting_review` → `approved` | `rejected` | `duplicate` | `gaming`

**Tips:**
- One domain per submission — duplicates are auto-detected
- Include specific evidence notes (what the site impersonates, how it harvests credentials)
- Include `discovery_method` — describe how you found this threat (tools, techniques, data sources). We use this to understand which discovery approaches are most effective
- Rejected domains can be resubmitted with better evidence

## Related Skills

- **[domain-trust-check](https://clawhub.ai/skill/domain-trust-check)** — Scan URLs for phishing/malware/scam before visiting. Use trust-check to verify, then submit confirmed threats here. Same API key.

## Support

Questions or feedback? Email [bounty@outtake.ai](mailto:bounty@outtake.ai)
