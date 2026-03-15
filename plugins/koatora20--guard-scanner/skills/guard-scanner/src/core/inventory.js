'use strict';

const fs = require('fs');
const path = require('path');

const CODE_EXTENSIONS = new Set(['.js', '.ts', '.mjs', '.cjs', '.py', '.sh', '.bash', '.ps1', '.rb', '.go', '.rs', '.php', '.pl']);
const DOC_EXTENSIONS = new Set(['.md', '.txt', '.rst', '.adoc']);
const DATA_EXTENSIONS = new Set(['.json', '.yaml', '.yml', '.toml', '.xml', '.csv']);
const BINARY_EXTENSIONS = new Set(['.png', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.wasm', '.wav', '.mp3', '.mp4', '.webm', '.ogg', '.pdf', '.zip', '.tar', '.gz', '.bz2', '.7z', '.exe', '.dll', '.so', '.dylib']);
const GENERATED_REPORT_FILES = new Set(['guard-scanner-report.json', 'guard-scanner-report.html', 'guard-scanner.sarif']);

function classifyFile(ext, relFile) {
    if (CODE_EXTENSIONS.has(ext)) return 'code';
    if (DOC_EXTENSIONS.has(ext)) return 'doc';
    if (DATA_EXTENSIONS.has(ext)) return 'data';
    const base = path.basename(relFile).toLowerCase();
    if (base === 'skill.md' || base === 'readme.md') return 'skill-doc';
    return 'other';
}

function isSelfNoisePath(skillName, relFile) {
    if (skillName !== 'guard-scanner') return false;
    return /^test\//.test(relFile)
        || /^dist\/__tests__\//.test(relFile)
        || /^ts-src\/__tests__\//.test(relFile)
        || /^docs\//.test(relFile)
        || relFile === 'ROADMAP-RESEARCH.md'
        || relFile === 'CHANGELOG.md';
}

function isSelfThreatCorpus(skillName, relFile) {
    if (skillName !== 'guard-scanner') return false;
    return /(^|\/)(ioc-db|patterns)\.(js|ts)$/.test(relFile);
}

function getFiles(dir) {
    const results = [];
    try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry of entries) {
            const fullPath = path.join(dir, entry.name);
            if (entry.isDirectory()) {
                if (entry.name === '.git' || entry.name === 'node_modules') continue;
                results.push(...getFiles(fullPath));
            } else {
                const baseName = entry.name.toLowerCase();
                if (GENERATED_REPORT_FILES.has(baseName)) continue;
                results.push(fullPath);
            }
        }
    } catch { }
    return results;
}

function listSkills(dir) {
    return fs.readdirSync(dir).filter((file) => {
        const fullPath = path.join(dir, file);
        return fs.statSync(fullPath).isDirectory();
    });
}

module.exports = {
    CODE_EXTENSIONS,
    DOC_EXTENSIONS,
    DATA_EXTENSIONS,
    BINARY_EXTENSIONS,
    GENERATED_REPORT_FILES,
    classifyFile,
    isSelfNoisePath,
    isSelfThreatCorpus,
    getFiles,
    listSkills,
};
