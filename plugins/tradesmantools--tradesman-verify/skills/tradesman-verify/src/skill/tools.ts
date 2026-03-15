/**
 * tradesman-verify — OpenClaw skill tool definitions
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * Five tools compatible with:
 *   - OpenClaw skill system
 *   - Claude tool_use (Anthropic)
 *   - OpenAI function calling
 *   - MCP tool format
 */

import { verifyContractor } from '../verify.js';
import { issueCredential, selfAttest, revokeCredential } from '../issue.js';
import { lookupBusinessEntity } from '../opencorporates.js';
import type { SkillTool, Signer, IssueCredentialParams } from '../types.js';

// ── Tool: verify_contractor ───────────────────────────────────────────────────

export const verifyContractorTool: SkillTool = {
  name: 'verify_contractor',
  description:
    'Verify a contractor\'s credentials by querying their Accumulate ADI on the blockchain. ' +
    'Returns verification level (none/basic/kyc/enhanced), credential details, and any missing or expired credentials.',

  inputSchema: {
    type: 'object',
    properties: {
      adi_url: {
        type: 'string',
        description: 'The contractor\'s Accumulate Digital Identifier, e.g. "acc://john-doe-electric.acme"',
      },
      require_kyc: {
        type: 'string',
        enum: ['true', 'false'],
        description: 'Whether to require a KYC credential (default: true)',
      },
      require_license: {
        type: 'string',
        enum: ['true', 'false'],
        description: 'Whether to require a contractor license credential (default: true)',
      },
      require_insurance: {
        type: 'string',
        enum: ['true', 'false'],
        description: 'Whether to require an insurance credential (default: true)',
      },
    },
    required: ['adi_url'],
  },

  async execute(input: Record<string, unknown>) {
    const adiUrl = input['adi_url'] as string;

    if (!adiUrl?.startsWith('acc://')) {
      return { error: 'adi_url must start with acc://' };
    }

    const result = await verifyContractor(adiUrl, {
      requireKyc: input['require_kyc'] !== 'false',
      requireLicense: input['require_license'] !== 'false',
      requireInsurance: input['require_insurance'] !== 'false',
    });

    return {
      adi_url: result.adiUrl,
      verified: result.verified,
      level: result.level,
      source: result.source,
      checked_at: result.checkedAt.toISOString(),
      credentials: {
        kyc: result.credentials.kyc
          ? {
              credential_id: result.credentials.kyc.credentialId,
              issuer: result.credentials.kyc.issuerAdi,
              expires_at: result.credentials.kyc.expiresAt?.toISOString() ?? null,
              days_until_expiry: result.credentials.kyc.daysUntilExpiry,
            }
          : null,
        license: result.credentials.license
          ? {
              credential_id: result.credentials.license.credentialId,
              issuer: result.credentials.license.issuerAdi,
              license_type: result.credentials.license.claims?.['licenseType'] ?? null,
              license_state: result.credentials.license.claims?.['licenseState'] ?? null,
              expires_at: result.credentials.license.expiresAt?.toISOString() ?? null,
              days_until_expiry: result.credentials.license.daysUntilExpiry,
            }
          : null,
        insurance: result.credentials.insurance
          ? {
              credential_id: result.credentials.insurance.credentialId,
              issuer: result.credentials.insurance.issuerAdi,
              insurance_type: result.credentials.insurance.claims?.['insuranceType'] ?? null,
              coverage_amount: result.credentials.insurance.claims?.['coverageAmount'] ?? null,
              expires_at: result.credentials.insurance.expiresAt?.toISOString() ?? null,
              days_until_expiry: result.credentials.insurance.daysUntilExpiry,
            }
          : null,
      },
      missing: result.missing,
      expired: result.expired,
      revoked: result.revoked,
      self_attested_only: result.selfAttestedOnly,
    };
  },
};

// ── Tool: self_attest_credential ──────────────────────────────────────────────

/**
 * Self-attestation tool.
 * Requires a Signer to be bound at skill initialization time.
 * @see createTradesmanVerifySkill
 */
