/**
 * lib/deploy.mjs
 * Deployment engine for LDM OS extensions.
 * Adapted from wip-universal-installer/install.js with three bugs fixed:
 *   #6: Runs build step for TypeScript extensions
 *   #7: Never rm -rf. Uses incremental copy (deploy to temp, verify, swap).
 *   #8: Respects OpenClaw plugin directory naming from config.
 * Zero external dependencies.
 */

import { execSync } from 'node:child_process';
import {
  existsSync, readFileSync, writeFileSync, cpSync, mkdirSync,
  lstatSync, readlinkSync, unlinkSync, chmodSync, readdirSync,
  renameSync, rmSync, statSync,
} from 'node:fs';
import { join, basename, resolve, dirname } from 'node:path';
import { tmpdir } from 'node:os';
import { detectInterfaces, describeInterfaces, detectToolbox } from './detect.mjs';
import { moveToTrash, appendToManifest } from './safe.mjs';

const HOME = process.env.HOME || '';
const LDM_ROOT = join(HOME, '.ldm');
const LDM_EXTENSIONS = join(LDM_ROOT, 'extensions');
const OC_ROOT = join(HOME, '.openclaw');
const OC_EXTENSIONS = join(OC_ROOT, 'extensions');
const REGISTRY_PATH = join(LDM_EXTENSIONS, 'registry.json');

// ── Logging ──

let DRY_RUN = false;
let JSON_OUTPUT = false;

export function setFlags(opts = {}) {
  DRY_RUN = opts.dryRun || false;
  JSON_OUTPUT = opts.jsonOutput || false;
}

function log(msg) { if (!JSON_OUTPUT) console.log(`  ${msg}`); }
function ok(msg) { if (!JSON_OUTPUT) console.log(`  + ${msg}`); }
function skip(msg) { if (!JSON_OUTPUT) console.log(`  - ${msg}`); }
function fail(msg) { if (!JSON_OUTPUT) console.error(`  x ${msg}`); }

// ── Helpers ──

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

function ensureBinExecutable(binNames) {
  try {
    const npmPrefix = execSync('npm config get prefix', { encoding: 'utf8' }).trim();
    for (const bin of binNames) {
      const binPath = join(npmPrefix, 'bin', bin);
      try { chmodSync(binPath, 0o755); } catch {}
    }
  } catch {}
}

// ── Registry ──

function loadRegistry() {
  return readJSON(REGISTRY_PATH) || { _format: 'v1', extensions: {} };
}

function saveRegistry(registry) {
  writeJSON(REGISTRY_PATH, registry);
}

function updateRegistry(name, info) {
  const registry = loadRegistry();
  registry.extensions[name] = {
    ...registry.extensions[name],
    ...info,
    updatedAt: new Date().toISOString(),
  };
  saveRegistry(registry);
}

// ── Migration detection ──

function findExistingInstalls(toolName, pkg, ocPluginConfig) {
  const matches = [];
  const packageName = pkg?.name;
  const pluginId = ocPluginConfig?.id;

  for (const extDir of [LDM_EXTENSIONS, OC_EXTENSIONS]) {
    if (!existsSync(extDir)) continue;
    let entries;
    try {
      entries = readdirSync(extDir, { withFileTypes: true });
    } catch { continue; }

    for (const entry of entries) {
      if (!entry.isDirectory() && !entry.isSymbolicLink()) continue;
      const dirName = entry.name;
      if (dirName === toolName) continue;
      if (dirName === 'registry.json') continue;

      const dirPath = join(extDir, dirName);

      if (packageName) {
        const dirPkg = readJSON(join(dirPath, 'package.json'));
        if (dirPkg?.name === packageName) {
          if (!matches.some(m => m.dirName === dirName)) {
            matches.push({ dirName, matchType: 'package', path: dirPath });
          }
          continue;
        }
      }

      if (pluginId) {
        const dirPlugin = readJSON(join(dirPath, 'openclaw.plugin.json'));
        if (dirPlugin?.id === pluginId) {
          if (!matches.some(m => m.dirName === dirName)) {
            matches.push({ dirName, matchType: 'plugin-id', path: dirPath });
          }
          continue;
        }
      }
    }
  }

  return matches;
}

// ── Build step (fix #6) ──

