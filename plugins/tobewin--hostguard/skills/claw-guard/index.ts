import { execSync } from 'child_process';
import fs from 'fs';
import os from 'os';
import path from 'path';

type HostAssessment =
  | 'loopback'
  | 'wildcard'
  | 'private-network'
  | 'public-network'
  | 'unknown';

interface ConfigSnapshot {
  envPath: string | null;
  host: string | null;
  port: number;
}

interface ListenerSnapshot {
  isListening: boolean;
  bindings: string[];
  assessment: HostAssessment;
  details: string | null;
}

interface PrivilegeSnapshot {
  isElevated: boolean | null;
  details: string;
}

interface ClawGuardOptions {
  cwd?: string;
  execCommand?: (command: string) => string;
  platform?: NodeJS.Platform;
  getUid?: (() => number) | null;
}

const LOOPBACK_HOSTS = new Set(['127.0.0.1', '::1', 'localhost']);
const WILDCARD_HOSTS = new Set(['0.0.0.0', '::', '*']);
const DEFAULT_ENV_FILES = [
  '.env.local',
  '.env.development',
  '.env.production',
  '.env',
];

export class ClawGuard {
  private readonly DEFAULT_PORT = 18789;
  private readonly cwd: string;
  private readonly execCommand: (command: string) => string;
  private readonly platform: NodeJS.Platform;
  private readonly getUid: (() => number) | null;

  constructor(options?: ClawGuardOptions) {
    this.cwd = options?.cwd ?? process.cwd();
    this.execCommand =
      options?.execCommand ??
      ((command: string) =>
        execSync(command, { stdio: ['ignore', 'pipe', 'ignore'] }).toString());
    this.platform = options?.platform ?? os.platform();
    this.getUid =
      options?.getUid === undefined
        ? typeof process.getuid === 'function'
          ? () => process.getuid()
          : null
        : options.getUid;
  }

  async check_security_health(): Promise<string> {
    const config = this.loadConfigSnapshot();
    const listener = this.inspectNetworkListener(config.port);
    const privileges = this.inspectPrivileges();

    const lines: string[] = [];
    lines.push(
      `[INFO] Config: host=${config.host ?? 'not set'}, port=${config.port}, env=${config.envPath ?? 'not found'}`
    );

    if (!listener.isListening) {
      lines.push(
        `[INFO] Network: No active listener detected on port ${config.port}. ${listener.details ?? 'OpenClaw may be stopped, using a different port, or the process may be inaccessible.'}`
      );
    } else if (listener.assessment === 'loopback') {
      lines.push(
        `[SAFE] Network: Service is bound to localhost only (${listener.bindings.join(', ')}).`
      );
    } else if (listener.assessment === 'wildcard') {
      lines.push(
        `[CRITICAL] Network: Service is listening on all interfaces (${listener.bindings.join(', ')}). This may allow access beyond localhost.`
      );
    } else if (listener.assessment === 'private-network') {
      lines.push(
        `[WARNING] Network: Service is bound to a non-loopback private address (${listener.bindings.join(', ')}). Devices on the same network may be able to reach it.`
      );
    } else if (listener.assessment === 'public-network') {
      lines.push(
        `[CRITICAL] Network: Service is bound to a public non-loopback address (${listener.bindings.join(', ')}).`
      );
    } else {
      lines.push(
        `[INFO] Network: Listener detected on port ${config.port}, but the binding could not be classified (${listener.bindings.join(', ')}).`
      );
    }

    if (config.host) {
      const hostAssessment = this.assessHost(config.host);
      if (hostAssessment === 'wildcard') {
        lines.push(
          '[WARNING] Config: HOST/OPENCLAW_HOST is configured as a wildcard address. Restarting the service may expose it beyond localhost.'
        );
      } else if (
        hostAssessment === 'private-network' ||
        hostAssessment === 'public-network'
      ) {
        lines.push(
          `[WARNING] Config: HOST/OPENCLAW_HOST is configured as ${config.host}, which is not loopback-only.`
        );
      } else if (hostAssessment === 'loopback') {
        lines.push('[SAFE] Config: HOST/OPENCLAW_HOST is restricted to loopback.');
      }
    } else {
      lines.push(
        '[INFO] Config: No HOST/OPENCLAW_HOST value found in the known env files. Runtime flags or a different config source may be in use.'
      );
    }

    if (privileges.isElevated === true) {
      lines.push(`[WARNING] Privileges: Process is running with elevated privileges. ${privileges.details}`);
    } else if (privileges.isElevated === false) {
      lines.push(`[SAFE] Privileges: Process is running without elevated privileges. ${privileges.details}`);
    } else {
      lines.push(`[INFO] Privileges: Could not determine elevation state. ${privileges.details}`);
    }

    return lines.join('\n');
  }

