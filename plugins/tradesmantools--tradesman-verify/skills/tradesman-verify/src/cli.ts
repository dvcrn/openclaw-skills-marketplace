#!/usr/bin/env node
/**
 * tradesman-verify CLI
 * MIT License | https://gitlab.com/lv8rlabs/tradesman-verify
 *
 * Commands:
 *   verify  <adi-url>   Verify a contractor's credentials (default command)
 *   issue               Issue a W3C VC to a contractor's ADI
 *   revoke              Revoke a previously issued credential
 *
 * Examples:
 *   tradesman-verify acc://john-doe-electric.acme
 *   tradesman-verify verify acc://john-doe-electric.acme --no-kyc --json
 *   tradesman-verify issue --issuer acc://tx-board.acme --subject acc://john-doe.acme \
 *     --type ContractorLicense --claims '{"licenseType":"electrical"}' \
 *     --expiration 2027-06-30T00:00:00Z --key-file ./issuer.pem
 *   tradesman-verify revoke --credential-id <id> --subject acc://john-doe.acme \
 *     --issuer acc://tx-board.acme --key-file ./issuer.pem
 */

import { verifyContractor } from './verify.js';
import { issueCredential, revokeCredential } from './issue.js';
import { loadSignerFromPem } from './signers.js';
import type { Signer, VerificationResult } from './types.js';

// ── Argument helpers ──────────────────────────────────────────────────────────

function getFlag(args: string[], flag: string): string | null {
  const idx = args.indexOf(flag);
  if (idx === -1 || idx + 1 >= args.length) return null;
  return args[idx + 1]!;
}

function hasFlag(args: string[], ...flags: string[]): boolean {
  return flags.some((f) => args.includes(f));
}

// ── Help strings ──────────────────────────────────────────────────────────────

const GLOBAL_HELP = `
tradesman-verify — Accumulate ADI credential verifier & issuer

Usage:
  tradesman-verify <adi-url> [options]          Verify a contractor (shorthand)
  tradesman-verify verify <adi-url> [options]   Verify a contractor
  tradesman-verify issue   [options]            Issue a credential
  tradesman-verify revoke  [options]            Revoke a credential

Commands:
  verify    Check KYC, license, and insurance credentials on-chain
  issue     Write a signed W3C VC to a contractor's ADI
  revoke    Write a revocation entry to a contractor's ADI

Run 'tradesman-verify <command> --help' for command-specific options.

Environment:
  ACCUMULATE_RPC_URL       Override Accumulate RPC endpoint
                           Default: https://mainnet.accumulatenetwork.io/v2
  TRADESMAN_VERIFY_DEBUG   Set to 'true' to log unparseable credential entries
`;

const VERIFY_HELP = `
tradesman-verify verify — Check contractor credentials on the Accumulate blockchain

Usage:
  tradesman-verify verify <adi-url> [options]

Options:
  --no-kyc          Skip KYC credential check
  --no-license      Skip contractor license check
  --no-insurance    Skip insurance credential check
  --json            Output raw JSON
  --debug           Enable RPC debug logging
  --help            Show this help

Exit codes:
  0  Verified
  1  Not verified (missing or expired credentials)
  2  Error

Examples:
  tradesman-verify verify acc://john-doe-electric.acme
  tradesman-verify verify acc://john-doe-electric.acme --no-kyc
  tradesman-verify verify acc://john-doe-electric.acme --json
`;

