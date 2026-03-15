#!/usr/bin/env node
/**
 * generate-readme-stats.js
 *
 * Runs `npm test` and injects actual test counts into README.md
 * Also updates the badge. Zero tolerance for hardcoded test numbers.
 *
 * Usage:
 *   node scripts/generate-readme-stats.js          # update README
 *   node scripts/generate-readme-stats.js --check   # CI mode: fail if drift detected
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const README_PATH = path.join(ROOT, 'README.md');

// Run tests and capture output (node --test puts stats on stderr)
let testOutput;
try {
    const result = execSync('node --test test/*.test.js', { cwd: ROOT, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'] });
    testOutput = result; // stdout contains the stats in newer Node
} catch (err) {
    // node --test puts stats on stderr; also exits non-zero on failures
    testOutput = (err.stdout || '') + '\n' + (err.stderr || '');
}

// Parse stats from output
const parseCount = (label) => {
    const re = new RegExp(`ℹ ${label} (\\d+)`, 'i');
    const m = testOutput.match(re);
    return m ? parseInt(m[1], 10) : null;
};

const tests = parseCount('tests');
const suites = parseCount('suites');
const pass = parseCount('pass');
const fail = parseCount('fail');

if (tests === null || suites === null) {
    console.error('❌ Could not parse test output. Raw output:\n', testOutput);
    process.exit(1);
}

console.log(`📊 Parsed: tests=${tests} suites=${suites} pass=${pass} fail=${fail}`);

if (fail > 0) {
    console.error(`❌ ${fail} tests failed. Fix tests before updating README.`);
    process.exit(1);
}

// Read README
let readme = fs.readFileSync(README_PATH, 'utf8');

// 1. Update badge: tests-NNN%20passed
const badgeRe = /tests-\d+%20passed/g;
const newBadge = `tests-${pass}%20passed`;
readme = readme.replace(badgeRe, newBadge);

// 2. Update test results block
const statsBlockRe = /ℹ tests \d+\nℹ suites \d+\nℹ pass \d+\nℹ fail \d+/;
const newStatsBlock = `ℹ tests ${tests}\nℹ suites ${suites}\nℹ pass ${pass}\nℹ fail ${fail}`;
readme = readme.replace(statsBlockRe, newStatsBlock);

const isCheck = process.argv.includes('--check');

if (isCheck) {
    const current = fs.readFileSync(README_PATH, 'utf8');
    if (current !== readme) {
        console.error('❌ README test stats are out of sync! Run: node scripts/generate-readme-stats.js');
        process.exit(1);
    }
    console.log('✅ README test stats are in sync.');
} else {
    fs.writeFileSync(README_PATH, readme);
    console.log(`✅ README updated: ${pass} tests / ${suites} suites / ${fail} fail`);
}