  async apply_lockdown_fix(): Promise<string> {
    const targetEnvPath = this.findEnvFileWithHostSetting();
    if (!targetEnvPath) {
      return '[ERROR] No known env file was found. I did not modify anything.';
    }

    const rawContent = fs.readFileSync(targetEnvPath, 'utf-8');
    const update = this.rewriteHostToLoopback(rawContent);

    if (update.status === 'already-secure') {
      return `[INFO] HOST/OPENCLAW_HOST is already loopback-only in ${path.basename(targetEnvPath)}.`;
    }

    if (update.status === 'not-found') {
      return `[ERROR] No HOST/OPENCLAW_HOST entry was found in ${path.basename(targetEnvPath)}. I did not add one automatically because the active config source may be elsewhere.`;
    }

    const backupPath = `${targetEnvPath}.bak`;
    fs.writeFileSync(backupPath, rawContent, 'utf-8');
    fs.writeFileSync(targetEnvPath, update.content, 'utf-8');

    return `[SUCCESS] Updated HOST/OPENCLAW_HOST to 127.0.0.1 in ${targetEnvPath}. Backup saved to ${backupPath}. Restart OpenClaw for the change to take effect.`;
  }

  private loadConfigSnapshot(): ConfigSnapshot {
    const envFiles = this.findEnvFiles();
    const envMaps = envFiles.map((envPath) => ({
      envPath,
      env: this.parseEnvFile(envPath),
    }));
    const hostSource = this.pickFirstEnvValue(envMaps, ['OPENCLAW_HOST', 'HOST']);
    const portSource = this.pickFirstEnvValue(envMaps, ['OPENCLAW_PORT', 'PORT']);
    const rawHost = hostSource?.value ?? null;
    const rawPort = portSource?.value;
    const port = this.parsePort(rawPort) ?? this.DEFAULT_PORT;

    return {
      envPath: hostSource?.envPath ?? portSource?.envPath ?? envFiles[0] ?? null,
      host: rawHost ? this.normalizeHost(rawHost) : null,
      port,
    };
  }

  private findEnvFiles(): string[] {
    const files: string[] = [];
    for (const file of DEFAULT_ENV_FILES) {
      const candidate = path.join(this.cwd, file);
      if (fs.existsSync(candidate) && fs.statSync(candidate).isFile()) {
        files.push(candidate);
      }
    }
    return files;
  }

  private findEnvFileWithHostSetting(): string | null {
    const envFiles = this.findEnvFiles();
    for (const envPath of envFiles) {
      const content = fs.readFileSync(envPath, 'utf-8');
      if (/^\s*(?:export\s+)?(?:OPENCLAW_HOST|HOST)\s*=/im.test(content)) {
        return envPath;
      }
    }

    return envFiles[0] ?? null;
  }

