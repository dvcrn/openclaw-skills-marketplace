#!/usr/bin/env node
/**
 * ldm - LDM OS CLI
 * The kernel for agent-native software.
 *
 * Commands:
 *   ldm init              Scaffold ~/.ldm/ and write version.json
 *   ldm install <target>  Detect interfaces + deploy + register
 *   ldm install           Install/update all registered components
 *   ldm doctor            Check health of all extensions
 *   ldm status            Show LDM OS version and extension count
 *   ldm --version         Show version
 */

import { existsSync, readFileSync, writeFileSync, mkdirSync, readdirSync } from 'node:fs';
import { join, basename, resolve, dirname } from 'node:path';
import { execSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const HOME = process.env.HOME || '';
const LDM_ROOT = join(HOME, '.ldm');
const LDM_EXTENSIONS = join(LDM_ROOT, 'extensions');
const VERSION_PATH = join(LDM_ROOT, 'version.json');
const REGISTRY_PATH = join(LDM_EXTENSIONS, 'registry.json');

// Read our own version from package.json
const pkgPath = join(__dirname, '..', 'package.json');
let PKG_VERSION = '0.2.0';
try {
  PKG_VERSION = JSON.parse(readFileSync(pkgPath, 'utf8')).version;
} catch {}

// Read catalog
const catalogPath = join(__dirname, '..', 'catalog.json');
let CATALOG = { components: [] };
try {
  CATALOG = JSON.parse(readFileSync(catalogPath, 'utf8'));
} catch {}

const args = process.argv.slice(2);
const command = args[0];
const DRY_RUN = args.includes('--dry-run');
const JSON_OUTPUT = args.includes('--json');
const YES_FLAG = args.includes('--yes') || args.includes('-y');
const NONE_FLAG = args.includes('--none');

function readJSON(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return null;
  }
}

function writeJSON(path, data) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, JSON.stringify(data, null, 2) + '\n');
}

// ── Catalog helpers ──

function loadCatalog() {
  return CATALOG.components || [];
}

function findInCatalog(id) {
  return loadCatalog().find(c => c.id === id);
}

// ── ldm init ──

async function cmdInit() {
  console.log('');
  console.log('  ldm init');
  console.log('  ────────────────────────────────────');

  const dirs = [
    join(LDM_ROOT, 'extensions'),
    join(LDM_ROOT, 'agents'),
    join(LDM_ROOT, 'memory'),
    join(LDM_ROOT, 'state'),
    join(LDM_ROOT, 'secrets'),
    join(LDM_ROOT, 'shared', 'boot'),
  ];

  const existing = existsSync(VERSION_PATH);

  if (DRY_RUN) {
    for (const dir of dirs) {
      if (existsSync(dir)) {
        console.log(`  - ${dir} (exists)`);
      } else {
        console.log(`  + would create ${dir}`);
      }
    }
    if (existing) {
      const v = readJSON(VERSION_PATH);
      console.log(`  - version.json exists (v${v?.version})`);
    } else {
      console.log(`  + would write version.json (v${PKG_VERSION})`);
    }
    console.log('');
    console.log('  Dry run complete. No changes made.');
    console.log('');
    return;
  }

  let created = 0;
  for (const dir of dirs) {
    if (!existsSync(dir)) {
      mkdirSync(dir, { recursive: true });
      console.log(`  + ${dir}`);
      created++;
    } else {
      console.log(`  - ${dir} (exists)`);
    }
  }

  // Write or update version.json
  const now = new Date().toISOString();
  if (existing) {
    const v = readJSON(VERSION_PATH);
    v.version = PKG_VERSION;
    v.updated = now;
    writeJSON(VERSION_PATH, v);
    console.log(`  + version.json updated to v${PKG_VERSION}`);
  } else {
    writeJSON(VERSION_PATH, {
      version: PKG_VERSION,
      installed: now,
      updated: now,
    });
    console.log(`  + version.json created (v${PKG_VERSION})`);
  }

  // Seed registry if missing
  if (!existsSync(REGISTRY_PATH)) {
    writeJSON(REGISTRY_PATH, { _format: 'v1', extensions: {} });
    console.log(`  + registry.json created`);
  }

  console.log('');
  console.log(`  LDM OS v${PKG_VERSION} initialized at ${LDM_ROOT}`);
  console.log('');

  // Show catalog picker (unless --none or --dry-run)
  if (!NONE_FLAG && !DRY_RUN) {
    await showCatalogPicker();
  }
}

