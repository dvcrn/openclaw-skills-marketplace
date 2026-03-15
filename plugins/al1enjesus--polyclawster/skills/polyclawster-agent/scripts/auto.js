#!/usr/bin/env node
/**
 * PolyClawster Auto-trade — autonomous trading loop
 * Designed to run via OpenClaw cron every 30-60 minutes.
 *
 * Usage:
 *   node auto.js                                    # Default: min-score 7, max-bet 5
 *   node auto.js --min-score 8 --max-bet 10         # Stricter filter, bigger bets
 *   node auto.js --topic "crypto"                   # Focus on specific topic
 *   node auto.js --daily-limit 50                   # Max daily spend
 *   node auto.js --demo                             # Demo mode only
 *   node auto.js --dry-run                          # Simulate, no trades
 */
'use strict';
const https = require('https');
const { loadConfig } = require('./setup');
const { getWalletBalance } = require('./balance');

const API_BASE = 'https://polyclawster.com';

function getJSON(url, apiKey) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const req = https.request({
      hostname: u.hostname,
      path: u.pathname + (u.search || ''),
      method: 'GET',
      headers: {
        'User-Agent': 'polyclawster-skill/1.2',
        ...(apiKey ? { 'X-Api-Key': apiKey } : {}),
      },
      timeout: 12000,
    }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => { try { resolve(JSON.parse(d)); } catch { reject(new Error('Invalid JSON')); } });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    req.end();
  });
}

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
      timeout: 20000,
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

async function runAutoTrade(opts = {}) {
  const {
    minScore   = 7,
    maxBet     = 5,
    dailyLimit = 100,
    topic      = '',
    isDemo     = false,
    dryRun     = false,
  } = opts;

  const config = loadConfig();
  if (!config?.apiKey) {
    throw new Error('Not configured. Run: node scripts/setup.js --auto');
  }

  console.log(`🤖 PolyClawster Auto-trade — ${dryRun ? 'DRY RUN' : isDemo ? 'DEMO' : 'LIVE'}`);
  console.log(`   Min score: ${minScore} | Max bet: $${maxBet} | Topic: "${topic || 'all'}"`);
  console.log('');

  // 1. Get portfolio
  const portfolio = await getWalletBalance().catch(() => null);
  const balance = isDemo
    ? parseFloat(portfolio?.demoBal || 0)
    : parseFloat(portfolio?.cashBalance || 0);

  console.log(`💰 Available: $${balance.toFixed(2)} (${isDemo ? 'demo' : 'live'})`);

  if (balance < 0.5) {
    console.log('⚠️  Insufficient balance. Deposit USDC to start trading.');
    return { traded: 0, skipped: 0 };
  }

  // 2. Fetch signals
  const signalsUrl = `${API_BASE}/api/signals${topic ? '?q=' + encodeURIComponent(topic) : ''}`;
  const signalsRes = await getJSON(signalsUrl, config.apiKey).catch(() => null);
  const signals = (signalsRes?.signals || signalsRes?.data || []).filter(Boolean);

  if (!signals.length) {
    console.log('📭 No signals available right now.');
    return { traded: 0, skipped: 0 };
  }

  // 3. Filter signals
  const goodSignals = signals.filter(s => {
    const score = parseFloat(s.score || s.signal_score || 0);
    return score >= minScore;
  });

  console.log(`📡 Signals: ${signals.length} total, ${goodSignals.length} above score ${minScore}`);
  console.log('');

  // 4. Get open bets to avoid duplicates
  const openBets = portfolio?.openBets || [];
  const openMarkets = new Set(openBets.map(b => b.market_id || b.market).filter(Boolean));

  let traded = 0, skipped = 0, totalSpent = 0;

  for (const signal of goodSignals) {
    if (totalSpent >= dailyLimit) {
      console.log(`⚠️  Daily limit $${dailyLimit} reached. Stopping.`);
      break;
    }
    if (balance - totalSpent < 0.5) {
      console.log('⚠️  Balance exhausted.');
      break;
    }

    const slug        = signal.slug || signal.market_slug || '';
    const market      = signal.question || signal.market || slug;
    const side        = (signal.side || signal.recommended_side || 'YES').toUpperCase();
    const score       = parseFloat(signal.score || signal.signal_score || 0);
    const betAmt      = Math.min(maxBet, balance - totalSpent);
    const conditionId = signal.conditionId || signal.marketId || null;
    const tokenIdYes  = signal.tokenIdYes || null;
    const tokenIdNo   = signal.tokenIdNo  || null;

    // Skip if already have open bet on this market
    if (openMarkets.has(slug) || openMarkets.has(market)) {
      console.log(`⏭️  Skip (already open): ${market.slice(0, 60)}`);
      skipped++;
      continue;
    }

    console.log(`📊 Signal: ${market.slice(0, 60)}`);
    console.log(`   Score: ${score} | Side: ${side} | Bet: $${betAmt.toFixed(2)}`);

    if (dryRun) {
      console.log(`   [DRY RUN] Would place ${side} $${betAmt.toFixed(2)}`);
      traded++;
      continue;
    }

    try {
      const { executeTrade } = require('./trade');
      const result = await executeTrade({
        market: slug || market,
        conditionId,
        tokenIdYes,
        tokenIdNo,
        side,
        amount: betAmt,
        isDemo,
      });

      if (result.ok !== false) {
        const id = result.betId || result.orderID || '?';
        console.log(`   ✅ Placed! ID: ${id} Status: ${result.status || 'open'}`);
        totalSpent += betAmt;
        traded++;
        openMarkets.add(slug);
        openMarkets.add(market);
      } else {
        console.log(`   ❌ Failed: ${result.error}`);
        skipped++;
      }
    } catch (e) {
      console.log(`   ❌ Error: ${e.message}`);
      skipped++;
    }

    // Small delay between trades
    await new Promise(r => setTimeout(r, 1000));
  }

  console.log('');
  console.log(`📋 Summary: ${traded} traded, ${skipped} skipped, $${totalSpent.toFixed(2)} spent`);

  return { traded, skipped, totalSpent };
}

module.exports = { runAutoTrade };

if (require.main === module) {
  const args = process.argv.slice(2);

  const getArg = (flag) => {
    const i = args.indexOf(flag);
    return i >= 0 && args[i + 1] ? args[i + 1] : null;
  };

  runAutoTrade({
    minScore:   parseFloat(getArg('--min-score')   || '7'),
    maxBet:     parseFloat(getArg('--max-bet')     || '5'),
    dailyLimit: parseFloat(getArg('--daily-limit') || '100'),
    topic:      getArg('--topic') || '',
    isDemo:     args.includes('--demo'),
    dryRun:     args.includes('--dry-run'),
  }).then(r => {
    process.exit(0);
  }).catch(e => {
    console.error('❌ Error:', e.message);
    process.exit(1);
  });
}
