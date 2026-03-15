/**
 * E2E Plugin Test — guard-scanner OpenClaw plugin integration
 *
 * Tests the actual package surface that OpenClaw discovers:
 * - package.json exposes openclaw.extensions
 * - dist/openclaw-plugin.mjs exists after build
 * - openclaw.plugin.json keeps the same plugin id
 */

const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const path = require('path');
const fs = require('fs');
const pkg = require('../package.json');
const manifest = require('../openclaw.plugin.json');

const PLUGIN_PATH = path.join(__dirname, '..', 'dist', 'openclaw-plugin.mjs');

describe('E2E Plugin: Package surface', () => {
    it('package.json should declare official openclaw.extensions discovery metadata', () => {
        assert.deepEqual(pkg.openclaw.extensions, ['./dist/openclaw-plugin.mjs']);
    });

    it('compiled plugin entry should exist after build', () => {
        assert.ok(fs.existsSync(PLUGIN_PATH), `compiled plugin should exist at ${PLUGIN_PATH}`);
    });

    it('manifest id should match the public plugin id', () => {
        assert.equal(manifest.id, 'guard-scanner');
    });
});
