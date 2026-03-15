'use strict';

const { RuleRegistry } = require('./core/rule-registry.js');

const FINDING_SCHEMA_VERSION = '2.0.0';

const registry = new RuleRegistry();
const PATTERN_METADATA = new Map(registry.getAllRules().map((pattern) => [pattern.id, pattern]));

const CATEGORY_FALSE_POSITIVES = {
    'prompt-injection': [
        'Documentation or research samples that quote malicious prompts for education.',
        'Security test fixtures intentionally embedding prompt payloads.',
    ],
    'malicious-code': [
        'Legitimate sandboxed examples demonstrating exec/eval behavior.',
        'Build or packaging scripts that reference execution primitives without attacker control.',
    ],
    'secret-detection': [
        'Synthetic placeholders, redacted values, or test tokens that resemble secrets.',
        'Checksums or opaque identifiers stored in code but not used as credentials.',
    ],
    'exfiltration': [
        'Benign telemetry or webhook examples in documentation.',
        'Internal endpoints that resemble exfiltration infrastructure but are controlled.',
    ],
    'structural': [
        'Minimal demo skills that intentionally omit production structure.',
        'Fixture directories designed to test missing-file behavior.',
    ],
    'runtime-guard': [
        'Security training material discussing the blocked command or phrase.',
        'Administrator-authored maintenance commands scanned outside execution context.',
    ],
};

function categoryDefaultFalsePositives(category) {
    return CATEGORY_FALSE_POSITIVES[category] || [
        'Benign examples or tests that intentionally reference the same pattern.',
        'Context where the matched text is documented but never executed or enforced.',
    ];
}

function inferValidationStatus(raw, source) {
    if (raw.validation_status) return raw.validation_status;
    if (raw.validation_state === 'chain-validated') return 'validated';
    if (raw.validation_state === 'semantic-match') return 'validated';
    if (raw.validation_state === 'lexical-match') return 'heuristic-only';
    if (raw.status) return raw.status;
    if (raw.validated === true) return 'validated';
    if (raw.validated === false) return 'heuristic-only';
    return source === 'runtime' ? 'runtime-observed' : 'heuristic-only';
}

function inferValidationState(raw, source) {
    if (raw.validation_state) return raw.validation_state;
    if (raw.validation_status === 'validated') return 'semantic-match';
    if (raw.validation_status === 'heuristic-only') return 'heuristic-only';
    if (raw.validation_status === 'runtime-observed') return 'runtime-observed';
    if (raw.validated === true) return 'chain-validated';
    if (raw.validated === false) return 'heuristic-only';
    return source === 'runtime' ? 'runtime-observed' : 'heuristic-only';
}

function inferCategory(raw, metadata, source) {
    return raw.category || raw.cat || metadata.cat || (source === 'runtime' ? 'runtime-guard' : 'unknown');
}

function inferDescription(raw, metadata) {
    return raw.description || raw.desc || metadata.desc || raw.id || 'Unknown finding';
}

function inferRationale(raw, metadata, category, description, source) {
    return raw.rationale
        || metadata.rationale
        || `${source === 'runtime' ? 'Runtime guard observed' : 'Static analysis matched'} ${description.toLowerCase()} in category "${category}".`;
}

function inferPreconditions(raw, metadata, source) {
    return raw.preconditions
        || raw.exploitPrecondition
        || metadata.exploitPrecondition
        || (source === 'runtime'
            ? 'The monitored tool call must reach execution or enforcement with attacker-controlled arguments.'
            : 'The matched file or content must be processed in a context where the detected pattern can influence agent behavior.');
}

function inferRemediation(raw, metadata, category, source) {
    return raw.remediation_hint
        || raw.remediationHint
        || metadata.remediationHint
        || (source === 'runtime'
            ? 'Block the tool call, review the triggering arguments, and require an explicit human-reviewed allowlist before retrying.'
            : `Review the ${category} finding, confirm execution context, and remove or isolate the risky construct before installation.`);
}

function inferFalsePositiveScenarios(raw, metadata, category) {
    const candidate = raw.false_positive_scenarios
        || raw.falsePositiveScenarios
        || metadata.falsePositiveScenarios;

    if (Array.isArray(candidate) && candidate.length > 0) return candidate;
    return categoryDefaultFalsePositives(category);
}

