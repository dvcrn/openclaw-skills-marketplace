# Trust Model

This document describes how `tradesman-verify` establishes trust when verifying contractor credentials on the Accumulate blockchain. This document is part of the ACME Foundation endorsement package.

---

## Overview

`tradesman-verify` uses the Accumulate protocol's identity and data account model to verify W3C Verifiable Credentials issued to licensed tradespeople.

The trust chain has three layers:

```
Issuing Authority (e.g., acc://kyc-issuer.acme)
    │
    │  issues W3C VC → writes to subject's credential data account
    ▼
Contractor ADI (e.g., acc://john-doe-electric.acme)
    │  acc://john-doe-electric.acme/credentials
    ▼
Verifier (tradesman-verify)
    │  queries blockchain directly
    ▼
VerificationResult { verified, level, credentials, revoked, selfAttestedOnly }
```

---

## Step-by-step verification

### 1. Confirm the ADI exists

```
GET acc://john-doe-electric.acme
```

The Accumulate `query` RPC is called with the contractor's ADI URL. If the ADI does not exist on-chain, verification fails immediately with `missing: ['ADI']`.

An ADI's existence on the Accumulate mainnet is cryptographically guaranteed — it cannot be forged. The key book associated with the ADI controls all writes to that identity's accounts.

### 2. Read the credentials data account

```
GET acc://john-doe-electric.acme/credentials
```

All credentials issued to this contractor are written to a `dataAccount` at this path. The data account is part of the contractor's ADI and can only be written to by the ADI's key holders or by delegated authorities that the contractor has granted write access.

### 3. Check for revocation entries

Before parsing credentials, `tradesman-verify` scans all entries for `CredentialRevocation` objects:

```json
{
  "type": "CredentialRevocation",
  "credentialId": "acc://issuer.acme/ContractorLicense/contractor.acme/<uuid>",
  "issuerAdiUrl": "acc://issuer.acme",
  "subjectAdiUrl": "acc://contractor.acme",
  "revokedAt": "2026-03-01T00:00:00Z",
  "reason": "License suspended"
}
```

Any credential whose `id` matches a revocation entry is marked as revoked and added to `result.revoked`. Revoked credentials are treated the same as missing credentials — they cause `verified: false`.

### 4. Parse W3C Verifiable Credentials

Each non-revocation entry in the data account is parsed as a W3C Verifiable Credential conforming to the [W3C VC Data Model v1.1](https://www.w3.org/TR/vc-data-model/).

A valid credential entry must include:
- `@context` containing `https://www.w3.org/2018/credentials/v1`
- `type` array containing `VerifiableCredential` and a specific type (e.g., `KYCCredential`)
- `issuer` — the ADI URL of the issuing authority
- `issuanceDate` — ISO 8601 timestamp
- `credentialSubject` — the claims object
- (optional) `expirationDate` — ISO 8601 timestamp
- (optional) `proof.txid` — the Accumulate transaction ID that anchored this credential

### 5. Check expiration

If `expirationDate` is present and is in the past, the credential is marked as `expired`. Expired credentials are listed in `result.expired` and do NOT appear in `result.credentials`.

Credentials with no `expirationDate` are treated as non-expiring. Issuers should set expiration dates on all compliance-sensitive credentials (KYC: 1 year, License: match state expiration, Insurance: match policy expiration).

### 6. Check issuer trust and self-attestation

The `issuer` field in each credential is the ADI URL of the entity that signed it. `tradesman-verify` identifies self-attested credentials when `issuer === credentialSubject.id`.

```typescript
const result = await verifyContractor('acc://contractor.acme');

// Self-attestation flags
console.log(result.selfAttestedOnly);            // true if ALL credentials are self-attested
console.log(result.credentials.kyc?.selfAttested); // per-credential flag

// Issuer trust — apply your own policy
const TRUSTED_KYC_ISSUERS = ['acc://trusted-kyc-issuer.acme'];
if (result.credentials.kyc) {
  const trusted = TRUSTED_KYC_ISSUERS.includes(result.credentials.kyc.issuerAdi);
}
```

`tradesman-verify` does not enforce a specific trusted issuer list — this is a policy decision for the consuming application. The library surfaces `issuerAdi` and `selfAttested` per credential; callers apply their own trust policy.

### 7. Compute verification level

| Level | Conditions |
|---|---|
| `enhanced` | Third-party KYC + license + insurance all valid |
| `kyc` | Third-party KYC valid (license/insurance may vary per requirements) |
| `basic` | Verified, but KYC absent or all credentials are self-attested |
| `none` | `verified: false` — missing, expired, or revoked credentials |

**Important**: `enhanced` and `kyc` levels require a third-party-issued KYC credential (`selfAttested: false`). A contractor with all self-attested credentials receives `level: 'basic'` even if all three credential types are present.

---

## Self-attestation

Self-attested credentials (where `issuer === subject`) are permitted on-chain and ARE included in the verification result. This is intentional — the library provides data, not policy.

Consuming applications should:
1. Check `result.selfAttestedOnly` as a quick gate
2. Check `result.credentials.*.selfAttested` per credential for finer control
3. Maintain their own trusted issuer list and validate `issuerAdi`

Self-attested credentials are useful for discovery and profile data before third-party verification is complete. They should be weighted lower than third-party-issued credentials in compliance decisions.

---

## Credential revocation

`tradesman-verify` checks for revocation entries in the same data account as the credentials. The revocation mechanism:

1. The original issuer calls `revokeCredential()`, which writes a `CredentialRevocation` entry to the contractor's `/credentials` data account
2. `verifyContractor()` scans all entries for revocations before processing credentials
3. Any credential whose `id` matches a revocation entry is excluded from `result.credentials` and added to `result.revoked`
4. `verified: false` is returned if any required credential is in `result.revoked`

Revocations are permanent on-chain entries — they cannot be deleted. If a revoked credential needs to be reinstated, the issuer must issue a new credential with a new ID.

---

## What tradesman-verify does NOT do

- **Store PII** — the library reads only credential metadata from the public blockchain; no personal data is persisted
- **Hold private keys** — the `Signer` interface requires callers to provide their own key management
- **Control which issuers are trusted** — this is a policy decision for the consuming application
- **Implement a full Accumulate transaction envelope** — the signing implementation in `accumulate.ts` is a reference implementation. See [acme-integration.md](acme-integration.md) for the production signing note.

---

## On-chain visibility

All credentials verified by this library are stored on the public Accumulate mainnet. This means:
- Anyone can query a contractor's credential data account directly
- Credential hashes are permanently anchored and auditable
- Revocation events are also public and auditable

Claims in the `credentialSubject` are stored on-chain. Issuers should omit sensitive fields (e.g., raw license numbers, SSN) from the credential claims. See [acme-integration.md](acme-integration.md) for recommended claim schemas.

---

## Threat model

| Threat | Mitigation |
|---|---|
| Forged ADI | ADIs require on-chain key material to create; cannot be forged without private key |
| Forged credential | Write access to `/credentials` data account requires ADI key authority |
| Stale credential | `expirationDate` enforced by verifier |
| Revoked credential | `CredentialRevocation` entries checked before credential validation |
| Untrusted issuer | Calling application must validate `issuerAdi` against its trusted issuer list; `selfAttested` flag surfaces self-issued credentials |
| RPC endpoint compromise | Use `ACCUMULATE_RPC_URL` to point to a trusted or self-hosted node |
| Credential ID collision | IDs generated with `crypto.randomUUID()` — collision probability negligible |
