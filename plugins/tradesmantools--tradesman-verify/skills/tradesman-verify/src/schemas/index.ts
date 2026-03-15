/**
 * tradesman-verify — W3C Verifiable Credential schema definitions
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * These schemas define the credential types issued for licensed tradespeople
 * on the Accumulate blockchain. Any ACME-compliant issuer may issue credentials
 * conforming to these schemas — issuance is open to any ACME-compliant organization.
 */

import type { W3CVerifiableCredential, KYCClaims, ContractorLicenseClaims, InsuranceClaims, BusinessEntityClaims } from '../types.js';

// W3C VC context URLs
export const VC_CONTEXT = 'https://www.w3.org/2018/credentials/v1';
// Pinned to v0.1.0 release tag — credentials issued against this URL remain
// verifiable long-term. The tag resolves via GitLab raw hosting immediately
// after `git push origin v0.1.0` (no npm publish required).
export const TRADESMAN_CONTEXT = 'https://gitlab.com/lv8rlabs/tradesman-verify/-/raw/v0.1.0/contexts/v1.json';

// Accumulate mainnet credential data account convention
// Issuers write credentials to: {issuerAdi}/credentials
// Subjects can list their credentials at: {subjectAdi}/credentials
export const CREDENTIAL_ACCOUNT_PATH = '/credentials';

// ── KYC Credential ────────────────────────────────────────────────────────────

export const KYC_CREDENTIAL_TYPE = 'KYCCredential';

export interface KYCCredential extends W3CVerifiableCredential {
  type: ['VerifiableCredential', 'KYCCredential'];
  credentialSubject: KYCClaims & { id: string };
}

export function isKYCCredential(vc: W3CVerifiableCredential): vc is KYCCredential {
  return vc.type.includes('KYCCredential');
}

export function validateKYCClaims(claims: Record<string, unknown>): claims is KYCClaims {
  return (
    typeof claims['kycLevel'] === 'string' &&
    ['basic', 'enhanced'].includes(claims['kycLevel'] as string) &&
    typeof claims['sanctionsCleared'] === 'boolean' &&
    typeof claims['riskScore'] === 'number'
  );
}

// ── Contractor License Credential ─────────────────────────────────────────────

export const CONTRACTOR_LICENSE_TYPE = 'ContractorLicense';

export interface ContractorLicenseCredential extends W3CVerifiableCredential {
  type: ['VerifiableCredential', 'ContractorLicense'];
  credentialSubject: ContractorLicenseClaims & { id: string };
}

export function isContractorLicenseCredential(
  vc: W3CVerifiableCredential
): vc is ContractorLicenseCredential {
  return vc.type.includes('ContractorLicense');
}

export const CONTRACTOR_LICENSE_TYPES = [
  'general_contractor',
  'electrical',
  'plumbing',
  'hvac',
  'roofing',
  'structural',
  'civil',
  'mechanical',
  'fire_protection',
  'elevator',
] as const;

export type ContractorLicenseType = typeof CONTRACTOR_LICENSE_TYPES[number];

// ── Insurance Credential ──────────────────────────────────────────────────────

export const INSURANCE_CREDENTIAL_TYPE = 'InsuranceCredential';

export interface InsuranceCredential extends W3CVerifiableCredential {
  type: ['VerifiableCredential', 'InsuranceCredential'];
  credentialSubject: InsuranceClaims & { id: string };
}

export function isInsuranceCredential(vc: W3CVerifiableCredential): vc is InsuranceCredential {
  return vc.type.includes('InsuranceCredential');
}

// Minimum coverage thresholds (USD) — these are defaults; callers may require more
export const MINIMUM_GL_COVERAGE = 1_000_000;
export const MINIMUM_WC_COVERAGE = 500_000;

// ── Business Entity Credential ────────────────────────────────────────────────

export const BUSINESS_ENTITY_CREDENTIAL_TYPE = 'BusinessEntityCredential';

export interface BusinessEntityCredential extends W3CVerifiableCredential {
  type: ['VerifiableCredential', 'BusinessEntityCredential'];
  credentialSubject: BusinessEntityClaims & { id: string };
}

export function isBusinessEntityCredential(
  vc: W3CVerifiableCredential
): vc is BusinessEntityCredential {
  return vc.type.includes('BusinessEntityCredential');
}

// ── Schema registry ───────────────────────────────────────────────────────────

export const CREDENTIAL_TYPES = {
  KYC: KYC_CREDENTIAL_TYPE,
  LICENSE: CONTRACTOR_LICENSE_TYPE,
  INSURANCE: INSURANCE_CREDENTIAL_TYPE,
  BUSINESS_ENTITY: BUSINESS_ENTITY_CREDENTIAL_TYPE,
} as const;

/**
 * Parse a W3C Verifiable Credential from a raw data account entry.
 * Returns null for non-VC entries (e.g. CredentialRevocation objects) — these
 * are expected and handled separately by parseRevocationIds().
 *
 * Set TRADESMAN_VERIFY_DEBUG=true to log entries that fail JSON parsing.
 */
export function parseCredentialFromEntry(
  entry: { data: string | Record<string, unknown> }
): W3CVerifiableCredential | null {
  try {
    const raw = typeof entry.data === 'string' ? JSON.parse(entry.data) : entry.data;

    if (
      !raw ||
      typeof raw !== 'object' ||
      !Array.isArray(raw['type']) ||
      !raw['type'].includes('VerifiableCredential')
    ) {
      // Not a VC — may be a revocation entry or other valid non-VC record.
      return null;
    }

    return raw as W3CVerifiableCredential;
  } catch (err) {
    if (process.env['TRADESMAN_VERIFY_DEBUG'] === 'true') {
      console.debug(
        '[tradesman-verify] skipped unparseable credential entry:',
        err instanceof Error ? err.message : String(err),
        '| raw:', typeof entry.data === 'string' ? entry.data.slice(0, 120) : entry.data
      );
    }
    return null;
  }
}
