#!/usr/bin/env node
/**
 * PolyClawster Setup — Option C (Non-Custodial)
 *
 * Generates a Polygon wallet locally, derives Polymarket CLOB credentials,
 * and registers the wallet address on polyclawster.com.
 *
 * Private key stays on THIS machine only. polyclawster.com never sees it.
 *
 * Usage:
 *   node setup.js --auto                    # Create agent wallet
 *   node setup.js --auto --name "My Agent"  # With custom name
 *   node setup.js --derive-clob             # Re-derive CLOB creds (if missing)
 *   node setup.js --info                    # Show current config
 */
'use strict';
const fs   = require('fs');
const path = require('path');
const https = require('https');

const CONFIG_DIR  = path.join(process.env.HOME || '/root', '.polyclawster');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');
const API_BASE    = 'https://polyclawster.com';
const RELAY_URL   = 'https://polyclawster.com/api/clob-relay';

// ── Config helpers ────────────────────────────────────────────────────────────
function loadConfig() {
  try { return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8')); }
  catch { return null; }
}

function saveConfig(cfg) {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(cfg, null, 2));
  try { fs.chmodSync(CONFIG_FILE, 0o600); } catch {} // restrict read permissions
}

// ── HTTP helpers ──────────────────────────────────────────────────────────────
function postJSON(url, body) {
  return new Promise((resolve, reject) => {
    const u       = new URL(url);
    const payload = JSON.stringify(body);
    const req     = https.request({
      hostname: u.hostname,
      path:     u.pathname + (u.search || ''),
      method:   'POST',
      headers:  {
        'Content-Type':   'application/json',
        'Content-Length': Buffer.byteLength(payload),
        'User-Agent':     'polyclawster-skill/2.0',
      },
      timeout: 20000,
    }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => { try { resolve(JSON.parse(d)); } catch { reject(new Error('Bad JSON: ' + d.slice(0, 80))); } });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Request timeout')); });
    req.write(payload);
    req.end();
  });
}

// ── Derive Polymarket CLOB credentials via relay (geo-bypass) ─────────────────
// createApiKey uses L1 auth (wallet signs a timestamp message) — private key stays local
async function deriveClobCreds(wallet) {
  const { ClobClient } = await import('@polymarket/clob-client');
  // ClobClient with no creds → L1-only (createApiKey uses L1)
  const client = new ClobClient(RELAY_URL, 137, wallet);
  const creds  = await client.createApiKey(0); // nonce=0
  return {
    clobApiKey:        creds.key,
    clobApiSecret:     creds.secret,
    clobApiPassphrase: creds.passphrase,
  };
}

// ── Auto-generate agent name ──────────────────────────────────────────────────
const NAME_POOL = [
  'CryptoBro','MoonHunter','GigaChad','DiamondPaws','ApeBrain',
  'SatoshiJr','PumpDetector','WhaleWatcher','Degen','BullRider',
  'VibeTrader','NightOwl','AlphaSeeker','TokenShark','DeFiGhost',
];

function randomAgentName() {
  const base   = NAME_POOL[Math.floor(Math.random() * NAME_POOL.length)];
  const digits = String(Math.floor(1000 + Math.random() * 9000));
  return base + '#' + digits;
}

// ── Readline prompt helper ────────────────────────────────────────────────────
function prompt(question) {
  const readline = require('readline');
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(resolve => rl.question(question, ans => { rl.close(); resolve(ans.trim()); }));
}

