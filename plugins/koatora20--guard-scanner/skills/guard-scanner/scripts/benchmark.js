#!/usr/bin/env node
/**
 * benchmark.js — Guard-Scanner Detection Quality Metrics
 *
 * Scans benchmark fixtures and computes precision, recall, and F1:
 *   - Benign fixtures should NOT produce findings (FP check)
 *   - Malicious fixtures should produce findings (TP check)
 *
 * Usage:
 *   node scripts/benchmark.js           # run benchmark
 *   node scripts/benchmark.js --json    # JSON output
 *   node scripts/benchmark.js --readme  # inject results into README
 */

const path = require('path');
const fs = require('fs');
const { GuardScanner } = require('../src/scanner.js');

const BENCHMARK_DIR = path.join(__dirname, '..', 'test', 'fixtures', 'benchmark');
const README_PATH = path.join(__dirname, '..', 'README.md');

function getSkills(dir) {
    if (!fs.existsSync(dir)) return [];
    return fs.readdirSync(dir)
        .filter(d => fs.statSync(path.join(dir, d)).isDirectory())
        .map(name => ({ name, path: path.join(dir, name) }));
}

function scanSkill(skillPath, skillName) {
    const scanner = new GuardScanner({ verbose: false, strict: false, quiet: true });
    scanner.scanSkill(skillPath, skillName);
    const entry = scanner.findings.find(f => f.skill === skillName);
    return {
        findings: entry ? entry.findings.length : 0,
        risk: entry ? entry.risk : 0,
        verdict: entry ? entry.verdict : 'CLEAN',
        categories: entry ? [...new Set(entry.findings.map(f => f.cat))] : []
    };
}

// ── Run Benchmark ──

const benignSkills = getSkills(path.join(BENCHMARK_DIR, 'benign'));
const maliciousSkills = getSkills(path.join(BENCHMARK_DIR, 'malicious'));

const results = {
    benign: [],
    malicious: [],
    metrics: {}
};

// Scan benign
for (const skill of benignSkills) {
    const r = scanSkill(skill.path, skill.name);
    results.benign.push({ ...skill, ...r, expected: 'SAFE', detected: r.findings > 0 });
}

// Scan malicious
for (const skill of maliciousSkills) {
    const r = scanSkill(skill.path, skill.name);
    results.malicious.push({ ...skill, ...r, expected: 'MALICIOUS', detected: r.findings > 0 });
}

// ── Compute Metrics ──

const TP = results.malicious.filter(r => r.detected).length;  // correctly identified malicious
const FN = results.malicious.filter(r => !r.detected).length; // missed malicious
const FP = results.benign.filter(r => r.detected).length;     // falsely flagged benign
const TN = results.benign.filter(r => !r.detected).length;    // correctly passed benign

const precision = TP + FP > 0 ? TP / (TP + FP) : 0;
const recall = TP + FN > 0 ? TP / (TP + FN) : 0;
const f1 = precision + recall > 0 ? 2 * (precision * recall) / (precision + recall) : 0;
const fpr = FP + TN > 0 ? FP / (FP + TN) : 0;

results.metrics = {
    total_benign: benignSkills.length,
    total_malicious: maliciousSkills.length,
    TP, FN, FP, TN,
    precision: Math.round(precision * 1000) / 10,
    recall: Math.round(recall * 1000) / 10,
    f1: Math.round(f1 * 1000) / 10,
    false_positive_rate: Math.round(fpr * 1000) / 10,
};

// ── Output ──

const isJson = process.argv.includes('--json');
const isReadme = process.argv.includes('--readme');

if (isJson) {
    console.log(JSON.stringify(results, null, 2));
} else {
    console.log('\n🛡️ Guard-Scanner Benchmark Results\n');
    console.log(`  Corpus: ${benignSkills.length} benign / ${maliciousSkills.length} malicious\n`);

    console.log('  Malicious skill results:');
    for (const r of results.malicious) {
        const icon = r.detected ? '✅' : '❌';
        console.log(`    ${icon} ${r.name}: ${r.verdict} (risk=${r.risk}, findings=${r.findings})`);
    }

    console.log('\n  Benign skill results:');
    for (const r of results.benign) {
        const icon = r.detected ? '⚠️ FP' : '✅';
        console.log(`    ${icon} ${r.name}: ${r.verdict} (risk=${r.risk}, findings=${r.findings})`);
    }

    console.log(`\n  ┌──────────────────────────────┐`);
    console.log(`  │ Precision:  ${String(results.metrics.precision).padStart(5)}%           │`);
    console.log(`  │ Recall:     ${String(results.metrics.recall).padStart(5)}%           │`);
    console.log(`  │ F1 Score:   ${String(results.metrics.f1).padStart(5)}%           │`);
    console.log(`  │ FP Rate:    ${String(results.metrics.false_positive_rate).padStart(5)}%           │`);
    console.log(`  │ TP=${TP} FN=${FN} FP=${FP} TN=${TN}`.padEnd(31) + `│`);
    console.log(`  └──────────────────────────────┘\n`);
}

// Inject into README if --readme
if (isReadme) {
    let readme = fs.readFileSync(README_PATH, 'utf8');
    const benchBlock = `### Benchmark Results

| Metric | Value |
|--------|-------|
| Corpus | ${benignSkills.length} benign / ${maliciousSkills.length} malicious |
| Precision | ${results.metrics.precision}% |
| Recall | ${results.metrics.recall}% |
| F1 Score | ${results.metrics.f1}% |
| False Positive Rate | ${results.metrics.false_positive_rate}% |

> Generated by \`node scripts/benchmark.js --readme\`. Run to verify.`;

    // Replace existing or insert before Test Results
    if (readme.includes('### Benchmark Results')) {
        readme = readme.replace(/### Benchmark Results[\s\S]*?> Generated by.*?verify\./m, benchBlock);
    } else {
        readme = readme.replace('## Test Results', `${benchBlock}\n\n## Test Results`);
    }
    fs.writeFileSync(README_PATH, readme);
    console.log('✅ README updated with benchmark results');
}