function buildEvidence(raw, options = {}) {
    const evidence = {};

    if (raw.file !== undefined) evidence.file = raw.file;
    if (raw.line !== undefined) evidence.line = raw.line;
    if (raw.sample !== undefined) evidence.sample = raw.sample;
    if (raw.matchCount !== undefined) evidence.match_count = raw.matchCount;
    if (raw.match_count !== undefined) evidence.match_count = raw.match_count;
    if (raw.matchCount === undefined && raw.match_count === undefined && raw.matchCount !== 0 && raw.match_count !== 0) {
        if (options.matchCount !== undefined) evidence.match_count = options.matchCount;
    }
    if (raw.toolName !== undefined || options.toolName !== undefined) evidence.tool_name = raw.toolName || options.toolName;
    if (raw.paramsPreview !== undefined || options.paramsPreview !== undefined) evidence.params_preview = raw.paramsPreview || options.paramsPreview;
    if (raw.layer !== undefined) evidence.layer = raw.layer;
    if (options.layer_name !== undefined) evidence.layer_name = options.layer_name;

    return evidence;
}

function buildEvidenceSpans(raw) {
    if (Array.isArray(raw.evidence_spans)) return raw.evidence_spans;
    if (raw.line || raw.startLine || raw.endLine) {
        return [{
            file: raw.file,
            start_line: raw.startLine || raw.line || 1,
            end_line: raw.endLine || raw.line || raw.startLine || 1,
        }];
    }
    return [];
}

function inferConfidence(raw, metadata, source) {
    if (typeof raw.confidence === 'number') {
        return Math.max(0, Math.min(1, Number(raw.confidence.toFixed(3))));
    }
    if (raw.validated === true || raw.validation_state === 'chain-validated') return 0.98;
    if (raw.validation_state === 'semantic-match') return 0.9;
    if (source === 'runtime') return 0.99;
    if (metadata.severity === 'CRITICAL') return 0.92;
    if (metadata.severity === 'HIGH') return 0.8;
    if (metadata.severity === 'MEDIUM') return 0.65;
    return 0.5;
}

function normalizeFinding(raw, options = {}) {
    const source = options.source || raw.source || (raw.layer ? 'runtime' : 'static');
    const metadata = options.ruleMetadata || PATTERN_METADATA.get(raw.id) || {};
    const category = inferCategory(raw, metadata, source);
    const description = inferDescription(raw, metadata);
    const validation_state = inferValidationState(raw, source);

    const normalized = {
        ...raw,
        schema_version: FINDING_SCHEMA_VERSION,
        source,
        rule_id: raw.rule_id || raw.id,
        id: raw.id || raw.rule_id,
        category,
        cat: raw.cat || category,
        severity: raw.severity || metadata.severity || 'LOW',
        description,
        desc: raw.desc || description,
        rationale: inferRationale(raw, metadata, category, description, source),
        preconditions: inferPreconditions(raw, metadata, source),
        false_positive_scenarios: inferFalsePositiveScenarios(raw, metadata, category),
        remediation_hint: inferRemediation(raw, metadata, category, source),
        validation_state,
        validation_status: inferValidationStatus(raw, source),
        confidence: inferConfidence(raw, metadata, source),
        evidence_spans: buildEvidenceSpans(raw),
        attack_chain_id: raw.attack_chain_id || null,
        evidence: buildEvidence(raw, options),
    };

    if (normalized.evidence.file !== undefined && normalized.file === undefined) normalized.file = normalized.evidence.file;
    if (normalized.evidence.line !== undefined && normalized.line === undefined) normalized.line = normalized.evidence.line;
    if (normalized.evidence.sample !== undefined && normalized.sample === undefined) normalized.sample = normalized.evidence.sample;
    if (normalized.evidence.match_count !== undefined && normalized.matchCount === undefined) normalized.matchCount = normalized.evidence.match_count;

    return normalized;
}

module.exports = {
    FINDING_SCHEMA_VERSION,
    normalizeFinding,
};