const ISSUE_HELP = `
tradesman-verify issue — Issue a W3C Verifiable Credential to a contractor's ADI

Usage:
  tradesman-verify issue --issuer <adi> --subject <adi> --type <type> \\
    --claims <json> [--expiration <date>] --key-file <pem>

Required:
  --issuer    <adi>   Issuer ADI URL, e.g. acc://tx-license-board.acme
  --subject   <adi>   Contractor ADI URL, e.g. acc://john-doe-electric.acme
  --type      <type>  Credential type: ContractorLicense | InsuranceCredential | KYCCredential | BusinessEntityCredential
  --claims    <json>  JSON string of claims, e.g. '{"licenseType":"electrical"}'
  --key-file  <path>  Path to Ed25519 private key PEM file (PKCS#8 format)

Optional:
  --expiration <date> ISO 8601 expiration date, e.g. 2027-06-30T00:00:00Z
  --json              Output raw JSON
  --help              Show this help

Self-attestation (issuer === subject):
  tradesman-verify issue --issuer acc://john.acme --subject acc://john.acme \\
    --type ContractorLicense --claims '{"licenseType":"electrical"}' \\
    --key-file ./john.pem

Generate a key:
  openssl genpkey -algorithm ed25519 -out issuer.pem
`;

const REVOKE_HELP = `
tradesman-verify revoke — Revoke a previously issued credential

Usage:
  tradesman-verify revoke --credential-id <id> --subject <adi> \\
    --issuer <adi> --key-file <pem> [--reason <text>]

Required:
  --credential-id  <id>    The credential ID to revoke
  --subject        <adi>   Contractor ADI URL
  --issuer         <adi>   Issuer ADI URL (must match original issuer)
  --key-file       <path>  Path to Ed25519 private key PEM file

Optional:
  --reason  <text>  Reason for revocation (default: "revoked")
  --json            Output raw JSON
  --help            Show this help
`;

// ── Verify command ────────────────────────────────────────────────────────────

function formatVerifyResult(result: VerificationResult): void {
  const icon = result.verified ? '✓' : '✗';
  const status = result.verified ? 'VERIFIED' : 'NOT VERIFIED';

  console.log(`\n${icon}  ${status} — ${result.adiUrl}`);
  console.log(`   Level: ${result.level}`);
  console.log(`   Source: ${result.source}`);
  console.log(`   Checked: ${result.checkedAt.toISOString()}`);

  if (result.credentials.kyc) {
    const { expiresAt, daysUntilExpiry, selfAttested } = result.credentials.kyc;
    console.log(`\n   KYC Credential${selfAttested ? ' (self-attested)' : ''}`);
    console.log(`     ID: ${result.credentials.kyc.credentialId}`);
    console.log(`     Issuer: ${result.credentials.kyc.issuerAdi}`);
    console.log(`     Expires: ${expiresAt?.toISOString() ?? 'never'}${daysUntilExpiry !== null ? ` (${daysUntilExpiry}d)` : ''}`);
  }

  if (result.credentials.license) {
    const { expiresAt, daysUntilExpiry, claims, selfAttested } = result.credentials.license;
    console.log(`\n   Contractor License${selfAttested ? ' (self-attested)' : ''}`);
    console.log(`     Type: ${(claims as Record<string, unknown>)?.['licenseType'] ?? 'general'}`);
    console.log(`     State: ${(claims as Record<string, unknown>)?.['licenseState'] ?? 'unknown'}`);
    console.log(`     Expires: ${expiresAt?.toISOString() ?? 'never'}${daysUntilExpiry !== null ? ` (${daysUntilExpiry}d)` : ''}`);
  }

  if (result.credentials.insurance) {
    const { expiresAt, daysUntilExpiry, claims, selfAttested } = result.credentials.insurance;
    console.log(`\n   Insurance${selfAttested ? ' (self-attested)' : ''}`);
    console.log(`     Type: ${(claims as Record<string, unknown>)?.['insuranceType'] ?? 'general_liability'}`);
    console.log(`     Coverage: $${((claims as Record<string, unknown>)?.['coverageAmount'] as number ?? 0).toLocaleString()}`);
    console.log(`     Expires: ${expiresAt?.toISOString() ?? 'never'}${daysUntilExpiry !== null ? ` (${daysUntilExpiry}d)` : ''}`);
  }

  if (result.credentials.businessEntity) {
    const { expiresAt, daysUntilExpiry, claims } = result.credentials.businessEntity;
    console.log(`\n   Business Entity`);
    console.log(`     Name: ${(claims as Record<string, unknown>)?.['businessName'] ?? 'unknown'}`);
    console.log(`     Status: ${(claims as Record<string, unknown>)?.['businessStatus'] ?? 'unknown'}`);
    console.log(`     Jurisdiction: ${(claims as Record<string, unknown>)?.['jurisdiction'] ?? 'unknown'}`);
    console.log(`     Source: ${(claims as Record<string, unknown>)?.['verificationSource'] ?? 'unknown'}`);
    if (expiresAt) {
      console.log(`     Expires: ${expiresAt.toISOString()}${daysUntilExpiry !== null ? ` (${daysUntilExpiry}d)` : ''}`);
    }
  }

  if (result.missing.length > 0) {
    console.log(`\n   Missing: ${result.missing.join(', ')}`);
  }

  if (result.expired.length > 0) {
    console.log(`   Expired: ${result.expired.join(', ')}`);
  }

  if (result.revoked.length > 0) {
    console.log(`   Revoked: ${result.revoked.join(', ')}`);
  }

  console.log('');
}

