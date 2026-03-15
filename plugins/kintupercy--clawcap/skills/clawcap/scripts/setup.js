#!/usr/bin/env node

/**
 * ClawCap Setup Script
 * Automatically patches ~/.openclaw/openclaw.json to route all providers through ClawCap.
 * Backs up the original config before making changes.
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const CLAWCAP_BASE = 'https://clawcap.co/proxy';

function getConfigPath() {
  const home = process.env.HOME || process.env.USERPROFILE;
  if (!home) {
    console.error('Error: Could not determine home directory.');
    process.exit(1);
  }
  return path.join(home, '.openclaw', 'openclaw.json');
}

function readConfig(configPath) {
  if (!fs.existsSync(configPath)) {
    console.error(`Error: OpenClaw config not found at ${configPath}`);
    console.error('Make sure OpenClaw is installed and has been run at least once.');
    process.exit(1);
  }
  try {
    const raw = fs.readFileSync(configPath, 'utf8');
    return JSON.parse(raw);
  } catch (err) {
    console.error(`Error: Could not parse ${configPath} — ${err.message}`);
    process.exit(1);
  }
}

function backupConfig(configPath) {
  const backupPath = configPath + '.backup';
  if (!fs.existsSync(backupPath)) {
    fs.copyFileSync(configPath, backupPath);
    console.log(`Backed up config to ${backupPath}`);
  } else {
    console.log('Backup already exists, skipping backup.');
  }
}

function getToken() {
  const token = process.env.CLAWCAP_TOKEN;
  if (token && token.startsWith('cc_live_')) {
    return token;
  }
  return null;
}

function askForToken() {
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    rl.question('Enter your ClawCap token (cc_live_...): ', (answer) => {
      rl.close();
      const token = answer.trim();
      if (!token.startsWith('cc_live_')) {
        console.error('Error: Token must start with cc_live_. Get yours at https://clawcap.co/setup');
        process.exit(1);
      }
      resolve(token);
    });
  });
}

function patchProviders(config, proxyUrl) {
  let patched = 0;

  // Handle providers as object (keyed by name)
  if (config.models && config.models.providers && typeof config.models.providers === 'object') {
    const providers = config.models.providers;

    if (Array.isArray(providers)) {
      // Array format: [{ name, baseUrl, ... }]
      for (const provider of providers) {
        if (provider.baseUrl && !provider.baseUrl.includes('clawcap.co')) {
          provider._originalBaseUrl = provider.baseUrl;
          provider.baseUrl = proxyUrl;
          patched++;
          console.log(`  Patched provider: ${provider.name || 'unnamed'}`);
        }
      }
    } else {
      // Object format: { "anthropic": { baseUrl, ... } }
      for (const [name, provider] of Object.entries(providers)) {
        if (provider && typeof provider === 'object' && provider.baseUrl && !provider.baseUrl.includes('clawcap.co')) {
          provider._originalBaseUrl = provider.baseUrl;
          provider.baseUrl = proxyUrl;
          patched++;
          console.log(`  Patched provider: ${name}`);
        }
      }
    }
  }

  // Also handle flat "providers" at root level (some config formats)
  if (config.providers && Array.isArray(config.providers)) {
    for (const provider of config.providers) {
      if (provider.baseUrl && !provider.baseUrl.includes('clawcap.co')) {
        provider._originalBaseUrl = provider.baseUrl;
        provider.baseUrl = proxyUrl;
        patched++;
        console.log(`  Patched provider: ${provider.name || 'unnamed'}`);
      }
    }
  }

  return patched;
}

async function main() {
  console.log('');
  console.log('ClawCap Setup');
  console.log('=============');
  console.log('');

  // 1. Get token
  let token = getToken();
  if (!token) {
    console.log('No CLAWCAP_TOKEN environment variable found.');
    token = await askForToken();
  } else {
    console.log(`Using token from CLAWCAP_TOKEN environment variable.`);
  }

  const proxyUrl = `${CLAWCAP_BASE}/${token}`;

  // 2. Read config
  const configPath = getConfigPath();
  console.log(`Reading config from ${configPath}`);
  const config = readConfig(configPath);

  // 3. Backup
  backupConfig(configPath);

  // 4. Patch providers
  console.log('');
  console.log('Patching providers...');
  const patched = patchProviders(config, proxyUrl);

  if (patched === 0) {
    console.log('');
    console.log('No providers found to patch. Either:');
    console.log('  - Your config has no providers with baseUrl set');
    console.log('  - Providers are already routed through ClawCap');
    console.log('');
    console.log('You can manually set baseUrl to:');
    console.log(`  ${proxyUrl}`);
    console.log('');
    process.exit(0);
  }

  // 5. Write config
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2) + '\n', 'utf8');

  console.log('');
  console.log(`Done! ${patched} provider(s) now route through ClawCap.`);
  console.log('');
  console.log('Your proxy URL:');
  console.log(`  ${proxyUrl}`);
  console.log('');
  console.log('Check your spend anytime:');
  console.log(`  curl ${proxyUrl}/status`);
  console.log('');
  console.log('To undo, restore from backup:');
  console.log(`  cp ${configPath}.backup ${configPath}`);
  console.log('');
}

main().catch((err) => {
  console.error('Setup failed:', err.message);
  process.exit(1);
});
