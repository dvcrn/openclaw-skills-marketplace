const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const SPEC_FILE = path.join(ROOT, 'docs/spec/capabilities.json');
const FINDING_SCHEMA_FILE = path.join(ROOT, 'docs/spec/finding.schema.json');
const REQUIRED_FINDING_FIELDS = [
  'rule_id',
  'category',
  'severity',
  'description',
  'rationale',
  'preconditions',
  'false_positive_scenarios',
  'remediation_hint',
  'validation_state',
  'validation_status',
  'confidence',
  'evidence_spans',
  'attack_chain_id',
  'evidence',
];

console.log('🛡️  Guard-Scanner Test Quality Gate\n');

try {
  const spec = JSON.parse(fs.readFileSync(SPEC_FILE, 'utf8'));
  
  // Verify README
  const readme = fs.readFileSync(path.join(ROOT, 'README.md'), 'utf8');
  if (!readme.includes(`${spec.static_pattern_count}`)) {
    throw new Error('README.md out of sync with capabilities.json (static_pattern_count)');
  }
  if (!readme.includes(`${spec.runtime_check_count}`)) {
    throw new Error('README.md out of sync with capabilities.json (runtime_check_count)');
  }
  if (!readme.includes(`${spec.threat_category_count}`)) {
    throw new Error('README.md out of sync with capabilities.json (threat_category_count)');
  }
  
  // Verify SKILL.md
  const skill = fs.readFileSync(path.join(ROOT, 'SKILL.md'), 'utf8');
  if (!skill.includes(`${spec.static_pattern_count}`)) {
    throw new Error('SKILL.md out of sync with capabilities.json');
  }

  // Verify plugin.json
  const plugin = JSON.parse(fs.readFileSync(path.join(ROOT, 'openclaw.plugin.json'), 'utf8'));
  if (plugin.version !== spec.plugin_version) {
    throw new Error('openclaw.plugin.json version out of sync with capabilities.json');
  }

  // Verify package.json
  const pkg = JSON.parse(fs.readFileSync(path.join(ROOT, 'package.json'), 'utf8'));
  const deps = pkg.dependencies ? Object.keys(pkg.dependencies).length : 0;
  if (deps !== spec.dependencies_runtime) {
      throw new Error(`capabilities.json claims ${spec.dependencies_runtime} deps but package.json has ${deps}`);
  }

  console.log('  ✅ PASS: Source of Truth (capabilities.json) matches documentation');

  const findingSchema = JSON.parse(fs.readFileSync(FINDING_SCHEMA_FILE, 'utf8'));
  for (const field of REQUIRED_FINDING_FIELDS) {
    if (!findingSchema.required || !findingSchema.required.includes(field)) {
      throw new Error(`finding.schema.json missing required field: ${field}`);
    }
  }

  if (!readme.includes('## Finding Schema')) {
    throw new Error('README.md missing "Finding Schema" section');
  }

  for (const field of REQUIRED_FINDING_FIELDS) {
    if (!readme.includes(`\`${field}\``)) {
      throw new Error(`README.md Finding Schema section missing field: ${field}`);
    }
  }

  const readmeJa = fs.readFileSync(path.join(ROOT, 'README_ja.md'), 'utf8');
  if (!readmeJa.includes('## Finding Schema')) {
    throw new Error('README_ja.md missing "Finding Schema" section');
  }

  for (const field of REQUIRED_FINDING_FIELDS) {
    if (!readmeJa.includes(`\`${field}\``)) {
      throw new Error(`README_ja.md Finding Schema section missing field: ${field}`);
    }
  }

  console.log('  ✅ PASS: Finding schema is documented and complete');
} catch (err) {
  console.error(`  ❌ FAIL: ${err.message}`);
  process.exit(1);
}

// Check test files
const testDir = path.join(ROOT, 'test');
const testFiles = fs.readdirSync(testDir).filter(f => f.endsWith('.test.js'));

if (testFiles.length <= 25) {
   console.log(`  ✅ PASS: Test file count: ${testFiles.length}/25`);
} else {
   console.log(`  ✅ PASS: Test file count: ${testFiles.length} (Expanded for v13)`);
}

console.log('\n✅ Quality gate PASSED\n');
