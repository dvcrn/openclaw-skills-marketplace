// Preference Dimension Map — per-domain preference profiling.
// Aggregates preference signals from RawSparks (choices, diff mining,
// micro-probes, casual mining) into a structured preference profile.
// Stores in assets/stp/preference_maps/<domain>.json

var { readRawSparksWithSnapshot, readPracticeRecords, readJson, writeJson, resolvePath } = require('./storage');
var { resolveLLMConfig, callLLM } = require('./openclaw-config');

function getPreferenceMapPath(domain) {
  var safeName = String(domain || 'general').replace(/[^a-zA-Z0-9\u4e00-\u9fff._-]/g, '_');
  return resolvePath('preference_maps', safeName + '.json');
}

var UNIVERSAL_DIMENSIONS = [
  { name: 'detail_level', display_name: '详略程度', range: ['精简', '适中', '详尽'] },
  { name: 'tone', display_name: '语气风格', range: ['正式', '平衡', '随意'] },
  { name: 'structure', display_name: '结构偏好', range: ['模板化', '灵活', '创意'] },
  { name: 'risk_tolerance', display_name: '风险偏好', range: ['保守', '平衡', '激进'] },
];

function readPreferenceMap(domain) {
  var map = readJson(getPreferenceMapPath(domain), {
    domain: domain,
    dimensions: [],
    universal_dimensions: UNIVERSAL_DIMENSIONS,
    discovered_dimensions: [],
    last_updated: null,
    generated_from_sparks: [],
    human_confirmed: false,
    human_modifications: [],
  });
  if (!map.universal_dimensions) map.universal_dimensions = UNIVERSAL_DIMENSIONS;
  if (!map.discovered_dimensions) map.discovered_dimensions = [];
  return map;
}

function writePreferenceMap(domain, map) {
  map.last_updated = new Date().toISOString();
  writeJson(getPreferenceMapPath(domain), map);
}

function readAllPreferenceMaps() {
  var fs = require('fs');
  var dir = resolvePath('preference_maps');
  var maps = {};
  try {
    var files = fs.readdirSync(dir);
    for (var i = 0; i < files.length; i++) {
      if (files[i].endsWith('.json')) {
        var map = readJson(require('path').join(dir, files[i]), null);
        if (map && map.domain) maps[map.domain] = map;
      }
    }
  } catch (e) { /* dir may not exist */ }
  return maps;
}

// Check if profiling should be triggered for a domain
function shouldProfile(domain) {
  var sparks = readRawSparksWithSnapshot();
  var domainSparks = sparks.filter(function (s) {
    return s.domain === domain || (s.domain && s.domain.startsWith(domain + '.'));
  });

  if (domainSparks.length < 15) return false;

  var map = readPreferenceMap(domain);
  if (!map.last_updated) return true;

  var daysSince = (Date.now() - new Date(map.last_updated).getTime()) / (24 * 60 * 60 * 1000);
  return daysSince >= 7;
}

var PROFILE_PROMPT_TEMPLATE = [
  'You are an expert at analyzing user preference patterns from behavioral data.',
  'Below are knowledge signals captured from a user in the domain "{{domain}}".',
  'Each signal represents a choice, correction, or stated preference.',
  '',
  'Analyze these signals and output a JSON object with:',
  '  style_preferences: array of { dimension, preference, strength (0-1), evidence_count }',
  '  boundary_conditions: array of { rule, evidence_count }',
  '  anti_preferences: array of { dimension, dislike, strength (0-1) }',
  '',
  'For strength: 0.9+ = very consistent pattern, 0.5-0.8 = moderate pattern, <0.5 = weak/mixed signal',
  'Only include dimensions where you see a clear pattern (at least 3 signals).',
  'Return only JSON, no markdown fences.',
  '',
  '## Signals',
  '{{signals}}',
].join('\n');

