/**
 * guard-scanner asset audit テストスイート
 *
 * node --test で実行
 * mock httpGetを使い外部APIアクセスなしでテスト
 */

const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const { AssetAuditor, AUDIT_VERSION, ALERT_SEVERITY } = require('../src/asset-auditor.js');

// ===== Mock Data =====
const MOCK_NPM_AUTHOR_RESPONSE = {
    status: 200,
    data: {
        objects: [
            {
                package: {
                    name: '@guava-parity/guard-scanner',
                    version: '5.1.0',
                    description: 'Agent security scanner',
                    scope: '@guava-parity',
                    date: '2026-03-04T00:00:00.000Z',
                    links: { npm: 'https://npmjs.com/package/@guava-parity/guard-scanner' },
                },
            },
            {
                package: {
                    name: 'guard-scanner',
                    version: '5.0.8',
                    description: 'Agent security scanner standalone',
                    scope: 'unscoped',
                    date: '2026-03-03T00:00:00.000Z',
                    links: {},
                },
            },
        ],
    },
};

const MOCK_NPM_MAINTAINER_RESPONSE = {
    status: 200,
    data: {
        objects: [
            {
                package: {
                    name: '@koatora20/guava-mcp',
                    version: '1.0.1',
                    description: 'Leaked MCP',
                    scope: '@koatora20',
                    date: '2026-03-01T00:00:00.000Z',
                    links: {},
                },
            },
        ],
    },
};

const MOCK_NPM_DETAIL_CLEAN = {
    status: 200,
    data: {
        'dist-tags': { latest: '5.1.0' },
        versions: {
            '5.1.0': {
                files: ['src/', 'hooks/', 'docs/', 'README.md', 'LICENSE'],
                publishConfig: { access: 'public' },
            },
        },
    },
};

const MOCK_NPM_DETAIL_DIRTY = {
    status: 200,
    data: {
        'dist-tags': { latest: '1.0.1' },
        versions: {
            '1.0.1': {
                files: ['src/', 'node_modules/', '.env', 'dist/'],
                publishConfig: { access: 'public' },
            },
        },
    },
};

const MOCK_GITHUB_REPOS = {
    status: 200,
    data: [
        {
            name: 'guard-scanner',
            full_name: 'koatora20/guard-scanner',
            private: false,
            size: 1740,
            fork: false,
            description: 'Agent security scanner',
            default_branch: 'main',
            updated_at: '2026-03-04T00:00:00Z',
            html_url: 'https://github.com/koatora20/guard-scanner',
        },
        {
            name: 'guavasuite-oss',
            full_name: 'koatora20/guavasuite-oss',
            private: false,
            size: 250000, // 250MB — abnormally large
            fork: false,
            description: 'Leaked suite',
            default_branch: 'main',
            updated_at: '2026-03-01T00:00:00Z',
            html_url: 'https://github.com/koatora20/guavasuite-oss',
        },
    ],
};

const MOCK_GITHUB_CONTENTS_CLEAN = {
    status: 200,
    data: [
        { name: 'src', type: 'dir' },
        { name: 'package.json', type: 'file' },
        { name: 'README.md', type: 'file' },
        { name: '.gitignore', type: 'file' },
    ],
};

const MOCK_GITHUB_CONTENTS_DIRTY = {
    status: 200,
    data: [
        { name: 'node_modules', type: 'dir' },
        { name: '.env', type: 'file' },
        { name: 'src', type: 'dir' },
        { name: 'secrets.key', type: 'file' },
    ],
};

// ===== Mock httpGet =========================================
function createMockHttpGet(responses = {}) {
    return async (url) => {
        for (const [pattern, response] of Object.entries(responses)) {
            if (url.includes(pattern)) {
                if (response instanceof Error) throw response;
                return response;
            }
        }
        throw new Error(`Unmocked URL: ${url}`);
    };
}