function runBuildIfNeeded(repoPath) {
  const pkg = readJSON(join(repoPath, 'package.json'));
  if (!pkg) return;

  const hasBuildScript = !!pkg.scripts?.build;
  const hasTsConfig = existsSync(join(repoPath, 'tsconfig.json'));
  const hasDist = existsSync(join(repoPath, 'dist'));

  // Build if: has a build script AND (no dist/ or tsconfig exists implying TS)
  if (hasBuildScript && (!hasDist || hasTsConfig)) {
    log(`Building ${pkg.name || basename(repoPath)}...`);
    try {
      // Install deps first if node_modules is missing
      if (!existsSync(join(repoPath, 'node_modules'))) {
        execSync('npm install', { cwd: repoPath, stdio: 'pipe' });
      }
      execSync('npm run build', { cwd: repoPath, stdio: 'pipe' });
      ok(`Build complete`);
    } catch (e) {
      fail(`Build failed: ${e.stderr?.toString()?.slice(0, 200) || e.message}`);
    }
  }
}

// ── Version comparison (fix #7) ──

function compareSemver(a, b) {
  if (!a || !b) return 0;
  const pa = a.split('.').map(Number);
  const pb = b.split('.').map(Number);
  for (let i = 0; i < 3; i++) {
    const na = pa[i] || 0;
    const nb = pb[i] || 0;
    if (na > nb) return 1;
    if (na < nb) return -1;
  }
  return 0;
}

// Config files that should never be overwritten during updates
const PRESERVE_PATTERNS = [
  'boot-config.json', '.env', '.env.local',
  'config.local.json', 'settings.local.json',
];

function isPreservedFile(filename) {
  return PRESERVE_PATTERNS.some(p => filename === p || filename.endsWith('.local'));
}

// ── Safe deploy (fix #7) ──
// Deploy to temp dir first, then atomic rename. Never rm -rf the live dir.
// Preserves config files from existing installs.

function copyFiltered(src, dest) {
  cpSync(src, dest, {
    recursive: true,
    filter: (s) => !s.includes('.git') && !s.includes('node_modules') && !s.includes('/ai/'),
  });
}

function restorePreservedFiles(oldDir, newDir) {
  if (!existsSync(oldDir)) return;
  try {
    const entries = readdirSync(oldDir);
    for (const entry of entries) {
      if (isPreservedFile(entry)) {
        const oldPath = join(oldDir, entry);
        const newPath = join(newDir, entry);
        if (existsSync(oldPath) && !existsSync(newPath)) {
          cpSync(oldPath, newPath);
          ok(`Preserved config: ${entry}`);
        }
      }
    }
  } catch {}
}

function safeDeployDir(repoPath, destDir, name) {
  const finalPath = join(destDir, name);
  const tempPath = join(tmpdir(), `ldm-deploy-${name}-${Date.now()}`);
  const backupPath = finalPath + '.bak';

  try {
    // 1. Copy to temp
    mkdirSync(tempPath, { recursive: true });
    copyFiltered(repoPath, tempPath);

    // 2. Install deps in temp
    if (existsSync(join(tempPath, 'package.json'))) {
      try {
        execSync('npm install --omit=dev', { cwd: tempPath, stdio: 'pipe' });
      } catch {}
    }

    // 3. Verify temp has package.json (basic sanity)
    if (!existsSync(join(tempPath, 'package.json'))) {
      fail(`Deploy verification failed: no package.json in staged copy`);
      rmSync(tempPath, { recursive: true, force: true });
      return false;
    }

    // 4. Swap: old -> backup, temp -> final
    mkdirSync(destDir, { recursive: true });
    if (existsSync(finalPath)) {
      renameSync(finalPath, backupPath);
    }
    renameSync(tempPath, finalPath);

    // 5. Restore preserved config files from old version
    if (existsSync(backupPath)) {
      restorePreservedFiles(backupPath, finalPath);
    }

    // 6. Trash the old version (never delete)
    if (existsSync(backupPath)) {
      const trashed = moveToTrash(backupPath);
      if (trashed) ok(`Old version moved to ${trashed}`);
    }

    return true;
  } catch (e) {
    // Rollback: if temp was moved but something else failed, try to restore backup
    if (!existsSync(finalPath) && existsSync(backupPath)) {
      try { renameSync(backupPath, finalPath); } catch {}
    }
    // Clean up temp if it still exists
    if (existsSync(tempPath)) {
      rmSync(tempPath, { recursive: true, force: true });
    }
    fail(`Deploy failed: ${e.message}`);
    return false;
  }
}

// ── OpenClaw plugin naming (fix #8) ──