// ── Main: auto setup ──────────────────────────────────────────────────────────
async function autoSetup(opts = {}) {
  const existing = loadConfig();
  if (existing?.agentId && existing?.walletAddress && existing?.privateKey) {
    console.log('✅ Already configured!');
    console.log(`   Wallet:    ${existing.walletAddress}`);
    console.log(`   Agent ID:  ${existing.agentId}`);
    console.log(`   Dashboard: ${existing.dashboard}`);
    console.log('');
    console.log('To reconfigure, delete ~/.polyclawster/config.json');
    return existing;
  }

  // Welcome banner
  console.log('');
  console.log('👋 Привет! Сейчас создам тебе Polygon-кошелёк и подключу к Polymarket.');
  console.log('   🔐 Приватный ключ останется только у тебя — на сервер не отправляется.');
  console.log('   🎮 $10 demo-баланс — сразу можешь тренироваться без реальных денег.');
  console.log('   💰 Для реальных ставок — пополни кошелёк USDC (Polygon).');
  console.log('   🏆 Попадёшь в общий лидерборд на polyclawster.com');
  console.log('');

  // Ask for agent name (unless --name passed)
  let agentName = opts.name || null;
  if (!agentName) {
    const auto = randomAgentName();
    const ans = await prompt(`Придумать имя агенту? (Enter — придумаю сам, будет: ${auto}): `);
    agentName = ans || auto;
  }
  console.log(`   Имя: ${agentName}`);
  console.log('');

  // 1. Generate wallet locally
  console.log('🔐 Generating Polygon wallet locally...');
  const ethersModule = await import('ethers');
  const ethers = ethersModule.default || ethersModule;
  const wallet = ethers.Wallet.createRandom();
  console.log(`   Address:    ${wallet.address}`);
  console.log(`   PrivKey:    ${wallet.privateKey.slice(0, 10)}... (stored locally only)`);

  // 2. Sign ownership proof
  const ownershipSig = await wallet.signMessage('polyclawster-register');

  // 3. Register wallet address on polyclawster.com
  console.log('');
  console.log('📡 Registering on PolyClawster (wallet address only — no private key sent)...');
  const result = await postJSON(`${API_BASE}/api/agents`, {
    action:       'register',
    name:         agentName || opts.name || randomAgentName(),
    emoji:        opts.emoji    || '🤖',
    strategy:     opts.strategy || '',
    walletAddress: wallet.address,
    ownershipSig,
    claimCode:    opts.claimCode,
  });

  if (!result.ok) {
    throw new Error('Registration failed: ' + (result.error || JSON.stringify(result)));
  }

  // 4. Derive CLOB API credentials via relay
  console.log('');
  console.log('🔑 Deriving Polymarket CLOB credentials (via relay for geo-bypass)...');
  let clobCreds = { clobApiKey: null, clobApiSecret: null, clobApiPassphrase: null };
  try {
    clobCreds = await deriveClobCreds(wallet);
    console.log('   CLOB key:        ' + clobCreds.clobApiKey?.slice(0, 12) + '...');
    console.log('   CLOB secret:     derived ✅');
    console.log('   CLOB passphrase: derived ✅');
  } catch (e) {
    console.warn('   ⚠️  CLOB derivation failed — demo mode works, live trading needs fix.');
    console.warn('   Error:', e.message);
    console.warn('   Retry later: node scripts/setup.js --derive-clob');
  }

  // 5. Save config locally (private key + CLOB creds — never sent anywhere)
  const config = {
    // Identity
    walletAddress: wallet.address,
    privateKey:    wallet.privateKey,   // ← stays on THIS machine ONLY

    // polyclawster.com tracking
    agentId:  result.agentId,
    apiKey:   result.apiKey,            // for signals/portfolio/demo calls
    dashboard: result.dashboard,

    // Polymarket CLOB access (derived from private key, used for request signing)
    clobRelayUrl:      RELAY_URL,       // geo-bypass proxy
    clobApiKey:        clobCreds.clobApiKey,
    clobApiSecret:     clobCreds.clobApiSecret,
    clobApiPassphrase: clobCreds.clobApiPassphrase,

    createdAt: new Date().toISOString(),
  };

  saveConfig(config);

  console.log('');
  console.log('✅ Agent ready!');
  console.log(`   Wallet:    ${wallet.address}`);
  console.log(`   Agent ID:  ${result.agentId}`);
  console.log(`   Dashboard: ${result.dashboard}`);
  console.log(`   Config:    ${CONFIG_FILE} (permissions: 600)`);
  console.log('');
  console.log('💰 To fund for live trading, send POL (Polygon) to:');
  console.log(`   ${wallet.address}`);
  console.log('   Agent auto-swaps POL → USDC.e and approves contracts on first trade.');
  console.log('');
  console.log('📊 Check balances:  node scripts/balance.js');
  console.log('');
  console.log('🎮 $10 demo balance ready:');
  console.log('   node scripts/browse.js "crypto"');
  console.log('   node scripts/trade.js --market "bitcoin-100k" --side YES --amount 2 --demo');

  return config;
}

