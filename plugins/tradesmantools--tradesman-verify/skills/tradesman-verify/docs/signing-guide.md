# Signing Guide

How to implement credential signing with `tradesman-verify`. This guide covers the Signer interface, built-in helpers, and production key management patterns.

---

## Quick start

```bash
# 1. Generate an Ed25519 key
openssl genpkey -algorithm ed25519 -out issuer.pem
chmod 600 issuer.pem  # restrict access

# 2. Issue a credential (CLI)
npx tradesman-verify issue \
  --issuer acc://tx-license-board.acme \
  --subject acc://john-doe-electric.acme \
  --type ContractorLicense \
  --claims '{"licenseType":"electrical","licenseState":"US-TX"}' \
  --key-file ./issuer.pem
```

```typescript
// 2. Issue a credential (programmatic)
import { loadSignerFromPem, issueCredential } from 'tradesman-verify';

const signer = loadSignerFromPem('./issuer.pem', 'acc://tx-license-board.acme');
const result = await issueCredential(
  {
    issuerAdiUrl: 'acc://tx-license-board.acme',
    subjectAdiUrl: 'acc://john-doe-electric.acme',
    credentialType: 'ContractorLicense',
    claims: { licenseType: 'electrical', licenseState: 'US-TX' },
    expirationDate: '2027-06-30T00:00:00Z',
  },
  signer
);
```

---

## The Signer interface

The library defines a minimal, HSM-friendly abstraction. The library **never holds private keys** — callers provide their own key management.

```typescript
interface Signer {
  /** ADI URL this signer controls (e.g. 'acc://my-org.acme') */
  adiUrl: string;
  /** Raw 32-byte Ed25519 public key */
  publicKey: Uint8Array;
  /** Sign raw bytes, return Ed25519 signature (64 bytes) */
  sign(data: Uint8Array): Promise<Uint8Array>;
}
```

**Design principles:**
- `sign()` is async — supports remote signers (HSM, cloud KMS, hardware tokens)
- Public key is carried alongside the signer for transaction envelope construction
- The `adiUrl` identifies which ADI key book authorizes this signer

---

## Built-in signer helpers

### `loadSignerFromPem(keyFile, adiUrl)`

Loads a PKCS#8 Ed25519 private key from a PEM file on disk.

```typescript
import { loadSignerFromPem } from 'tradesman-verify';

const signer = loadSignerFromPem('./issuer.pem', 'acc://my-org.acme');
```

- Extracts the raw 32-byte public key from the DER-encoded SubjectPublicKeyInfo
- Signing uses Node.js `crypto.sign()` (Ed25519, no digest — the library hashes internally)
- Throws if the PEM is not an Ed25519 PKCS#8 key

### `loadSignerFromPemString(pem, adiUrl)`

Same as above but accepts the PEM content as a string. Useful when the key comes from an environment variable, secret manager, or Vault agent.

```typescript
import { loadSignerFromPemString } from 'tradesman-verify';

// Key injected by Vault agent, Kubernetes secret, or CI variable
const signer = loadSignerFromPemString(process.env.ISSUER_KEY!, 'acc://my-org.acme');
```

---

## How signing works internally

When you call `issueCredential()` or `revokeCredential()`, the library:

1. Serializes the transaction body to canonical JSON
2. Hashes the JSON with SHA-256 (`crypto.subtle.digest`)
3. Calls `signer.sign(txHash)` — your code signs the 32-byte hash
4. Wraps the result in a signature envelope:

```json
{
  "signature": {
    "type": "ed25519",
    "publicKey": "<hex-encoded 32-byte public key>",
    "signature": "<hex-encoded 64-byte signature>",
    "signerUrl": "acc://my-org.acme"
  }
}
```

5. Attaches an `AccumulateProof2024` proof to the issued W3C VC:

```json
{
  "proof": {
    "type": "AccumulateProof2024",
    "created": "2026-01-15T00:00:00Z",
    "verificationMethod": "acc://my-org.acme/book",
    "proofPurpose": "assertionMethod",
    "txid": "<accumulate-transaction-id>"
  }
}
```