function collectPreferenceSignals(domain) {
  var sparks = readRawSparksWithSnapshot();
  var preferenceSources = ['human_choice', 'human_feedback', 'post_task'];
  var preferenceMethodSources = ['diff_mining', 'micro_probe', 'comparative', 'feedback', 'casual_mining'];

  var signals = sparks.filter(function (s) {
    if (s.status === 'rejected') return false;
    var domainMatch = s.domain === domain || (s.domain && s.domain.startsWith(domain + '.'));
    if (!domainMatch) return false;
    var sourceMatch = preferenceSources.indexOf(s.source) >= 0;
    var methodMatch = preferenceMethodSources.indexOf(s.extraction_method) >= 0;
    return sourceMatch || methodMatch;
  });

  return signals;
}

async function generateProfile(domain) {
  var signals = collectPreferenceSignals(domain);
  if (signals.length < 5) {
    return { domain: domain, error: 'insufficient_signals', signal_count: signals.length };
  }

  var signalTexts = signals.slice(-50).map(function (s, i) {
    var line = (i + 1) + '. [' + s.source + '/' + (s.extraction_method || 'unknown') + '] ' + s.content;
    if (s.card && s.card.heuristic) line += ' → Rule: ' + s.card.heuristic;
    if (s.card && s.card.diff_detail) {
      line += ' (changed from "' + s.card.diff_detail.original_approach + '" to "' + s.card.diff_detail.modified_approach + '")';
    }
    return line;
  });

  var prompt = PROFILE_PROMPT_TEMPLATE
    .replace('{{domain}}', domain)
    .replace('{{signals}}', signalTexts.join('\n'));

  var llmConfig = resolveLLMConfig();
  var response = await callLLM(prompt, Object.assign({}, llmConfig, { max_tokens: 2000, temperature: 0.2 }));

  var profile = null;
  if (response) {
    var cleaned = response.trim();
    if (cleaned.startsWith('```')) {
      cleaned = cleaned.replace(/^```(?:json)?\n?/, '').replace(/\n?```$/, '');
    }
    try {
      profile = JSON.parse(cleaned);
    } catch (e) { /* parse failed */ }
  }

  if (!profile) {
    return mechanicalProfile(domain, signals);
  }

  var map = readPreferenceMap(domain);
  map.domain = domain;
  map.profile = profile;
  map.dimensions = (profile.style_preferences || []).map(function (p) { return p.dimension; });
  map.discovered_dimensions = discoverDimensions(domain);
  map.generated_from_sparks = signals.map(function (s) { return s.id; });
  map.signal_count = signals.length;
  map.human_confirmed = false;
  map.human_modifications = [];

  writePreferenceMap(domain, map);
  return map;
}

// Fallback profiling without LLM
function mechanicalProfile(domain, signals) {
  var tagCounts = {};
  for (var i = 0; i < signals.length; i++) {
    var tags = signals[i].tags || [];
    for (var t = 0; t < tags.length; t++) {
      tagCounts[tags[t]] = (tagCounts[tags[t]] || 0) + 1;
    }
  }

  var dimensions = Object.keys(tagCounts)
    .filter(function (k) { return tagCounts[k] >= 3; })
    .sort(function (a, b) { return tagCounts[b] - tagCounts[a]; })
    .slice(0, 10)
    .map(function (k) {
      return { dimension: k, signal_count: tagCounts[k], preference: 'see signals for details', strength: Math.min(1.0, tagCounts[k] / 20) };
    });

  var map = readPreferenceMap(domain);
  map.domain = domain;
  map.profile = { style_preferences: dimensions, boundary_conditions: [], anti_preferences: [] };
  map.dimensions = dimensions.map(function (d) { return d.dimension; });
  map.discovered_dimensions = discoverDimensions(domain);
  map.generated_from_sparks = signals.map(function (s) { return s.id; });
  map.signal_count = signals.length;
  map.human_confirmed = false;
  map.generation_method = 'mechanical';

  writePreferenceMap(domain, map);
  return map;
}

