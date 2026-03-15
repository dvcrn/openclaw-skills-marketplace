/**
 * tradesman-verify — blockchain-based credential verification
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * Reads W3C Verifiable Credentials directly from the Accumulate blockchain.
 * No database required. No proprietary backend required.
 * Works against any ACME-compliant credential issuer.
 */

import { defaultClient, type AccumulateClient } from './accumulate.js';
import {
  CREDENTIAL_ACCOUNT_PATH,
  parseCredentialFromEntry,
  isKYCCredential,
  isContractorLicenseCredential,
  isInsuranceCredential,
  isBusinessEntityCredential,
} from './schemas/index.js';
import type {
  VerificationResult,
  VerificationRequirements,
  CredentialStatus,
  W3CVerifiableCredential,
  DataAccount,
} from './types.js';

// ── Helpers ───────────────────────────────────────────────────────────────────

function daysUntil(date: Date): number {
  return Math.floor((date.getTime() - Date.now()) / 86_400_000);
}

function credentialStatus(vc: W3CVerifiableCredential): CredentialStatus {
  const expiresAt = vc.expirationDate ? new Date(vc.expirationDate) : null;
  const expired = expiresAt ? expiresAt < new Date() : false;
  const issuerAdi = typeof vc.issuer === 'string' ? vc.issuer : String(vc.issuer);
  const subjectAdi = (vc.credentialSubject['id'] as string) ?? '';
  const selfAttested = issuerAdi === subjectAdi;

  return {
    type: vc.type.find((t) => t !== 'VerifiableCredential') ?? 'VerifiableCredential',
    credentialId: vc.id,
    issuerAdi,
    subjectAdi,
    issuedAt: new Date(vc.issuanceDate),
    expiresAt,
    daysUntilExpiry: expiresAt ? daysUntil(expiresAt) : null,
    expired,
    selfAttested,
    claims: vc.credentialSubject,
  };
}

/**
 * Parse revocation entries from the raw data account entries.
 * Returns a Set of revoked credential IDs.
 */
function parseRevocationIds(entries: DataAccount['entries']): Set<string> {
  const revokedIds = new Set<string>();
  for (const entry of entries) {
    try {
      const raw = typeof entry.data === 'string' ? JSON.parse(entry.data) : entry.data;
      if (
        raw &&
        typeof raw === 'object' &&
        (raw as Record<string, unknown>)['type'] === 'CredentialRevocation' &&
        typeof (raw as Record<string, unknown>)['credentialId'] === 'string'
      ) {
        revokedIds.add((raw as Record<string, unknown>)['credentialId'] as string);
      }
    } catch {
      // ignore unparseable entries
    }
  }
  return revokedIds;
}

// ── Core verification function ────────────────────────────────────────────────

/**
 * Verify a contractor's credentials by querying their ADI on the Accumulate blockchain.
 *
 * Reads from: `{adiUrl}/credentials` data account
 *
 * Checks for:
 * - KYC, ContractorLicense, and InsuranceCredential entries
 * - Expiration dates
 * - Explicit CredentialRevocation entries written by the original issuer
 *
 * Note on self-attestation: self-attested credentials (issuer === subject) ARE
 * included in the verification result. Check `result.selfAttestedOnly` and
 * per-credential `selfAttested` flags to apply your own issuer trust policy.
 * Level `enhanced` and `kyc` require a third-party-issued KYC credential.
 *
 * @param adiUrl - The contractor's ADI URL, e.g. "acc://john-doe-electric.acme"
 * @param requirements - Which credential types to check (default: all three)
 * @param client - Optional custom Accumulate client (uses mainnet by default)
 */