async function showCatalogPicker() {
  const components = loadCatalog();
  if (components.length === 0) return;

  // Check what's already installed
  const registry = readJSON(REGISTRY_PATH);
  const installed = Object.keys(registry?.extensions || {});

  const available = components.filter(c => c.status !== 'coming-soon' && !installed.includes(c.id));
  const comingSoon = components.filter(c => c.status === 'coming-soon');

  if (available.length === 0 && comingSoon.length === 0) return;

  console.log('  Available components:');
  console.log('');

  let idx = 1;
  const selectable = [];
  for (const c of available) {
    const rec = c.recommended ? ' (recommended)' : '';
    console.log(`    ${idx}. ${c.name}${rec}`);
    console.log(`       ${c.description}`);
    console.log('');
    selectable.push(c);
    idx++;
  }

  for (const c of comingSoon) {
    console.log(`    ${idx}. ${c.name} (coming soon)`);
    console.log(`       ${c.description}`);
    console.log('');
    idx++;
  }

  // If --yes, install recommended only
  if (YES_FLAG) {
    const recommended = selectable.filter(c => c.recommended);
    if (recommended.length > 0) {
      for (const c of recommended) {
        console.log(`  Installing ${c.name}...`);
        try {
          execSync(`ldm install ${c.repo}`, { stdio: 'inherit' });
        } catch (e) {
          console.error(`  x Failed to install ${c.name}: ${e.message}`);
        }
      }
    }
    return;
  }

  // Interactive prompt (skip if not a TTY)
  if (!process.stdin.isTTY) return;

  const { createInterface } = await import('node:readline');
  const rl = createInterface({ input: process.stdin, output: process.stdout });

  const answer = await new Promise((resolve) => {
    rl.question('  Install components? [1,2,all,none]: ', (a) => {
      rl.close();
      resolve(a.trim().toLowerCase());
    });
  });

  if (!answer || answer === 'none' || answer === 'n') return;

  let toInstall = [];
  if (answer === 'all' || answer === 'a') {
    toInstall = selectable;
  } else {
    const nums = answer.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n));
    toInstall = nums.map(n => selectable[n - 1]).filter(Boolean);
  }

  for (const c of toInstall) {
    console.log('');
    console.log(`  Installing ${c.name}...`);
    try {
      execSync(`ldm install ${c.repo}`, { stdio: 'inherit' });
    } catch (e) {
      console.error(`  x Failed to install ${c.name}: ${e.message}`);
    }
  }
}

// ── ldm install ──

