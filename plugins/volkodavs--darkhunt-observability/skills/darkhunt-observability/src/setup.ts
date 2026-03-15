import * as readline from 'node:readline/promises';
import { stdin, stdout } from 'node:process';
import type { PayloadMode } from './types.js';
import { serializeConfig, validate } from './config.js';

// ── ANSI helpers ────────────────────────────────────────────────

const dim = (s: string) => `\x1b[2m${s}\x1b[0m`;
const bold = (s: string) => `\x1b[1m${s}\x1b[0m`;
const green = (s: string) => `\x1b[32m${s}\x1b[0m`;
const yellow = (s: string) => `\x1b[33m${s}\x1b[0m`;
const cyan = (s: string) => `\x1b[36m${s}\x1b[0m`;

// ── Interactive setup wizard ─────────────────────────────────────

export interface SetupResult {
  saved: boolean;
  config: Record<string, unknown>;
}

export async function runSetupWizard(
  existingConfig?: Record<string, unknown>,
): Promise<SetupResult> {
  const rl = readline.createInterface({ input: stdin, output: stdout });

  try {
    console.log('');
    console.log(`  ${bold('Trace Hub Telemetry')} ${dim('— Setup Wizard')}`);
    console.log(dim('  ─'.repeat(24)));
    console.log('');

    // ── Step 1: Export target ──────────────────────────────────

    const target = await selectOption(rl, 'Where should telemetry be sent?', [
      { key: '1', label: `Darkhunt Observability ${dim('(production)')}`, value: 'tracehub' },
      { key: '2', label: `Local OTel collector ${dim('(troubleshooting)')}`, value: 'local' },
      { key: '3', label: 'Custom endpoint', value: 'custom' },
    ], '1');

    let tracesEndpoint: string;
    let logsEndpoint: string | undefined;
    let headers: Record<string, string> | undefined;

    if (target === 'local') {
      console.log('');
      const baseUrl = await ask(rl, 'Collector base URL', 'http://localhost:4318');
      tracesEndpoint = `${baseUrl.replace(/\/+$/, '')}/v1/traces`;
      logsEndpoint = `${baseUrl.replace(/\/+$/, '')}/v1/logs`;
    } else if (target === 'tracehub') {
      console.log('');
      const baseUrl = await ask(rl, 'Trace Hub API base URL', 'https://api.darkhunt.ai/trace-hub');
      const tenantId = await ask(rl, 'Tenant ID');
      const base = baseUrl.replace(/\/+$/, '');
      tracesEndpoint = `${base}/otlp/t/${tenantId}/v1/traces`;
      logsEndpoint = `${base}/otlp/t/${tenantId}/v1/logs`;

      console.log('');
      const workspaceId = await ask(rl, 'X-Workspace-Id');
      const applicationId = await ask(rl, 'X-Application-Id');

      console.log('');
      console.log(`  ${dim('Paste the Bearer token from your API key:')}`);
      const authToken = await ask(rl, 'Authorization (Bearer token)');

      headers = {};
      if (authToken) headers['Authorization'] = authToken.startsWith('Bearer ') ? authToken : `Bearer ${authToken}`;
      if (workspaceId) headers['X-Workspace-Id'] = workspaceId;
      if (applicationId) headers['X-Application-Id'] = applicationId;
      if (Object.keys(headers).length === 0) headers = undefined;
    } else {
      console.log('');
      tracesEndpoint = await ask(rl, 'Traces endpoint URL');
      const wantLogs = await confirm(rl, 'Configure a logs endpoint too?', false);
      logsEndpoint = wantLogs ? await ask(rl, 'Logs endpoint URL') : undefined;

      const wantHeaders = await confirm(rl, 'Add HTTP headers?', false);
      if (wantHeaders) {
        headers = {};
        console.log(`  ${dim('Enter headers one at a time. Leave name blank to finish.')}`);
        while (true) {
          const key = await ask(rl, '  Header name', '', true);
          if (!key) break;
          const value = await ask(rl, `  ${key}`);
          headers[key] = value;
        }
        if (Object.keys(headers).length === 0) headers = undefined;
      }
    }

    // ── Step 2: Payload mode ──────────────────────────────────

    console.log('');
    const payloadMode = await selectOption(rl, 'How much content should spans include?', [
      { key: '1', label: `metadata ${dim('(default)')} — tokens, cost, duration, tool names. No prompts or outputs.`, value: 'metadata' as PayloadMode },
      { key: '2', label: `debug    ${dim('— metadata + truncated content (500 chars).')}`, value: 'debug' as PayloadMode },
      { key: '3', label: `full     ${dim('— includes everything subject to size limits.')}`, value: 'full' as PayloadMode },
    ], '1');

    // ── Build + validate config ───────────────────────────────

    const config = validate({
      traces_endpoint: tracesEndpoint,
      logs_endpoint: logsEndpoint,
      headers,
      payload_mode: payloadMode,
      enabled: true,
    });

    const serialized = serializeConfig(config);

    // ── Summary ───────────────────────────────────────────────

    console.log('');
    console.log(dim('  ─'.repeat(24)));
    console.log(`  ${bold('Summary')}`);
    console.log('');
    console.log(`  traces_endpoint  ${cyan(config.traces_endpoint)}`);
    if (config.logs_endpoint) {
      console.log(`  logs_endpoint    ${cyan(config.logs_endpoint)}`);
    }
    if (config.headers) {
      for (const [k, v] of Object.entries(config.headers)) {
        const display = k === 'Authorization' ? v.slice(0, 15) + '...' : v;
        console.log(`  ${k}  ${dim(display)}`);
      }
    }
    console.log(`  payload_mode     ${cyan(config.payload_mode)}`);
    console.log('');

    const ok = await confirm(rl, 'Save this configuration?', true);
    if (!ok) {
      console.log('');
      console.log(yellow('  Setup cancelled. No changes were made.'));
      console.log('');
      return { saved: false, config: existingConfig ?? {} };
    }

    return { saved: true, config: serialized };
  } finally {
    rl.close();
  }
}

