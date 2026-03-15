const fs = require('fs');
const path = require('path');
const { PATTERNS } = require('../src/patterns.js');
const { RUNTIME_CHECKS } = require('../src/runtime-guard.js');
const { TOOLS } = require('../src/mcp-server.js');
const packageJson = require('../package.json');
const pluginJson = require('../openclaw.plugin.json');

const specDir = path.join(__dirname, '../docs/spec');
const capabilitiesPath = path.join(specDir, 'capabilities.json');
const testDir = path.join(__dirname, '../test');

if (!fs.existsSync(specDir)) {
    fs.mkdirSync(specDir, { recursive: true });
}

// Calculate true values from source code — single source of truth
const categories = new Set(PATTERNS.map(p => p.cat));
const testFiles = fs.readdirSync(testDir).filter(f => f.endsWith('.test.js'));

const spec = {
    package_version: packageJson.version,
    plugin_version: pluginJson.version,
    static_pattern_count: PATTERNS.length,
    threat_category_count: categories.size,
    runtime_check_count: RUNTIME_CHECKS.length,
    test_file_count: testFiles.length,
    dependencies_runtime: Object.keys(packageJson.dependencies || {}).length,
    dependencies_dev: Object.keys(packageJson.devDependencies || {}).length,
    mcp_tools: TOOLS.map(t => t.name),
    cli_commands: ["scan", "serve", "watch", "audit", "crawl", "patrol"],
    supported_outputs: ["json", "sarif", "html", "terminal"],
    supported_integrations: ["openclaw", "mcp", "virustotal", "github", "npm"]
};

fs.writeFileSync(capabilitiesPath, JSON.stringify(spec, null, 2));
console.log(`✅ Generated SSoT at ${capabilitiesPath}`);
console.log(JSON.stringify(spec, null, 2));