export function makeSelfAttestTool(signer: Signer): SkillTool {
  return {
    name: 'self_attest_credential',
    description:
      'Write a self-attested credential to your own Accumulate ADI. ' +
      'Self-attested claims are unverified — they declare what the contractor claims about themselves. ' +
      'Useful for profile data (trade type, service area) before third-party verification.',

    inputSchema: {
      type: 'object',
      properties: {
        subject_adi_url: {
          type: 'string',
          description: 'Your ADI URL, e.g. "acc://john-doe-electric.acme"',
        },
        credential_type: {
          type: 'string',
          // Skill tools expose the four core ACME credential types.
          // For custom credential types, use issueCredential() directly.
          enum: ['ContractorLicense', 'InsuranceCredential', 'KYCCredential', 'BusinessEntityCredential'],
          description: 'Type of credential to self-attest',
        },
        claims: {
          type: 'string',
          description: 'JSON string of claims to attest, e.g. \'{"licenseType":"electrical","licenseState":"US-TX"}\'',
        },
        expiration_date: {
          type: 'string',
          description: 'Optional ISO 8601 expiration date, e.g. "2027-06-30T00:00:00Z"',
        },
      },
      required: ['subject_adi_url', 'credential_type', 'claims'],
    },

    async execute(input: Record<string, unknown>) {
      const subjectAdiUrl = input['subject_adi_url'] as string;
      const credentialType = input['credential_type'] as string;
      const claimsStr = input['claims'] as string;

      if (!subjectAdiUrl?.startsWith('acc://')) {
        return { error: 'subject_adi_url must start with acc://' };
      }

      let claims: Record<string, unknown>;
      try {
        claims = JSON.parse(claimsStr);
      } catch {
        return { error: 'claims must be valid JSON' };
      }

      const result = await selfAttest(
        {
          subjectAdiUrl,
          credentialType,
          claims,
          expirationDate: input['expiration_date'] as string | undefined,
        },
        signer
      );

      return {
        txid: result.txid,
        status: result.status,
        credential_id: result.credentialId,
        data_account_url: result.dataAccountUrl,
        self_attested: result.selfAttested,
        timestamp: result.timestamp,
      };
    },
  };
}

// ── Tool: issue_credential ────────────────────────────────────────────────────

/**
 * Third-party issuance tool.
 * Requires a Signer authorized for the issuer ADI.
 * @see createTradesmanVerifySkill
 */
export function makeIssueCredentialTool(signer: Signer): SkillTool {
  return {
    name: 'issue_credential',
    description:
      'Issue a signed W3C Verifiable Credential from your issuer ADI to a contractor\'s ADI. ' +
      'The credential is written to the contractor\'s credential data account on the Accumulate blockchain. ' +
      'Use this when you are an authorized issuer (licensing board, insurance verifier, etc.).',

    inputSchema: {
      type: 'object',
      properties: {
        issuer_adi_url: {
          type: 'string',
          description: 'Your issuer ADI URL, e.g. "acc://tx-license-board.acme"',
        },
        subject_adi_url: {
          type: 'string',
          description: 'Contractor\'s ADI URL, e.g. "acc://john-doe-electric.acme"',
        },
        credential_type: {
          type: 'string',
          // Skill tools expose the four core ACME credential types.
          // For custom credential types, use issueCredential() directly.
          enum: ['ContractorLicense', 'InsuranceCredential', 'KYCCredential', 'BusinessEntityCredential'],
          description: 'Type of credential to issue',
        },
        claims: {
          type: 'string',
          description: 'JSON string of verified claims',
        },
        expiration_date: {
          type: 'string',
          description: 'ISO 8601 expiration date',
        },
      },
      required: ['issuer_adi_url', 'subject_adi_url', 'credential_type', 'claims'],
    },

    async execute(input: Record<string, unknown>) {
      const issuerAdiUrl = input['issuer_adi_url'] as string;
      const subjectAdiUrl = input['subject_adi_url'] as string;

      if (!issuerAdiUrl?.startsWith('acc://') || !subjectAdiUrl?.startsWith('acc://')) {
        return { error: 'ADI URLs must start with acc://' };
      }

      let claims: Record<string, unknown>;
      try {
        claims = JSON.parse(input['claims'] as string);
      } catch {
        return { error: 'claims must be valid JSON' };
      }

      const params: IssueCredentialParams = {
        issuerAdiUrl,
        subjectAdiUrl,
        credentialType: input['credential_type'] as string,
        claims,
        expirationDate: input['expiration_date'] as string | undefined,
      };

      const result = await issueCredential(params, signer);

      return {
        txid: result.txid,
        status: result.status,
        credential_id: result.credentialId,
        data_account_url: result.dataAccountUrl,
        self_attested: result.selfAttested,
        timestamp: result.timestamp,
      };
    },
  };
}

// ── Tool: revoke_credential ───────────────────────────────────────────────────

