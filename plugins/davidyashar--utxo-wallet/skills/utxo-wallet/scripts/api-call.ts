/**
 * API Call Helper — cross-platform HTTP requests for UTXO agent
 *
 * Works around Windows PowerShell curl JSON escaping issues.
 * JSON body can be passed as an argument, via --body-file, or via stdin.
 *
 * Usage:
 *   node scripts/api-call.js GET /api/agent/wallet/balance
 *   node scripts/api-call.js POST /api/agent/token/launch --body-file body.json --auth
 *   node scripts/api-call.js POST /api/agent/swap --body-file buy-body.json --auth
 *
 * Options:
 *   --auth             Read session token from .session.json and send Authorization header
 *   --base-url <url>   Override base URL (default: http://localhost:3000)
 *   --body-file <path> Read JSON body from a file (avoids shell escaping issues)
 */

import * as fs from 'fs';
import * as path from 'path';

// ---------------------------------------------------------------------------
// Base URL validation (mirrors wallet-connect.ts)
// ---------------------------------------------------------------------------

const ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'utxo.fun'];

function isAllowedBaseUrl(url: string): boolean {
  if (process.env.UTXO_ALLOW_CUSTOM_BASE_URL === '1') return true;
  try {
    const parsed = new URL(url);
    const host = parsed.hostname;
    if (ALLOWED_HOSTS.includes(host)) return true;
    if (host.endsWith('.utxo.fun')) return true;
    return false;
  } catch {
    return false;
  }
}

function findFile(name: string): string | null {
  const candidates = [
    path.join(process.cwd(), name),
    path.join(process.cwd(), 'agent-workspace', name),
  ];
  return candidates.find((p) => fs.existsSync(p)) || null;
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.error('Usage: node api-call.js <METHOD> <PATH> [JSON_BODY] [--auth] [--base-url <url>]');
    process.exit(1);
  }

  const method = args[0].toUpperCase();
  const urlPath = args[1];

  let body: string | null = null;
  let useAuth = false;
  let baseUrl = process.env.UTXO_API_BASE_URL || 'http://localhost:3000';
  let bodyFile: string | null = null;

  for (let i = 2; i < args.length; i++) {
    if (args[i] === '--auth') {
      useAuth = true;
    } else if (args[i] === '--base-url' && args[i + 1]) {
      baseUrl = args[++i];
    } else if (args[i] === '--body-file' && args[i + 1]) {
      bodyFile = args[++i];
    } else if (!args[i].startsWith('--')) {
      body = args[i];
      console.error('WARNING: Passing JSON as a CLI argument is discouraged. Use --body-file instead.');
    }
  }

  // Validate base URL to prevent sending credentials to malicious servers
  if (!isAllowedBaseUrl(baseUrl)) {
    console.error(`ERROR: Base URL not allowed: ${baseUrl}`);
    console.error('Allowed: localhost, 127.0.0.1, utxo.fun, *.utxo.fun');
    console.error('Set UTXO_ALLOW_CUSTOM_BASE_URL=1 to override.');
    process.exit(1);
  }

  // Read body from file if specified (avoids shell escaping issues)
  if (bodyFile) {
    const bodyPath = path.resolve(bodyFile);
    // Prevent path traversal — body file must be under CWD
    const cwd = process.cwd();
    if (!bodyPath.startsWith(cwd + path.sep) && bodyPath !== cwd) {
      console.error(`ERROR: Body file must be under current working directory.`);
      console.error(`  CWD:  ${cwd}`);
      console.error(`  File: ${bodyPath}`);
      process.exit(1);
    }
    if (!fs.existsSync(bodyPath)) {
      console.error(`ERROR: Body file not found: ${bodyPath}`);
      process.exit(1);
    }
    body = fs.readFileSync(bodyPath, 'utf-8').trim();
  }

  // Build headers
  const headers: Record<string, string> = {};
  if (body) {
    headers['Content-Type'] = 'application/json';
  }

  if (useAuth) {
    const sessionPath = findFile('.session.json');
    if (!sessionPath) {
      console.error('ERROR: .session.json not found. Run wallet-connect.js first.');
      process.exit(1);
    }
    const session = JSON.parse(fs.readFileSync(sessionPath, 'utf-8'));
    if (!session.session_token) {
      console.error('ERROR: .session.json has no session_token.');
      process.exit(1);
    }
    const token = String(session.session_token).trim();
    if (!token || /[\r\n]/.test(token)) {
      console.error('ERROR: .session.json contains an invalid session_token.');
      process.exit(1);
    }
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Make the request (with 30s timeout)
  const url = `${baseUrl}${urlPath}`;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 30_000);
  const fetchOpts: RequestInit = { method, headers, signal: controller.signal };
  if (body && method !== 'GET') {
    fetchOpts.body = body;
  }

  try {
    const res = await fetch(url, fetchOpts);
    clearTimeout(timeout);
    const text = await res.text();

    // Try to pretty-print JSON
    try {
      const json = JSON.parse(text);
      console.log(JSON.stringify(json, null, 2));
    } catch {
      console.log(text);
    }

    // Print status for non-200 responses
    if (!res.ok) {
      console.error(`\nHTTP ${res.status}`);
      process.exit(1);
    }
  } catch (err: any) {
    if (err.name === 'AbortError') {
      console.error(`Request timed out after 30s: ${url}`);
    } else {
      console.error(`Request failed: ${err.message}`);
    }
    process.exit(1);
  }
}

main();
