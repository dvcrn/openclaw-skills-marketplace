# ACME Integration Specification

This document describes how `tradesman-verify` integrates with the Accumulate (ACME) blockchain and what ACME-compliant issuers must implement to be compatible. This document is part of the ACME Foundation endorsement package.

---

## Accumulate protocol requirements

### ADI structure

Each contractor must have an ADI on the Accumulate mainnet:

```
acc://<contractor-identifier>.acme
│
├── /book              (key book — controls write access)
└── /credentials       (data account — credential and revocation storage)
```

The `/credentials` data account must be readable by any party (public). Write access is controlled by the ADI's key book.

### Credential data account format

Each W3C Verifiable Credential entry in `acc://<contractor>.acme/credentials`:

```json
{
  "@context": [
    "https://www.w3.org/2018/credentials/v1",
    "https://gitlab.com/lv8rlabs/tradesman-verify/-/raw/main/contexts/v1.json"
  ],
  "id": "acc://<issuer>.acme/credentials/<uuid>",
  "type": ["VerifiableCredential", "<CredentialType>"],
  "issuer": "acc://<issuer>.acme",
  "issuanceDate": "2026-01-15T00:00:00Z",
  "expirationDate": "2027-01-15T00:00:00Z",
  "credentialSubject": {
    "id": "acc://<contractor>.acme",
    "<claim-key>": "<claim-value>"
  },
  "proof": {
    "type": "AccumulateProof2024",
    "created": "2026-01-15T00:00:00Z",
    "verificationMethod": "acc://<issuer>.acme/book",
    "proofPurpose": "assertionMethod",
    "txid": "<accumulate-transaction-id>"
  }
}
```

### Revocation entry format

Revocation entries coexist with credentials in the same data account. When a credential must be invalidated, the issuer writes:

```json
{
  "type": "CredentialRevocation",
  "credentialId": "acc://<issuer>.acme/credentials/<uuid>",
  "issuerAdiUrl": "acc://<issuer>.acme",
  "subjectAdiUrl": "acc://<contractor>.acme",
  "revokedAt": "2026-03-01T00:00:00Z",
  "reason": "License suspended by TDLR"
}
```

`tradesman-verify` scans all data account entries for `CredentialRevocation` objects before processing credentials. A revoked credential is excluded from the verification result and added to `result.revoked`.

---

## Supported credential types

### `KYCCredential`

Issued after identity verification. Claims:

```json
{
  "id": "acc://<contractor>.acme",
  "kycLevel": "basic | enhanced",
  "sanctionsCleared": true,
  "pepStatus": "not_pep | pep | pep_related",
  "riskScore": 85,
  "documentType": "driving_license | passport | id_card"
}
```

**Do NOT include in claims:** full name, date of birth, address, document number. These are PII and must not be written on-chain.

### `ContractorLicense`

Issued after license verification with the appropriate state licensing board. Claims:

```json
{
  "id": "acc://<contractor>.acme",
  "licenseType": "electrical",
  "licenseState": "US-TX",
  "licenseClass": "A",
  "issuingAuthority": "Texas Department of Licensing and Regulation"
}
```

**Do NOT include in claims:** raw license number. Use the ADI as the unique identifier.

### `InsuranceCredential`

Issued after certificate of insurance verification. Claims:

```json
{
  "id": "acc://<contractor>.acme",
  "insuranceType": "general_liability",
  "coverageAmount": 2000000,
  "carrier": "Liberty Mutual"
}
```

**Do NOT include in claims:** policy number, policyholder details.

### `BusinessEntityCredential`

Issued after business entity verification against a company registry (e.g. OpenCorporates). Records that a legal business entity exists and is registered, without placing PII on-chain. This is an optional credential — it is surfaced in `result.credentials.businessEntity` when present but not required by default.

```json
{
  "id": "acc://<contractor>.acme",
  "businessName": "ABC Roofing LLC",
  "companyNumber": "0803456789",
  "jurisdiction": "us_tx",
  "businessStatus": "Active",
  "incorporationDate": "2020-05-15",
  "companyType": "LLC",
  "verificationSource": "OpenCorporates",
  "verifiedAt": "2026-02-28T00:00:00.000Z"
}
```

