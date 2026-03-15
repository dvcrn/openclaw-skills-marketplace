// Migration tool — converts learner (LKP) and spark-protocol data to STP format.

const fs = require('fs');
const path = require('path');
const { STP_SCHEMA_VERSION, computeAssetId, generateId } = require('../core/asset-id');
const { getInitialConfidence, createCredibility } = require('../core/credibility');
const { appendRawSpark, appendEmber, getStpAssetsDir, ensureDir } = require('../core/storage');

// Migrate learner Notes -> STP RawSparks
function migrateNotes(notesPath) {
  if (!fs.existsSync(notesPath)) return { migrated: 0, error: 'file not found: ' + notesPath };

  var raw = fs.readFileSync(notesPath, 'utf8');
  var lines = raw.split('\n').filter(Boolean);
  var migrated = 0;

  for (var i = 0; i < lines.length; i++) {
    try {
      var note = JSON.parse(lines[i]);
      var spark = {
        type: 'RawSpark',
        schema_version: STP_SCHEMA_VERSION,
        id: generateId('raw_migrated'),
        source: mapNoteSource(note.source),
        trigger: note.trigger || 'migrated_from_learner',
        content: note.content || '',
        domain: note.domain || 'general',
        tags: note.tags || [],
        contributor: { type: 'human', id: 'owner', domain_expertise: 0.5 },
        context: { task_type: null, scenario: '' },
        confidence: note.confidence || 0.3,
        visibility: 'private',
        related_task: note.related_task || null,
        related_session: note.related_session || null,
        extraction_method: mapNoteSource(note.source) === 'human_teaching' ? 'teaching' : 'observation',
        confirmation_status: note.status === 'active' ? 'agent_confirmed' : 'unconfirmed',
        practice_count: note.practice_count || 0,
        success_count: note.success_count || 0,
        status: note.status || 'active',
        created_at: note.created_at || new Date().toISOString(),
        valid_until: null,
        freshness_half_life_days: 60,
        asset_id: null,
      };
      spark.asset_id = computeAssetId(spark);
      appendRawSpark(spark);
      migrated++;
    } catch (e) { /* skip malformed */ }
  }

  return { migrated: migrated, source: notesPath };
}

function mapNoteSource(source) {
  var map = {
    user_teaching: 'human_teaching',
    user_feedback: 'human_feedback',
    rl_inference: 'human_choice',
    web_search: 'web_exploration',
    self_diagnosis: 'self_diagnosis',
    agent_exchange: 'agent_exchange',
    post_task: 'post_task',
  };
  return map[source] || 'post_task';
}

// Migrate spark-protocol Sparks -> STP Embers
function migrateSparks(sparksPath) {
  if (!fs.existsSync(sparksPath)) return { migrated: 0, error: 'file not found: ' + sparksPath };

  var data;
  try {
    data = JSON.parse(fs.readFileSync(sparksPath, 'utf8'));
  } catch (e) {
    return { migrated: 0, error: 'parse error: ' + e.message };
  }

  var sparks = Array.isArray(data.sparks) ? data.sparks : [];
  var migrated = 0;

  for (var i = 0; i < sparks.length; i++) {
    var s = sparks[i];
    var cred = s.credibility || {};

    var ember = {
      type: 'Ember',
      schema_version: STP_SCHEMA_VERSION,
      id: generateId('ember_migrated'),
      source_refined_id: null,
      domain: s.domain || 'general',
      summary: (s.insight && s.insight.summary) || '',
      insight: s.insight || {},
      applicable_when: [],
      not_applicable_when: (s.context && s.context.not_applicable_when) || [],
      keywords: s.tfidf_keywords || [],
      task_type: (s.context && s.context.task_type) || null,
      contributor_chain: [{ type: 'agent', id: (s.origin && s.origin.node_id) || 'unknown', contributions: 1, weight: 1.0 }],
      credibility: {
        internal: {
          score: cred.score || 0.5,
          practice_count: cred.citations || 0,
          success_count: cred.upvotes || 0,
          human_confirmations: 0,
          last_validated_at: null,
        },
        external: {
          score: cred.score || 0.5,
          citations: cred.citations || 0,
          upvotes: cred.upvotes || 0,
          downvotes: cred.downvotes || 0,
          weighted_upvotes: cred.upvotes || 0,
          weighted_downvotes: cred.downvotes || 0,
          unique_agents: 0,
          unique_domains: 0,
        },
        composite: cred.score || 0.5,
        trend: 'stable',
      },
      pricing: { model: 'free', price: 0, currency: 'USD', trial_uses: 3 },
      license: 'open',
      relations: [],
      citation_count: cred.citations || 0,
      upvotes: cred.upvotes || 0,
      downvotes: cred.downvotes || 0,
      status: 'candidate',
      published_at: (s.origin && s.origin.created_at) || new Date().toISOString(),
      valid_until: (s.context && s.context.valid_until) || null,
      freshness_half_life_days: (s.context && s.context.freshness_half_life) || 90,
      forge_eligible: false,
      asset_id: null,
    };
    ember.asset_id = computeAssetId(ember);
    appendEmber(ember);
    migrated++;
  }

  return { migrated: migrated, source: sparksPath };
}

