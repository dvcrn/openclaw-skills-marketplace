#!/usr/bin/env node
/**
 * monitor.js — Price monitor with auto-sell at target/stoploss
 * 
 * Usage:
 *   node scripts/monitor.js --bet-id 148 --target 0.50 --stop 0.28 --interval 300
 * 
 * Checks price every --interval seconds (default 300 = 5 min)
 * Sells automatically when price hits target (take-profit) or stop (stop-loss)
 */
'use strict';
const fs = require('fs');
const path = require('path');
const https = require('https');

function loadConfig() {
  const p = path.join(process.env.HOME || '/root', '.polyclawster', 'config.json');
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function httpsGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'polyclawster-monitor/1.0' }, timeout: 10000 }, res => {
      let d = ''; res.on('data', c => d += c);
      res.on('end', () => { try { resolve(JSON.parse(d)); } catch { resolve(null); } });
    }).on('error', reject).on('timeout', function() { this.destroy(); reject(new Error('timeout')); });
  });
}

async function getCurrentPrice(conditionId, side) {
  const mkt = await httpsGet('https://clob.polymarket.com/markets/' + conditionId);
  if (!mkt?.tokens) return null;
  const token = mkt.tokens.find(t => t.outcome.toUpperCase() === side.toUpperCase());
  return token ? parseFloat(token.price) : null;
}

async function main() {
  const args = process.argv.slice(2);
  const getArg = (name) => { const i = args.indexOf('--' + name); return i >= 0 ? args[i + 1] : null; };

  const betId = parseInt(getArg('bet-id'));
  const target = parseFloat(getArg('target'));
  const stop = parseFloat(getArg('stop'));
  const interval = parseInt(getArg('interval') || '300');

  if (!betId || !target || !stop) {
    console.log('Usage: node scripts/monitor.js --bet-id N --target 0.50 --stop 0.28 [--interval 300]');
    process.exit(1);
  }

  const config = loadConfig();

  // Get bet info from API
  const profile = await httpsGet(`https://polyclawster.com/api/agents?action=profile&id=${config.agentId}`);
  const bet = profile?.agent?.recentBets?.find(b => b.id === betId);
  if (!bet) { console.error('Bet not found:', betId); process.exit(1); }

  const entry = parseFloat(bet.price);
  console.log(`📊 Monitoring bet #${betId}`);
  console.log(`   Market: ${bet.market}`);
  console.log(`   Side: ${bet.side} | Entry: $${entry.toFixed(3)} | Amount: $${bet.amount}`);
  console.log(`   🎯 Target: $${target.toFixed(3)} (${((target/entry-1)*100).toFixed(0)}% profit)`);
  console.log(`   🛑 Stop: $${stop.toFixed(3)} (${((stop/entry-1)*100).toFixed(0)}% loss)`);
  console.log(`   Checking every ${interval}s...\n`);

  const conditionId = bet.market_id;

  const check = async () => {
    const price = await getCurrentPrice(conditionId, bet.side).catch(() => null);
    if (!price) { console.log(`   [${new Date().toISOString().slice(11,19)}] Price fetch failed, retrying...`); return; }

    const pnlPct = ((price / entry - 1) * 100).toFixed(1);
    const emoji = price >= entry ? '📈' : '📉';
    console.log(`   ${emoji} [${new Date().toISOString().slice(11,19)}] $${price.toFixed(3)} (${pnlPct}%)`);

    if (price >= target) {
      console.log(`\n   🎯 TARGET HIT! Selling...`);
      const { execSync } = require('child_process');
      execSync(`node ${path.join(__dirname, 'sell.js')} --bet-id ${betId}`, { stdio: 'inherit' });
      process.exit(0);
    }

    if (price <= stop) {
      console.log(`\n   🛑 STOP LOSS HIT! Selling...`);
      const { execSync } = require('child_process');
      execSync(`node ${path.join(__dirname, 'sell.js')} --bet-id ${betId}`, { stdio: 'inherit' });
      process.exit(0);
    }
  };

  await check();
  setInterval(check, interval * 1000);
}

main().catch(e => { console.error('Error:', e.message); process.exit(1); });
