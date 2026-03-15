#!/usr/bin/env node
/**
 * Amazon Ads — All-in-one convenience wrapper (Step 1 + wait + Step 2)
 * Requests report, waits 60s, then polls until done.
 * Use in crons that can afford a 10-min timeout.
 *
 * Usage: node scripts/get-report.js [--days 7]
 */

const { spawnSync } = require('child_process');
const path = require('path');

const SCRIPTS = path.join(__dirname);
const args = process.argv.slice(2);
const WAIT_MS = 60000; // 1 min initial wait before first poll

function run(script, extraArgs = []) {
  const result = spawnSync('node', [path.join(SCRIPTS, script), ...args, ...extraArgs], {
    stdio: 'inherit',
    encoding: 'utf8',
  });
  if (result.status !== 0) {
    process.exit(result.status || 1);
  }
}

async function main() {
  console.log('⚡ Amazon Ads Get-Report (all-in-one)\n');

  // Step 1: Request
  run('request-report.js');

  // Wait before first poll
  console.log(`\n⏳ Waiting ${WAIT_MS / 1000}s before polling (report generation takes 1-10 min)...`);
  await new Promise(r => setTimeout(r, WAIT_MS));

  // Step 2: Poll
  run('poll-report.js');
}

main().catch(e => { console.error('❌', e.message); process.exit(1); });
