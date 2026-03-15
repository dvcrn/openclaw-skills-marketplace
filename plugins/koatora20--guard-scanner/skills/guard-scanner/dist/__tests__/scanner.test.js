"use strict";
/**
 * guard-scanner v3.0.0 — Test Suite
 *
 * Guava Standard v5 §4: T-Wada / Red-Green-Refactor
 * Phase 1: RED — All tests written BEFORE implementation changes.
 *
 * Run: node --test dist/__tests__/scanner.test.js
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const node_test_1 = require("node:test");
const assert = __importStar(require("node:assert/strict"));
const path = __importStar(require("node:path"));
const scanner_js_1 = require("../scanner.js");
// ── Fixtures ────────────────────────────────────────────────────────────────
// Fixtures live in test/fixtures/ (project root), not in ts-src or dist.
// Resolve from __dirname (dist/__tests__/) → ../../test/fixtures/
const FIXTURES_DIR = path.resolve(__dirname, '..', '..', 'test', 'fixtures');
const CLEAN_SKILL = path.join(FIXTURES_DIR, 'clean-skill');
const MALICIOUS_SKILL = path.join(FIXTURES_DIR, 'malicious-skill');
const COMPACTION_SKILL = path.join(FIXTURES_DIR, 'compaction-skill');
// ── Helper: scan a single skill ─────────────────────────────────────────────
function scanSingleSkill(skillPath, skillName) {
    const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true });
    scanner.scanSkill(skillPath, skillName);
    const result = scanner.findings[0];
    return {
        findings: result?.findings ?? [],
        risk: result?.risk ?? 0,
        verdict: result?.verdict ?? 'CLEAN',
    };
}
// ── Helper: collect findings by running scanner private methods via scanSkill ─
function findingsContain(findings, id) {
    return findings.some((f) => f.id === id);
}
function findingsOfCat(findings, cat) {
    return findings.filter((f) => f.cat === cat);
}
// ══════════════════════════════════════════════════════════════════════════════
// TEST SUITE
// ══════════════════════════════════════════════════════════════════════════════
(0, node_test_1.describe)('guard-scanner v3.0.0', () => {
    // ── Version ─────────────────────────────────────────────────────────────
    (0, node_test_1.it)('T01: exports correct version', () => {
        assert.equal(scanner_js_1.VERSION, '3.2.0');
    });
    // ── IoC Detection ───────────────────────────────────────────────────────
    (0, node_test_1.describe)('checkIoCs', () => {
        (0, node_test_1.it)('T02: detects known malicious IP', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(findingsContain(result.findings, 'IOC_IP'), 'Should detect known malicious IP 91.92.242.30');
            const iocIp = result.findings.find((f) => f.id === 'IOC_IP');
            assert.equal(iocIp?.severity, 'CRITICAL');
        });
        (0, node_test_1.it)('T03: detects known exfil domain', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(findingsContain(result.findings, 'IOC_DOMAIN'), 'Should detect webhook.site domain');
        });
        (0, node_test_1.it)('T04: detects known typosquat skill name', () => {
            const result = scanSingleSkill(CLEAN_SKILL, 'clawhub');
            assert.ok(findingsContain(result.findings, 'KNOWN_TYPOSQUAT'), 'Should detect typosquat name "clawhub"');
            const ts = result.findings.find((f) => f.id === 'KNOWN_TYPOSQUAT');
            assert.equal(ts?.severity, 'CRITICAL');
        });
    });
    // ── Pattern Detection ─────────────────────────────────────────────────
    (0, node_test_1.describe)('checkPatterns', () => {
        (0, node_test_1.it)('T05: detects prompt injection [System Message]', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(findingsContain(result.findings, 'PI_SYSTEM_MSG'), 'Should detect [System Message] prompt injection');
        });
        (0, node_test_1.it)('T06: detects eval() in code', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(findingsContain(result.findings, 'MAL_EVAL'), 'Should detect eval() usage');
        });
        (0, node_test_1.it)('T07: detects identity hijack (SOUL.md write)', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(findingsContain(result.findings, 'HIJACK_SOUL_WRITE') ||
                findingsContain(result.findings, 'MEM_WRITE_SOUL'), 'Should detect writeFileSync(SOUL.md)');
        });
    });
    // ── Signature Detection (hbg-scan compatible) ─────────────────────────
    (0, node_test_1.describe)('checkSignatures', () => {
        (0, node_test_1.it)('T08: detects SIG-001 post-compaction audit', () => {
            const result = scanSingleSkill(COMPACTION_SKILL, 'compaction-skill');
            const sigFindings = result.findings.filter((f) => f.id.startsWith('SIG_SIG-001'));
            assert.ok(sigFindings.length > 0, 'Should detect SIG-001 Post-Compaction Audit pattern');
        });
        (0, node_test_1.it)('T09: detects SIG-006 AMOS stealer pattern', () => {
            // AMOS patterns are in malicious-skill but osascript is not present there
            // so this tests that signature matching only fires on actual patterns
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            // We don't expect SIG-006 here since osascript isn't in fixtures
            // This test validates no false positive
            const sig006 = result.findings.filter((f) => f.id === 'SIG_SIG-006');
            assert.equal(sig006.length, 0, 'Should NOT false-positive SIG-006 without osascript');
        });
    });
    // ── Compaction Persistence ─────────────────────────────────────────────
    (0, node_test_1.describe)('checkCompactionPersistence', () => {
        (0, node_test_1.it)('T10: detects WORKFLOW_AUTO marker', () => {
            const result = scanSingleSkill(COMPACTION_SKILL, 'compaction-skill');
            const cpFindings = findingsOfCat(result.findings, 'compaction-persistence');
            const hasWorkflow = cpFindings.some((f) => f.desc.includes('WORKFLOW_AUTO'));
            assert.ok(hasWorkflow, 'Should detect WORKFLOW_AUTO marker');
        });
        (0, node_test_1.it)('T11: detects HEARTBEAT.md reference', () => {
            const result = scanSingleSkill(COMPACTION_SKILL, 'compaction-skill');
            const cpFindings = findingsOfCat(result.findings, 'compaction-persistence');
            const hasHeartbeat = cpFindings.some((f) => f.desc.includes('HEARTBEAT.md'));
            assert.ok(hasHeartbeat, 'Should detect HEARTBEAT.md reference');
        });
    });
    // ── Hardcoded Secrets ─────────────────────────────────────────────────
    (0, node_test_1.describe)('checkHardcodedSecrets', () => {
        (0, node_test_1.it)('T12: detects high-entropy API key', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(findingsContain(result.findings, 'SECRET_ENTROPY'), 'Should detect high-entropy string as possible leaked secret');
        });
        (0, node_test_1.it)('T13: does NOT flag placeholder values', () => {
            const result = scanSingleSkill(CLEAN_SKILL, 'clean-skill');
            assert.ok(!findingsContain(result.findings, 'SECRET_ENTROPY'), 'Should not detect secrets in clean skill');
        });
    });
    // ── JS Data Flow ──────────────────────────────────────────────────────
    (0, node_test_1.describe)('checkJSDataFlow', () => {
        (0, node_test_1.it)('T14: detects credential → network flow', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(findingsContain(result.findings, 'AST_CRED_TO_NET'), 'Should detect data flow from secret read to network call');
        });
        (0, node_test_1.it)('T15: detects exfiltration trifecta (fs + child_process + net)', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.ok(findingsContain(result.findings, 'AST_EXFIL_TRIFECTA'), 'Should detect exfiltration trifecta pattern');
        });
    });
    // ── Risk Scoring ──────────────────────────────────────────────────────
    (0, node_test_1.describe)('calculateRisk', () => {
        (0, node_test_1.it)('T16: clean skill → risk 0', () => {
            const result = scanSingleSkill(CLEAN_SKILL, 'clean-skill');
            assert.equal(result.risk, 0, 'Clean skill should have zero risk');
        });
        (0, node_test_1.it)('T17: single LOW finding → risk 2', () => {
            // Use calculateRisk directly via scanner instance
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true });
            const lowFindings = [
                { severity: 'LOW', id: 'TEST_LOW', cat: 'test', desc: 'test', file: 'test.js' },
            ];
            // Access private method via type assertion
            const risk = scanner.calculateRisk(lowFindings);
            assert.equal(risk, 2, 'Single LOW finding should score 2');
        });
        (0, node_test_1.it)('T18: credential + exfiltration amplifier → score×2', () => {
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true });
            const findings = [
                { severity: 'HIGH', id: 'CRED_ENV_ACCESS', cat: 'credential-handling', desc: 'cred', file: 'a.js' },
                { severity: 'HIGH', id: 'EXFIL_WEBHOOK', cat: 'exfiltration', desc: 'exfil', file: 'a.js' },
            ];
            const risk = scanner.calculateRisk(findings);
            // 15+15=30, ×2=60
            assert.ok(risk >= 60, `Cred+exfil should amplify to ≥60, got ${risk}`);
        });
        (0, node_test_1.it)('T19: compaction + prompt injection → ≥90', () => {
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true });
            const findings = [
                { severity: 'CRITICAL', id: 'COMPACTION_PERSISTENCE', cat: 'compaction-persistence', desc: 'cp', file: 'a.md' },
                { severity: 'CRITICAL', id: 'PI_SYSTEM_MSG', cat: 'prompt-injection', desc: 'pi', file: 'a.md' },
            ];
            const risk = scanner.calculateRisk(findings);
            assert.ok(risk >= 90, `Compaction+PI should score ≥90, got ${risk}`);
        });
    });
    // ── Verdict ───────────────────────────────────────────────────────────
    (0, node_test_1.describe)('getVerdict', () => {
        (0, node_test_1.it)('T20: risk 0 → CLEAN', () => {
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true });
            const verdict = scanner.getVerdict(0);
            assert.equal(verdict.label, 'CLEAN');
        });
        (0, node_test_1.it)('T21: risk 80 → MALICIOUS (normal mode)', () => {
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true });
            const verdict = scanner.getVerdict(80);
            assert.equal(verdict.label, 'MALICIOUS');
        });
    });
    // ── Integration Tests ─────────────────────────────────────────────────
    (0, node_test_1.describe)('Integration: scanSkill', () => {
        (0, node_test_1.it)('T22: clean skill scan → CLEAN verdict', () => {
            const result = scanSingleSkill(CLEAN_SKILL, 'clean-test-skill');
            assert.equal(result.verdict, 'CLEAN', 'Clean skill should get CLEAN verdict');
            assert.equal(result.findings.length, 0, 'Clean skill should have 0 findings');
        });
        (0, node_test_1.it)('T23: malicious skill scan → MALICIOUS verdict', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.equal(result.verdict, 'MALICIOUS', 'Malicious skill should get MALICIOUS verdict');
            assert.ok(result.risk >= 80, `Risk should be ≥80, got ${result.risk}`);
        });
    });
    // ── Report Output ─────────────────────────────────────────────────────
    (0, node_test_1.describe)('Report Generation', () => {
        (0, node_test_1.it)('T24: toJSON produces valid report structure', () => {
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const report = scanner.toJSON();
            assert.equal(report.scanner, `guard-scanner v${scanner_js_1.VERSION}`);
            assert.equal(report.mode, 'normal');
            assert.ok(report.timestamp);
            assert.ok(report.stats);
            assert.ok(report.findings);
            assert.ok(Array.isArray(report.recommendations));
        });
        (0, node_test_1.it)('T25: toSARIF produces valid SARIF 2.1.0', () => {
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const sarif = scanner.toSARIF('/test');
            assert.equal(sarif.version, '2.1.0');
            assert.equal(sarif.$schema, 'https://json.schemastore.org/sarif-2.1.0.json');
            assert.equal(sarif.runs.length, 1);
            assert.ok(sarif.runs[0].tool.driver.name, 'guard-scanner');
            assert.ok(sarif.runs[0].results.length > 0, 'Should have SARIF results');
        });
    });
    // ── OWASP 2025 Mapping Guarantee ─────────────────────────────────────
    (0, node_test_1.describe)('OWASP 2025 Mapping', () => {
        (0, node_test_1.it)('T26: every pattern in PATTERNS has an owasp field', () => {
            // T-Wada: This test guarantees OWASP coverage.
            // If a developer adds a pattern without owasp, this fails RED.
            const { PATTERNS } = require('../patterns.js');
            const missing = PATTERNS.filter((p) => !p.owasp);
            assert.equal(missing.length, 0, `${missing.length} pattern(s) missing owasp field: ${missing.map((p) => p.id).join(', ')}`);
        });
        (0, node_test_1.it)('T27: owasp values are valid LLM01-LLM10', () => {
            const { PATTERNS } = require('../patterns.js');
            const validOwasp = new Set(['LLM01', 'LLM02', 'LLM03', 'LLM04', 'LLM05', 'LLM06', 'LLM07', 'LLM08', 'LLM09', 'LLM10']);
            const invalid = PATTERNS.filter((p) => p.owasp && !validOwasp.has(p.owasp));
            assert.equal(invalid.length, 0, `Invalid owasp values: ${invalid.map((p) => `${p.id}=${p.owasp}`).join(', ')}`);
        });
        (0, node_test_1.it)('T28: prompt-injection patterns map to LLM01', () => {
            const { PATTERNS } = require('../patterns.js');
            const piPatterns = PATTERNS.filter((p) => p.cat === 'prompt-injection');
            assert.ok(piPatterns.length > 0, 'Should have prompt-injection patterns');
            const wrongMapping = piPatterns.filter((p) => p.owasp !== 'LLM01');
            assert.equal(wrongMapping.length, 0, `prompt-injection patterns not mapped to LLM01: ${wrongMapping.map((p) => p.id).join(', ')}`);
        });
        (0, node_test_1.it)('T29: memory-poisoning patterns map to LLM04', () => {
            const { PATTERNS } = require('../patterns.js');
            const mpPatterns = PATTERNS.filter((p) => p.cat === 'memory-poisoning');
            assert.ok(mpPatterns.length > 0, 'Should have memory-poisoning patterns');
            const wrongMapping = mpPatterns.filter((p) => p.owasp !== 'LLM04');
            assert.equal(wrongMapping.length, 0, `memory-poisoning patterns not mapped to LLM04: ${wrongMapping.map((p) => p.id).join(', ')}`);
        });
    });
    // ── System Prompt Leakage (LLM07) ────────────────────────────────────
    (0, node_test_1.describe)('LLM07: System Prompt Leakage', () => {
        const LEAKAGE_SKILL = path.join(path.resolve(__dirname, '..', '..', 'ts-src', '__tests__', 'fixtures'), 'prompt-leakage-skill');
        (0, node_test_1.it)('T30: detects "output your system prompt" pattern', () => {
            const result = scanSingleSkill(LEAKAGE_SKILL, 'prompt-leakage-skill');
            assert.ok(findingsContain(result.findings, 'SPL_DUMP_SYSTEM'), 'Should detect system prompt dump request');
        });
        (0, node_test_1.it)('T31: detects "repeat everything above" pattern', () => {
            const result = scanSingleSkill(LEAKAGE_SKILL, 'prompt-leakage-skill');
            assert.ok(findingsContain(result.findings, 'SPL_REPEAT_ABOVE'), 'Should detect repeat-above extraction');
        });
        (0, node_test_1.it)('T32: detects "tell me your rules" pattern', () => {
            const result = scanSingleSkill(LEAKAGE_SKILL, 'prompt-leakage-skill');
            assert.ok(findingsContain(result.findings, 'SPL_TELL_RULES'), 'Should detect rule extraction attempt');
        });
        (0, node_test_1.it)('T33: detects SOUL.md shell extraction', () => {
            const result = scanSingleSkill(LEAKAGE_SKILL, 'prompt-leakage-skill');
            assert.ok(findingsContain(result.findings, 'SPL_SOUL_EXFIL'), 'Should detect SOUL.md content extraction via shell command');
        });
        (0, node_test_1.it)('T34: clean skill has ZERO LLM07 findings (false positive guard)', () => {
            const result = scanSingleSkill(CLEAN_SKILL, 'clean-skill');
            const llm07 = result.findings.filter((f) => f.cat === 'system-prompt-leakage');
            assert.equal(llm07.length, 0, `Clean skill should have 0 LLM07 findings, got ${llm07.length}: ${llm07.map(f => f.id).join(', ')}`);
        });
    });
    // ── install-check Integration ─────────────────────────────────────────
    (0, node_test_1.describe)('install-check Integration', () => {
        (0, node_test_1.it)('T35: malicious skill → MALICIOUS verdict with ≥20 findings', () => {
            const result = scanSingleSkill(MALICIOUS_SKILL, 'malicious-skill');
            assert.equal(result.verdict, 'MALICIOUS');
            assert.ok(result.findings.length >= 20, `Expected ≥20 findings for aggressive malicious skill, got ${result.findings.length}`);
        });
        (0, node_test_1.it)('T36: clean skill → exactly 0 findings (strictest possible)', () => {
            const result = scanSingleSkill(CLEAN_SKILL, 'clean-skill');
            assert.equal(result.findings.length, 0, 'Clean skill MUST have exactly 0 findings');
            assert.equal(result.risk, 0, 'Clean skill MUST have risk 0');
            assert.equal(result.verdict, 'CLEAN', 'Clean skill MUST be CLEAN');
        });
        (0, node_test_1.it)('T37: strict mode lowers thresholds', () => {
            const normal = new scanner_js_1.GuardScanner({ summaryOnly: true });
            const strict = new scanner_js_1.GuardScanner({ summaryOnly: true, strict: true });
            // Strict thresholds should be lower
            assert.ok(strict.thresholds.suspicious < normal.thresholds.suspicious, 'Strict suspicious threshold should be lower than normal');
            assert.ok(strict.thresholds.malicious < normal.thresholds.malicious, 'Strict malicious threshold should be lower than normal');
        });
        (0, node_test_1.it)('T38: prompt-leakage skill → SUSPICIOUS or higher', () => {
            const result = scanSingleSkill(path.join(path.resolve(__dirname, '..', '..', 'ts-src', '__tests__', 'fixtures'), 'prompt-leakage-skill'), 'prompt-leakage-skill');
            assert.ok(result.verdict === 'SUSPICIOUS' || result.verdict === 'MALICIOUS', `Prompt leakage skill should be SUSPICIOUS or MALICIOUS, got ${result.verdict} (risk: ${result.risk})`);
        });
    });
    // ── SARIF OWASP Tags ─────────────────────────────────────────────────
    (0, node_test_1.describe)('SARIF OWASP Tags', () => {
        (0, node_test_1.it)('T39: SARIF rules include OWASP/* tags for pattern-based findings', () => {
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const sarif = scanner.toSARIF('/test');
            const rulesWithOwasp = sarif.runs[0].tool.driver.rules.filter((r) => r.properties.tags.some((t) => t.startsWith('OWASP/')));
            assert.ok(rulesWithOwasp.length > 0, 'At least one SARIF rule should have OWASP/* tag');
        });
        (0, node_test_1.it)('T40: OWASP tags follow OWASP/LLMxx format', () => {
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const sarif = scanner.toSARIF('/test');
            for (const rule of sarif.runs[0].tool.driver.rules) {
                const owaspTags = rule.properties.tags.filter((t) => t.startsWith('OWASP/'));
                for (const tag of owaspTags) {
                    assert.match(tag, /^OWASP\/LLM(?:0[1-9]|10)$/, `Invalid OWASP tag format: ${tag} in rule ${rule.id}`);
                }
            }
        });
        (0, node_test_1.it)('T41: PI_SYSTEM_MSG rule has OWASP/LLM01 tag', () => {
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const sarif = scanner.toSARIF('/test');
            const piRule = sarif.runs[0].tool.driver.rules.find((r) => r.id === 'PI_SYSTEM_MSG');
            assert.ok(piRule, 'Should have PI_SYSTEM_MSG rule');
            assert.ok(piRule.properties.tags.includes('OWASP/LLM01'), `PI_SYSTEM_MSG should have OWASP/LLM01 tag, got: ${piRule.properties.tags}`);
        });
    });
    // ── Compaction Skill Cross-Check ──────────────────────────────────────
    (0, node_test_1.describe)('Compaction Skill Cross-Check', () => {
        (0, node_test_1.it)('T42: compaction-skill has ZERO LLM07 findings (no false positives)', () => {
            const result = scanSingleSkill(COMPACTION_SKILL, 'compaction-skill');
            const llm07 = result.findings.filter((f) => f.cat === 'system-prompt-leakage');
            assert.equal(llm07.length, 0, `Compaction skill should have 0 LLM07 findings, got ${llm07.length}: ${llm07.map(f => f.id).join(', ')}`);
        });
    });
    // ── v3.2.0: Quiet Mode + Format Stdout ──────────────────────────────
    (0, node_test_1.describe)('v3.2.0: Quiet Mode', () => {
        (0, node_test_1.it)('T43: quiet mode suppresses console output during scanDirectory', () => {
            const logs = [];
            const origLog = console.log;
            console.log = (...args) => logs.push(args.join(' '));
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true, quiet: true });
            scanner.scanDirectory(FIXTURES_DIR);
            console.log = origLog;
            // In quiet mode, scanDirectory should produce no console.log output
            assert.equal(logs.length, 0, `Quiet mode should suppress all console.log, got ${logs.length} lines: ${logs.slice(0, 3).join(' | ')}`);
        });
        (0, node_test_1.it)('T44: quiet mode still populates findings array', () => {
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true, quiet: true });
            scanner.scanDirectory(FIXTURES_DIR);
            assert.ok(scanner.findings.length > 0, 'Quiet mode should still populate findings');
            const malicious = scanner.findings.find(f => f.skill === 'malicious-skill');
            assert.ok(malicious, 'Should find malicious-skill in quiet mode');
            assert.ok(malicious.findings.length >= 20, 'malicious-skill should have ≥20 findings');
        });
    });
    (0, node_test_1.describe)('v3.2.0: Format Stdout Output', () => {
        (0, node_test_1.it)('T45: toJSON output is valid parseable JSON string', () => {
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true, quiet: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const report = scanner.toJSON();
            const jsonStr = JSON.stringify(report);
            // Must be parseable
            const parsed = JSON.parse(jsonStr);
            assert.equal(parsed.scanner, `guard-scanner v${scanner_js_1.VERSION}`);
            assert.ok(parsed.findings.length > 0, 'JSON output should contain findings');
            assert.ok(parsed.stats.scanned > 0, 'JSON output should have scan stats');
        });
        (0, node_test_1.it)('T46: toSARIF output has required SARIF 2.1.0 fields for GitHub Code Scanning', () => {
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true, quiet: true });
            scanner.scanSkill(MALICIOUS_SKILL, 'malicious-skill');
            const sarif = scanner.toSARIF('/test');
            const sarifStr = JSON.stringify(sarif);
            const parsed = JSON.parse(sarifStr);
            // Required SARIF 2.1.0 fields per spec
            assert.equal(parsed.version, '2.1.0');
            assert.equal(parsed.$schema, 'https://json.schemastore.org/sarif-2.1.0.json');
            assert.ok(parsed.runs.length === 1, 'Should have exactly 1 run');
            assert.equal(parsed.runs[0].tool.driver.name, 'guard-scanner');
            assert.ok(parsed.runs[0].tool.driver.rules.length > 0, 'Should have rules');
            assert.ok(parsed.runs[0].results.length > 0, 'Should have results');
            // Each result must have ruleId and location
            for (const result of parsed.runs[0].results) {
                assert.ok(result.ruleId, 'Each result must have ruleId');
                assert.ok(result.locations?.length > 0, 'Each result must have locations');
            }
        });
        (0, node_test_1.it)('T47: scanDirectory in quiet mode + toJSON = pipeable combo', () => {
            const logs = [];
            const origLog = console.log;
            console.log = (...args) => logs.push(args.join(' '));
            const scanner = new scanner_js_1.GuardScanner({ summaryOnly: true, quiet: true });
            scanner.scanDirectory(FIXTURES_DIR);
            const report = scanner.toJSON();
            const jsonStr = JSON.stringify(report, null, 2);
            console.log = origLog;
            // No console.log pollution
            assert.equal(logs.length, 0, 'Quiet+format should have zero console output');
            // JSON is valid
            const parsed = JSON.parse(jsonStr);
            assert.ok(parsed.stats.scanned >= 5, `Should scan ≥5 skills, got ${parsed.stats.scanned}`);
            assert.ok(parsed.findings.length > 0, 'Should have at least 1 finding group');
        });
    });
});
//# sourceMappingURL=scanner.test.js.map