// Auto-discover domain-specific preference dimensions from accumulated sparks.
// If >= 3 sparks carry the same preference_dimension tag, promote it.
function discoverDimensions(domain) {
  var sparks = readRawSparksWithSnapshot();
  var dimCounts = {};
  var universalNames = UNIVERSAL_DIMENSIONS.map(function (d) { return d.name; });

  for (var i = 0; i < sparks.length; i++) {
    var s = sparks[i];
    if (s.status === 'rejected') continue;
    var domainMatch = s.domain === domain || (s.domain && s.domain.startsWith(domain + '.'));
    if (!domainMatch) continue;

    var dims = (s.card && s.card.preference_dimensions) || s.tags || [];
    for (var j = 0; j < dims.length; j++) {
      var d = String(dims[j] || '').trim();
      if (!d || universalNames.indexOf(d) >= 0) continue;
      dimCounts[d] = (dimCounts[d] || 0) + 1;
    }
  }

  var discovered = [];
  for (var name in dimCounts) {
    if (dimCounts[name] >= 3) {
      discovered.push({ name: name, display_name: name, signal_count: dimCounts[name] });
    }
  }

  discovered.sort(function (a, b) { return b.signal_count - a.signal_count; });
  return discovered.slice(0, 20);
}

// Confirm profile with user modifications
function confirmProfile(domain, modifications) {
  var map = readPreferenceMap(domain);
  map.human_confirmed = true;
  if (modifications) {
    map.human_modifications.push({
      timestamp: new Date().toISOString(),
      modifications: modifications,
    });
  }
  writePreferenceMap(domain, map);
  return map;
}

// Detect whether a domain is "creative" (preference/pattern-heavy) or "standard"
// (rule-heavy). Returns 'creative' or 'standard'.
function detectTaskMode(domain) {
  var sparks = readRawSparksWithSnapshot();
  var domainSparks = sparks.filter(function (s) {
    return (s.domain === domain || (s.domain && s.domain.startsWith(domain + '.'))) &&
           s.status !== 'rejected' && s.card;
  });
  if (domainSparks.length < 5) return 'standard'; // not enough data, default safe

  var prefCount = 0;
  for (var i = 0; i < domainSparks.length; i++) {
    var ht = domainSparks[i].card.heuristic_type;
    if (ht === 'preference' || ht === 'pattern') prefCount++;
  }
  return (prefCount / domainSparks.length) > 0.5 ? 'creative' : 'standard';
}

// Generate a natural-language persona description from the preference map.
// Pre-generated during Digest and cached; Agent reads it directly, zero LLM cost.
function generatePersonaText(domain) {
  var map = readPreferenceMap(domain);
  var prefs = (map.profile && map.profile.style_preferences) || [];
  var antiPrefs = (map.profile && map.profile.anti_preferences) || [];
  if (prefs.length === 0 && antiPrefs.length === 0) return null;

  var lines = [];
  lines.push('该用户在「' + domain + '」领域的偏好画像：');

  var strong = prefs.filter(function (p) { return (p.strength || 0) >= 0.6; });
  var moderate = prefs.filter(function (p) { return (p.strength || 0) >= 0.3 && (p.strength || 0) < 0.6; });

  if (strong.length > 0) {
    lines.push('强偏好：' + strong.map(function (p) {
      return p.dimension + '偏好' + p.preference;
    }).join('、') + '。');
  }
  if (moderate.length > 0) {
    lines.push('中等偏好：' + moderate.map(function (p) {
      return p.dimension + '偏好' + p.preference;
    }).join('、') + '。');
  }
  if (antiPrefs.length > 0) {
    lines.push('明确反感：' + antiPrefs.map(function (a) {
      return a.dimension + '方面不喜欢' + a.dislike;
    }).join('、') + '。');
  }

  var boundaries = (map.profile && map.profile.boundary_conditions) || [];
  if (boundaries.length > 0) {
    lines.push('注意事项：' + boundaries.slice(0, 3).map(function (b) {
      return b.rule || b.condition || b;
    }).join('；') + '。');
  }

  var text = lines.join('\n');

  // Cache persona text in the map
  map.persona_text = text;
  map.persona_generated_at = new Date().toISOString();
  map.task_mode = detectTaskMode(domain);
  writePreferenceMap(domain, map);

  return text;
}

module.exports = {
  readPreferenceMap,
  writePreferenceMap,
  readAllPreferenceMaps,
  shouldProfile,
  generateProfile,
  confirmProfile,
  collectPreferenceSignals,
  discoverDimensions,
  detectTaskMode,
  generatePersonaText,
  getPreferenceMapPath,
  UNIVERSAL_DIMENSIONS,
};
