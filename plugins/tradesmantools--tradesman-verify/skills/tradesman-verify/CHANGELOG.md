# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-02-28

Initial release. Open-core verification layer for licensed tradespeople on the
Accumulate blockchain. ACME Foundation reviewed and approved for public distribution.

### Added

**Core verification**
- `verifyContractor(adiUrl, options)` — query an Accumulate ADI and return a
  structured `VerificationResult` with credential summaries and a pass/fail verdict
- `verifyCredentials(entries)` — batch-parse W3C VCs from raw data account entries
- `parseRevocationIds(entries)` — extract revoked credential IDs for cross-checking

**Credential types** (W3C Verifiable Credential schemas)
- `KYCCredential` — identity verification level (`basic` | `enhanced`), sanctions
  clearance, and numeric risk score
- `ContractorLicense` — trade type, issuing state/jurisdiction, license number,
  expiry date
- `InsuranceCredential` — GL and WC policy numbers, coverage amounts, expiry dates
- `BusinessEntityCredential` — EIN, entity type, state of formation, DBA name,
  good-standing flag

**Credential issuance**
- `issueCredential(issuerAdi, subjectAdi, credential, signingKey)` — write a
  W3C VC to `{issuerAdi}/credentials` on Accumulate mainnet
- `revokeCredential(issuerAdi, credentialId, signingKey)` — write a
  `CredentialRevocation` record to the same account

**Accumulate client**
- Lightweight `AccumulateClient` wrapping the JSON-RPC v3 API
- `queryDataEntries(adiUrl)` with in-memory LRU-style cache (TTL configurable via
  `TRADESMAN_VERIFY_CACHE_TTL_MS`; default 5 min)
- Lazy singleton — client is only instantiated on first call; no startup cost when
  the package is imported as a library

**CLI** (`tradesman-verify`)
- `--adi-url <url>` — verify by ADI URL
- `--business-name <name> --jurisdiction <state>` — resolve ADI by business name
  lookup (requires `ACCUMULATE_ADI_REGISTRY_URL` or falls back to mock)
- `--mock` — run against bundled fixture data without a live network call
- `--json` — emit machine-readable JSON to stdout
- `--debug` — verbose credential-by-credential trace output

**OpenClaw skill** (`src/skill/`)
- `verify_contractor` — verify a contractor by ADI URL, returns structured JSON
- `verify_license` — check a single license credential
- `verify_insurance` — check a single insurance credential
- `verify_kyc` — check identity/KYC tier
- `verify_business_entity` — check business entity standing
- `issue_credential` — issue a W3C VC to the Accumulate chain
- `revoke_credential` — revoke an existing credential

**Documentation**
- `docs/trust-model.md` — credential trust hierarchy and verification logic
- `docs/acme-integration.md` — ACME ADI naming conventions and registry protocol
- `docs/privacy.md` — on-chain data minimisation and PII handling policy
- `docs/pipeline.md` — end-to-end issuance → verification pipeline
- `docs/publish-checklist.md` — pre-publish review checklist (Foundation sign-off)

**Context**
- `contexts/v1.json` — JSON-LD context for all four credential types, pinned at
  `https://gitlab.com/lv8rlabs/tradesman-verify/-/raw/v0.1.0/contexts/v1.json`

### Security

- Hash salt placeholder (`TRADESMAN_VERIFY_HASH_SALT`) documented in README;
  operators must set a non-default value before issuing production credentials
- Default ADI namespace (`acc://tradesman.acme`) intended for development only;
  production deployments should use a dedicated issuer ADI
- No PII is written on-chain; all credential subjects are identified by ADI URL only

[0.1.0]: https://gitlab.com/lv8rlabs/tradesman-verify/-/tags/v0.1.0