async function runVerify(args: string[]): Promise<void> {
  if (hasFlag(args, '--help', '-h')) {
    console.log(VERIFY_HELP);
    process.exit(0);
  }

  const adiUrl = args[0];

  if (!adiUrl || !adiUrl.startsWith('acc://')) {
    console.error('Error: ADI URL must start with acc:// (e.g. acc://contractor.acme)');
    process.exit(1);
  }

  const jsonMode = hasFlag(args, '--json');

  if (!jsonMode) {
    console.log(`Verifying ${adiUrl} on Accumulate mainnet...`);
  }

  try {
    const result = await verifyContractor(adiUrl, {
      requireKyc: !hasFlag(args, '--no-kyc'),
      requireLicense: !hasFlag(args, '--no-license'),
      requireInsurance: !hasFlag(args, '--no-insurance'),
    });

    if (jsonMode) {
      console.log(JSON.stringify(result, null, 2));
    } else {
      formatVerifyResult(result);
    }

    process.exit(result.verified ? 0 : 1);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    if (jsonMode) {
      console.log(JSON.stringify({ error: msg }));
    } else {
      console.error(`Error: ${msg}`);
    }
    process.exit(2);
  }
}

// ── Issue command ─────────────────────────────────────────────────────────────

async function runIssue(args: string[]): Promise<void> {
  if (hasFlag(args, '--help', '-h')) {
    console.log(ISSUE_HELP);
    process.exit(0);
  }

  const issuerAdiUrl = getFlag(args, '--issuer');
  const subjectAdiUrl = getFlag(args, '--subject');
  const credentialType = getFlag(args, '--type');
  const claimsStr = getFlag(args, '--claims');
  const expirationDate = getFlag(args, '--expiration') ?? undefined;
  const keyFile = getFlag(args, '--key-file');
  const jsonMode = hasFlag(args, '--json');

  const missing: string[] = [];
  if (!issuerAdiUrl) missing.push('--issuer');
  if (!subjectAdiUrl) missing.push('--subject');
  if (!credentialType) missing.push('--type');
  if (!claimsStr) missing.push('--claims');
  if (!keyFile) missing.push('--key-file');

  if (missing.length > 0) {
    console.error(`Error: missing required options: ${missing.join(', ')}`);
    console.error('Run with --help for usage.');
    process.exit(1);
  }

  let claims: Record<string, unknown>;
  try {
    claims = JSON.parse(claimsStr!);
  } catch {
    console.error('Error: --claims must be valid JSON');
    process.exit(1);
  }

  let signer: Signer;
  try {
    signer = loadSignerFromPem(keyFile!, issuerAdiUrl!);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`Error loading key file: ${msg}`);
    process.exit(1);
  }

  if (!jsonMode) {
    const selfAttested = issuerAdiUrl === subjectAdiUrl;
    const verb = selfAttested ? 'Self-attesting' : 'Issuing';
    console.log(`${verb} ${credentialType} credential...`);
  }

  try {
    const result = await issueCredential(
      {
        issuerAdiUrl: issuerAdiUrl!,
        subjectAdiUrl: subjectAdiUrl!,
        credentialType: credentialType!,
        claims,
        expirationDate,
      },
      signer!
    );

    if (jsonMode) {
      console.log(JSON.stringify(result, null, 2));
    } else {
      console.log(`\n✓  Credential issued`);
      console.log(`   Credential ID: ${result.credentialId}`);
      console.log(`   Data account: ${result.dataAccountUrl}`);
      console.log(`   Transaction: ${result.txid}`);
      console.log(`   Status: ${result.status}`);
      console.log(`   Self-attested: ${result.selfAttested}`);
      console.log('');
    }

    process.exit(0);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    if (jsonMode) {
      console.log(JSON.stringify({ error: msg }));
    } else {
      console.error(`Error: ${msg}`);
    }
    process.exit(2);
  }
}

