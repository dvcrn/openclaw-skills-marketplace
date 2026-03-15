const { describe, it } = require('node:test');
const assert = require('node:assert/strict');

const {
    compareOpenClawVersions,
    evaluateOpenClawBaseline,
    normalizeGitHubReleaseVersion,
    evaluateOpenClawSourceParity,
} = require('../src/openclaw-upstream.js');

describe('OpenClaw upstream version comparison', () => {
    it('treats a stable release as newer than an older stable release', () => {
        assert.equal(compareOpenClawVersions('2026.3.8', '2026.3.7'), 1);
    });

    it('treats a stable release as newer than the same prerelease', () => {
        assert.equal(compareOpenClawVersions('2026.3.8', '2026.3.8-beta.1'), 1);
    });

    it('treats an older stable release as behind the latest stable release', () => {
        assert.equal(compareOpenClawVersions('2026.3.7', '2026.3.8'), -1);
    });
});

describe('OpenClaw upstream baseline evaluation', () => {
    it('returns upToDate when the pinned version matches upstream', () => {
        const result = evaluateOpenClawBaseline({
            pinnedVersion: '2026.3.8',
            latestVersion: '2026.3.8',
            latestPublishedAt: '2026-03-09T07:44:44.237Z',
            source: 'npm',
        });

        assert.equal(result.upToDate, true);
        assert.equal(result.behind, false);
    });

    it('returns behind with measured delta when upstream is newer', () => {
        const result = evaluateOpenClawBaseline({
            pinnedVersion: '2026.3.7',
            latestVersion: '2026.3.8',
            latestPublishedAt: '2026-03-09T07:44:44.237Z',
            source: 'npm',
        });

        assert.equal(result.upToDate, false);
        assert.equal(result.behind, true);
        assert.equal(result.pinnedVersion, '2026.3.7');
        assert.equal(result.latestVersion, '2026.3.8');
        assert.equal(result.source, 'npm');
    });
});

describe('OpenClaw source parity evaluation', () => {
    it('normalizes GitHub release tags before comparison', () => {
        assert.equal(normalizeGitHubReleaseVersion('v2026.3.8'), '2026.3.8');
    });

    it('reports parity when npm and GitHub agree on the stable release', () => {
        const result = evaluateOpenClawSourceParity({
            npmLatestVersion: '2026.3.8',
            githubLatestVersion: 'v2026.3.8',
        });

        assert.equal(result.inParity, true);
        assert.equal(result.npmLatestVersion, '2026.3.8');
        assert.equal(result.githubLatestVersion, '2026.3.8');
    });

    it('reports mismatch when npm and GitHub disagree', () => {
        const result = evaluateOpenClawSourceParity({
            npmLatestVersion: '2026.3.8',
            githubLatestVersion: 'v2026.3.7',
        });

        assert.equal(result.inParity, false);
    });
});
