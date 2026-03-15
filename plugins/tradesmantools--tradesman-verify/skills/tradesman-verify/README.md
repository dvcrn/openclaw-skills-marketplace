# tradesman-verify

ACME Foundation reference implementation for contractor credential verification on the Accumulate blockchain.

Issues and verifies W3C Verifiable Credentials — KYC, contractor license, and insurance — stored in Accumulate Digital Identifiers (ADIs). No database required. No proprietary backend required. Any ACME-compliant issuer can write credentials this library will read.

**Compatibility**: Works as a standalone npm library, an [OpenClaw](https://openclaw.ai) skill, a Claude `tool_use` set, an OpenAI function set, or an MCP server tool set.

**Documentation**: [LV8R Labs Docs](https://lv8rlabs.gitbook.io/lv8r-labs) — [tradesman-verify](https://lv8rlabs.gitbook.io/lv8r-labs/lv8r-labs/tradesman-verify) · [ADI Credential Basics](https://lv8rlabs.gitbook.io/lv8r-labs/guides/adi-basics) · [Contractor Compliance](https://lv8rlabs.gitbook.io/lv8r-labs/shared/contractor-compliance)

---

## Install

```bash
npm install tradesman-verify
```

---

## CLI

```bash
# Verify a contractor's full credential set
npx tradesman-verify acc://john-doe-electric.acme

# ✓  VERIFIED — acc://john-doe-electric.acme
#    Level: enhanced
#    Source: blockchain
#    Checked: 2026-02-28T14:00:00.000Z
#
#    KYC Credential
#      ID: acc://tx-kyc-issuer.acme/KYCCredential/john-doe-electric.acme/1709125200000
#      Issuer: acc://tx-kyc-issuer.acme
#      Expires: 2027-02-28T00:00:00.000Z (365d)
#
#    Contractor License
#      Type: electrical
#      State: US-TX
#      Expires: 2027-06-30T00:00:00.000Z (487d)
#
#    Insurance
#      Type: general_liability
#      Coverage: $2,000,000
#      Expires: 2027-01-01T00:00:00.000Z (307d)

# Verify subcommand (explicit)
npx tradesman-verify verify acc://john-doe-electric.acme --no-kyc

# JSON output (exit 0 = verified, 1 = not verified, 2 = error)
npx tradesman-verify verify acc://john-doe-electric.acme --json

# Issue a credential (requires Ed25519 key PEM)
npx tradesman-verify issue \
  --issuer acc://tx-license-board.acme \
  --subject acc://john-doe-electric.acme \
  --type ContractorLicense \
  --claims '{"licenseType":"electrical","licenseState":"US-TX"}' \
  --expiration 2027-06-30T00:00:00Z \
  --key-file ./issuer.pem

# Self-attest (issuer === subject — unverified declaration)
npx tradesman-verify issue \
  --issuer acc://john-doe-electric.acme \
  --subject acc://john-doe-electric.acme \
  --type ContractorLicense \
  --claims '{"licenseType":"electrical","licenseState":"US-TX"}' \
  --key-file ./my-key.pem

# Revoke a credential
npx tradesman-verify revoke \
  --credential-id acc://tx-license-board.acme/ContractorLicense/john-doe-electric.acme/1709125200000 \
  --subject acc://john-doe-electric.acme \
  --issuer acc://tx-license-board.acme \
  --key-file ./issuer.pem

# Generate an Ed25519 key (openssl)
openssl genpkey -algorithm ed25519 -out issuer.pem
```

---

## Programmatic API

### Verify

```typescript
import { verifyContractor } from 'tradesman-verify';

const result = await verifyContractor('acc://john-doe-electric.acme');

if (result.verified && result.level === 'enhanced') {
  // Third-party KYC + license + insurance all present, valid, not expired, not revoked
}

// Revoked credentials appear in result.revoked — verified is false
if (result.revoked.length > 0) {
  console.log('Revoked credentials:', result.revoked); // e.g. ['ContractorLicense']
}

// Self-attestation — check before making compliance decisions
if (result.selfAttestedOnly) {
  // All credentials are self-declared — no third-party verification present
}
// Or check per-credential:
if (result.credentials.kyc?.selfAttested) {
  // KYC is self-attested — weight accordingly
}

// Partial check — license and insurance only
const sub = await verifyContractor(
  'acc://subcontractor.acme',
  { requireKyc: false, requireLicense: true, requireInsurance: true }
);
```

**Verification levels:**

| Level | Meaning |
|---|---|
| `enhanced` | Third-party KYC + license + insurance all valid |
| `kyc` | Third-party KYC valid (license/insurance per requirements) |
| `basic` | Verified but KYC absent, or all credentials are self-attested |
| `none` | Not verified — missing, expired, or revoked credentials |

> **Self-attestation note**: Self-attested credentials (issuer === subject) pass verification and appear in `result.credentials`. They are capped at `level: 'basic'` and flagged with `selfAttested: true`. Consuming applications should check `issuerAdi` and `selfAttested` per credential and apply their own issuer trust policy.

### Issue

```typescript
import { issueCredential, selfAttest } from 'tradesman-verify';
import type { Signer } from 'tradesman-verify';

// Implement the Signer interface with your key management solution
const signer: Signer = {
  adiUrl: 'acc://tx-license-board.acme',
  publicKey: new Uint8Array(/* 32-byte Ed25519 public key */),
  sign: async (data: Uint8Array) => {
    // Sign with your HSM, Vault, or key file
    return new Uint8Array(/* Ed25519 signature */);
  },
};

// Issue from an authorized issuer (e.g. a licensing board)
const result = await issueCredential(
  {
    issuerAdiUrl: 'acc://tx-license-board.acme',
    subjectAdiUrl: 'acc://john-doe-electric.acme',
    credentialType: 'ContractorLicense',
    claims: { licenseType: 'electrical', licenseState: 'US-TX', issuingAuthority: 'TDLR' },
    expirationDate: '2027-06-30T00:00:00Z',
  },
  signer
);
// result.txid, result.credentialId, result.dataAccountUrl

// Self-attestation shorthand (issuer === subject)
const selfResult = await selfAttest(
  {
    subjectAdiUrl: 'acc://john-doe-electric.acme',
    credentialType: 'ContractorLicense',
    claims: { licenseType: 'electrical', licenseState: 'US-TX' },
  },
  signer
);
```

### Revoke

```typescript
import { revokeCredential } from 'tradesman-verify';

await revokeCredential(
  {
    credentialId: 'acc://tx-license-board.acme/ContractorLicense/john-doe.acme/1709125200000',
    subjectAdiUrl: 'acc://john-doe-electric.acme',
    issuerAdiUrl: 'acc://tx-license-board.acme',
    reason: 'License expired and not renewed',
  },
  signer
);
```

---

## OpenClaw / Claude / OpenAI / MCP Skill

tradesman-verify ships as a ready-to-load skill compatible with [OpenClaw](https://openclaw.ai), Claude `tool_use`, OpenAI function calling, and the Model Context Protocol.

### OpenClaw

```typescript
import { createTradesmanVerifySkill } from 'tradesman-verify';

// Verify-only (no signing)
const skill = createTradesmanVerifySkill();
agent.loadSkill(skill);

// With write capabilities (issue + revoke + self-attest)
const skill = createTradesmanVerifySkill({ signer });
agent.loadSkill(skill);
```

### Claude tool_use

```typescript
import Anthropic from '@anthropic-ai/sdk';
import { createTradesmanVerifySkill } from 'tradesman-verify';

const skill = createTradesmanVerifySkill({ signer });
const tools = skill.toClaudeTools();

const response = await anthropic.messages.create({
  model: 'claude-opus-4-6',
  tools,
  messages: [{ role: 'user', content: 'Verify acc://john-doe-electric.acme' }],
});
```

### OpenAI function calling

```typescript
import OpenAI from 'openai';
import { createTradesmanVerifySkill } from 'tradesman-verify';

const openai = new OpenAI();
const skill = createTradesmanVerifySkill();
const tools = skill.toOpenAIFunctions().map((f) => ({ type: 'function' as const, function: f }));

const messages = [{ role: 'user' as const, content: 'Is acc://john-doe-electric.acme verified?' }];

// First turn — model picks the tool
const res = await openai.chat.completions.create({ model: 'gpt-4o', messages, tools });
const msg = res.choices[0]!.message;
messages.push(msg);

// Execute tool calls
for (const call of msg.tool_calls ?? []) {
  const result = await skill.executeTool(call.function.name, JSON.parse(call.function.arguments));
  messages.push({ role: 'tool', tool_call_id: call.id, content: JSON.stringify(result) });
}

// Second turn — model summarizes
const summary = await openai.chat.completions.create({ model: 'gpt-4o', messages });
console.log(summary.choices[0]!.message.content);
```

Full example with all tools: [examples/openai-integration.ts](examples/openai-integration.ts)

### MCP (Model Context Protocol)

```typescript
import { createTradesmanVerifySkill } from 'tradesman-verify';

const skill = createTradesmanVerifySkill({ signer });
const mcpTools = skill.toMCPTools();
// Register mcpTools with your MCP server
```

### Available tools

| Tool | Requires signer | Description |
|------|----------------|-------------|
| `verify_contractor` | No | Verify KYC, license, and insurance credentials on-chain |
| `verify_business_entity` | No | Look up a business entity via OpenCorporates (140+ jurisdictions) |
| `self_attest_credential` | Yes | Write unverified self-declared claims |
| `issue_credential` | Yes | Issue a signed VC from an authorized issuer |
| `revoke_credential` | Yes | Write a revocation entry |

`verify_business_entity` requires `OPENCORPORATES_API_KEY` (free tier: 200 calls/month). It returns `suggested_claims` pre-formatted for `issue_credential` with `credential_type: BusinessEntityCredential`. See [docs/pipeline.md](docs/pipeline.md) for the full off-chain → on-chain workflow.

---

## Key management

This library ships two signer helpers for Ed25519 key loading:

```typescript
import { loadSignerFromPem, loadSignerFromPemString } from 'tradesman-verify';

// From a PEM file on disk
const signer = loadSignerFromPem('./issuer.pem', 'acc://my-org.acme');

// From a string (env var, Vault agent, K8s secret)
const signer = loadSignerFromPemString(process.env.ISSUER_KEY!, 'acc://my-org.acme');
```

For production deployments (HSM, Vault, AWS KMS), implement the `Signer` interface directly. See **[docs/signing-guide.md](docs/signing-guide.md)** for patterns, error handling, and security best practices.

---

## Custom RPC endpoint

```typescript
import { createClient, verifyContractor } from 'tradesman-verify';

const client = createClient({
  rpcUrl: 'https://testnet.accumulatenetwork.io/v2',
  debug: true,
});

const result = await verifyContractor('acc://contractor.acme', {}, client);
```

---

## How it works

1. Confirm the contractor's [ADI](https://docs.accumulatenetwork.io/accumulate/concepts/adi) exists on the Accumulate blockchain.
2. Read the `{adiUrl}/credentials` data account.
3. Scan all entries for `CredentialRevocation` objects — build the revoked ID set.
4. Parse remaining entries as [W3C Verifiable Credentials](https://www.w3.org/TR/vc-data-model/).
5. Find credentials matching required types (`KYCCredential`, `ContractorLicense`, `InsuranceCredential`).
6. Cross-reference each found credential against the revoked set.
7. Check expiration on non-revoked credentials.
8. Return a `VerificationResult` with level `none | basic | kyc | enhanced`.

**Credential sources**: Any ACME-compliant issuer — licensing boards, KYC providers, insurance carriers, or the contractor themselves (self-attestation). Relying parties decide how much weight to give each based on the `issuerAdi` and `selfAttested` fields.

**`BusinessEntityCredential`** is surfaced automatically in `result.credentials.businessEntity` when present on-chain. It is not required by default — set `requireBusinessEntity: true` to enforce it.

Full trust model: [docs/trust-model.md](docs/trust-model.md)

Off-chain → on-chain pipeline: [docs/pipeline.md](docs/pipeline.md)

---

## Credential data account convention

Credentials are stored as JSON-encoded W3C VCs in a data account at:

```
{adiUrl}/credentials
```

Each entry must include:

```jsonc
{
  "@context": [
    "https://www.w3.org/2018/credentials/v1",
    "https://gitlab.com/lv8rlabs/tradesman-verify/-/raw/main/contexts/v1.json"
  ],
  "type": ["VerifiableCredential", "ContractorLicense"],
  "issuer": "acc://tx-license-board.acme",
  "issuanceDate": "2026-02-28T00:00:00.000Z",
  "expirationDate": "2027-06-30T00:00:00Z",
  "credentialSubject": {
    "id": "acc://john-doe-electric.acme",
    "licenseType": "electrical",
    "licenseState": "US-TX"
  }
}
```

Full schema: [docs/acme-integration.md](docs/acme-integration.md)

---

## Open-core model

This library is fully open-source (MIT). The off-chain data sources are split into two tiers:

**OSS tier** — no additional API keys required beyond Accumulate:
- `verify_contractor` — reads from the Accumulate mainnet (free)
- `issue_credential` / `revoke_credential` — writes to Accumulate (credits required by issuer)
- `verify_business_entity` — OpenCorporates free tier (200 calls/month with `OPENCORPORATES_API_KEY`)

**Premium tier** — separate providers, not included in this library:
- Automated license verification + identity KYC + risk scoring: [MicroPay Technologies](https://micropaytechnologies.com) via the PPCS Pro API
- Real-time license monitoring webhooks: PPCS Pro

Consuming applications can call premium providers and then use `issue_credential` from this library to anchor results on-chain. See [docs/pipeline.md](docs/pipeline.md) for the full workflow.

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `ACCUMULATE_RPC_URL` | `https://mainnet.accumulatenetwork.io/v2` | Accumulate JSON-RPC endpoint |
| `OPENCORPORATES_API_KEY` | — | Required for `verify_business_entity` tool (free tier at opencorporates.com) |
| `TRADESMAN_VERIFY_DEBUG` | `false` | Set to `true` to log unparseable credential entries to `console.debug` |

---

## Contributing

Issues and pull requests welcome at [gitlab.com/lv8rlabs/tradesman-verify](https://gitlab.com/lv8rlabs/tradesman-verify).

This library is the reference implementation of the ACME Foundation contractor credential standard. Issuer integration guidance: [docs/acme-integration.md](docs/acme-integration.md).

---

## License

MIT — see [LICENSE](LICENSE)