export function makeRevokeCredentialTool(signer: Signer): SkillTool {
  return {
    name: 'revoke_credential',
    description:
      'Revoke a previously issued credential by writing a revocation entry to the blockchain. ' +
      'The signer must be the original issuer. Verifiers checking the credential data account ' +
      'will see the revocation entry and treat the credential as invalid.',

    inputSchema: {
      type: 'object',
      properties: {
        credential_id: {
          type: 'string',
          description: 'The credential ID to revoke',
        },
        subject_adi_url: {
          type: 'string',
          description: 'The contractor\'s ADI URL',
        },
        issuer_adi_url: {
          type: 'string',
          description: 'Your issuer ADI URL (must match original issuer)',
        },
        reason: {
          type: 'string',
          description: 'Optional reason for revocation',
        },
      },
      required: ['credential_id', 'subject_adi_url', 'issuer_adi_url'],
    },

    async execute(input: Record<string, unknown>) {
      const result = await revokeCredential(
        {
          credentialId: input['credential_id'] as string,
          subjectAdiUrl: input['subject_adi_url'] as string,
          issuerAdiUrl: input['issuer_adi_url'] as string,
          reason: input['reason'] as string | undefined,
        },
        signer
      );

      return {
        txid: result.txid,
        status: result.status,
        credential_id: result.credentialId,
        revoked_at: result.revokedAt,
      };
    },
  };
}

// ── Tool: verify_business_entity ──────────────────────────────────────────────

/**
 * OpenCorporates business entity lookup.
 * No signer required — read-only against the OpenCorporates API.
 * Requires OPENCORPORATES_API_KEY environment variable.
 *
 * Returns pre-formatted `suggested_claims` ready to pass to `issue_credential`
 * with credential_type: BusinessEntityCredential.
 */
export const verifyBusinessEntityTool: SkillTool = {
  name: 'verify_business_entity',
  description:
    'Verify a business entity via the OpenCorporates API (140+ jurisdictions). ' +
    'Returns company registration status, incorporation date, active status, and company number. ' +
    'The returned suggested_claims field is pre-formatted to pass directly to issue_credential ' +
    'with credential_type: BusinessEntityCredential to anchor the result to the contractor\'s ADI. ' +
    'Requires OPENCORPORATES_API_KEY environment variable (free tier: 200 calls/month at opencorporates.com).',

  inputSchema: {
    type: 'object',
    properties: {
      business_name: {
        type: 'string',
        description: 'Legal business name to search for, e.g. "ABC Roofing LLC"',
      },
      jurisdiction: {
        type: 'string',
        description:
          'OpenCorporates jurisdiction code, e.g. "us_tx" (Texas), "gb" (UK), "ca_on" (Ontario). ' +
          'Full list: https://api.opencorporates.com/documentation/API-Reference#jurisdictions',
      },
    },
    required: ['business_name', 'jurisdiction'],
  },

  async execute(input: Record<string, unknown>) {
    const businessName = input['business_name'] as string;
    const jurisdiction = input['jurisdiction'] as string;

    const result = await lookupBusinessEntity(businessName, jurisdiction);

    if (!result.ok) {
      switch (result.error.kind) {
        case 'not_found':
          return {
            found: false,
            business_name: businessName,
            jurisdiction,
            message:
              'No registered business found. Verify the business name spelling and jurisdiction code. ' +
              'Try variations (e.g. "LLC" vs "L.L.C.") or check a broader jurisdiction.',
          };
        case 'auth_failed':
          return {
            error: 'OPENCORPORATES_API_KEY environment variable not set or invalid',
            help: 'Get a free API key at https://opencorporates.com — free tier includes 200 calls/month',
          };
        case 'rate_limit':
          return {
            error: 'OpenCorporates rate limit exceeded',
            help: 'Free tier: 200 calls/month. Upgrade at https://opencorporates.com/pricing/',
          };
        case 'network':
          return { error: `Network error calling OpenCorporates: ${result.error.message}` };
        case 'api_error':
          return { error: `OpenCorporates API error: HTTP ${result.error.status}` };
      }
    }

    const { data } = result;
    return {
      found: true,
      is_active: data.isActive,
      company_name: data.name,
      company_number: data.companyNumber,
      jurisdiction: data.jurisdiction,
      incorporation_date: data.incorporationDate,
      current_status: data.currentStatus,
      company_type: data.companyType,
      verification_source: 'OpenCorporates',
      verified_at: data.claims?.verifiedAt,
      /**
       * Pass this directly to issue_credential:
       *   credential_type: "BusinessEntityCredential"
       *   subject_adi_url: "acc://contractor.acme"
       *   claims: <suggested_claims value>
       */
      suggested_claims: JSON.stringify(data.claims),
      next_step: data.isActive
        ? 'Business is active. Pass suggested_claims to issue_credential with credential_type: BusinessEntityCredential to write to the contractor\'s ADI.'
        : 'WARNING: Business is NOT active. Verify with contractor before issuing any credentials.',
    };
  },
};