  private parseEnvFile(filePath: string): Record<string, string> {
    const content = fs.readFileSync(filePath, 'utf-8');
    const env: Record<string, string> = {};

    for (const rawLine of content.split(/\r?\n/)) {
      const line = rawLine.trim();
      if (!line || line.startsWith('#')) {
        continue;
      }

      const match = rawLine.match(/^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$/);
      if (!match) {
        continue;
      }

      env[match[1]] = this.stripInlineComment(match[2]).trim().replace(/^['"]|['"]$/g, '');
    }

    return env;
  }

  private pickFirstDefined(
    env: Record<string, string>,
    keys: string[]
  ): string | undefined {
    for (const key of keys) {
      const value = env[key];
      if (value) {
        return value;
      }
    }
    return undefined;
  }

  private pickFirstEnvValue(
    envMaps: Array<{ envPath: string; env: Record<string, string> }>,
    keys: string[]
  ): { envPath: string; value: string } | null {
    for (const entry of envMaps) {
      const value = this.pickFirstDefined(entry.env, keys);
      if (value) {
        return {
          envPath: entry.envPath,
          value,
        };
      }
    }
    return null;
  }

  private parsePort(value: string | undefined): number | null {
    if (!value) {
      return null;
    }

    const port = Number.parseInt(value, 10);
    if (!Number.isInteger(port) || port <= 0 || port > 65535) {
      return null;
    }
    return port;
  }

  private inspectNetworkListener(port: number): ListenerSnapshot {
    const isWin = this.platform === 'win32';
    const cmd = isWin
      ? `netstat -ano -p tcp | findstr :${port}`
      : `lsof -nP -iTCP:${port} -sTCP:LISTEN`;

    try {
      const output = this.execCommand(cmd);
      const bindings = isWin
        ? this.parseWindowsBindings(output, port)
        : this.parseUnixBindings(output, port);

      if (bindings.length === 0) {
        return {
          isListening: true,
          bindings: [],
          assessment: 'unknown',
          details: 'Port listener found, but address parsing was inconclusive.',
        };
      }

      return {
        isListening: true,
        bindings,
        assessment: this.assessBindings(bindings),
        details: null,
      };
    } catch {
      return {
        isListening: false,
        bindings: [],
        assessment: 'unknown',
        details: 'Command output was unavailable.',
      };
    }
  }

  private parseUnixBindings(output: string, port: number): string[] {
    const bindings = new Set<string>();
    for (const line of output.split(/\r?\n/)) {
      if (!line.includes(`:${port}`)) {
        continue;
      }

      const match = line.match(/(?:TCP)\s+(.+?):\d+\s+\(LISTEN\)/);
      if (!match) {
        continue;
      }

      bindings.add(this.normalizeHost(match[1]));
    }
    return [...bindings];
  }

  private parseWindowsBindings(output: string, port: number): string[] {
    const bindings = new Set<string>();
    for (const line of output.split(/\r?\n/)) {
      if (!line.toUpperCase().includes('LISTENING')) {
        continue;
      }

      const columns = line.trim().split(/\s+/);
      if (columns.length < 2) {
        continue;
      }

      const localAddress = columns[1];
      const host = this.extractHostFromEndpoint(localAddress, port);
      if (host) {
        bindings.add(host);
      }
    }
    return [...bindings];
  }

  private extractHostFromEndpoint(endpoint: string, port: number): string | null {
    if (endpoint.endsWith(`:${port}`)) {
      return this.normalizeHost(endpoint.slice(0, -(String(port).length + 1)));
    }

    const bracketMatch = endpoint.match(/^\[(.*)\]:(\d+)$/);
    if (bracketMatch && Number(bracketMatch[2]) === port) {
      return this.normalizeHost(bracketMatch[1]);
    }

    return null;
  }

  private assessBindings(bindings: string[]): HostAssessment {
    const assessments = bindings.map((binding) => this.assessHost(binding));
    if (assessments.includes('public-network')) {
      return 'public-network';
    }
    if (assessments.includes('wildcard')) {
      return 'wildcard';
    }
    if (assessments.includes('private-network')) {
      return 'private-network';
    }
    if (assessments.every((value) => value === 'loopback')) {
      return 'loopback';
    }
    return 'unknown';
  }

  private assessHost(host: string): HostAssessment {
    const normalized = this.normalizeHost(host);
    if (!normalized) {
      return 'unknown';
    }
    if (LOOPBACK_HOSTS.has(normalized)) {
      return 'loopback';
    }
    if (WILDCARD_HOSTS.has(normalized)) {
      return 'wildcard';
    }

    if (normalized.startsWith('::ffff:')) {
      return this.assessHost(normalized.slice('::ffff:'.length));
    }

    if (normalized.startsWith('fe80:') || normalized.startsWith('fc') || normalized.startsWith('fd')) {
      return 'private-network';
    }

    if (this.isIPv4(normalized)) {
      if (this.isPrivateIPv4(normalized)) {
        return 'private-network';
      }
      return 'public-network';
    }

    if (normalized.includes(':')) {
      return 'public-network';
    }

    return 'unknown';
  }

  private inspectPrivileges(): PrivilegeSnapshot {
    if (this.platform === 'win32') {
      try {
        this.execCommand('net session');
        return {
          isElevated: true,
          details: 'Detected Windows administrative token.',
        };
      } catch {
        try {
          const groups = this.execCommand('whoami /groups');
          if (groups.includes('S-1-5-32-544')) {
            return {
              isElevated: true,
              details: 'Detected membership in the local Administrators group.',
            };
          }
          return {
            isElevated: false,
            details: 'Windows administrative group membership was not detected.',
          };
        } catch {
          return {
            isElevated: null,
            details: 'Windows elevation check was inconclusive.',
          };
        }
      }
    }

    if (this.getUid) {
      const uid = this.getUid();
      if (uid === 0) {
        return {
          isElevated: true,
          details: 'Current uid is 0 (root).',
        };
      }
      return {
        isElevated: false,
        details: `Current uid is ${uid}.`,
      };
    }

    return {
      isElevated: null,
      details: 'The runtime does not expose process.getuid().',
    };
  }

  private rewriteHostToLoopback(content: string): {
    status: 'updated' | 'already-secure' | 'not-found';
    content: string;
  } {
    const lines = content.split(/\r?\n/);
    let found = false;
    let updated = false;

    const nextLines = lines.map((line) => {
      const match = line.match(
        /^(\s*(?:export\s+)?(?:OPENCLAW_HOST|HOST)\s*=\s*)([^#\r\n]*?)(\s*)(#.*)?$/i
      );
      if (!match) {
        return line;
      }

      found = true;
      const rawValue = match[2].trim();
      const quote = rawValue.startsWith('"') || rawValue.startsWith("'") ? rawValue[0] : '';
      const currentValue = rawValue.replace(/^['"]|['"]$/g, '');
      if (this.assessHost(currentValue) === 'loopback') {
        return line;
      }

      updated = true;
      const nextValue = quote ? `${quote}127.0.0.1${quote}` : '127.0.0.1';
      return `${match[1]}${nextValue}${match[3]}${match[4] ?? ''}`;
    });

    if (!found) {
      return { status: 'not-found', content };
    }
    if (!updated) {
      return { status: 'already-secure', content };
    }

    return { status: 'updated', content: nextLines.join('\n') };
  }

  private stripInlineComment(value: string): string {
    let inSingleQuote = false;
    let inDoubleQuote = false;

    for (let i = 0; i < value.length; i += 1) {
      const char = value[i];
      if (char === "'" && !inDoubleQuote) {
        inSingleQuote = !inSingleQuote;
        continue;
      }
      if (char === '"' && !inSingleQuote) {
        inDoubleQuote = !inDoubleQuote;
        continue;
      }
      if (char === '#' && !inSingleQuote && !inDoubleQuote) {
        return value.slice(0, i);
      }
    }

    return value;
  }

  private normalizeHost(host: string): string {
    return host.trim().replace(/^\[|\]$/g, '').toLowerCase();
  }

  private isIPv4(host: string): boolean {
    return /^\d{1,3}(?:\.\d{1,3}){3}$/.test(host);
  }

  private isPrivateIPv4(host: string): boolean {
    const parts = host.split('.').map((value) => Number.parseInt(value, 10));
    if (parts.some((value) => Number.isNaN(value) || value < 0 || value > 255)) {
      return false;
    }

    const [a, b] = parts;
    return (
      a === 10 ||
      a === 127 ||
      (a === 172 && b >= 16 && b <= 31) ||
      (a === 192 && b === 168) ||
      (a === 169 && b === 254)
    );
  }
}
