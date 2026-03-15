/**
 * guard-scanner v3.0.0 — Detection Patterns (TypeScript)
 *
 * 20+ threat categories, 190+ regex patterns.
 * Ported from patterns.js with TypeScript interfaces.
 *
 * Categories:
 *   prompt-injection, malicious-code, credential-handling, exfiltration,
 *   obfuscation, suspicious-download, leaky-skills, memory-poisoning,
 *   prompt-worm, persistence, cve-patterns, identity-hijack,
 *   pii-exposure, shadow-ai, system-prompt-leakage
 *
 * OWASP LLM Top 10 2025 Mapping:
 *   LLM01 — Prompt Injection
 *   LLM02 — Sensitive Information Disclosure
 *   LLM03 — Supply Chain Vulnerabilities
 *   LLM04 — Data and Model Poisoning
 *   LLM05 — Improper Output Handling
 *   LLM06 — Excessive Agency
 *   LLM07 — System Prompt Leakage
 *   LLM08 — Vector and Embedding Weaknesses
 *   LLM09 — Misinformation
 *   LLM10 — Unbounded Consumption
 */
import type { PatternRule } from './types.js';
export declare const PATTERNS: PatternRule[];
//# sourceMappingURL=patterns.d.ts.map