export async function verifyContractor(
  adiUrl: string,
  requirements: VerificationRequirements = {},
  client: AccumulateClient = defaultClient
): Promise<VerificationResult> {
  const {
    requireKyc = true,
    requireLicense = true,
    requireInsurance = true,
    requireBusinessEntity = false,
  } = requirements;

  const result: VerificationResult = {
    adiUrl,
    verified: false,
    level: 'none',
    credentials: {},
    missing: [],
    expired: [],
    revoked: [],
    selfAttestedOnly: false,
    checkedAt: new Date(),
    source: 'blockchain',
  };

  // 1. Confirm the ADI exists on-chain
  try {
    await client.queryADI(adiUrl);
  } catch {
    result.missing.push('ADI');
    return result;
  }

  // 2. Read the credentials data account
  const credentialAccountUrl = adiUrl.replace(/\/$/, '') + CREDENTIAL_ACCOUNT_PATH;
  const dataAccount = await client.getDataAccount(credentialAccountUrl);

  if (!dataAccount || dataAccount.entries.length === 0) {
    if (requireKyc) result.missing.push('KYCCredential');
    if (requireLicense) result.missing.push('ContractorLicense');
    if (requireInsurance) result.missing.push('InsuranceCredential');
    if (requireBusinessEntity) result.missing.push('BusinessEntityCredential');
    return result;
  }

  // 3. Extract revocation entries first
  const revokedIds = parseRevocationIds(dataAccount.entries);

  // 4. Parse W3C VC entries
  const credentials = dataAccount.entries
    .map(parseCredentialFromEntry)
    .filter((vc): vc is NonNullable<typeof vc> => vc !== null);

  // 5. Find and validate each required credential type

  if (requireKyc) {
    const kycVC = credentials.find(isKYCCredential);
    if (!kycVC) {
      result.missing.push('KYCCredential');
    } else if (revokedIds.has(kycVC.id)) {
      result.revoked.push('KYCCredential');
    } else {
      const status = credentialStatus(kycVC);
      if (status.expired) {
        result.expired.push('KYCCredential');
      } else {
        result.credentials.kyc = status;
      }
    }
  }

  if (requireLicense) {
    const licenseVC = credentials.find(isContractorLicenseCredential);
    if (!licenseVC) {
      result.missing.push('ContractorLicense');
    } else if (revokedIds.has(licenseVC.id)) {
      result.revoked.push('ContractorLicense');
    } else {
      const status = credentialStatus(licenseVC);
      if (status.expired) {
        result.expired.push('ContractorLicense');
      } else {
        result.credentials.license = status;
      }
    }
  }

  if (requireInsurance) {
    const insuranceVC = credentials.find(isInsuranceCredential);
    if (!insuranceVC) {
      result.missing.push('InsuranceCredential');
    } else if (revokedIds.has(insuranceVC.id)) {
      result.revoked.push('InsuranceCredential');
    } else {
      const status = credentialStatus(insuranceVC);
      if (status.expired) {
        result.expired.push('InsuranceCredential');
      } else {
        result.credentials.insurance = status;
      }
    }
  }

  // 5d. Business entity — always surfaced when present; required only if requireBusinessEntity
  const businessEntityVC = credentials.find(isBusinessEntityCredential);
  if (businessEntityVC && !revokedIds.has(businessEntityVC.id)) {
    const status = credentialStatus(businessEntityVC);
    if (!status.expired) {
      result.credentials.businessEntity = status;
    }
  }
  if (requireBusinessEntity && !result.credentials.businessEntity) {
    // Distinguish: was there a credential that got revoked, or was there none at all?
    if (businessEntityVC && revokedIds.has(businessEntityVC.id)) {
      result.revoked.push('BusinessEntityCredential');
    } else {
      result.missing.push('BusinessEntityCredential');
    }
  }

  // 6. Compute selfAttestedOnly
  const presentCreds = [
    result.credentials.kyc,
    result.credentials.license,
    result.credentials.insurance,
  ].filter(Boolean) as CredentialStatus[];

  result.selfAttestedOnly =
    presentCreds.length > 0 && presentCreds.every((c) => c.selfAttested);

  // 7. Compute verification level
  //    Requires zero missing, expired, or revoked credentials.
  //    Level 'enhanced' and 'kyc' require a third-party-issued KYC credential.
  //    Self-attested-only results are capped at 'basic'.
  if (result.missing.length === 0 && result.expired.length === 0 && result.revoked.length === 0) {
    result.verified = true;
    const { kyc, license, insurance } = result.credentials;

    if (kyc && !kyc.selfAttested && license && insurance) {
      result.level = 'enhanced';
    } else if (kyc && !kyc.selfAttested) {
      result.level = 'kyc';
    } else {
      result.level = 'basic';
    }
  }

  return result;
}

/**
 * Check whether a credential is expired.
 */
export function isExpired(expirationDate: string | null | undefined): boolean {
  if (!expirationDate) return false;
  return new Date(expirationDate) < new Date();
}

/**
 * Get days until a credential expires (negative if already expired).
 */
export function getDaysUntilExpiry(expirationDate: string | null | undefined): number | null {
  if (!expirationDate) return null;
  return daysUntil(new Date(expirationDate));
}
