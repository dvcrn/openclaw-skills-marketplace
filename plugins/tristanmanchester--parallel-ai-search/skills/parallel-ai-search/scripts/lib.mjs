#!/usr/bin/env node
/* eslint-disable no-console */

import fs from 'node:fs/promises';
import process from 'node:process';

export const API_KEY_ENV = 'PARALLEL_API_KEY';
export const DEFAULT_BASE_URL = 'https://api.parallel.ai';
export const DEFAULT_BETA_HEADER = 'search-extract-2025-10-10';

export function die(message, code = 1) {
  console.error(message);
  process.exit(code);
}

export function printJson(obj, { pretty = true } = {}) {
  const space = pretty ? 2 : 0;
  console.log(JSON.stringify(obj, null, space));
}

/**
 * Parse CLI args with a minimist-like interface (no deps).
 * Supports:
 *  - --key value, --key=value
 *  - --flag (boolean true)
 *  - --no-flag (boolean false)
 *  - repeatable multi options
 *  - simple aliases (e.g. -h -> --help)
 */
export function parseCli(argv, { multi = [], booleans = [], aliases = {} } = {}) {
  const out = {};

  const multiSet = new Set(multi);
  const boolSet = new Set(booleans);

  function push(key, value) {
    if (multiSet.has(key)) {
      if (!Array.isArray(out[key])) out[key] = [];
      out[key].push(value);
    } else {
      out[key] = value;
    }
  }

  function isBoolLiteral(x) {
    if (typeof x !== 'string') return false;
    return ['true', 'false', '1', '0', 'yes', 'no'].includes(x.toLowerCase());
  }

  function parseBoolLiteral(x) {
    const v = String(x).toLowerCase();
    return v === 'true' || v === '1' || v === 'yes';
  }

  for (let i = 2; i < argv.length; i += 1) {
    let arg = argv[i];

    if (aliases[arg]) arg = aliases[arg];

    if (arg === '--') break;

    if (arg.startsWith('--no-')) {
      const key = arg.slice(5);
      push(key, false);
      continue;
    }

    if (arg.startsWith('--')) {
      const eq = arg.indexOf('=');
      const key = (eq >= 0 ? arg.slice(2, eq) : arg.slice(2)).trim();

      if (!key) throw new Error(`Unknown argument: ${arg}`);

      if (eq >= 0) {
        const rawVal = arg.slice(eq + 1);
        if (boolSet.has(key) && isBoolLiteral(rawVal)) push(key, parseBoolLiteral(rawVal));
        else push(key, rawVal);
        continue;
      }

      if (boolSet.has(key)) {
        // Allow either "--flag" or "--flag true/false"
        const next = argv[i + 1];
        if (next !== undefined && !next.startsWith('-') && isBoolLiteral(next)) {
          push(key, parseBoolLiteral(next));
          i += 1;
        } else {
          push(key, true);
        }
        continue;
      }

      const next = argv[i + 1];
      if (next === undefined) throw new Error(`${arg} requires a value`);
      if (next.startsWith('-')) throw new Error(`${arg} requires a value (got: ${next})`);
      push(key, next);
      i += 1;
      continue;
    }

    if (arg.startsWith('-')) {
      // Only support aliases that map to full --long options (e.g. -h)
      if (aliases[arg]) {
        i -= 1; // reprocess after alias rewrite above (unlikely here)
        continue;
      }
      throw new Error(`Unknown short flag: ${arg}`);
    }

    // Positional args are ignored (these CLIs use named flags).
  }

  return out;
}

async function readStdin() {
  const chunks = [];
  for await (const c of process.stdin) chunks.push(c);
  return Buffer.concat(chunks).toString('utf8');
}

export async function loadRequestJson({ requestPath, requestJson, allowStdin }) {
  if (requestPath) {
    const raw = await fs.readFile(String(requestPath), 'utf8');
    return JSON.parse(raw);
  }

  if (requestJson) {
    return JSON.parse(String(requestJson));
  }

  if (allowStdin && !process.stdin.isTTY) {
    const raw = (await readStdin()).trim();
    if (!raw) return null;
    return JSON.parse(raw);
  }

  return null;
}

