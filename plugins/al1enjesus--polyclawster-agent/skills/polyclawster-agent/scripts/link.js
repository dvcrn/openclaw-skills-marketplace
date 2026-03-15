#!/usr/bin/env node
/**
 * PolyClawster Link — connect agent to a TMA account
 *
 * Usage:
 *   node link.js PC-A3F7K9
 */
'use strict';
const https = require('https');
const { loadConfig } = require('./setup');

const API_BASE = 'https://polyclawster.com';

function postJSON(url, body, apiKey) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const payload = JSON.stringify(body);
    const req = https.request({
      hostname: u.hostname,
      path: u.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload),
        'User-Agent': 'polyclawster-skill/1.2',
        ...(apiKey ? { 'X-Api-Key': apiKey } : {}),
      },
      timeout: 10000,
    }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => { try { resolve(JSON.parse(d)); } catch { reject(new Error('Invalid JSON')); } });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    req.write(payload);
    req.end();
  });
}

async function linkAgent(claimCode) {
  const config = loadConfig();
  if (!config?.apiKey) {
    throw new Error('Not configured. Run: node scripts/setup.js --auto');
  }

  console.log(`🔗 Linking agent with code ${claimCode}...`);

  const result = await postJSON(`${API_BASE}/api/agents`, {
    action: 'link',
    claimCode,
  }, config.apiKey);

  if (!result.ok) {
    throw new Error(result.error || 'Link failed');
  }

  console.log('✅', result.message);
  console.log('   Your agent is now visible in the PolyClawster TMA under "Мои агенты".');
}

module.exports = { linkAgent };

if (require.main === module) {
  const claimCode = process.argv[2];
  if (!claimCode) {
    console.log('Usage: node link.js PC-XXXXXX');
    console.log('');
    console.log('Get your claim code in the PolyClawster app → Agents → "+ Подключить"');
    process.exit(0);
  }

  linkAgent(claimCode).catch(e => {
    console.error('❌ Error:', e.message);
    process.exit(1);
  });
}
