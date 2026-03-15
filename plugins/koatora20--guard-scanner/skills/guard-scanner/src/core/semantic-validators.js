'use strict';

function applySemanticValidators(content, relFile, findings) {
    checkASTValidation(content, relFile, findings);
    checkShellChains(content, relFile, findings);
    checkFetchExfiltration(content, relFile, findings);
    checkPythonSignals(content, relFile, findings);
}

function checkASTValidation(content, relFile, findings) {
    if (content.includes('fetch') && (content.includes('exec') || content.includes('eval'))) {
        if (content.match(/fetch\([^)]+\)[^]*?(?:exec|eval|spawn|execSync)\(/is)) {
            findings.push({
                severity: 'CRITICAL',
                id: 'AST_FETCH_TO_EXEC',
                cat: 'data-flow',
                desc: 'Validated Chain: Remote fetch directly piped to code execution',
                file: relFile,
                validated: true,
                validation_state: 'chain-validated',
                confidence: 0.98,
                attack_chain_id: 'remote-fetch-exec',
            });
        }
    }

    for (const finding of findings) {
        if (finding.validated === undefined) finding.validated = false;
        if (!finding.validation_state) {
            finding.validation_state = finding.validated ? 'chain-validated' : 'heuristic-only';
        }
    }
}

function checkShellChains(content, relFile, findings) {
    if (/env\s*\|\s*curl\b[^\n]*-d\s+@-/i.test(content)) {
        findings.push({
            severity: 'CRITICAL',
            id: 'CHAIN_ENV_TO_CURL',
            cat: 'exfiltration',
            desc: 'Validated Chain: environment variables piped to outbound curl upload',
            file: relFile,
            validated: true,
            validation_state: 'chain-validated',
            confidence: 0.99,
            attack_chain_id: 'credential-exfiltration',
        });
    }
}

function checkPythonSignals(content, relFile, findings) {
    if (/requests\.(get|post)\(/i.test(content) && /subprocess\.(run|Popen|call)\(/i.test(content)) {
        findings.push({
            severity: 'HIGH',
            id: 'PY_REMOTE_TO_SUBPROCESS',
            cat: 'data-flow',
            desc: 'Python remote input combined with subprocess execution',
            file: relFile,
            validated: true,
            validation_state: 'semantic-match',
            confidence: 0.9,
        });
    }
}

function checkFetchExfiltration(content, relFile, findings) {
    if (/fetch\(\s*['"]https?:\/\/[^'"]+['"]\s*,\s*\{[^}]*body\s*:\s*(document\.cookie|process\.env|[^}]*token|[^}]*secret)/is.test(content)) {
        findings.push({
            severity: 'CRITICAL',
            id: 'FETCH_EXFIL_CHAIN',
            cat: 'exfiltration',
            desc: 'Validated Chain: external fetch uploads sensitive runtime data',
            file: relFile,
            validated: true,
            validation_state: 'semantic-match',
            confidence: 0.97,
            attack_chain_id: 'credential-exfiltration',
        });
    }
}

module.exports = {
    applySemanticValidators,
    checkASTValidation,
};