// ── Prompt helpers ───────────────────────────────────────────────

async function ask(
  rl: readline.Interface,
  prompt: string,
  defaultValue?: string,
  optional?: boolean,
): Promise<string> {
  const suffix = defaultValue ? ` ${dim(`[${defaultValue}]`)}` : '';
  const answer = await rl.question(`  ${prompt}${suffix}: `);
  const value = answer.trim() || defaultValue || '';
  if (!value && !optional && !defaultValue) {
    return ask(rl, prompt, defaultValue, optional);
  }
  return value;
}

async function confirm(
  rl: readline.Interface,
  prompt: string,
  defaultValue: boolean,
): Promise<boolean> {
  const hint = dim(defaultValue ? '[Y/n]' : '[y/N]');
  const answer = await rl.question(`  ${prompt} ${hint} `);
  const trimmed = answer.trim().toLowerCase();
  if (!trimmed) return defaultValue;
  return trimmed === 'y' || trimmed === 'yes';
}

interface SelectOption<T> {
  key: string;
  label: string;
  value: T;
}

async function selectOption<T>(
  rl: readline.Interface,
  prompt: string,
  options: SelectOption<T>[],
  defaultKey?: string,
): Promise<T> {
  console.log(`  ${prompt}`);
  console.log('');
  for (const opt of options) {
    console.log(`    ${green(opt.key)}) ${opt.label}`);
  }
  console.log('');
  const suffix = defaultKey ? ` ${dim(`[${defaultKey}]`)}` : '';
  const answer = await rl.question(`  ${dim('>')}${suffix} `);
  const key = answer.trim() || defaultKey;
  const match = options.find(o => o.key === key);
  if (!match) {
    console.log(`  ${yellow('Invalid choice, try again.')}`);
    return selectOption(rl, prompt, options, defaultKey);
  }
  return match.value;
}
