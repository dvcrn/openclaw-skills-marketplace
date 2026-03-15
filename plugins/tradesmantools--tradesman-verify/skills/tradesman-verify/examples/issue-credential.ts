/**
 * tradesman-verify — example: issue and revoke credentials
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * Demonstrates:
 *   - Self-attestation (contractor writes their own unverified claims)
 *   - Third-party issuance (authorized issuer writes a signed credential)
 *   - Revocation (issuer writes a revocation entry)
 *   - OpenClaw / Claude tool_use skill initialization
 *
 * NOTE: These examples require a real Accumulate signer with an ADI and
 * credits. Replace the stub signer with your actual key management solution.
 */

import {
  issueCredential,
  selfAttest,
  revokeCredential,
  createTradesmanVerifySkill,
  loadSignerFromPem,
} from '../src/index.js';
import type { Signer } from '../src/index.js';

// ── Signer from PEM file ─────────────────────────────────────────────────────
// Generate a key:  openssl genpkey -algorithm ed25519 -out issuer.pem
//
// For production, use loadSignerFromPemString() with secrets from Vault/KMS,
// or implement the Signer interface directly with your HSM.
// See docs/signing-guide.md for patterns.

function makeSigner(adiUrl: string): Signer {
  // Option A: Load from PEM file (real signer — uncomment when you have a key)
  // return loadSignerFromPem('./issuer.pem', adiUrl);

  // Option B: Stub for running examples without a real Accumulate ADI
  return {
    adiUrl,
    publicKey: new Uint8Array(32),
    sign: async (_data: Uint8Array): Promise<Uint8Array> => {
      console.warn('  [stub signer] Replace with loadSignerFromPem() or HSM — see docs/signing-guide.md');
      return new Uint8Array(64); // dummy 64-byte Ed25519 signature
    },
  };
}

// ── Example 1: Self-attestation ───────────────────────────────────────────────
// The contractor writes their own unverified claims to their ADI.
// Relying parties should weight self-attested credentials lower than
// credentials issued by an authorized third party.

async function selfAttestExample() {
  const signer = makeSigner('acc://john-doe-electric.acme');

  const result = await selfAttest(
    {
      subjectAdiUrl: 'acc://john-doe-electric.acme',
      credentialType: 'ContractorLicense',
      claims: {
        licenseType: 'electrical',
        licenseState: 'US-TX',
      },
      expirationDate: '2027-06-30T00:00:00Z',
    },
    signer
  );

  console.log('Self-attested credential written');
  console.log('  Credential ID:', result.credentialId);
  console.log('  Data account:', result.dataAccountUrl);
  console.log('  Transaction:', result.txid);
  console.log('  Self-attested:', result.selfAttested); // true
}

// ── Example 2: Third-party issuance ──────────────────────────────────────────
// An authorized issuer (e.g. a licensing board) writes a signed credential
// to the contractor's ADI. The signer must control the issuer ADI's key book.

async function thirdPartyIssueExample() {
  const signer = makeSigner('acc://tx-license-board.acme');

  const result = await issueCredential(
    {
      issuerAdiUrl: 'acc://tx-license-board.acme',
      subjectAdiUrl: 'acc://john-doe-electric.acme',
      credentialType: 'ContractorLicense',
      claims: {
        licenseType: 'electrical',
        licenseState: 'US-TX',
        issuingAuthority: 'TDLR',
        licenseNumber: 'TECL-12345',
      },
      expirationDate: '2027-06-30T00:00:00Z',
    },
    signer
  );

  console.log('Credential issued by licensing board');
  console.log('  Credential ID:', result.credentialId);
  console.log('  Data account:', result.dataAccountUrl);
  console.log('  Transaction:', result.txid);
  console.log('  Self-attested:', result.selfAttested); // false

  return result.credentialId;
}

// ── Example 3: Revocation ─────────────────────────────────────────────────────
// The original issuer writes a revocation entry to the contractor's credential
// data account. Verifiers calling verifyContractor() will see the revocation.

async function revokeExample(credentialId: string) {
  const signer = makeSigner('acc://tx-license-board.acme');

  const result = await revokeCredential(
    {
      credentialId,
      subjectAdiUrl: 'acc://john-doe-electric.acme',
      issuerAdiUrl: 'acc://tx-license-board.acme',
      reason: 'License suspended by TDLR',
    },
    signer
  );

  console.log('Credential revoked');
  console.log('  Credential ID:', result.credentialId);
  console.log('  Transaction:', result.txid);
  console.log('  Revoked at:', result.revokedAt);
}

// ── Example 4: OpenClaw / Claude tool_use skill ───────────────────────────────
// Initialize the skill and get tools in the format each runtime expects.

function skillExample() {
  const signer = makeSigner('acc://my-issuer.acme');

  // With signer — all 4 tools available
  const skill = createTradesmanVerifySkill({ signer });

  // Claude tool_use
  const claudeTools = skill.toClaudeTools();
  console.log('Claude tools:', claudeTools.map((t) => t.name));
  // ['verify_contractor', 'self_attest_credential', 'issue_credential', 'revoke_credential']

  // OpenAI function calling
  const openAIFunctions = skill.toOpenAIFunctions();
  console.log('OpenAI functions:', openAIFunctions.map((f) => f.name));

  // MCP tool format
  const mcpTools = skill.toMCPTools();
  console.log('MCP tools:', mcpTools.map((t) => t.name));

  // Verify-only — no signer required
  const readOnlySkill = createTradesmanVerifySkill();
  console.log('Read-only tools:', readOnlySkill.tools.map((t) => t.name));
  // ['verify_contractor']
}

// Run examples
selfAttestExample().catch(console.error);
skillExample();
