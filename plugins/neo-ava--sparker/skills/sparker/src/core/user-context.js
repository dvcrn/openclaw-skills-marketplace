// User Context Adapter — reads OpenClaw's memory system to enrich sparks
// with ANONYMOUS professional context only.
//
// Purpose: make sparks carry "what kind of expert, in what conditions,
// made what decision" — NOT "who made it".
//
// Extracts: role, industry, experience level, expertise, work style
// Never extracts: name, company, phone, email, location, or any PII

var fs = require('fs');
var path = require('path');

var CACHE_TTL_MS = Number(process.env.STP_USER_CONTEXT_CACHE_MS || 10 * 60 * 1000);
var _cache = null;
var _cacheTime = 0;

function getWorkspaceDir() {
  return process.env.OPENCLAW_WORKSPACE || process.cwd();
}

function tryRead(filePath) {
  try {
    if (fs.existsSync(filePath)) return fs.readFileSync(filePath, 'utf8');
  } catch (e) { /* best effort */ }
  return '';
}

function walkMdFiles(dir) {
  var results = [];
  try {
    if (!fs.existsSync(dir)) return results;
    var entries = fs.readdirSync(dir, { withFileTypes: true });
    for (var i = 0; i < entries.length; i++) {
      var e = entries[i];
      var full = path.join(dir, e.name);
      if (e.isSymbolicLink && e.isSymbolicLink()) continue;
      if (e.isDirectory()) {
        results = results.concat(walkMdFiles(full));
      } else if (e.isFile() && e.name.endsWith('.md')) {
        results.push(full);
      }
    }
  } catch (e) { /* dir might not exist */ }
  return results;
}

function parseYamlFrontMatter(text) {
  if (!text || !text.startsWith('---')) return {};
  var end = text.indexOf('\n---', 3);
  if (end < 0) return {};
  var yaml = text.slice(4, end).trim();
  var obj = {};
  var lines = yaml.split('\n');
  for (var i = 0; i < lines.length; i++) {
    var m = lines[i].match(/^(\w[\w_]*)\s*:\s*(.+)$/);
    if (m) obj[m[1]] = m[2].trim().replace(/^["']|["']$/g, '');
  }
  return obj;
}

function extractFieldsFromText(text, fieldNames) {
  var found = {};
  if (!text) return found;
  for (var i = 0; i < fieldNames.length; i++) {
    var name = fieldNames[i];
    var patterns = [
      new RegExp('[#*]*\\s*' + name + '\\s*[:：]\\s*(.+)', 'i'),
      new RegExp(name + '\\s*[:：]\\s*(.+)', 'i'),
    ];
    for (var j = 0; j < patterns.length; j++) {
      var m = text.match(patterns[j]);
      if (m && m[1]) {
        found[name.toLowerCase().replace(/\s+/g, '_')] = m[1].trim();
        break;
      }
    }
  }
  return found;
}

// Only professional/contextual fields — no PII
var PROFILE_FIELDS = [
  'role', '角色', '职业', 'profession', 'occupation', 'job',
  'industry', '行业', '领域',
  'experience', '经验', '从业年限', 'years',
  'expertise', '专长', '擅长',
];

var STYLE_FIELDS = [
  'style', '风格', '偏好风格',
  'tone', '语气', '语调',
  'language', '语言',
  'communication', '沟通风格', '沟通方式',
  'values', '价值观',
];

function buildUserContext() {
  var ws = getWorkspaceDir();

  var memoryMd = tryRead(path.join(ws, 'MEMORY.md')) || tryRead(path.join(ws, 'memory.md'));
  var userMd = tryRead(path.join(ws, 'USER.md'));
  var profileMd = tryRead(path.join(ws, 'profile.md'));

  var factualDir = path.join(ws, 'memory', 'factual');
  var proceduralDir = path.join(ws, 'memory', 'procedural');
  var factualFiles = walkMdFiles(factualDir);
  var proceduralFiles = walkMdFiles(proceduralDir);

  var factualText = factualFiles.map(tryRead).join('\n');
  var proceduralText = proceduralFiles.map(tryRead).join('\n');
  var allText = [memoryMd, userMd, profileMd, factualText, proceduralText].join('\n');

  var frontMatter = parseYamlFrontMatter(profileMd) || {};
  var userFrontMatter = parseYamlFrontMatter(userMd) || {};

  var profile = extractFieldsFromText(allText, PROFILE_FIELDS);
  var workStyle = extractFieldsFromText(allText, STYLE_FIELDS);

  if (userFrontMatter.role && !profile.role) profile.role = userFrontMatter.role;
  if (userFrontMatter.industry && !profile.industry) profile.industry = userFrontMatter.industry;
  if (frontMatter.role && !profile.role) profile.role = frontMatter.role;
  if (userFrontMatter.system_prompt) {
    var sysFields = extractFieldsFromText(userFrontMatter.system_prompt, PROFILE_FIELDS);
    for (var k in sysFields) { if (!profile[k]) profile[k] = sysFields[k]; }
  }

  var ctx = {
    contributor_profile: Object.keys(profile).length > 0 ? profile : null,
    work_style: Object.keys(workStyle).length > 0 ? workStyle : null,
    memory_sources: [],
  };

  if (memoryMd) ctx.memory_sources.push('MEMORY.md');
  if (userMd) ctx.memory_sources.push('USER.md');
  if (profileMd) ctx.memory_sources.push('profile.md');
  if (factualFiles.length) ctx.memory_sources.push('memory/factual/ (' + factualFiles.length + ' files)');
  if (proceduralFiles.length) ctx.memory_sources.push('memory/procedural/ (' + proceduralFiles.length + ' files)');

  ctx._built_at = new Date().toISOString();
  return ctx;
}

function getUserContext() {
  var now = Date.now();
  if (_cache && (now - _cacheTime) < CACHE_TTL_MS) return _cache;
  _cache = buildUserContext();
  _cacheTime = now;
  return _cache;
}

function invalidateCache() {
  _cache = null;
  _cacheTime = 0;
}

module.exports = {
  getUserContext,
  invalidateCache,
  buildUserContext,
  getWorkspaceDir,
};
