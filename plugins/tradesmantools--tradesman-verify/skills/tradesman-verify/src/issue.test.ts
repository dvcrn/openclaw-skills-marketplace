/**
 * tradesman-verify — Issuance and revocation tests
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * Tests issueCredential, selfAttest, and revokeCredential with mock client.
 */

import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { issueCredential, selfAttest, revokeCredential } from './issue.js';
import type { AccumulateClient } from './accumulate.js';
import type { Signer } from './types.js';

// ── Mock client + signer ─────────────────────────────────────────────────────

function createMockClient(): AccumulateClient {
  return {
    queryADI: async () => ({ url: '', type: '', accounts: [] }),
    getDataAccount: async () => null,
    getTokenAccount: async () => null,
    writeData: async (params) => ({
      txid: 'mock-tx-' + Date.now(),
      status: 'delivered',
      dataAccountUrl: params.url,
      timestamp: new Date().toISOString(),
    }),
  };
}

const mockSigner: Signer = {
  adiUrl: 'acc://issuer.acme',
  publicKey: new Uint8Array(32),
  sign: async (data: Uint8Array) => new Uint8Array(64),
};

// ── Tests ────────────────────────────────────────────────────────────────────

describe('issueCredential', () => {
  it('issues a W3C Verifiable Credential', async () => {
    const client = createMockClient();
    const result = await issueCredential(
      {
        issuerAdiUrl: 'acc://issuer.acme',
        subjectAdiUrl: 'acc://contractor.acme',
        credentialType: 'ContractorLicense',
        claims: { licenseType: 'electrical', licenseState: 'US-TX' },
        expirationDate: '2027-12-31T00:00:00Z',
      },
      mockSigner,
      client,
    );

    assert.ok(result.txid.startsWith('mock-tx-'));
    assert.equal(result.status, 'delivered');
    assert.equal(result.selfAttested, false);
    assert.ok(result.credentialId.includes('ContractorLicense'));
    assert.ok(result.w3cCredential);
    assert.equal(result.w3cCredential.issuer, 'acc://issuer.acme');
    assert.deepEqual(result.w3cCredential.type, ['VerifiableCredential', 'ContractorLicense']);
    assert.equal(result.w3cCredential.credentialSubject['licenseType'], 'electrical');
  });

  it('attaches proof with txid', async () => {
    const client = createMockClient();
    const result = await issueCredential(
      {
        issuerAdiUrl: 'acc://issuer.acme',
        subjectAdiUrl: 'acc://contractor.acme',
        credentialType: 'KYCCredential',
        claims: { kycLevel: 'enhanced' },
      },
      mockSigner,
      client,
    );

    assert.ok(result.w3cCredential.proof);
    assert.equal(result.w3cCredential.proof!.type, 'AccumulateProof2024');
    assert.ok(result.w3cCredential.proof!.txid);
  });

  it('generates unique credential IDs', async () => {
    const client = createMockClient();
    const r1 = await issueCredential(
      { issuerAdiUrl: 'acc://a.acme', subjectAdiUrl: 'acc://b.acme', credentialType: 'KYCCredential', claims: {} },
      mockSigner,
      client,
    );
    const r2 = await issueCredential(
      { issuerAdiUrl: 'acc://a.acme', subjectAdiUrl: 'acc://b.acme', credentialType: 'KYCCredential', claims: {} },
      mockSigner,
      client,
    );

    assert.notEqual(r1.credentialId, r2.credentialId);
  });
});

describe('selfAttest', () => {
  it('creates a self-attested credential', async () => {
    const client = createMockClient();
    const selfSigner: Signer = {
      adiUrl: 'acc://contractor.acme',
      publicKey: new Uint8Array(32),
      sign: async () => new Uint8Array(64),
    };

    const result = await selfAttest(
      {
        subjectAdiUrl: 'acc://contractor.acme',
        credentialType: 'ContractorLicense',
        claims: { licenseType: 'plumbing', licenseState: 'US-CA' },
      },
      selfSigner,
      client,
    );

    assert.equal(result.selfAttested, true);
    assert.equal(result.w3cCredential.issuer, 'acc://contractor.acme');
    assert.equal(result.w3cCredential.credentialSubject['id'], 'acc://contractor.acme');
  });
});

describe('revokeCredential', () => {
  it('writes a revocation entry', async () => {
    let writtenData: Record<string, unknown> | null = null;
    const client: AccumulateClient = {
      queryADI: async () => ({ url: '', type: '', accounts: [] }),
      getDataAccount: async () => null,
      getTokenAccount: async () => null,
      writeData: async (params) => {
        writtenData = params.data;
        return {
          txid: 'revoke-tx-123',
          status: 'delivered',
          dataAccountUrl: params.url,
          timestamp: new Date().toISOString(),
        };
      },
    };

    const result = await revokeCredential(
      {
        credentialId: 'test-cred-id',
        subjectAdiUrl: 'acc://contractor.acme',
        issuerAdiUrl: 'acc://issuer.acme',
        reason: 'license expired',
      },
      mockSigner,
      client,
    );

    assert.equal(result.txid, 'revoke-tx-123');
    assert.equal(result.credentialId, 'test-cred-id');
    assert.ok(result.revokedAt);
    assert.ok(writtenData);
    assert.equal((writtenData as Record<string, unknown>)['type'], 'CredentialRevocation');
    assert.equal((writtenData as Record<string, unknown>)['reason'], 'license expired');
  });
});
