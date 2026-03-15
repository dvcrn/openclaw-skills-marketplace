/**
 * tradesman-verify
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * Issue and verify contractor credentials on the Accumulate blockchain.
 * Reads and writes W3C Verifiable Credentials to Accumulate Digital Identifiers (ADIs).
 * Reference implementation for the ACME Foundation credential standard.
 */

// ── Verify ────────────────────────────────────────────────────────────────────
export { verifyContractor, isExpired, getDaysUntilExpiry } from './verify.js';

// ── Issue / Revoke ────────────────────────────────────────────────────────────
export { issueCredential, selfAttest, revokeCredential } from './issue.js';

// ── Signers ──────────────────────────────────────────────────────────────────
export { loadSignerFromPem, loadSignerFromPemString } from './signers.js';

// ── Skill (OpenClaw / Claude / OpenAI / MCP) ──────────────────────────────────
export {
  createTradesmanVerifySkill,
  SKILL_NAME,
  SKILL_VERSION,
} from './skill/index.js';

// ── Skill tools (export individually for custom skill assembly) ───────────────
export {
  verifyContractorTool,
  verifyBusinessEntityTool,
  makeSelfAttestTool,
  makeIssueCredentialTool,
  makeRevokeCredentialTool,
} from './skill/tools.js';

// ── OpenCorporates ────────────────────────────────────────────────────────────
export { lookupBusinessEntity } from './opencorporates.js';
export type { BusinessEntityResult, BusinessEntityError, BusinessEntityLookupResult } from './opencorporates.js';

// ── Client ────────────────────────────────────────────────────────────────────
export { createClient, defaultClient, clearCache } from './accumulate.js';

// ── Schemas ───────────────────────────────────────────────────────────────────
export {
  CREDENTIAL_ACCOUNT_PATH,
  CREDENTIAL_TYPES,
  CONTRACTOR_LICENSE_TYPES,
  MINIMUM_GL_COVERAGE,
  MINIMUM_WC_COVERAGE,
  BUSINESS_ENTITY_CREDENTIAL_TYPE,
  parseCredentialFromEntry,
  isKYCCredential,
  isContractorLicenseCredential,
  isInsuranceCredential,
  isBusinessEntityCredential,
} from './schemas/index.js';

// ── Types ─────────────────────────────────────────────────────────────────────
export type {
  // Verification
  VerificationResult,
  VerificationRequirements,
  VerificationLevel,
  CredentialStatus,
  CredentialType,
  // Claims
  KYCClaims,
  ContractorLicenseClaims,
  InsuranceClaims,
  BusinessEntityClaims,
  W3CVerifiableCredential,
  // Issuance
  Signer,
  IssueCredentialParams,
  SelfAttestParams,
  WriteCredentialResult,
  RevokeCredentialParams,
  RevokeCredentialResult,
  // Skill
  SkillTool,
  Skill,
  // Client
  ADIMetadata,
  DataAccount,
  TokenAccount,
  AccumulateClientConfig,
} from './types.js';
export type {
  TradesmanVerifySkill,
  SkillOptions,
} from './skill/index.js';