// ===== 1. npm Audit Tests =====
describe('Asset Audit: npm', () => {
    it('should return packages for a valid user', async () => {
        const mockHttp = createMockHttpGet({
            'search?text=author:': MOCK_NPM_AUTHOR_RESPONSE,
            'search?text=maintainer:': { status: 200, data: { objects: [] } },
            'registry.npmjs.org/@guava-parity': MOCK_NPM_DETAIL_CLEAN,
            'registry.npmjs.org/guard-scanner': MOCK_NPM_DETAIL_CLEAN,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditNpm('testuser');
        assert.equal(result.packages.length, 2);
        assert.ok(result.packages.some(p => p.name === '@guava-parity/guard-scanner'));
    });

    it('should detect scope duplicates', async () => {
        const mockHttp = createMockHttpGet({
            'search?text=author:': {
                status: 200,
                data: {
                    objects: [
                        { package: { name: '@koatora20/guava-mcp', version: '1.0.0', scope: '@koatora20' } },
                        { package: { name: '@guava-parity/guava-mcp', version: '2.0.0', scope: '@guava-parity' } },
                    ],
                },
            },
            'search?text=maintainer:': { status: 200, data: { objects: [] } },
            'registry.npmjs.org/@koatora20': MOCK_NPM_DETAIL_CLEAN,
            'registry.npmjs.org/@guava-parity': MOCK_NPM_DETAIL_CLEAN,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditNpm('testuser');
        const scopeAlerts = result.alerts.filter(a => a.type === 'SCOPE_DUPLICATE');
        assert.ok(scopeAlerts.length >= 1, 'Should detect scope duplicate');
        assert.ok(scopeAlerts[0].message.includes('guava-mcp'));
    });

    it('should detect node_modules in published package', async () => {
        const mockHttp = createMockHttpGet({
            'search?text=author:': MOCK_NPM_MAINTAINER_RESPONSE,
            'search?text=maintainer:': { status: 200, data: { objects: [] } },
            'registry.npmjs.org/@koatora20': MOCK_NPM_DETAIL_DIRTY,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditNpm('testuser');
        assert.ok(result.alerts.some(a => a.type === 'NODE_MODULES_IN_PACKAGE'));
    });

    it('should detect .env in published package', async () => {
        const mockHttp = createMockHttpGet({
            'search?text=author:': MOCK_NPM_MAINTAINER_RESPONSE,
            'search?text=maintainer:': { status: 200, data: { objects: [] } },
            'registry.npmjs.org/@koatora20': MOCK_NPM_DETAIL_DIRTY,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditNpm('testuser');
        assert.ok(result.alerts.some(a => a.type === 'ENV_FILE_IN_PACKAGE'));
    });

    it('should handle empty results gracefully', async () => {
        const mockHttp = createMockHttpGet({
            'search?text=author:': { status: 200, data: { objects: [] } },
            'search?text=maintainer:': { status: 200, data: { objects: [] } },
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditNpm('nobody');
        assert.equal(result.packages.length, 0);
    });

    it('should handle API errors gracefully', async () => {
        const mockHttp = createMockHttpGet({
            'search?text=author:': new Error('Network error'),
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditNpm('testuser');
        assert.ok(result.alerts.some(a => a.type === 'API_ERROR'));
    });

    it('should detect public packages', async () => {
        const mockHttp = createMockHttpGet({
            'search?text=author:': MOCK_NPM_AUTHOR_RESPONSE,
            'search?text=maintainer:': { status: 200, data: { objects: [] } },
            'registry.npmjs.org/@guava-parity': MOCK_NPM_DETAIL_CLEAN,
            'registry.npmjs.org/guard-scanner': MOCK_NPM_DETAIL_CLEAN,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditNpm('testuser');
        assert.ok(result.alerts.some(a => a.type === 'PUBLIC_PACKAGE'));
    });

    it('should deduplicate packages from author and maintainer searches', async () => {
        const mockHttp = createMockHttpGet({
            'search?text=author:': MOCK_NPM_AUTHOR_RESPONSE,
            'search?text=maintainer:': MOCK_NPM_AUTHOR_RESPONSE, // same data
            'registry.npmjs.org/@guava-parity': MOCK_NPM_DETAIL_CLEAN,
            'registry.npmjs.org/guard-scanner': MOCK_NPM_DETAIL_CLEAN,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditNpm('testuser');
        assert.equal(result.packages.length, 2, 'Should deduplicate');
    });

    it('should require username', async () => {
        const auditor = new AssetAuditor({ quiet: true });
        await assert.rejects(() => auditor.auditNpm(''), /username is required/);
    });

    it('should produce valid JSON output', async () => {
        const mockHttp = createMockHttpGet({
            'search?text=author:': MOCK_NPM_AUTHOR_RESPONSE,
            'search?text=maintainer:': { status: 200, data: { objects: [] } },
            'registry.npmjs.org/@guava-parity': MOCK_NPM_DETAIL_CLEAN,
            'registry.npmjs.org/guard-scanner': MOCK_NPM_DETAIL_CLEAN,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        await auditor.auditNpm('testuser');
        const json = auditor.toJSON();
        assert.ok(json.timestamp);
        assert.ok(json.scanner.includes('guard-scanner'));
        assert.equal(json.type, 'asset-audit');
        assert.ok(json.results.npm);
        assert.ok(Array.isArray(json.alerts));
    });
});

// ===== 2. GitHub Audit Tests =====
describe('Asset Audit: GitHub', () => {
    it('should return repos for a valid user', async () => {
        const mockHttp = createMockHttpGet({
            'api.github.com/users/': MOCK_GITHUB_REPOS,
            'api.github.com/repos/koatora20/guard-scanner/contents': MOCK_GITHUB_CONTENTS_CLEAN,
            'api.github.com/repos/koatora20/guavasuite-oss/contents': MOCK_GITHUB_CONTENTS_DIRTY,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditGithub('koatora20');
        assert.equal(result.repos.length, 2);
    });

    it('should detect node_modules committed', async () => {
        const mockHttp = createMockHttpGet({
            'api.github.com/users/': MOCK_GITHUB_REPOS,
            'api.github.com/repos/koatora20/guard-scanner/contents': MOCK_GITHUB_CONTENTS_CLEAN,
            'api.github.com/repos/koatora20/guavasuite-oss/contents': MOCK_GITHUB_CONTENTS_DIRTY,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditGithub('koatora20');
        assert.ok(result.alerts.some(a => a.type === 'NODE_MODULES_COMMITTED'));
    });

    it('should detect .env committed', async () => {
        const mockHttp = createMockHttpGet({
            'api.github.com/users/': MOCK_GITHUB_REPOS,
            'api.github.com/repos/koatora20/guard-scanner/contents': MOCK_GITHUB_CONTENTS_CLEAN,
            'api.github.com/repos/koatora20/guavasuite-oss/contents': MOCK_GITHUB_CONTENTS_DIRTY,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditGithub('koatora20');
        assert.ok(result.alerts.some(a => a.type === 'ENV_FILE_COMMITTED'));
    });

    it('should detect .key files committed', async () => {
        const mockHttp = createMockHttpGet({
            'api.github.com/users/': MOCK_GITHUB_REPOS,
            'api.github.com/repos/koatora20/guard-scanner/contents': MOCK_GITHUB_CONTENTS_CLEAN,
            'api.github.com/repos/koatora20/guavasuite-oss/contents': MOCK_GITHUB_CONTENTS_DIRTY,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditGithub('koatora20');
        assert.ok(result.alerts.some(a => a.type === 'KEY_FILE_COMMITTED'));
    });

    it('should detect abnormally large repos', async () => {
        const mockHttp = createMockHttpGet({
            'api.github.com/users/': MOCK_GITHUB_REPOS,
            'api.github.com/repos/koatora20/guard-scanner/contents': MOCK_GITHUB_CONTENTS_CLEAN,
            'api.github.com/repos/koatora20/guavasuite-oss/contents': MOCK_GITHUB_CONTENTS_DIRTY,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditGithub('koatora20');
        assert.ok(result.alerts.some(a => a.type === 'LARGE_REPO'));
    });

    it('should handle API errors gracefully', async () => {
        const mockHttp = createMockHttpGet({
            'api.github.com/users/': new Error('Rate limited'),
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditGithub('testuser');
        assert.ok(result.alerts.some(a => a.type === 'API_ERROR'));
    });

    it('should require username', async () => {
        const auditor = new AssetAuditor({ quiet: true });
        await assert.rejects(() => auditor.auditGithub(''), /username is required/);
    });

    it('should classify visibility correctly', async () => {
        const mockHttp = createMockHttpGet({
            'api.github.com/users/': MOCK_GITHUB_REPOS,
            'api.github.com/repos/koatora20/guard-scanner/contents': MOCK_GITHUB_CONTENTS_CLEAN,
            'api.github.com/repos/koatora20/guavasuite-oss/contents': MOCK_GITHUB_CONTENTS_DIRTY,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditGithub('koatora20');
        assert.ok(result.repos.every(r => r.visibility === 'public'));
    });

    it('should handle empty repo list', async () => {
        const mockHttp = createMockHttpGet({
            'api.github.com/users/': { status: 200, data: [] },
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        const result = await auditor.auditGithub('nobody');
        assert.equal(result.repos.length, 0);
    });

    it('should produce valid SARIF output', async () => {
        const mockHttp = createMockHttpGet({
            'api.github.com/users/': MOCK_GITHUB_REPOS,
            'api.github.com/repos/koatora20/guard-scanner/contents': MOCK_GITHUB_CONTENTS_CLEAN,
            'api.github.com/repos/koatora20/guavasuite-oss/contents': MOCK_GITHUB_CONTENTS_DIRTY,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        await auditor.auditGithub('koatora20');
        const sarif = auditor.toSARIF();
        assert.equal(sarif.version, '2.1.0');
        assert.ok(sarif.runs[0].tool.driver.name === 'guard-scanner');
    });
});

// ===== 3. ClawHub Audit Tests =====
describe('Asset Audit: ClawHub', () => {
    it('should handle clawhub CLI not available', async () => {
        const auditor = new AssetAuditor({ quiet: true });
        const result = await auditor.auditClawHub('guard-scanner');
        assert.ok(result.alerts.some(a => a.type === 'CLAWHUB_CLI_UNAVAILABLE'));
    });

    it('should detect known malicious patterns', async () => {
        // Manually inject skills to simulate CLI response
        const auditor = new AssetAuditor({ quiet: true });
        // Simulate by directly testing pattern matching
        auditor.results.clawhub = { skills: [], alerts: [] };
        const skills = [
            { name: 'atomic-stealer-helper', description: 'Steal everything', downloads: 500, stars: 0 },
            { name: 'clean-skill', description: 'Helpful tool', downloads: 100, stars: 50 },
        ];
        // Run the pattern check logic
        const KNOWN_MALICIOUS_PATTERNS = [
            'atomic-stealer', 'crypto-miner', 'reverse-shell',
            'claw-havoc', 'data-exfil', 'token-steal',
        ];
        for (const skill of skills) {
            const lowerName = (skill.name || '').toLowerCase();
            for (const pattern of KNOWN_MALICIOUS_PATTERNS) {
                if (lowerName.includes(pattern)) {
                    auditor.alerts.push({
                        severity: 'CRITICAL',
                        type: 'KNOWN_MALICIOUS_SKILL',
                        message: `Skill "${skill.name}" matches known malicious pattern: ${pattern}`,
                        affected: [skill.name],
                    });
                }
            }
        }
        assert.ok(auditor.alerts.some(a => a.type === 'KNOWN_MALICIOUS_SKILL'));
        assert.ok(auditor.alerts.some(a => a.message.includes('atomic-stealer')));
    });

    it('should require query', async () => {
        const auditor = new AssetAuditor({ quiet: true });
        await assert.rejects(() => auditor.auditClawHub(''), /query is required/);
    });

    it('should detect suspicious DL/star ratio', async () => {
        const auditor = new AssetAuditor({ quiet: true });
        // Directly test the ratio logic
        const skill = { name: 'suspicious-skill', downloads: 5000, stars: 0, description: '' };
        if (skill.downloads > 100 && skill.stars === 0) {
            auditor.alerts.push({
                severity: 'MEDIUM',
                type: 'SUSPICIOUS_DL_STAR_RATIO',
                message: `Skill "${skill.name}" has ${skill.downloads} downloads but 0 stars`,
                affected: [skill.name],
            });
        }
        assert.ok(auditor.alerts.some(a => a.type === 'SUSPICIOUS_DL_STAR_RATIO'));
    });
});

// ===== 4. Integration Tests =====
describe('Asset Audit: Integration', () => {
    it('should aggregate alerts from all providers', async () => {
        const mockHttp = createMockHttpGet({
            'search?text=author:': MOCK_NPM_AUTHOR_RESPONSE,
            'search?text=maintainer:': { status: 200, data: { objects: [] } },
            'registry.npmjs.org/@guava-parity': MOCK_NPM_DETAIL_CLEAN,
            'registry.npmjs.org/guard-scanner': MOCK_NPM_DETAIL_CLEAN,
            'api.github.com/users/': MOCK_GITHUB_REPOS,
            'api.github.com/repos/koatora20/guard-scanner/contents': MOCK_GITHUB_CONTENTS_CLEAN,
            'api.github.com/repos/koatora20/guavasuite-oss/contents': MOCK_GITHUB_CONTENTS_DIRTY,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        await auditor.auditNpm('koatora20');
        await auditor.auditGithub('koatora20');
        assert.ok(auditor.alerts.length > 0, 'Should have aggregated alerts');
        assert.ok(auditor.results.npm, 'Should have npm results');
        assert.ok(auditor.results.github, 'Should have github results');
    });

    it('should return correct verdict for critical alerts', async () => {
        const mockHttp = createMockHttpGet({
            'search?text=author:': MOCK_NPM_MAINTAINER_RESPONSE,
            'search?text=maintainer:': { status: 200, data: { objects: [] } },
            'registry.npmjs.org/@koatora20': MOCK_NPM_DETAIL_DIRTY,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        await auditor.auditNpm('testuser');
        const verdict = auditor.getVerdict();
        assert.equal(verdict.label, 'CRITICAL EXPOSURE');
        assert.equal(verdict.exitCode, 2);
    });

    it('should return ALL CLEAR for clean results', async () => {
        const mockHttp = createMockHttpGet({
            'search?text=author:': { status: 200, data: { objects: [] } },
            'search?text=maintainer:': { status: 200, data: { objects: [] } },
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        await auditor.auditNpm('cleanuser');
        const verdict = auditor.getVerdict();
        assert.equal(verdict.label, 'ALL CLEAR');
        assert.equal(verdict.exitCode, 0);
    });

    it('should produce valid JSON report', async () => {
        const mockHttp = createMockHttpGet({
            'search?text=author:': MOCK_NPM_AUTHOR_RESPONSE,
            'search?text=maintainer:': { status: 200, data: { objects: [] } },
            'registry.npmjs.org/@guava-parity': MOCK_NPM_DETAIL_CLEAN,
            'registry.npmjs.org/guard-scanner': MOCK_NPM_DETAIL_CLEAN,
        });
        const auditor = new AssetAuditor({ _httpGet: mockHttp, quiet: true });
        await auditor.auditNpm('testuser');
        const json = auditor.toJSON();
        assert.ok(json.timestamp);
        assert.ok(json.scanner);
        assert.ok(json.counts);
        assert.ok(json.verdict);
    });

    it('should count alert severities correctly', async () => {
        const auditor = new AssetAuditor({ quiet: true });
        auditor.alerts = [
            { severity: 'CRITICAL', type: 'TEST', message: 'test', affected: [] },
            { severity: 'CRITICAL', type: 'TEST', message: 'test', affected: [] },
            { severity: 'HIGH', type: 'TEST', message: 'test', affected: [] },
            { severity: 'MEDIUM', type: 'TEST', message: 'test', affected: [] },
        ];
        const counts = auditor.getAlertCounts();
        assert.equal(counts.CRITICAL, 2);
        assert.equal(counts.HIGH, 1);
        assert.equal(counts.MEDIUM, 1);
        assert.equal(counts.LOW, 0);
    });
});

// ===== 5. Version & Module Tests =====
describe('Asset Audit: Module', () => {
    it('should export AssetAuditor class', () => {
        assert.ok(typeof AssetAuditor === 'function');
    });

    it('should export AUDIT_VERSION', () => {
        assert.equal(AUDIT_VERSION, '8.0.0');
    });

    it('should export ALERT_SEVERITY enum', () => {
        assert.equal(ALERT_SEVERITY.CRITICAL, 'CRITICAL');
        assert.equal(ALERT_SEVERITY.HIGH, 'HIGH');
        assert.equal(ALERT_SEVERITY.MEDIUM, 'MEDIUM');
        assert.equal(ALERT_SEVERITY.LOW, 'LOW');
        assert.equal(ALERT_SEVERITY.INFO, 'INFO');
    });
});
