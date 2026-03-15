/**
 * tradesman-verify — credential issuance
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * Issue and revoke W3C Verifiable Credentials on the Accumulate blockchain.
 *
 * Two flows:
 *   - Self-attestation: a contractor writes their own unverified claims
 *   - Issuer flow: an authorized third party issues signed credentials
 *
 * Both use the same underlying mechanism — a W3C VC written to the
 * subject's credential data account. Relying parties decide how much
 * weight to give each based on the issuer ADI.
 */

import { defaultClient, type AccumulateClient } from './accumulate.js';
import { CREDENTIAL_ACCOUNT_PATH, VC_CONTEXT, TRADESMAN_CONTEXT } from './schemas/index.js';
import type {
  Signer,
  IssueCredentialParams,
  SelfAttestParams,
  WriteCredentialResult,
  RevokeCredentialParams,
  RevokeCredentialResult,
  W3CVerifiableCredential,
} from './types.js';

// ── Credential ID generation ──────────────────────────────────────────────────

function generateCredentialId(issuerAdi: string, subjectAdi: string, type: string): string {
  // Use randomUUID for collision resistance (Date.now() is not safe for batch issuance)
  const uid = crypto.randomUUID();
  return `${issuerAdi}/${type}/${subjectAdi}/${uid}`;
}

// ── Build W3C VC ──────────────────────────────────────────────────────────────

function buildW3CCredential(params: {
  credentialId: string;
  issuerAdiUrl: string;
  subjectAdiUrl: string;
  credentialType: string;
  claims: Record<string, unknown>;
  expirationDate?: string;
}): W3CVerifiableCredential {
  const vc: W3CVerifiableCredential = {
    '@context': [VC_CONTEXT, TRADESMAN_CONTEXT],
    id: params.credentialId,
    type: ['VerifiableCredential', params.credentialType],
    issuer: params.issuerAdiUrl,
    issuanceDate: new Date().toISOString(),
    credentialSubject: {
      id: params.subjectAdiUrl,
      ...params.claims,
    },
  };

  if (params.expirationDate) {
    vc.expirationDate = params.expirationDate;
  }

  return vc;
}

// ── Issue ──────────────────────────────────────────────────────────────────────

/**
 * Issue a W3C Verifiable Credential from an issuer ADI to a subject ADI.
 *
 * The credential is written to `{subjectAdiUrl}/credentials` (or a custom path).
 * The signer must control the issuer ADI's key book.
 *
 * For self-attestation, set issuerAdiUrl === subjectAdiUrl.
 * For third-party issuance, set different ADIs.
 *
 * @example
 * // Self-attestation
 * const result = await issueCredential({
 *   issuerAdiUrl: 'acc://john-doe-electric.acme',
 *   subjectAdiUrl: 'acc://john-doe-electric.acme',
 *   credentialType: 'ContractorLicense',
 *   claims: { licenseType: 'electrical', licenseState: 'US-TX' },
 *   expirationDate: '2027-06-30T00:00:00Z',
 * }, signer);
 *
 * // Third-party issuance
 * const result = await issueCredential({
 *   issuerAdiUrl: 'acc://tx-license-board.acme',
 *   subjectAdiUrl: 'acc://john-doe-electric.acme',
 *   credentialType: 'ContractorLicense',
 *   claims: { licenseType: 'electrical', licenseState: 'US-TX', issuingAuthority: 'TDLR' },
 *   expirationDate: '2027-06-30T00:00:00Z',
 * }, signer);
 */
export async function issueCredential(
  params: IssueCredentialParams,
  signer: Signer,
  client: AccumulateClient = defaultClient
): Promise<WriteCredentialResult> {
  const {
    issuerAdiUrl,
    subjectAdiUrl,
    credentialType,
    claims,
    expirationDate,
    credentialAccountPath = CREDENTIAL_ACCOUNT_PATH,
  } = params;

  const credentialId = generateCredentialId(issuerAdiUrl, subjectAdiUrl, credentialType);
  const dataAccountUrl = subjectAdiUrl.replace(/\/$/, '') + credentialAccountPath;
  const selfAttested = issuerAdiUrl === subjectAdiUrl;

  const vc = buildW3CCredential({
    credentialId,
    issuerAdiUrl,
    subjectAdiUrl,
    credentialType,
    claims,
    expirationDate,
  });

  const writeResult = await client.writeData({
    url: dataAccountUrl,
    data: vc as unknown as Record<string, unknown>,
    createAccount: true,
    signer,
  });

  // Attach proof with txid once we have it
  if (writeResult.txid) {
    vc.proof = {
      type: 'AccumulateProof2024',
      created: writeResult.timestamp,
      verificationMethod: `${signer.adiUrl}/book`,
      proofPurpose: 'assertionMethod',
      txid: writeResult.txid,
    };
  }

  return {
    txid: writeResult.txid,
    status: writeResult.status,
    credentialId,
    dataAccountUrl,
    timestamp: writeResult.timestamp,
    selfAttested,
    w3cCredential: vc,
  };
}

/**
 * Self-attestation shorthand.
 * The contractor writes their own unverified claims to their ADI.
 * Relying parties can use these for discovery but should weight them
 * lower than third-party issued credentials.
 */
export async function selfAttest(
  params: SelfAttestParams,
  signer: Signer,
  client: AccumulateClient = defaultClient
): Promise<WriteCredentialResult> {
  return issueCredential(
    {
      issuerAdiUrl: params.subjectAdiUrl,
      subjectAdiUrl: params.subjectAdiUrl,
      credentialType: params.credentialType,
      claims: params.claims,
      expirationDate: params.expirationDate,
      credentialAccountPath: params.credentialAccountPath,
    },
    signer,
    client
  );
}

// ── Revoke ────────────────────────────────────────────────────────────────────

/**
 * Revoke a credential by writing a revocation entry to the subject's
 * credential data account.
 *
 * The signer must control the issuer ADI that originally issued the credential.
 * Verifiers should check for revocation entries when validating credentials.
 */
export async function revokeCredential(
  params: RevokeCredentialParams,
  signer: Signer,
  client: AccumulateClient = defaultClient
): Promise<RevokeCredentialResult> {
  const {
    credentialId,
    subjectAdiUrl,
    issuerAdiUrl,
    reason,
    credentialAccountPath = CREDENTIAL_ACCOUNT_PATH,
  } = params;

  const dataAccountUrl = subjectAdiUrl.replace(/\/$/, '') + credentialAccountPath;
  const revokedAt = new Date().toISOString();

  const revocationEntry = {
    type: 'CredentialRevocation',
    credentialId,
    issuerAdiUrl,
    subjectAdiUrl,
    revokedAt,
    reason: reason ?? 'revoked',
  };

  const writeResult = await client.writeData({
    url: dataAccountUrl,
    data: revocationEntry,
    signer,
  });

  return {
    txid: writeResult.txid,
    status: writeResult.status,
    credentialId,
    revokedAt,
  };
}