async function cmdInstall() {
  // Ensure LDM is initialized
  if (!existsSync(VERSION_PATH)) {
    console.log('  LDM OS not initialized. Running init first...');
    console.log('');
    cmdInit();
  }

  const { setFlags, installFromPath, installSingleTool, installToolbox } = await import('../lib/deploy.mjs');
  const { detectInterfacesJSON } = await import('../lib/detect.mjs');

  setFlags({ dryRun: DRY_RUN, jsonOutput: JSON_OUTPUT });

  // Find the target (skip flags)
  const target = args.slice(1).find(a => !a.startsWith('--'));

  if (!target) {
    // Bare `ldm install`: show catalog status + update registered
    return cmdInstallCatalog();
  }

  // Check if target is a catalog ID (e.g. "memory-crystal")
  const catalogEntry = findInCatalog(target);
  if (catalogEntry) {
    console.log('');
    console.log(`  Resolved "${target}" via catalog to ${catalogEntry.repo}`);

    // Use the repo field to clone from GitHub
    const repoTarget = catalogEntry.repo;
    const repoName = basename(repoTarget);
    const repoPath = join('/tmp', `ldm-install-${repoName}`);
    const httpsUrl = `https://github.com/${repoTarget}.git`;
    const sshUrl = `git@github.com:${repoTarget}.git`;

    console.log(`  Cloning ${repoTarget}...`);
    try {
      if (existsSync(repoPath)) {
        execSync(`rm -rf "${repoPath}"`, { stdio: 'pipe' });
      }
      try {
        execSync(`git clone "${httpsUrl}" "${repoPath}"`, { stdio: 'pipe' });
      } catch {
        console.log(`  HTTPS failed. Trying SSH...`);
        if (existsSync(repoPath)) execSync(`rm -rf "${repoPath}"`, { stdio: 'pipe' });
        execSync(`git clone "${sshUrl}" "${repoPath}"`, { stdio: 'pipe' });
      }
      console.log(`  + Cloned to ${repoPath}`);
    } catch (e) {
      console.error(`  x Clone failed: ${e.message}`);
      process.exit(1);
    }

    if (JSON_OUTPUT) {
      const result = detectInterfacesJSON(repoPath);
      console.log(JSON.stringify(result, null, 2));
      if (DRY_RUN) process.exit(0);
    }

    await installFromPath(repoPath);
    return;
  }

  // Resolve target: GitHub URL, org/repo shorthand, or local path
  let repoPath;

  if (target.startsWith('http') || target.startsWith('git@') || target.match(/^[\w-]+\/[\w.-]+$/)) {
    const isShorthand = target.match(/^[\w-]+\/[\w.-]+$/);
    const httpsUrl = isShorthand
      ? `https://github.com/${target}.git`
      : target;
    const sshUrl = isShorthand
      ? `git@github.com:${target}.git`
      : target.replace(/^https:\/\/github\.com\//, 'git@github.com:');
    const repoName = basename(httpsUrl).replace('.git', '');
    repoPath = join('/tmp', `ldm-install-${repoName}`);

    console.log('');
    console.log(`  Cloning ${isShorthand ? target : httpsUrl}...`);
    try {
      if (existsSync(repoPath)) {
        execSync(`rm -rf "${repoPath}"`, { stdio: 'pipe' });
      }
      try {
        execSync(`git clone "${httpsUrl}" "${repoPath}"`, { stdio: 'pipe' });
      } catch {
        console.log(`  HTTPS failed. Trying SSH...`);
        if (existsSync(repoPath)) execSync(`rm -rf "${repoPath}"`, { stdio: 'pipe' });
        execSync(`git clone "${sshUrl}" "${repoPath}"`, { stdio: 'pipe' });
      }
      console.log(`  + Cloned to ${repoPath}`);
    } catch (e) {
      console.error(`  x Clone failed: ${e.message}`);
      process.exit(1);
    }
  } else {
    repoPath = resolve(target);
    if (!existsSync(repoPath)) {
      console.error(`  x Path not found: ${repoPath}`);
      process.exit(1);
    }
  }

  if (JSON_OUTPUT) {
    const result = detectInterfacesJSON(repoPath);
    console.log(JSON.stringify(result, null, 2));
    if (DRY_RUN) process.exit(0);
  }

  await installFromPath(repoPath);
}

// ── Auto-detect unregistered extensions ──

function autoDetectExtensions() {
  if (!existsSync(LDM_EXTENSIONS)) return;
  const registry = readJSON(REGISTRY_PATH);
  if (!registry) return;

  const registered = Object.keys(registry.extensions || {});
  let found = 0;

  try {
    const dirs = readdirSync(LDM_EXTENSIONS, { withFileTypes: true });
    for (const dir of dirs) {
      if (!dir.isDirectory()) continue;
      if (dir.name === '_trash' || dir.name.startsWith('.')) continue;

      const extPath = join(LDM_EXTENSIONS, dir.name);
      const pkgPath = join(extPath, 'package.json');
      if (!existsSync(pkgPath)) continue;

      // Check if already registered (by directory name or by ldmPath)
      const alreadyRegistered = registered.some(name => {
        const info = registry.extensions[name];
        return name === dir.name || info?.ldmPath === extPath;
      });
      if (alreadyRegistered) continue;

      // Auto-register
      const pkg = readJSON(pkgPath);
      if (!pkg) continue;

      registry.extensions[dir.name] = {
        name: dir.name,
        version: pkg.version || '?',
        source: null,
        interfaces: [],
        ldmPath: extPath,
        updatedAt: new Date().toISOString(),
        autoDetected: true,
      };
      found++;
    }
  } catch {}

  if (found > 0) {
    writeJSON(REGISTRY_PATH, registry);
  }
  return found;
}

// ── ldm install (bare): scan system, show real state, update if needed ──

async function cmdInstallCatalog() {
  autoDetectExtensions();

  const { detectSystemState, reconcileState, formatReconciliation } = await import('../lib/state.mjs');
  const state = detectSystemState();
  const reconciled = reconcileState(state);

  // Show the real system state
  console.log(formatReconciliation(reconciled));

  // Check catalog: use registryMatches + cliMatches to detect what's really installed
  const registry = readJSON(REGISTRY_PATH);
  const registeredNames = Object.keys(registry?.extensions || {});
  const reconciledNames = Object.keys(reconciled);
  const components = loadCatalog();

  function isCatalogItemInstalled(c) {
    // Direct ID match
    if (registeredNames.includes(c.id) || reconciled[c.id]) return true;
    // Check registryMatches (aliases)
    const matches = c.registryMatches || [];
    if (matches.some(m => registeredNames.includes(m) || reconciled[m])) return true;
    // Check CLI binaries
    const cliMatches = c.cliMatches || [];
    if (cliMatches.some(b => state.cliBinaries[b])) return true;
    return false;
  }

  const available = components.filter(c =>
    c.status !== 'coming-soon' && !isCatalogItemInstalled(c)
  );

  if (available.length > 0) {
    console.log('  Available in catalog (not yet installed):');
    for (const c of available) {
      console.log(`    [ ] ${c.name} ... ${c.description}`);
    }
    console.log('');
  } else {
    console.log('  All catalog components are installed.');
    console.log('');
  }

  if (DRY_RUN) {
    // Show what an update would do
    const updatable = Object.values(reconciled).filter(e =>
      e.registryHasSource
    );

    if (updatable.length > 0) {
      console.log(`  Would update ${updatable.length} extension(s) from source repos.`);
      console.log('  No data (crystal.db, agent files) would be touched.');
      console.log('  Old versions would be moved to ~/.ldm/_trash/ (never deleted).');
    } else {
      console.log('  Everything is up to date. No changes needed.');
    }

    console.log('');
    console.log('  Dry run complete. No changes made.');
    console.log('');
    return;
  }

  // Real update: only touch things with linked source repos
  const updatable = Object.values(reconciled).filter(e =>
    e.registryHasSource
  );

  if (updatable.length === 0) {
    console.log('  No extensions have linked source repos to update from.');
    console.log('  Link them with: ldm install <org/repo>');
    console.log('');

    // Still offer catalog install if TTY
    if (available.length > 0 && !YES_FLAG && !NONE_FLAG && process.stdin.isTTY) {
      const { createInterface } = await import('node:readline');
      const rl = createInterface({ input: process.stdin, output: process.stdout });
      const answer = await new Promise((resolve) => {
        rl.question('  Install from catalog? [number,all,none]: ', (a) => {
          rl.close();
          resolve(a.trim().toLowerCase());
        });
      });

      if (answer && answer !== 'none' && answer !== 'n') {
        let toInstall = [];
        if (answer === 'all' || answer === 'a') {
          toInstall = available;
        } else {
          const nums = answer.split(',').map(s => parseInt(s.trim(), 10)).filter(n => !isNaN(n));
          toInstall = nums.map(n => available[n - 1]).filter(Boolean);
        }
        for (const c of toInstall) {
          console.log(`  Installing ${c.name}...`);
          try {
            execSync(`ldm install ${c.repo}`, { stdio: 'inherit' });
          } catch (e) {
            console.error(`  x Failed to install ${c.name}: ${e.message}`);
          }
        }
      }
    }
    return;
  }

  // Write revert manifest before starting
  const { createRevertManifest } = await import('../lib/safe.mjs');
  const manifestPath = createRevertManifest(
    `ldm install (update ${updatable.length} extensions)`,
    updatable.map(e => ({
      action: 'update',
      name: e.name,
      currentVersion: e.ldmVersion || e.registryVersion,
      source: e.registrySource,
    }))
  );
  console.log(`  Revert plan saved: ${manifestPath}`);
  console.log('');

  const { setFlags, installFromPath } = await import('../lib/deploy.mjs');
  setFlags({ dryRun: DRY_RUN, jsonOutput: JSON_OUTPUT });

  let updated = 0;
  for (const entry of updatable) {
    await installFromPath(entry.registrySource);
    updated++;
  }

  console.log('');
  console.log(`  Updated ${updated}/${updatable.length} extension(s).`);
  console.log('');
}

async function cmdUpdateAll() {
  // Delegate to the catalog flow which now has full state awareness
  return cmdInstallCatalog();
}

// ── ldm doctor ──

async function cmdDoctor() {
  console.log('');
  console.log('  ldm doctor');
  console.log('  ────────────────────────────────────');

  // Auto-detect unregistered extensions before checking
  const detected = autoDetectExtensions();
  if (detected > 0) {
    console.log(`  + Auto-detected ${detected} unregistered extension(s)`);
  }

  let issues = 0;

  // 1. Check LDM root
  if (!existsSync(LDM_ROOT)) {
    console.log('  x ~/.ldm/ does not exist. Run: ldm init');
    issues++;
  } else {
    console.log('  + ~/.ldm/ exists');
  }

  // 2. Check version.json
  const version = readJSON(VERSION_PATH);
  if (!version) {
    console.log('  x version.json missing. Run: ldm init');
    issues++;
  } else {
    console.log(`  + version.json: v${version.version} (installed ${version.installed?.split('T')[0]})`);
  }

  // 3. Full system state scan
  const { detectSystemState, reconcileState, formatReconciliation } = await import('../lib/state.mjs');
  const state = detectSystemState();
  const reconciled = reconcileState(state);

  // Show reconciled view
  console.log(formatReconciliation(reconciled, { verbose: true }));

  // Count issues from reconciliation
  for (const entry of Object.values(reconciled)) {
    if (entry.status === 'registered-missing') issues++;
    if (entry.issues.length > 0 && entry.status !== 'installed-unlinked' && entry.status !== 'external') {
      issues += entry.issues.length;
    }
  }

  // 4. Check sacred locations
  const sacred = [
    { path: join(LDM_ROOT, 'memory'), label: 'memory/' },
    { path: join(LDM_ROOT, 'agents'), label: 'agents/' },
    { path: join(LDM_ROOT, 'state'), label: 'state/' },
  ];

  for (const s of sacred) {
    if (existsSync(s.path)) {
      console.log(`  + ${s.label} exists`);
    } else {
      console.log(`  ! ${s.label} missing (run: ldm init)`);
      issues++;
    }
  }

  // 5. Check settings.json for hooks
  const settingsPath = join(HOME, '.claude', 'settings.json');
  const settings = readJSON(settingsPath);
  if (settings?.hooks) {
    const hookCount = Object.values(settings.hooks).reduce((sum, arr) => sum + (arr?.length || 0), 0);
    console.log(`  + Claude Code hooks: ${hookCount} configured`);
  } else {
    console.log(`  - Claude Code hooks: none configured`);
  }

  // 6. MCP servers
  const mcpCount = Object.keys(state.mcp).length;
  console.log(`  + MCP servers: ${mcpCount} registered`);

  // 7. CLI binaries
  const binCount = Object.keys(state.cliBinaries).length;
  if (binCount > 0) {
    console.log(`  + CLI binaries: ${Object.keys(state.cliBinaries).join(', ')}`);
  }

  console.log('');
  if (issues === 0) {
    console.log('  All checks passed.');
  } else {
    console.log(`  ${issues} issue(s) found.`);
  }
  console.log('');
}

// ── ldm status ──

function cmdStatus() {
  const version = readJSON(VERSION_PATH);
  const registry = readJSON(REGISTRY_PATH);
  const extCount = Object.keys(registry?.extensions || {}).length;

  if (JSON_OUTPUT) {
    console.log(JSON.stringify({
      version: version?.version || null,
      installed: version?.installed || null,
      updated: version?.updated || null,
      extensions: extCount,
      ldmRoot: LDM_ROOT,
    }, null, 2));
    return;
  }

  if (!version) {
    console.log('  LDM OS not installed. Run: ldm init');
    return;
  }

  console.log('');
  console.log(`  LDM OS v${version.version}`);
  console.log(`  Installed: ${version.installed?.split('T')[0]}`);
  console.log(`  Updated:   ${version.updated?.split('T')[0]}`);
  console.log(`  Extensions: ${extCount}`);
  console.log(`  Root: ${LDM_ROOT}`);

  if (extCount > 0) {
    console.log('');
    for (const [name, info] of Object.entries(registry.extensions)) {
      console.log(`    ${name} v${info.version || '?'} (${(info.interfaces || []).join(', ')})`);
    }
  }

  console.log('');
}

// ── Main ──

async function main() {
  if (!command || command === '--help' || command === '-h') {
    console.log('');
    console.log('  ldm ... LDM OS kernel');
    console.log('');
    console.log('  Usage:');
    console.log('    ldm init                    Scaffold ~/.ldm/ and write version.json');
    console.log('    ldm install <org/repo>      Install from GitHub (clones, detects, deploys)');
    console.log('    ldm install /path/to/repo   Install from local path');
    console.log('    ldm install                 Update all registered extensions');
    console.log('    ldm doctor                  Check health of all extensions');
    console.log('    ldm status                  Show version and extension list');
    console.log('');
    console.log('  Flags:');
    console.log('    --dry-run   Show what would happen without making changes');
    console.log('    --json      Output results as JSON');
    console.log('');
    console.log('  Interfaces detected:');
    console.log('    CLI        ... package.json bin -> npm install -g');
    console.log('    Module     ... ESM main/exports -> importable');
    console.log('    MCP Server ... mcp-server.mjs -> claude mcp add --scope user');
    console.log('    OpenClaw   ... openclaw.plugin.json -> ~/.ldm/extensions/ + ~/.openclaw/extensions/');
    console.log('    Skill      ... SKILL.md -> ~/.openclaw/skills/<tool>/');
    console.log('    CC Hook    ... guard.mjs or claudeCode.hook -> ~/.claude/settings.json');
    console.log('');
    console.log(`  v${PKG_VERSION}`);
    console.log('');
    process.exit(0);
  }

  if (command === '--version' || command === '-v') {
    console.log(PKG_VERSION);
    process.exit(0);
  }

  switch (command) {
    case 'init':
      await cmdInit();
      break;
    case 'install':
      await cmdInstall();
      break;
    case 'update':
      // Alias: `ldm update` = `ldm install` (update all registered)
      await cmdUpdateAll();
      break;
    case 'doctor':
      cmdDoctor();
      break;
    case 'status':
      cmdStatus();
      break;
    default:
      console.error(`  Unknown command: ${command}`);
      console.error(`  Run: ldm --help`);
      process.exit(1);
  }
}

main().catch(e => {
  console.error(`  x ${e.message}`);
  process.exit(1);
});