function resolveOcPluginName(repoPath, toolName) {
  // OpenClaw matches plugins by directory name, not plugin id.
  // Check openclaw.json for existing references to this plugin.
  const ocConfigPath = join(OC_ROOT, 'openclaw.json');
  const ocConfig = readJSON(ocConfigPath);
  if (!ocConfig?.extensions) return toolName;

  const ocPlugin = readJSON(join(repoPath, 'openclaw.plugin.json'));
  if (!ocPlugin?.id) return toolName;

  // Scan openclaw.json extensions array for a matching plugin id
  // and use whatever directory name it expects
  for (const ext of ocConfig.extensions) {
    if (ext.id === ocPlugin.id && ext.path) {
      const existingName = basename(ext.path);
      if (existingName !== toolName) {
        log(`OpenClaw expects plugin at "${existingName}" (not "${toolName}"). Using existing name.`);
        return existingName;
      }
    }
  }

  // Also check if a directory already exists with this plugin's package
  if (existsSync(OC_EXTENSIONS)) {
    try {
      const entries = readdirSync(OC_EXTENSIONS, { withFileTypes: true });
      for (const entry of entries) {
        if (!entry.isDirectory()) continue;
        const dirPlugin = readJSON(join(OC_EXTENSIONS, entry.name, 'openclaw.plugin.json'));
        if (dirPlugin?.id === ocPlugin.id && entry.name !== toolName) {
          log(`OpenClaw has plugin at "${entry.name}" (not "${toolName}"). Using existing name.`);
          return entry.name;
        }
      }
    } catch {}
  }

  return toolName;
}

// ── Install functions ──

