/**
 * tradesman-verify — shared types
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 */

// ── Accumulate Protocol ──────────────────────────────────────────────────────

export interface ADIMetadata {
  url: string;
  type: string;
  keyBook?: {
    url: string;
    keys: Array<{
      publicKey: string;
      keyHash: string;
      delegate?: string;
    }>;
  };
  accounts: Array<{
    url: string;
    type: string;
  }>;
  creditBalance?: number;
}

export interface DataAccount {
  url: string;
  type: string;
  entries: Array<{
    hash: string;
    data: string | Record<string, unknown>;
    timestamp?: string;
  }>;
}

export interface TokenAccount {
  url: string;
  type: string;
  tokenUrl: string;
  balance: string;
  metadata?: Record<string, unknown>;
}

// ── Signing ───────────────────────────────────────────────────────────────────

/**
 * Signer interface — callers provide their own key management.
 * The library never holds private keys.
 *
 * Production implementations should back this with an HSM, Vault,
 * or hardware key. For local testing, use a file-based Ed25519 key.
 *
 * @example
 * import { createSign } from 'crypto';
 *
 * const signer: Signer = {
 *   adiUrl: 'acc://my-org.acme',
 *   publicKey: myPublicKeyBytes,
 *   async sign(data) {
 *     const sig = createSign('SHA256').update(data).sign(myPrivateKey);
 *     return new Uint8Array(sig);
 *   }
 * };
 */
export interface Signer {
  /** The ADI URL this signer is authorized to act on behalf of */
  adiUrl: string;
  /** Raw public key bytes (Ed25519) */
  publicKey: Uint8Array;
  /** Sign raw bytes and return the signature */
  sign(data: Uint8Array): Promise<Uint8Array>;
}

// ── W3C Verifiable Credentials ───────────────────────────────────────────────

export interface W3CVerifiableCredential {
  '@context': string[];
  id: string;
  type: string[];
  issuer: string;
  issuanceDate: string;
  expirationDate?: string;
  credentialSubject: Record<string, unknown>;
  proof?: {
    type: string;
    created: string;
    verificationMethod: string;
    proofPurpose: string;
    proofValue?: string;
    txid?: string;
  };
}

// ── Credential Types ──────────────────────────────────────────────────────────

export type CredentialType =
  | 'KYCCredential'
  | 'ContractorLicense'
  | 'InsuranceCredential'
  | 'BusinessEntityCredential'
  | 'ToolPublisherVerification'
  | string;

export interface KYCClaims {
  kycLevel: 'basic' | 'enhanced';
  sanctionsCleared: boolean;
  pepStatus: 'not_pep' | 'pep' | 'pep_related';
  riskScore: number;
  documentType: 'driving_license' | 'passport' | 'id_card';
  verifiedFirstName?: string;
  verifiedLastName?: string;
  verifiedNationality?: string;
  /** The service used to perform verification, e.g. "MicroPay Technologies" */
  verificationSource?: string;
  [key: string]: unknown;
}

export interface ContractorLicenseClaims {
  licenseType: string;
  licenseNumber?: string;
  licenseState: string;
  licenseClass?: string;
  issuingAuthority?: string;
  /** The source used to validate the license, e.g. "TDLR", "CSLB", "MicroPay Technologies" */
  verificationSource?: string;
  [key: string]: unknown;
}

export interface InsuranceClaims {
  insuranceType: 'general_liability' | 'workers_comp' | 'professional_liability' | string;
  coverageAmount: number;
  carrier?: string;
  policyNumber?: string;
  /** The source used to confirm the policy, e.g. "Hiscox", "Thimble", "manual" */
  verificationSource?: string;
  [key: string]: unknown;
}

/**
 * Claims for a BusinessEntityCredential.
 * Populated from OpenCorporates or an equivalent business registry API.
 * Records legal registration status and the source that confirmed it.
 */
export interface BusinessEntityClaims {
  /** Legal business name as registered */
  businessName: string;
  /** Registry company number, e.g. OpenCorporates company_number */
  companyNumber?: string;
  /** OpenCorporates jurisdiction code, e.g. "us_tx", "gb", "ca_on" */
  jurisdiction: string;
  /** Registry status at time of verification, e.g. "Active", "Dissolved" */
  businessStatus: string;
  /** ISO 8601 date of incorporation */
  incorporationDate?: string;
  /** Legal entity type, e.g. "LLC", "Corporation" */
  companyType?: string;
  /** API or service that performed the lookup, e.g. "OpenCorporates", "Middesk" */
  verificationSource: string;
  /** ISO 8601 timestamp of when the verification API was called */
  verifiedAt: string;
  [key: string]: unknown;
}

