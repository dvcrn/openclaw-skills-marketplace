#!/usr/bin/env node

/**
 * ClawCap Uninstall Script
 * Restores the original OpenClaw config from backup.
 */

const fs = require('fs');
const path = require('path');

function getConfigPath() {
  const home = process.env.HOME || process.env.USERPROFILE;
  if (!home) {
    console.error('Error: Could not determine home directory.');
    process.exit(1);
  }
  return path.join(home, '.openclaw', 'openclaw.json');
}

function main() {
  console.log('');
  console.log('ClawCap Uninstall');
  console.log('=================');
  console.log('');

  const configPath = getConfigPath();
  const backupPath = configPath + '.backup';

  if (fs.existsSync(backupPath)) {
    fs.copyFileSync(backupPath, configPath);
    fs.unlinkSync(backupPath);
    console.log('Restored original config from backup.');
    console.log('ClawCap proxy routing has been removed.');
  } else {
    console.log('No backup found. Removing ClawCap URLs from config...');

    if (!fs.existsSync(configPath)) {
      console.log('No OpenClaw config found. Nothing to do.');
      process.exit(0);
    }

    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    let restored = 0;

    function restoreProviders(providers) {
      if (Array.isArray(providers)) {
        for (const p of providers) {
          if (p._originalBaseUrl) {
            p.baseUrl = p._originalBaseUrl;
            delete p._originalBaseUrl;
            restored++;
          }
        }
      } else if (typeof providers === 'object') {
        for (const [, p] of Object.entries(providers)) {
          if (p && p._originalBaseUrl) {
            p.baseUrl = p._originalBaseUrl;
            delete p._originalBaseUrl;
            restored++;
          }
        }
      }
    }

    if (config.models && config.models.providers) restoreProviders(config.models.providers);
    if (config.providers) restoreProviders(config.providers);

    fs.writeFileSync(configPath, JSON.stringify(config, null, 2) + '\n', 'utf8');
    console.log(`Restored ${restored} provider(s) to original URLs.`);
  }

  console.log('');
}

main();
