# Off-Chain Verify → On-Chain Issue Pipeline

This document describes how `tradesman-verify` fits into a complete contractor credential workflow — from off-chain data sources through to on-chain W3C Verifiable Credentials anchored to an Accumulate ADI.

---

## Overview

`tradesman-verify` handles two distinct roles in the pipeline:

1. **Off-chain lookup** (`verify_business_entity` tool) — query external data sources and return structured results
2. **On-chain write** (`issue_credential` tool) — anchor verified results as W3C VCs on the Accumulate blockchain

These roles can be performed by the same agent in one session, or by separate systems with a human-in-the-loop review step between them.

---

## End-to-End Flow

```
Off-Chain Sources           tradesman-verify           Accumulate Blockchain
─────────────────           ────────────────           ─────────────────────

OpenCorporates API  ──────► verify_business_entity ──► suggested_claims JSON
                                                            │
State licensing board        (manual lookup or              │
(manual or MicroPay Tech)     future tool)                  │
                                                            ▼
KYC / risk provider                                 issue_credential
(MicroPay Technologies)                                  │
                                                          │
                                                          ▼
                                              {contractor}.acme/credentials
                                              ┌────────────────────────────┐
                                              │ BusinessEntityCredential   │
                                              │ ContractorLicense          │
                                              │ KYCCredential              │
                                              │ InsuranceCredential        │
                                              └────────────────────────────┘
                                                          │
                                                          ▼
                                              verify_contractor
                                              (any relying party)
```

---

## Step-by-Step: Business Entity

### Step 1 — Verify business entity (off-chain)

```typescript
// Via the skill tool (works in Claude, OpenAI, MCP, OpenClaw)
const result = await skill.executeTool('verify_business_entity', {
  business_name: 'ABC Roofing LLC',
  jurisdiction: 'us_tx',
});

// result.suggested_claims is pre-formatted for issue_credential
// result.next_step tells you what to do if the business is active or not
```

### Step 2 — Issue the credential (on-chain)

```typescript
// Pass suggested_claims directly to issue_credential
const issued = await skill.executeTool('issue_credential', {
  issuer_adi_url: 'acc://your-org.acme',
  subject_adi_url: 'acc://abc-roofing.acme',
  credential_type: 'BusinessEntityCredential',
  claims: result.suggested_claims,  // JSON string from step 1
  expiration_date: '2027-02-28T00:00:00Z',
});
// issued.data_account_url — where the credential now lives on-chain
```

### Step 3 — Verify (any relying party)

```typescript
import { verifyContractor } from 'tradesman-verify';

const verification = await verifyContractor('acc://abc-roofing.acme', {
  requireKyc: true,
  requireLicense: true,
  requireInsurance: true,
  requireBusinessEntity: false,  // surfaced automatically when present
});

// verification.credentials.businessEntity — present if Step 2 was completed
// verification.level — 'enhanced' when KYC + license + insurance all valid
```

---

## Step-by-Step: Full Credential Set

A complete onboarding run issues all four credential types:

```
1. verify_business_entity  →  issue_credential (BusinessEntityCredential)
2. [license lookup]        →  issue_credential (ContractorLicense)
3. [KYC provider]          →  issue_credential (KYCCredential)
4. [insurance COI]         →  issue_credential (InsuranceCredential)
```

After all four are on-chain, `verify_contractor` returns `level: 'enhanced'` for any relying party — no proprietary backend needed.

---

## Open-Core Boundary

`tradesman-verify` (this library) is fully open-source under MIT. The off-chain data sources it can optionally call split into two tiers:

### OSS tier (no additional keys required)

| Capability | Tool | Source |
|---|---|---|
| Blockchain read | `verify_contractor` | Accumulate mainnet (free) |
| Blockchain write | `issue_credential`, `self_attest_credential`, `revoke_credential` | Accumulate mainnet (credits required) |
| Business entity lookup | `verify_business_entity` | OpenCorporates (free tier: 200 calls/month) |

### Premium tier (separate API keys required)

The following integrations are **not included** in this library. They are available in commercial products built on top of `tradesman-verify`:

| Capability | Provider | Notes |
|---|---|---|
| Automated license verification + identity KYC + risk scoring | MicroPay Technologies (PPCS Pro API) | US state licensing boards, all 50 states |
| Enhanced business intelligence | Middesk | US-only, includes officers/addresses |
| Real-time monitoring webhooks | PPCS Pro | License status change alerts |

Consuming apps that need premium data sources can call those APIs themselves, then use `issue_credential` from this library to anchor the results on-chain.

---

## Issuer Trust

`tradesman-verify` does not maintain a centralized trusted issuer registry. The consuming application is responsible for its own trust policy:

- Check `result.credentials.*.issuerAdi` per credential
- Check `result.credentials.*.selfAttested` — self-attested credentials are valid on-chain but unverified
- Check `result.selfAttestedOnly` — true when every present credential is self-declared

For `level: 'enhanced'`, the library already enforces that the KYC credential must be third-party issued (`!kyc.selfAttested`).

---

## Further Reading

- [ACME integration spec](./acme-integration.md) — credential schemas and RPC methods
- [Trust model](./trust-model.md) — verification levels and threat model
- [Privacy](./privacy.md) — PII handling and write mode disclosure
