# Privacy Statement

This document is part of the ACME Foundation endorsement package for `tradesman-verify`.

---

## What this library does

`tradesman-verify` reads and optionally writes to the public Accumulate blockchain. It has two operating modes:

**Verify mode (read-only, no credentials required)**
- Queries the public Accumulate blockchain for credential data
- Parses W3C Verifiable Credentials from the blockchain
- Returns a structured verification result to the calling application

**Issuance mode (write, requires a `Signer`)**
- Writes W3C Verifiable Credentials to a contractor's credential data account
- Writes revocation entries when credentials are invalidated
- The `Signer` interface is caller-provided — this library never holds private keys

Both modes are available in the same package. Issuance mode is opt-in and requires the caller to supply key material.

---

## What this library does NOT handle

- **No PII storage** — The library does not persist any data between calls. Nothing is written to disk or a database.
- **No PII transmission** — Credentials written by this library contain only verified status indicators (e.g., `kycLevel: "enhanced"`, `sanctionsCleared: true`). Raw PII (names, dates of birth, document numbers) must not appear in credential claims — see [acme-integration.md](acme-integration.md).
- **No key management** — Private keys are never held by this library. Callers implement the `Signer` interface with their own key management solution (HSM, Vault, file-based key).
- **No KYC pipeline** — The identity verification pipeline (document capture, liveness check, sanctions screening) that produces the inputs for a `KYCCredential` is out of scope for this library. That process is handled by separate, authorized issuers.
- **No external API calls beyond Accumulate RPC** — The only network requests this library makes are to the Accumulate JSON-RPC endpoint.
- **No telemetry or analytics** — No usage data is sent anywhere.

---

## On-chain data visibility

All credentials written and verified by this library are stored on the **public Accumulate mainnet**. This means:

- Credential data is publicly readable by anyone who queries the blockchain
- Credential hashes are permanently anchored and auditable
- Revocation entries are also public and auditable

Issuers are responsible for ensuring that credential claims comply with their applicable privacy regulations (GDPR, CCPA, etc.). Specifically:
- Raw PII (names, dates of birth, addresses, document numbers) **must NOT** be written to on-chain credential claims
- Claims should contain only verified status indicators

See [acme-integration.md](acme-integration.md) for approved claim schemas.

---

## GDPR applicability

`tradesman-verify` does not process personal data within the meaning of GDPR Article 4(1) because:

1. It reads only verified status indicators from the public blockchain (not personal data)
2. It does not store, transmit, or analyze personal data
3. Credential claims written by this library contain no personal data by design (enforced by schema)
4. Any personal data processing occurs in the issuer's credential issuance pipeline, which is a separate service governed by its own privacy policies and data processing agreements

Organizations that use this library as part of a system that processes personal data (e.g., associating an ADI URL with a named individual in a database) must implement appropriate GDPR/privacy controls in their own system.

---

## Data retention

This library has no data retention. The in-memory cache (60-second TTL by default, read operations only) holds blockchain query results, not personal data. The cache is cleared when the process exits and holds no write operation data.

---

## Contact

Privacy questions: Open an issue at https://gitlab.com/lv8rlabs/tradesman-verify/-/issues