**Do NOT include in claims:** officer names, registered agent details, business address. These are PII or operationally sensitive.

**Verification source**: Any business registry API may be used. The `verificationSource` field must identify the source (e.g., `"OpenCorporates"`, `"Middesk"`, `"Companies House"`). The `verify_business_entity` skill tool uses OpenCorporates and pre-formats claims ready for `issue_credential`.

---

## RPC methods used

`tradesman-verify` uses the following Accumulate JSON-RPC 2.0 methods:

| Method | Parameters | Purpose | Mode |
|---|---|---|---|
| `query` | `{ url: adiUrl, prove: false }` | Confirm ADI existence | Read |
| `query` | `{ url: dataAccountUrl, prove: false }` | Read credential data account | Read |
| `execute` | signed `writeData` payload | Write credential or revocation | Write (optional) |

Write operations require a `Signer` and are used only by `issueCredential()`, `selfAttest()`, and `revokeCredential()`. Read-only usage (`verifyContractor()`) requires no authentication.

### Default RPC endpoint

```
https://mainnet.accumulatenetwork.io/v2
```

Override with `ACCUMULATE_RPC_URL` environment variable. Compatible with any Accumulate node that supports JSON-RPC 2.0.

---

## Transaction signing — reference implementation note

The signing implementation in `src/accumulate.ts` (`buildSignedPayload`) is a **reference implementation** that signs the SHA-256 hash of the canonical transaction JSON body using Ed25519. It is intended to demonstrate the signing pattern, not to be a complete Accumulate protocol client.

**Production issuers must implement** the full Accumulate transaction envelope per the protocol specification at https://docs.accumulatenetwork.io/. The envelope includes:

- Transaction header (principal, initiator hash)
- Transaction body (type, fields)
- Signature set (key page index, timestamp, signer version, vote)

This library's reference signing is sufficient for testnet and development. Use the official Accumulate SDK or a fully-validated implementation for production issuance.

---

## Issuer requirements

Any organization that wishes to issue credentials compatible with `tradesman-verify` must:

1. **Have an ADI** on the Accumulate mainnet (e.g., `acc://your-org.acme`)
2. **Implement the claim schemas** defined in this document
3. **Write credentials** to the contractor's `/credentials` data account using the `writeData` execute method, signed by the issuer's key book
4. **Set `expirationDate`** on all compliance-sensitive credentials (KYC: 1 year, License: match state expiration, Insurance: match policy expiration)
5. **Implement revocation** by writing a `CredentialRevocation` entry when a credential is invalidated — `tradesman-verify` checks for these entries during verification
6. **Omit PII** from credential claims — see the claim schemas above

There is no centralized registry of trusted issuers. The consuming application (e.g., a GC's portal or a job platform) is responsible for maintaining its own trusted issuer list and validating the `issuer` field in each credential.

---

## Self-attestation

`tradesman-verify` supports self-attested credentials (where `issuer === subject`). These are valid on-chain entries and are included in verification results, but are flagged with `selfAttested: true` per credential and surfaced in `result.selfAttestedOnly`.

Self-attested credentials are capped at verification `level: 'basic'` — they cannot produce `level: 'kyc'` or `level: 'enhanced'`. Consuming applications should check `selfAttested` per credential and apply their own trust policy.

---

## ACME token usage

This library does not consume ACME tokens for read operations. Reading from data accounts on the Accumulate mainnet is free. Write operations (credential issuance and revocation) require ACME credits paid by the issuer — credit acquisition is out of scope for `tradesman-verify`.

---

## Compatibility

| Component | Requirement |
|---|---|
| Accumulate protocol | v3+ (JSON-RPC 2.0) |
| W3C VC Data Model | v1.1 |
| Node.js | 18+ |
| TypeScript | 5.3+ (if using types) |

---

## Contact

ACME integration questions: Open an issue at https://gitlab.com/lv8rlabs/tradesman-verify/-/issues