// Auto-detect and migrate all existing data
function migrateAll() {
  var results = { notes: null, sparks: null };
  var cwd = process.cwd();

  // Look for learner notes
  var notesPaths = [
    path.join(cwd, 'assets/lkp/notes.jsonl'),
    path.join(cwd, 'skills/learner/assets/lkp/notes.jsonl'),
  ];
  for (var i = 0; i < notesPaths.length; i++) {
    if (fs.existsSync(notesPaths[i])) {
      results.notes = migrateNotes(notesPaths[i]);
      break;
    }
  }

  // Look for spark-protocol sparks
  var sparksPaths = [
    path.join(cwd, 'assets/sparks/sparks.json'),
    path.join(cwd, 'skills/spark-protocol/assets/sparks/sparks.json'),
  ];
  for (var j = 0; j < sparksPaths.length; j++) {
    if (fs.existsSync(sparksPaths[j])) {
      results.sparks = migrateSparks(sparksPaths[j]);
      break;
    }
  }

  return results;
}

// ── V2 Migration: add six-dimension fields to existing sparks ──

var KNOWLEDGE_TYPE_MAP = {
  rule: 'rule',
  preference: 'preference',
  pattern: 'pattern',
  lesson: 'lesson',
  boundary: 'rule',
  methodology: 'methodology',
};

var EFFECT_MAP = {
  do_not_apply: 'skip',
  skip: 'skip',
  modify: 'modify',
  warn: 'warn',
  apply: 'skip',
  best_practice: 'skip',
  recommended: 'skip',
};

function migrateSparkToV2(spark) {
  if (spark.schema_version === '2.0.0') return spark;

  var card = spark.card || {};
  var ce = card.context_envelope || {};
  var domainStr = spark.domain || 'general';
  var domainParts = domainStr.split('.');

  // WHEN
  spark.when = {
    trigger: spark.trigger || card.heuristic || (spark.content || '').slice(0, 100) || '',
    conditions: extractConditionsFromExtra(ce.extra),
  };

  // WHERE
  spark.where = {
    domain: ce.domain || domainParts[0] || '',
    sub_domain: ce.sub_domain || domainParts.slice(1).join('.') || '',
    scenario: flattenExtra(ce.extra),
    audience: ce.audience_type || '',
  };

  // WHY — old data doesn't have it
  spark.why = spark.why || '';

  // HOW
  spark.how = {
    summary: card.heuristic || '',
    detail: spark.content || '',
  };

  // RESULT
  spark.result = {
    expected_outcome: '',
    feedback_log: [],
  };

  // NOT
  var boundaries = card.boundary_conditions || [];
  spark.not = boundaries.map(function(b) {
    if (typeof b === 'string') return { condition: b, effect: 'skip', reason: '' };
    return {
      condition: b.condition || '',
      effect: EFFECT_MAP[b.effect] || 'skip',
      reason: b.reason || '',
    };
  });

  // knowledge_type
  spark.knowledge_type = KNOWLEDGE_TYPE_MAP[card.heuristic_type] || 'rule';

  spark.schema_version = '2.0.0';
  return spark;
}

function extractConditionsFromExtra(extra) {
  if (!extra || typeof extra !== 'object') return [];
  var conditions = [];
  for (var k in extra) {
    var val = extra[k];
    if (typeof val === 'string' && val.length > 0 && val.length < 60) {
      conditions.push(val);
    } else if (Array.isArray(val)) {
      for (var i = 0; i < val.length; i++) {
        if (typeof val[i] === 'string' && val[i].length < 60) conditions.push(val[i]);
      }
    }
  }
  return conditions;
}

function flattenExtra(extra) {
  if (!extra || typeof extra !== 'object') return '';
  var parts = [];
  for (var k in extra) {
    var val = extra[k];
    if (typeof val === 'string' && val.length > 0) {
      parts.push(val);
    } else if (Array.isArray(val)) {
      parts.push(val.join('、'));
    }
  }
  return parts.join('；');
}

// Batch migrate all raw sparks in the JSONL file
function migrateAllToV2() {
  var stpDir = getStpAssetsDir();
  var rawPath = path.join(stpDir, 'raw_sparks', 'raw_sparks.jsonl');
  if (!fs.existsSync(rawPath)) return { migrated: 0, total: 0, error: 'no raw sparks file' };

  var raw = fs.readFileSync(rawPath, 'utf8');
  var lines = raw.split('\n').filter(Boolean);
  var migrated = 0;
  var total = lines.length;
  var outputLines = [];

  for (var i = 0; i < lines.length; i++) {
    try {
      var spark = JSON.parse(lines[i]);
      if (spark.schema_version !== '2.0.0') {
        spark = migrateSparkToV2(spark);
        migrated++;
      }
      outputLines.push(JSON.stringify(spark));
    } catch (e) {
      outputLines.push(lines[i]);
    }
  }

  fs.writeFileSync(rawPath, outputLines.join('\n') + '\n');

  // Also migrate snapshot if it exists
  var snapshotPath = path.join(stpDir, 'raw_sparks', 'raw_sparks_snapshot.json');
  if (fs.existsSync(snapshotPath)) {
    try {
      var snapshot = JSON.parse(fs.readFileSync(snapshotPath, 'utf8'));
      if (Array.isArray(snapshot)) {
        snapshot = snapshot.map(migrateSparkToV2);
        fs.writeFileSync(snapshotPath, JSON.stringify(snapshot, null, 2));
      }
    } catch (e) { /* skip */ }
  }

  return { migrated: migrated, total: total };
}

module.exports = { migrateNotes, migrateSparks, migrateAll, migrateSparkToV2, migrateAllToV2 };