export function toInt(value, { name = 'value', min = undefined, max = undefined } = {}) {
  const n = Number.parseInt(String(value), 10);
  if (Number.isNaN(n)) throw new Error(`${name} must be an integer (got: ${value})`);
  if (min !== undefined && n < min) throw new Error(`${name} must be >= ${min} (got: ${n})`);
  if (max !== undefined && n > max) throw new Error(`${name} must be <= ${max} (got: ${n})`);
  return n;
}

export function toBool(value, { name = 'value' } = {}) {
  if (typeof value === 'boolean') return value;
  const v = String(value).toLowerCase();
  if (['true', '1', 'yes'].includes(v)) return true;
  if (['false', '0', 'no'].includes(v)) return false;
  throw new Error(`${name} must be a boolean (true/false) (got: ${value})`);
}

export function normaliseDomain(input) {
  if (input === undefined || input === null) return null;
  let s = String(input).trim();
  if (!s) return null;

  try {
    if (s.includes('://')) {
      s = new URL(s).hostname;
    }
  } catch {
    // ignore
  }

  // Strip paths/fragments if the user gave "example.com/path".
  s = s.split('/')[0].split('?')[0].split('#')[0];
  s = s.toLowerCase().replace(/^www\./, '').replace(/\.+$/, '');

  if (!/^[a-z0-9.-]+$/.test(s)) return null;
  return s;
}

export function buildHeaders({ apiKey, betaHeader }) {
  if (!apiKey) {
    throw new Error(`Missing ${API_KEY_ENV}. Set it in the environment before running this script.`);
  }

  return {
    'content-type': 'application/json',
    'x-api-key': String(apiKey),
    'parallel-beta': String(betaHeader ?? DEFAULT_BETA_HEADER),
    'user-agent': 'parallel-ai-search-skill/1.1',
  };
}

export async function postJson(url, { headers, body, timeoutMs = 120_000 } = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  let res;
  try {
    res = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(body ?? {}),
      signal: controller.signal,
    });
  } finally {
    clearTimeout(timeout);
  }

  const text = await res.text();
  let data = null;

  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const msg = typeof data === 'object' && data !== null
      ? JSON.stringify(data)
      : String(data ?? `${res.status} ${res.statusText}`);

    const err = new Error(msg);
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}

export function printMarkdownSearchResults(res) {
  const results = Array.isArray(res?.results) ? res.results : [];
  console.log('# Search results\n');
  for (let i = 0; i < results.length; i += 1) {
    const r = results[i] ?? {};
    const title = r.title || r.url || '(untitled)';
    console.log(`## ${i + 1}. ${title}\n`);
    if (r.url) console.log(`- URL: ${r.url}`);
    console.log(`- Publish date: ${r.publish_date ?? 'unknown'}`);
    if (Array.isArray(r.excerpts) && r.excerpts.length) {
      const excerpt = String(r.excerpts[0]);
      console.log('\n```text\n' + excerpt + '\n```\n');
    } else {
      console.log('');
    }
  }
}

export function printMarkdownExtractResults(res) {
  const results = Array.isArray(res?.results) ? res.results : [];
  console.log('# Extract results\n');
  for (let i = 0; i < results.length; i += 1) {
    const r = results[i] ?? {};
    const title = r.title || r.url || '(untitled)';
    console.log(`## ${i + 1}. ${title}\n`);
    if (r.url) console.log(`- URL: ${r.url}`);
    console.log(`- Publish date: ${r.publish_date ?? 'unknown'}`);

    if (Array.isArray(r.excerpts) && r.excerpts.length) {
      const excerpt = String(r.excerpts[0]);
      console.log('\n```text\n' + excerpt + '\n```\n');
    }

    if (typeof r.full_content === 'string' && r.full_content.trim()) {
      console.log('\n```markdown\n' + r.full_content + '\n```\n');
    } else {
      console.log('');
    }
  }

  if (Array.isArray(res?.errors) && res.errors.length) {
    console.log('## Errors\n');
    console.log('```json\n' + JSON.stringify(res.errors, null, 2) + '\n```\n');
  }
}
