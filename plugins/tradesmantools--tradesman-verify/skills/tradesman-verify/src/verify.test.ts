/**
 * tradesman-verify — Verification flow tests
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * Tests verifyContractor with mock Accumulate client.
 */

import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { verifyContractor } from './verify.js';
import type { AccumulateClient } from './accumulate.js';
import type { ADIMetadata, DataAccount, TokenAccount } from './types.js';

// ── Mock client factory ──────────────────────────────────────────────────────

function createMockClient(overrides: Partial<AccumulateClient> = {}): AccumulateClient {
  return {
    queryADI: async (_url: string): Promise<ADIMetadata> => ({
      url: _url,
      type: 'identity',
      accounts: [],
    }),
    getDataAccount: async (_url: string): Promise<DataAccount | null> => null,
    getTokenAccount: async (_url: string): Promise<TokenAccount | null> => null,
    writeData: async () => ({ txid: '', status: '', dataAccountUrl: '', timestamp: '' }),
    ...overrides,
  };
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function makeVC(type: string, issuer: string, subject: string, expired = false) {
  const now = new Date();
  const expiry = expired
    ? new Date(now.getTime() - 86_400_000).toISOString()
    : new Date(now.getTime() + 365 * 86_400_000).toISOString();
  return JSON.stringify({
    '@context': ['https://www.w3.org/2018/credentials/v1'],
    id: `${issuer}/${type}/${subject}/${crypto.randomUUID()}`,
    type: ['VerifiableCredential', type],
    issuer,
    issuanceDate: now.toISOString(),
    expirationDate: expiry,
    credentialSubject: {
      id: subject,
      ...(type === 'KYCCredential' ? { kycLevel: 'enhanced' } : {}),
      ...(type === 'ContractorLicense' ? { licenseType: 'electrical', licenseState: 'US-TX' } : {}),
      ...(type === 'InsuranceCredential' ? { policyType: 'general_liability', coverageAmount: 2000000 } : {}),
    },
  });
}

// ── Tests ────────────────────────────────────────────────────────────────────

describe('verifyContractor', () => {
  const adiUrl = 'acc://test-contractor.acme';
  const issuerAdi = 'acc://license-board.acme';

  it('returns level "none" when ADI does not exist', async () => {
    const client = createMockClient({
      queryADI: async () => { throw new Error('Not found'); },
    });

    const result = await verifyContractor(adiUrl, {}, client);

    assert.equal(result.verified, false);
    assert.equal(result.level, 'none');
    assert.ok(result.missing.includes('ADI'));
  });

  it('returns missing credentials when data account is empty', async () => {
    const client = createMockClient();

    const result = await verifyContractor(adiUrl, {}, client);

    assert.equal(result.verified, false);
    assert.ok(result.missing.includes('KYCCredential'));
    assert.ok(result.missing.includes('ContractorLicense'));
    assert.ok(result.missing.includes('InsuranceCredential'));
  });

  it('returns "enhanced" when all three credentials are valid (third-party issued)', async () => {
    const client = createMockClient({
      getDataAccount: async () => ({
        url: `${adiUrl}/credentials`,
        type: 'dataAccount',
        entries: [
          { hash: 'a1', data: makeVC('KYCCredential', issuerAdi, adiUrl) },
          { hash: 'a2', data: makeVC('ContractorLicense', issuerAdi, adiUrl) },
          { hash: 'a3', data: makeVC('InsuranceCredential', issuerAdi, adiUrl) },
        ],
      }),
    });

    const result = await verifyContractor(adiUrl, {}, client);

    assert.equal(result.verified, true);
    assert.equal(result.level, 'enhanced');
    assert.equal(result.missing.length, 0);
    assert.equal(result.selfAttestedOnly, false);
  });

  it('returns "basic" for self-attested credentials', async () => {
    const client = createMockClient({
      getDataAccount: async () => ({
        url: `${adiUrl}/credentials`,
        type: 'dataAccount',
        entries: [
          { hash: 'a1', data: makeVC('KYCCredential', adiUrl, adiUrl) },
          { hash: 'a2', data: makeVC('ContractorLicense', adiUrl, adiUrl) },
          { hash: 'a3', data: makeVC('InsuranceCredential', adiUrl, adiUrl) },
        ],
      }),
    });

    const result = await verifyContractor(adiUrl, {}, client);

    assert.equal(result.verified, true);
    assert.equal(result.level, 'basic');
    assert.equal(result.selfAttestedOnly, true);
  });

  it('detects expired credentials', async () => {
    const client = createMockClient({
      getDataAccount: async () => ({
        url: `${adiUrl}/credentials`,
        type: 'dataAccount',
        entries: [
          { hash: 'a1', data: makeVC('KYCCredential', issuerAdi, adiUrl, true) },
          { hash: 'a2', data: makeVC('ContractorLicense', issuerAdi, adiUrl) },
          { hash: 'a3', data: makeVC('InsuranceCredential', issuerAdi, adiUrl) },
        ],
      }),
    });

    const result = await verifyContractor(adiUrl, {}, client);

    assert.equal(result.verified, false);
    assert.ok(result.expired.includes('KYCCredential'));
  });

  it('detects revoked credentials', async () => {
    const credId = `${issuerAdi}/KYCCredential/${adiUrl}/test-id`;
    const client = createMockClient({
      getDataAccount: async () => ({
        url: `${adiUrl}/credentials`,
        type: 'dataAccount',
        entries: [
          {
            hash: 'a1',
            data: JSON.stringify({
              '@context': ['https://www.w3.org/2018/credentials/v1'],
              id: credId,
              type: ['VerifiableCredential', 'KYCCredential'],
              issuer: issuerAdi,
              issuanceDate: new Date().toISOString(),
              expirationDate: new Date(Date.now() + 365 * 86_400_000).toISOString(),
              credentialSubject: { id: adiUrl, kycLevel: 'enhanced' },
            }),
          },
          { hash: 'a2', data: makeVC('ContractorLicense', issuerAdi, adiUrl) },
          { hash: 'a3', data: makeVC('InsuranceCredential', issuerAdi, adiUrl) },
          {
            hash: 'rev1',
            data: JSON.stringify({
              type: 'CredentialRevocation',
              credentialId: credId,
              issuerAdiUrl: issuerAdi,
              revokedAt: new Date().toISOString(),
              reason: 'test revocation',
            }),
          },
        ],
      }),
    });

    const result = await verifyContractor(adiUrl, {}, client);

    assert.equal(result.verified, false);
    assert.ok(result.revoked.includes('KYCCredential'));
  });

  it('respects custom requirements (skip insurance)', async () => {
    const client = createMockClient({
      getDataAccount: async () => ({
        url: `${adiUrl}/credentials`,
        type: 'dataAccount',
        entries: [
          { hash: 'a1', data: makeVC('KYCCredential', issuerAdi, adiUrl) },
          { hash: 'a2', data: makeVC('ContractorLicense', issuerAdi, adiUrl) },
        ],
      }),
    });

    const result = await verifyContractor(adiUrl, { requireInsurance: false }, client);

    assert.equal(result.verified, true);
    assert.equal(result.missing.length, 0);
  });
});