function installCLI(repoPath, door) {
  const pkg = readJSON(join(repoPath, 'package.json'));
  const binNames = typeof door.bin === 'string' ? [basename(repoPath)] : Object.keys(door.bin || {});
  const newVersion = pkg?.version;

  // Check if already installed at this version
  if (newVersion && binNames.length > 0) {
    try {
      const installed = execSync(`npm list -g ${pkg.name} --json 2>/dev/null`, { encoding: 'utf8' });
      const data = JSON.parse(installed);
      const deps = data.dependencies || {};
      if (deps[pkg.name]?.version === newVersion) {
        ensureBinExecutable(binNames);
        skip(`CLI: ${binNames.join(', ')} already at v${newVersion}`);
        return true;
      }
    } catch {}
  }

  if (DRY_RUN) {
    ok(`CLI: would install ${binNames.join(', ')} globally (dry run)`);
    return true;
  }

  // Build if needed (fix #6)
  runBuildIfNeeded(repoPath);

  try {
    execSync('npm install -g .', { cwd: repoPath, stdio: 'pipe' });
    ensureBinExecutable(binNames);
    ok(`CLI: ${binNames.join(', ')} installed globally`);
    return true;
  } catch (e) {
    const stderr = e.stderr?.toString() || '';
    if (stderr.includes('EEXIST')) {
      for (const bin of binNames) {
        try {
          const binPath = execSync('npm config get prefix', { encoding: 'utf8' }).trim() + '/bin/' + bin;
          if (existsSync(binPath) && lstatSync(binPath).isSymbolicLink()) {
            const target = readlinkSync(binPath);
            if (!target.includes(pkg.name.replace(/^@[^/]+\//, ''))) {
              unlinkSync(binPath);
            }
          }
        } catch {}
      }
      try {
        execSync('npm install -g .', { cwd: repoPath, stdio: 'pipe' });
        ensureBinExecutable(binNames);
        ok(`CLI: ${binNames.join(', ')} installed globally (replaced stale symlink)`);
        return true;
      } catch {}
    }
    try {
      execSync('npm link', { cwd: repoPath, stdio: 'pipe' });
      ensureBinExecutable(binNames);
      ok(`CLI: linked globally via npm link`);
      return true;
    } catch {
      fail(`CLI: install failed. Run manually: cd "${repoPath}" && npm install -g .`);
      return false;
    }
  }
}

function deployExtension(repoPath, name) {
  const sourcePkg = readJSON(join(repoPath, 'package.json'));
  const ldmDest = join(LDM_EXTENSIONS, name);
  const installedPkg = readJSON(join(ldmDest, 'package.json'));
  const newVersion = sourcePkg?.version;
  const currentVersion = installedPkg?.version;

  const cmp = compareSemver(newVersion, currentVersion);
  if (newVersion && currentVersion && cmp <= 0) {
    skip(`LDM: ${name} already at v${currentVersion}${cmp < 0 ? ` (source is older: v${newVersion})` : ''}`);
    // Ensure OC copy exists too
    const ocName = resolveOcPluginName(repoPath, name);
    const ocDest = join(OC_EXTENSIONS, ocName);
    if (!existsSync(ocDest) && !DRY_RUN) {
      mkdirSync(ocDest, { recursive: true });
      cpSync(ldmDest, ocDest, { recursive: true });
      ok(`OpenClaw: synced to ${ocDest}`);
    } else {
      skip(`OpenClaw: ${ocName} already at v${currentVersion}`);
    }
    return true;
  }

  if (DRY_RUN) {
    if (currentVersion) {
      ok(`LDM: would upgrade ${name} v${currentVersion} -> v${newVersion} (dry run)`);
    } else {
      ok(`LDM: would deploy ${name} v${newVersion || 'unknown'} to ${ldmDest} (dry run)`);
    }
    ok(`OpenClaw: would deploy (dry run)`);
    return true;
  }

  // Build if needed (fix #6)
  runBuildIfNeeded(repoPath);

  // Safe deploy to LDM (fix #7: no rm -rf)
  if (!safeDeployDir(repoPath, LDM_EXTENSIONS, name)) {
    return false;
  }

  if (currentVersion) {
    ok(`LDM: upgraded ${name} v${currentVersion} -> v${newVersion}`);
  } else {
    ok(`LDM: deployed to ${ldmDest}`);
  }

  // OpenClaw copy (fix #8: respect plugin naming)
  const ocName = resolveOcPluginName(repoPath, name);
  if (!safeDeployDir(ldmDest, OC_EXTENSIONS, ocName)) {
    fail(`OpenClaw: deploy failed for ${ocName}`);
  } else {
    ok(`OpenClaw: deployed to ${join(OC_EXTENSIONS, ocName)}`);
    // Verify openclaw.json references match actual directory
    verifyOcConfig(ocName);
  }

  return true;
}

function verifyOcConfig(pluginDirName) {
  const ocConfigPath = join(OC_ROOT, 'openclaw.json');
  const ocConfig = readJSON(ocConfigPath);
  if (!ocConfig?.extensions) return;

  const pluginPath = join(OC_EXTENSIONS, pluginDirName);
  const pluginJson = readJSON(join(pluginPath, 'openclaw.plugin.json'));
  if (!pluginJson?.id) return;

  // Check if openclaw.json has an entry whose path references a different dir
  for (const ext of ocConfig.extensions) {
    if (ext.id === pluginJson.id) {
      const configDir = basename(ext.path || '');
      if (configDir && configDir !== pluginDirName) {
        log(`Warning: openclaw.json references "${configDir}" but plugin is at "${pluginDirName}"`);
        log(`  Update openclaw.json or rename the directory to match.`);
      }
      return;
    }
  }
}

function registerMCP(repoPath, door, toolName) {
  const rawName = toolName || door.name || basename(repoPath);
  const name = rawName.replace(/^@[\w-]+\//, '');
  const ldmServerPath = join(LDM_EXTENSIONS, name, door.file);
  const ldmFallbackPath = join(LDM_EXTENSIONS, basename(repoPath), door.file);
  const repoServerPath = join(repoPath, door.file);
  const mcpPath = existsSync(ldmServerPath) ? ldmServerPath
    : existsSync(ldmFallbackPath) ? ldmFallbackPath
    : repoServerPath;

  // Check ~/.claude.json (user-level MCP)
  const ccUserPath = join(HOME, '.claude.json');
  const ccUser = readJSON(ccUserPath);
  const alreadyRegistered = ccUser?.mcpServers?.[name]?.args?.includes(mcpPath);

  if (alreadyRegistered) {
    skip(`MCP: ${name} already registered at ${mcpPath}`);
    return true;
  }

  if (DRY_RUN) {
    ok(`MCP: would register ${name} at user scope (dry run)`);
    return true;
  }

  // Register with Claude Code CLI at user scope
  try {
    try {
      execSync(`claude mcp remove ${name} --scope user`, { stdio: 'pipe' });
    } catch {}
    const envFlag = existsSync(OC_ROOT) ? ` -e OPENCLAW_HOME="${OC_ROOT}"` : '';
    execSync(`claude mcp add --scope user ${name}${envFlag} -- node "${mcpPath}"`, { stdio: 'pipe' });
    ok(`MCP: registered ${name} at user scope`);
    return true;
  } catch (e) {
    // Fallback: write to ~/.claude.json directly
    try {
      const mcpConfig = readJSON(ccUserPath) || {};
      if (!mcpConfig.mcpServers) mcpConfig.mcpServers = {};
      mcpConfig.mcpServers[name] = {
        command: 'node',
        args: [mcpPath],
      };
      writeJSON(ccUserPath, mcpConfig);
      ok(`MCP: registered ${name} in ~/.claude.json (fallback)`);
      return true;
    } catch (e2) {
      fail(`MCP: registration failed. ${e.message}`);
      return false;
    }
  }
}

function installClaudeCodeHook(repoPath, door) {
  const settingsPath = join(HOME, '.claude', 'settings.json');
  let settings = readJSON(settingsPath);

  if (!settings) {
    skip(`Claude Code: no settings.json found`);
    return false;
  }

  const toolName = basename(repoPath);
  const installedGuard = join(LDM_EXTENSIONS, toolName, 'guard.mjs');
  const hookCommand = existsSync(installedGuard)
    ? `node ${installedGuard}`
    : (door.command || `node "${join(repoPath, 'guard.mjs')}"`);

  if (DRY_RUN) {
    ok(`Claude Code: would add ${door.event || 'PreToolUse'} hook (dry run)`);
    return true;
  }

  if (!settings.hooks) settings.hooks = {};
  const event = door.event || 'PreToolUse';
  if (!settings.hooks[event]) settings.hooks[event] = [];

  const existingIdx = settings.hooks[event].findIndex(entry =>
    entry.hooks?.some(h => {
      const cmd = h.command || '';
      return cmd.includes(`/${toolName}/`) || cmd === hookCommand;
    })
  );

  if (existingIdx !== -1) {
    const existingCmd = settings.hooks[event][existingIdx].hooks?.[0]?.command || '';
    if (existingCmd === hookCommand) {
      skip(`Claude Code: ${event} hook already configured`);
      return true;
    }
    settings.hooks[event][existingIdx].hooks[0].command = hookCommand;
    settings.hooks[event][existingIdx].hooks[0].timeout = door.timeout || 10;
    try {
      writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + '\n');
      ok(`Claude Code: ${event} hook updated`);
      return true;
    } catch (e) {
      fail(`Claude Code: failed to update settings.json. ${e.message}`);
      return false;
    }
  }

  settings.hooks[event].push({
    matcher: door.matcher || undefined,
    hooks: [{
      type: 'command',
      command: hookCommand,
      timeout: door.timeout || 10,
    }],
  });

  try {
    writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + '\n');
    ok(`Claude Code: ${event} hook added`);
    return true;
  } catch (e) {
    fail(`Claude Code: failed to update settings.json. ${e.message}`);
    return false;
  }
}

function installSkill(repoPath, toolName) {
  const skillSrc = join(repoPath, 'SKILL.md');
  const ocSkillDir = join(OC_ROOT, 'skills', toolName);
  const ocSkillDest = join(ocSkillDir, 'SKILL.md');

  if (existsSync(ocSkillDest)) {
    try {
      const srcContent = readFileSync(skillSrc, 'utf8');
      const destContent = readFileSync(ocSkillDest, 'utf8');
      if (srcContent === destContent) {
        skip(`Skill: ${toolName} already deployed`);
        return true;
      }
    } catch {}
  }

  if (DRY_RUN) {
    ok(`Skill: would deploy ${toolName}/SKILL.md (dry run)`);
    return true;
  }

  try {
    mkdirSync(ocSkillDir, { recursive: true });
    cpSync(skillSrc, ocSkillDest);
    ok(`Skill: deployed to ${ocSkillDir}`);
    return true;
  } catch (e) {
    fail(`Skill: deploy failed. ${e.message}`);
    return false;
  }
}

// ── Single tool install ──

export function installSingleTool(toolPath) {
  const { interfaces, pkg } = detectInterfaces(toolPath);
  const ifaceNames = Object.keys(interfaces);

  if (ifaceNames.length === 0) return 0;

  const toolName = pkg?.name?.replace(/^@\w+\//, '') || basename(toolPath);

  if (!JSON_OUTPUT) {
    console.log('');
    console.log(`  Installing: ${toolName}${DRY_RUN ? ' (dry run)' : ''}`);
    console.log(`  ${'─'.repeat(40)}`);
    log(`Detected ${ifaceNames.length} interface(s): ${ifaceNames.join(', ')}`);
    console.log('');
  }

  if (DRY_RUN && !JSON_OUTPUT) {
    console.log(describeInterfaces(interfaces));

    const existing = findExistingInstalls(toolName, pkg, interfaces.openclaw?.config);
    if (existing.length > 0) {
      console.log('');
      for (const m of existing) {
        log(`Migration: would rename "${m.dirName}" -> "${toolName}" (matched by ${m.matchType})`);
      }
    }

    return ifaceNames.length;
  }

  let installed = 0;
  const registryInfo = {
    name: toolName,
    version: pkg?.version || 'unknown',
    source: toolPath,
    interfaces: ifaceNames,
  };

  if (interfaces.cli) {
    if (installCLI(toolPath, interfaces.cli)) installed++;
  }

  if (interfaces.openclaw) {
    if (deployExtension(toolPath, toolName)) {
      installed++;
      registryInfo.ldmPath = join(LDM_EXTENSIONS, toolName);
      registryInfo.ocPath = join(OC_EXTENSIONS, toolName);
    }
  } else if (interfaces.mcp) {
    const extName = basename(toolPath);
    if (deployExtension(toolPath, extName)) {
      registryInfo.ldmPath = join(LDM_EXTENSIONS, extName);
      registryInfo.ocPath = join(OC_EXTENSIONS, extName);
    }
  }

  if (interfaces.mcp) {
    if (registerMCP(toolPath, interfaces.mcp, toolName)) installed++;
  }

  if (interfaces.claudeCodeHook) {
    if (installClaudeCodeHook(toolPath, interfaces.claudeCodeHook)) installed++;
  }

  if (interfaces.skill) {
    if (installSkill(toolPath, toolName)) installed++;
  }

  if (interfaces.module) {
    ok(`Module: import from "${interfaces.module.main}"`);
    installed++;
  }

  // Update registry
  if (!DRY_RUN) {
    try {
      mkdirSync(LDM_EXTENSIONS, { recursive: true });
      updateRegistry(toolName, registryInfo);
      ok(`Registry: updated`);
    } catch (e) {
      fail(`Registry: update failed. ${e.message}`);
    }
  }

  return installed;
}

// ── Toolbox install ──

export function installToolbox(repoPath) {
  const subTools = detectToolbox(repoPath);
  if (subTools.length === 0) return { tools: 0, interfaces: 0 };

  const toolboxPkg = readJSON(join(repoPath, 'package.json'));
  const toolboxName = toolboxPkg?.name?.replace(/^@\w+\//, '') || basename(repoPath);

  if (!JSON_OUTPUT) {
    console.log('');
    console.log(`  Toolbox: ${toolboxName}`);
    console.log(`  ${'='.repeat(50)}`);
    log(`Found ${subTools.length} sub-tool(s): ${subTools.map(t => t.name).join(', ')}`);
  }

  let totalInstalled = 0;
  let toolsProcessed = 0;

  for (const subTool of subTools) {
    const count = installSingleTool(subTool.path);
    totalInstalled += count;
    if (count > 0) toolsProcessed++;
  }

  if (!JSON_OUTPUT) {
    console.log('');
    console.log(`  ${'='.repeat(50)}`);
    if (DRY_RUN) {
      console.log(`  Dry run complete. ${toolsProcessed} tool(s) scanned, ${totalInstalled} interface(s) detected.`);
    } else {
      console.log(`  Done. ${toolsProcessed} tool(s), ${totalInstalled} interface(s) processed.`);
    }
    console.log('');
  }

  return { tools: toolsProcessed, interfaces: totalInstalled };
}

// ── Full install pipeline ──

export async function installFromPath(repoPath) {
  const subTools = detectToolbox(repoPath);

  if (subTools.length > 0) {
    return installToolbox(repoPath);
  }

  const installed = installSingleTool(repoPath);

  if (installed === 0) {
    skip('No installable interfaces detected.');
  } else if (!JSON_OUTPUT) {
    console.log('');
    if (DRY_RUN) {
      console.log('  Dry run complete. No changes made.');
    } else {
      console.log(`  Done. ${installed} interface(s) processed.`);
    }
    console.log('');
  }

  return { tools: 1, interfaces: installed };
}

// ── Exports for ldm CLI ──

export { loadRegistry, saveRegistry, updateRegistry, readJSON, writeJSON, runBuildIfNeeded };
