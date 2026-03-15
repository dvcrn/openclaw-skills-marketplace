const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.join(__dirname, '..');
const DOCS = ['README.md', 'README_ja.md', 'SKILL.md', 'CHANGELOG.md'];
const BANNED = [
    /fully OpenClaw-compatible/i,
    /dist\/runtime-plugin\.js/,
    /test\/manifest\.test\.js/,
];

describe('stale compatibility claims', () => {
    for (const file of DOCS) {
        it(`${file} omits stale OpenClaw compatibility claims`, () => {
            const content = fs.readFileSync(path.join(ROOT, file), 'utf8');
            for (const regex of BANNED) {
                assert.equal(regex.test(content), false, `${file} should not contain ${regex}`);
            }
        });
    }
});