// ── Issuance Params ───────────────────────────────────────────────────────────

/**
 * Issue a W3C VC from one ADI to another.
 * When issuerAdiUrl === subjectAdiUrl, this is a self-attestation.
 */
export interface IssueCredentialParams {
  issuerAdiUrl: string;
  subjectAdiUrl: string;
  credentialType: CredentialType;
  claims: Record<string, unknown>;
  expirationDate?: string;            // ISO 8601
  credentialAccountPath?: string;     // defaults to '/credentials'
}

/** Shorthand for self-attestation (issuer === subject) */
export interface SelfAttestParams {
  subjectAdiUrl: string;
  credentialType: CredentialType;
  claims: Record<string, unknown>;
  expirationDate?: string;
  credentialAccountPath?: string;
}

export interface WriteCredentialResult {
  txid: string;
  status: string;
  credentialId: string;
  dataAccountUrl: string;
  timestamp: string;
  selfAttested: boolean;
  w3cCredential: W3CVerifiableCredential;
}

export interface RevokeCredentialParams {
  credentialId: string;
  subjectAdiUrl: string;
  issuerAdiUrl: string;
  reason?: string;
  credentialAccountPath?: string;
}

export interface RevokeCredentialResult {
  txid: string;
  status: string;
  credentialId: string;
  revokedAt: string;
}

// ── Verification Results ──────────────────────────────────────────────────────

export type VerificationLevel = 'none' | 'basic' | 'kyc' | 'enhanced';

export interface CredentialStatus {
  type: CredentialType;
  credentialId: string;
  issuerAdi: string;
  subjectAdi: string;
  issuedAt: Date;
  expiresAt: Date | null;
  daysUntilExpiry: number | null;
  expired: boolean;
  selfAttested: boolean;
  claims?: Record<string, unknown>;
}

export interface VerificationResult {
  adiUrl: string;
  verified: boolean;
  /**
   * Verification level based on which credentials are present and third-party issued.
   *
   * - `none`     — verification failed (missing or expired credentials)
   * - `basic`    — verified, but KYC not present or all credentials are self-attested
   * - `kyc`      — third-party KYC credential present (license/insurance may vary)
   * - `enhanced` — third-party KYC + license + insurance all present and valid
   */
  level: VerificationLevel;
  credentials: {
    kyc?: CredentialStatus;
    license?: CredentialStatus;
    insurance?: CredentialStatus;
    /**
     * Business entity credential sourced from a registry (e.g. OpenCorporates).
     * Always surfaced when present on-chain, regardless of requireBusinessEntity.
     */
    businessEntity?: CredentialStatus;
  };
  missing: CredentialType[];
  expired: CredentialType[];
  /** Credential types that were found on-chain but have been explicitly revoked. */
  revoked: CredentialType[];
  /**
   * True when every credential in `result.credentials` is self-attested
   * (issuer === subject). Check per-credential `selfAttested` for finer control.
   * Self-attested-only results are capped at level `basic`.
   */
  selfAttestedOnly: boolean;
  checkedAt: Date;
  source: 'blockchain';
}

export interface VerificationRequirements {
  requireKyc?: boolean;
  requireLicense?: boolean;
  requireInsurance?: boolean;
  /**
   * Require a BusinessEntityCredential (company registry verification).
   * Default: false — business entity is surfaced when present but not required.
   */
  requireBusinessEntity?: boolean;
}

// ── Skill ─────────────────────────────────────────────────────────────────────

/** JSON Schema property definition */
export interface JSONSchemaProperty {
  type: string;
  description?: string;
  enum?: string[];
  properties?: Record<string, JSONSchemaProperty>;
  required?: string[];
  items?: JSONSchemaProperty;
}

/** Tool definition — compatible with Claude tool_use, OpenAI functions, and MCP */
export interface SkillTool<TInput = Record<string, unknown>, TOutput = unknown> {
  name: string;
  description: string;
  inputSchema: {
    type: 'object';
    properties: Record<string, JSONSchemaProperty>;
    required: string[];
  };
  execute(input: TInput): Promise<TOutput>;
}

export interface Skill {
  name: string;
  version: string;
  description: string;
  tools: SkillTool[];
}

// ── Client Config ─────────────────────────────────────────────────────────────

export interface AccumulateClientConfig {
  rpcUrl?: string;
  cacheTtlMs?: number;
  timeoutMs?: number;
  debug?: boolean;
}
