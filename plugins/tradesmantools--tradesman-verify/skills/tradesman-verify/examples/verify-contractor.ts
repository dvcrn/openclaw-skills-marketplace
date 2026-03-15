/**
 * tradesman-verify — example: programmatic verification
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 */

import { verifyContractor, createClient } from '../src/index.js';

// ── Example 1: Verify with all credentials using default mainnet client ────────

async function verifyWithDefaults() {
  const result = await verifyContractor('acc://john-doe-electric.acme');

  console.log('Verified:', result.verified);
  console.log('Level:', result.level);

  if (result.credentials.kyc) {
    console.log('KYC expires:', result.credentials.kyc.expiresAt?.toISOString());
    console.log('KYC self-attested:', result.credentials.kyc.selfAttested);
  }

  if (result.credentials.license) {
    const claims = result.credentials.license.claims as { licenseType?: string; licenseState?: string };
    console.log('License type:', claims.licenseType, 'State:', claims.licenseState);
  }

  if (!result.verified) {
    console.log('Missing:', result.missing);
    console.log('Expired:', result.expired);
  }
}

// ── Example 2: Custom RPC endpoint or testnet ─────────────────────────────────

async function verifyWithCustomClient() {
  const client = createClient({
    rpcUrl: 'https://testnet.accumulatenetwork.io/v2',
    cacheTtlMs: 30_000,
    debug: true,
  });

  const result = await verifyContractor(
    'acc://test-contractor.acme',
    { requireKyc: true, requireLicense: true, requireInsurance: false },
    client
  );

  return result;
}

// ── Example 3: License-only check for a subcontractor ─────────────────────────

async function verifySubcontractor(adiUrl: string) {
  const result = await verifyContractor(
    adiUrl,
    { requireKyc: false, requireLicense: true, requireInsurance: true }
  );

  if (result.level === 'enhanced') {
    console.log(`${adiUrl} has license + insurance — cleared for job site`);
    return true;
  }

  console.log(`${adiUrl} not cleared. Missing: ${result.missing.join(', ')}`);
  return false;
}

// Run examples
verifyWithDefaults().catch(console.error);
verifySubcontractor('acc://example-contractor.acme').catch(console.error);