> **Reference implementation note:** The signing in `src/accumulate.ts` is a reference implementation sufficient for testnet and development. Production issuers should implement the full Accumulate transaction envelope per the [protocol specification](https://docs.accumulatenetwork.io/). See [acme-integration.md](acme-integration.md) for details.

---

## Production signer patterns

### Pattern 1: File-based (development / single-server)

```typescript
import { loadSignerFromPem } from 'tradesman-verify';

const signer = loadSignerFromPem('/etc/secrets/issuer.pem', 'acc://my-org.acme');
```

**Security checklist:**
- `chmod 600` on the PEM file
- Store on an encrypted volume
- Never commit to version control (add `*.pem` to `.gitignore`)
- Rotate keys on a schedule (quarterly recommended)

### Pattern 2: Environment variable (CI/CD, containers)

```typescript
import { loadSignerFromPemString } from 'tradesman-verify';

const signer = loadSignerFromPemString(
  process.env.ISSUER_PRIVATE_KEY!,
  'acc://my-org.acme'
);
```

Works with: Docker secrets, Kubernetes secrets, GitHub Actions secrets, Vault agent.

### Pattern 3: HashiCorp Vault (production)

```typescript
import type { Signer } from 'tradesman-verify';

async function createVaultSigner(adiUrl: string): Promise<Signer> {
  // Fetch public key from Vault transit engine
  const keyInfo = await vault.read('transit/keys/issuer-ed25519');
  const publicKeyHex = keyInfo.data.keys['1'].public_key;
  const publicKey = new Uint8Array(Buffer.from(publicKeyHex, 'base64'));

  return {
    adiUrl,
    publicKey,
    sign: async (data: Uint8Array): Promise<Uint8Array> => {
      const result = await vault.write('transit/sign/issuer-ed25519', {
        input: Buffer.from(data).toString('base64'),
      });
      return new Uint8Array(Buffer.from(result.data.signature.split(':')[2], 'base64'));
    },
  };
}
```

### Pattern 4: AWS KMS

```typescript
import { KMSClient, SignCommand, GetPublicKeyCommand } from '@aws-sdk/client-kms';
import type { Signer } from 'tradesman-verify';

async function createKmsSigner(keyId: string, adiUrl: string): Promise<Signer> {
  const kms = new KMSClient({});

  const pubKeyRes = await kms.send(new GetPublicKeyCommand({ KeyId: keyId }));
  // Extract raw 32 bytes from SubjectPublicKeyInfo DER
  const publicKey = new Uint8Array(pubKeyRes.PublicKey!.slice(-32));

  return {
    adiUrl,
    publicKey,
    sign: async (data: Uint8Array): Promise<Uint8Array> => {
      const res = await kms.send(new SignCommand({
        KeyId: keyId,
        Message: data,
        MessageType: 'RAW',
        SigningAlgorithm: 'ECDSA_SHA_256',
      }));
      return new Uint8Array(res.Signature!);
    },
  };
}
```

> **Note:** AWS KMS Ed25519 support varies by region. Check [AWS docs](https://docs.aws.amazon.com/kms/latest/developerguide/symm-asymm-concepts.html) for current availability.

---

## Key management best practices

| Practice | Why |
|----------|-----|
| Never commit private keys to git | Even in private repos — git history is forever |
| Use `chmod 600` on PEM files | Prevent other users/processes from reading |
| Rotate keys quarterly | Limits blast radius of key compromise |
| Use separate keys per environment | Dev/staging/prod should have different ADIs and keys |
| Prefer Vault/KMS over file-based | Audit trail, access control, automatic rotation |
| Back up keys in a separate secure location | Lost key = lost write access to the ADI |

### If a key is compromised

1. Remove the compromised key from the ADI's key book (Accumulate key page update)
2. Generate a new key and add it to the key book
3. Revoke any credentials issued after the suspected compromise date
4. Re-issue revoked credentials with the new key
5. Audit the ADI's transaction history for unauthorized writes

---

## Error handling

```typescript
import { loadSignerFromPem, issueCredential } from 'tradesman-verify';

let signer;
try {
  signer = loadSignerFromPem('./issuer.pem', 'acc://my-org.acme');
} catch (err) {
  // Key loading failures: file not found, invalid PEM format, wrong algorithm
  console.error('Failed to load signing key:', err.message);
  process.exit(1);
}

try {
  const result = await issueCredential({ ... }, signer);
} catch (err) {
  // Signing/RPC failures: network timeout, insufficient credits, invalid ADI
  console.error('Credential issuance failed:', err.message);
}
```

Common error scenarios:
- **File not found** — PEM path is wrong or file permissions block read
- **Invalid PEM** — Not an Ed25519 key, or not PKCS#8 format (try `openssl pkey -in key.pem -text` to debug)
- **32-byte key assertion** — The PEM contains an RSA or EC key, not Ed25519
- **RPC timeout** — Accumulate node unreachable (check `ACCUMULATE_RPC_URL`)
- **Insufficient credits** — The issuer ADI needs ACME credits for write operations

---

## Related docs

- [README.md](../README.md) — API overview with signing examples
- [acme-integration.md](acme-integration.md) — Accumulate protocol details and reference signing note
- [trust-model.md](trust-model.md) — Verification flow (read-side, no signing required)
- [pipeline.md](pipeline.md) — Off-chain verification → on-chain credential issuance workflow
