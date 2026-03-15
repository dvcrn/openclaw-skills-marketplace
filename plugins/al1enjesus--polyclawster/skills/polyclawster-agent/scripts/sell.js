#!/usr/bin/env node
/**
 * PolyClawster Sell — close an open position
 *
 * Demo:  marks bet as closed on polyclawster.com, simulates return
 * Live:  signs SELL order locally → submits via relay → Polymarket CLOB
 *
 * Usage:
 *   node sell.js --list               # Show open positions
 *   node sell.js --bet-id 42          # Close position by bet ID
 *   node sell.js --bet-id 42 --demo   # Close demo position
 */
'use strict';
const https = require('https');
const { loadConfig } = require('./setup');

const API_BASE = 'https://polyclawster.com';

function apiCall(method, path, body, apiKey) {
  return new Promise((resolve, reject) => {
    const u       = new URL(`${API_BASE}${path}`);
    const payload = body ? JSON.stringify(body) : null;
    const req     = https.request({
      hostname: u.hostname,
      path:     u.pathname + (u.search || ''),
      method,
      headers: {
        'Content-Type':   'application/json',
        'User-Agent':     'polyclawster-skill/2.0',
        ...(payload ? { 'Content-Length': Buffer.byteLength(payload) } : {}),
        ...(apiKey  ? { 'X-Api-Key': apiKey } : {}),
      },
      timeout: 20000,
    }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => { try { resolve(JSON.parse(d)); } catch { reject(new Error('Bad JSON')); } });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    if (payload) req.write(payload);
    req.end();
  });
}

// ── List open positions ───────────────────────────────────────────────────────
async function listPositions(isDemo) {
  const config = loadConfig();
  if (!config?.agentId) throw new Error('Not configured. Run: node scripts/setup.js --auto');

  const portfolio = await apiCall('GET', '/api/agents?action=portfolio', null, config.apiKey);
  if (!portfolio?.ok) throw new Error(portfolio?.error || 'Failed to load portfolio');

  const bets = (portfolio.openBets || []).filter(b => !!b.is_demo === !!isDemo);

  if (!bets.length) {
    console.log(`No open ${isDemo ? 'demo' : 'live'} positions.`);
    return [];
  }

  console.log(`📊 Open ${isDemo ? 'demo ' : ''}positions:`);
  bets.forEach(b => {
    console.log(`  [${b.id}] ${b.side} $${parseFloat(b.amount).toFixed(2)} @ ${parseFloat(b.price).toFixed(2)} — ${(b.market || '?').slice(0, 60)}`);
  });

  return bets;
}

// ── Close a position ──────────────────────────────────────────────────────────
async function closePosition({ betId, isDemo }) {
  const config = loadConfig();
  if (!config?.agentId) throw new Error('Not configured. Run: node scripts/setup.js --auto');

  console.log(`🔄 Closing ${isDemo ? 'demo ' : ''}position #${betId}...`);

  // ── Demo close: call close_bet on agents API ────────────────────────────
  if (isDemo) {
    const r = await apiCall('POST', '/api/agents', {
      action: 'close_bet',
      betId:  parseInt(betId),
      isDemo: true,
    }, config.apiKey);
    if (!r?.ok) throw new Error(r?.error || 'Failed to close demo position');
    console.log(`✅ Demo position closed! Return: $${parseFloat(r.returnAmount || 0).toFixed(2)} (PnL: ${r.pnl >= 0 ? '+' : ''}$${parseFloat(r.pnl || 0).toFixed(2)})`);
    return r;
  }

  // ── Live close: sign SELL order locally → submit via relay ──────────────
  if (!config.privateKey) throw new Error('No private key. Run: node scripts/setup.js --auto');
  if (!config.clobApiKey || !config.clobApiSecret) throw new Error('No CLOB creds. Run: node scripts/setup.js --derive-clob');

  // Get bet details from polyclawster.com
  const portfolio = await apiCall('GET', '/api/agents?action=portfolio', null, config.apiKey);
  if (!portfolio?.ok) throw new Error(portfolio?.error || 'Failed to load portfolio');

  const bet = (portfolio.openBets || []).find(b => b.id === parseInt(betId));
  if (!bet) throw new Error(`Bet #${betId} not found or already closed`);

  // market_id stores the tokenId (the CLOB token we hold)
  const tokenId = bet.market_id;
  if (!tokenId || tokenId.length < 10) {
    throw new Error('No tokenId stored for this bet — cannot sell. You may need to sell manually on Polymarket.');
  }

  const { ethers } = await import('ethers');
  const { ClobClient, SignatureType, OrderType, Side } = await import('@polymarket/clob-client');

  const wallet = new ethers.Wallet(config.privateKey);
  const creds  = {
    key:        config.clobApiKey,
    secret:     config.clobApiSecret,
    passphrase: config.clobApiPassphrase,
  };
  const client = new ClobClient(config.clobRelayUrl, 137, wallet, creds, SignatureType.EOA);

  // To close a position: SELL the outcome tokens we hold
  // We hold YES or NO tokens depending on original bet side
  // SELL amount = number of shares (bet_amount / buy_price)
  const buyAmount = parseFloat(bet.amount || 0);
  const buyPrice  = parseFloat(bet.price || 0.5);
  const shares    = buyAmount / buyPrice;

  console.log(`   Selling ${bet.side} tokens (${shares.toFixed(4)} shares)...`);
  console.log(`   Token: ${tokenId.slice(0, 20)}...`);
  console.log('   Signing sell order locally...');

  const order = await client.createMarketOrder({
    tokenID: tokenId,
    side:    Side.SELL,      // SELL to close position
    amount:  shares,         // number of outcome tokens to sell
  });

  console.log('   Submitting via relay...');
  const response = await client.postOrder(order, OrderType.FOK);
  const orderID  = response?.orderID || response?.orderId || '';

  if (!orderID && (response?.error || response?.errorMsg)) {
    throw new Error('CLOB rejected sell: ' + (response.error || response.errorMsg || JSON.stringify(response)));
  }

  // Mark bet as closed on polyclawster.com
  await apiCall('POST', '/api/agents', {
    action:  'close_bet',
    betId:   parseInt(betId),
    orderID,
  }, config.apiKey).catch(e => {
    console.warn('   ⚠️ Failed to update bet status on polyclawster.com:', e.message);
  });

  console.log('');
  console.log('✅ Position closed!');
  console.log(`   Order ID: ${orderID}`);
  console.log(`   Status:   ${response?.status || 'submitted'}`);
  return { ok: true, orderID, status: response?.status };
}

module.exports = { closePosition, listPositions };

// ── CLI ───────────────────────────────────────────────────────────────────────
if (require.main === module) {
  const args   = process.argv.slice(2);
  const getArg = f => { const i = args.indexOf(f); return i >= 0 ? args[i + 1] : null; };
  const isDemo = args.includes('--demo');

  if (args.includes('--list')) {
    listPositions(isDemo).catch(e => { console.error('❌', e.message); process.exit(1); });
  } else {
    const betId = getArg('--bet-id') || getArg('--id');
    if (!betId) {
      console.log('Usage:');
      console.log('  node sell.js --list               # Show open positions');
      console.log('  node sell.js --list --demo        # Show open demo positions');
      console.log('  node sell.js --bet-id 42          # Close live position');
      console.log('  node sell.js --bet-id 42 --demo   # Close demo position');
      process.exit(0);
    }
    closePosition({ betId: parseInt(betId), isDemo })
      .catch(e => { console.error('❌ Error:', e.message); process.exit(1); });
  }
}