// ── Revoke command ────────────────────────────────────────────────────────────

async function runRevoke(args: string[]): Promise<void> {
  if (hasFlag(args, '--help', '-h')) {
    console.log(REVOKE_HELP);
    process.exit(0);
  }

  const credentialId = getFlag(args, '--credential-id');
  const subjectAdiUrl = getFlag(args, '--subject');
  const issuerAdiUrl = getFlag(args, '--issuer');
  const reason = getFlag(args, '--reason') ?? undefined;
  const keyFile = getFlag(args, '--key-file');
  const jsonMode = hasFlag(args, '--json');

  const missing: string[] = [];
  if (!credentialId) missing.push('--credential-id');
  if (!subjectAdiUrl) missing.push('--subject');
  if (!issuerAdiUrl) missing.push('--issuer');
  if (!keyFile) missing.push('--key-file');

  if (missing.length > 0) {
    console.error(`Error: missing required options: ${missing.join(', ')}`);
    console.error('Run with --help for usage.');
    process.exit(1);
  }

  let signer: Signer;
  try {
    signer = loadSignerFromPem(keyFile!, issuerAdiUrl!);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error(`Error loading key file: ${msg}`);
    process.exit(1);
  }

  if (!jsonMode) {
    console.log(`Revoking credential ${credentialId}...`);
  }

  try {
    const result = await revokeCredential(
      {
        credentialId: credentialId!,
        subjectAdiUrl: subjectAdiUrl!,
        issuerAdiUrl: issuerAdiUrl!,
        reason,
      },
      signer!
    );

    if (jsonMode) {
      console.log(JSON.stringify(result, null, 2));
    } else {
      console.log(`\n✓  Credential revoked`);
      console.log(`   Credential ID: ${result.credentialId}`);
      console.log(`   Transaction: ${result.txid}`);
      console.log(`   Status: ${result.status}`);
      console.log(`   Revoked at: ${result.revokedAt}`);
      console.log('');
    }

    process.exit(0);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    if (jsonMode) {
      console.log(JSON.stringify({ error: msg }));
    } else {
      console.error(`Error: ${msg}`);
    }
    process.exit(2);
  }
}

// ── Router ────────────────────────────────────────────────────────────────────

const argv = process.argv.slice(2);

if (argv.length === 0 || hasFlag(argv, '--help', '-h')) {
  console.log(GLOBAL_HELP);
  process.exit(0);
}

const command = argv[0]!;

if (command === 'verify') {
  runVerify(argv.slice(1));
} else if (command === 'issue') {
  runIssue(argv.slice(1));
} else if (command === 'revoke') {
  runRevoke(argv.slice(1));
} else if (command.startsWith('acc://')) {
  // Backwards-compatible shorthand: tradesman-verify <adi-url> [options]
  runVerify(argv);
} else {
  console.error(`Unknown command: ${command}`);
  console.error('Run tradesman-verify --help for usage.');
  process.exit(1);
}