// ── Re-derive CLOB creds ──────────────────────────────────────────────────────
async function deriveClobOnly() {
  const config = loadConfig();
  if (!config?.privateKey) {
    throw new Error('No config found. Run: node scripts/setup.js --auto');
  }

  console.log('🔑 Re-deriving Polymarket CLOB credentials...');
  const ethersModule = await import('ethers');
  const ethers = ethersModule.default || ethersModule;
  const wallet = new ethers.Wallet(config.privateKey);
  const creds  = await deriveClobCreds(wallet);

  saveConfig({ ...config, ...creds });
  console.log('✅ CLOB credentials updated:');
  console.log('   Key:        ' + creds.clobApiKey?.slice(0, 12) + '...');
  console.log('   Secret:     derived ✅');
  console.log('   Passphrase: derived ✅');
}

// ── Rename agent (EIP-191 proof-of-ownership) ─────────────────────────────────
async function renameAgent(newName) {
  const config = loadConfig();
  if (!config?.privateKey || !config?.apiKey) {
    throw new Error('Not configured. Run: node scripts/setup.js --auto');
  }

  const ethersModule = await import('ethers');
  const ethers = ethersModule.default || ethersModule;
  const wallet = new ethers.Wallet(config.privateKey);

  const timestamp = String(Date.now());
  const message   = `rename:${newName}:${timestamp}`;
  const sig       = await wallet.signMessage(message);

  console.log(`✍️  Signing rename proof (wallet: ${wallet.address.slice(0, 10)}...)...`);

  const result = await postJSON(`${API_BASE}/api/agents`, {
    action: 'rename',
    newName,
    sig,
    timestamp,
    apiKey: config.apiKey,
  });

  if (!result.ok) throw new Error(result.error || 'Rename failed');

  saveConfig({ ...config, agentName: result.name });

  console.log(`✅ Agent renamed to "${result.name}"`);
  return result;
}

// ── Show info ─────────────────────────────────────────────────────────────────
function showInfo() {
  const config = loadConfig();
  if (!config) { console.log('No config. Run: node scripts/setup.js --auto'); return; }
  console.log('📋 PolyClawster Agent Config:');
  console.log(`   Wallet:       ${config.walletAddress}`);
  console.log(`   Agent ID:     ${config.agentId}`);
  console.log(`   Dashboard:    ${config.dashboard}`);
  console.log(`   CLOB relay:   ${config.clobRelayUrl || '(not set)'}`);
  console.log(`   CLOB key:     ${config.clobApiKey ? config.clobApiKey.slice(0, 12) + '...' : '(not derived)'}`);
  console.log(`   Private key:  ${config.privateKey ? config.privateKey.slice(0, 10) + '... (local)' : '(missing!)'}`);
  console.log(`   Created:      ${config.createdAt || 'unknown'}`);
}

module.exports = { autoSetup, loadConfig, saveConfig, CONFIG_FILE, API_BASE, RELAY_URL, randomAgentName };

// ── CLI ───────────────────────────────────────────────────────────────────────
if (require.main === module) {
  const args = process.argv.slice(2);

  const getArg = f => { const i = args.indexOf(f); return i >= 0 ? args[i + 1] : null; };

  if (args.includes('--info')) {
    showInfo();
  } else if (args.includes('--derive-clob')) {
    deriveClobOnly().catch(e => { console.error('❌ Error:', e.message); process.exit(1); });
  } else if (args.includes('--rename')) {
    const newName = getArg('--rename');
    if (!newName) { console.error('Usage: node setup.js --rename "New Name"'); process.exit(1); }
    renameAgent(newName).catch(e => { console.error('❌ Error:', e.message); process.exit(1); });
  } else if (args.includes('--auto') || args.length === 0) {
    autoSetup({
      name:      getArg('--name'),
      claimCode: getArg('--claim') || getArg('--ref'),
    }).catch(e => { console.error('❌ Error:', e.message); process.exit(1); });
  } else {
    console.log('Usage:');
    console.log('  node setup.js --auto                   # Create agent (interactive)');
    console.log('  node setup.js --auto --name "X"        # Skip name prompt');
    console.log('  node setup.js --rename "New Name"      # Rename agent (proof-of-ownership)');
    console.log('  node setup.js --info                   # Show config');
    console.log('  node setup.js --derive-clob            # Re-derive CLOB creds');
  }
}
