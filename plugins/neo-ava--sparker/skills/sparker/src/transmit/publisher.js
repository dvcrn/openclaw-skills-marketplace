// Ember publisher — converts RefinedSpark to Ember and publishes to SparkHub.
// Handles desensitization, owner confirmation, privacy levels, and retry queue.
//
// Publish state machine:
//   candidate → pending_remote (local saved, remote not confirmed)
//             → synced         (remote confirmed)
//             → sync_failed    (remote rejected, no retry)

const { STP_SCHEMA_VERSION, computeAssetId, generateId, getNodeId } = require('../core/asset-id');
const { createCredibility } = require('../core/credibility');
const { appendEmber, updateEmber, readEmbers, readRefinedSparks, updateRefinedSpark, resolvePath, readJson, writeJson, ensureDir } = require('../core/storage');
const { sanitizeForPublishing, checkContentSafety } = require('./sanitizer');
const { buildPublishMessage, sendToHub } = require('./hub-client');
const { getAgentName, getBindingKey } = require('./auth');
const path = require('path');

// Convert RefinedSpark to Ember (desensitized publishing form)
function createEmber(refinedSpark, opts) {
  var o = opts || {};
  var sanitized = sanitizeForPublishing(refinedSpark);

  // Content safety check
  var safetyCheck = checkContentSafety(sanitized.summary + ' ' + JSON.stringify(sanitized.insight));
  if (!safetyCheck.safe) {
    return { error: 'content_safety_failed', issues: safetyCheck.issues };
  }

  var now = new Date().toISOString();
  var ember = {
    type: 'Ember',
    schema_version: STP_SCHEMA_VERSION,
    id: generateId('ember'),
    source_refined_id: refinedSpark.id,
    domain: refinedSpark.domain,

    // ── Core Layer: six dimensions (sanitized) ──
    knowledge_type: sanitized.knowledge_type || refinedSpark.knowledge_type || 'rule',
    when: sanitized.when || refinedSpark.when || { trigger: '', conditions: [] },
    where: sanitized.where || refinedSpark.where || { domain: '', sub_domain: '', scenario: '', audience: '' },
    why: sanitized.why || refinedSpark.why || '',
    how: sanitized.how || refinedSpark.how || { summary: '', detail: '' },
    result: {
      expected_outcome: (sanitized.result || refinedSpark.result || {}).expected_outcome || '',
      practice_count: (refinedSpark.result || {}).practice_count || 0,
      success_rate: (refinedSpark.result || {}).success_rate || null,
      feedback_log: [],
    },
    not: sanitized.not || refinedSpark.not || [],

    // ── Compatibility Layer ──
    summary: sanitized.summary || (refinedSpark.when && refinedSpark.when.trigger
      ? refinedSpark.when.trigger + ' → ' + (refinedSpark.how || {}).summary
      : refinedSpark.summary || ''),
    insight: sanitized.insight,
    applicable_when: sanitized.applicable_when || refinedSpark.applicable_when || [],
    not_applicable_when: sanitized.not_applicable_when || refinedSpark.not_applicable_when || [],
    keywords: extractKeywords(refinedSpark),
    task_type: refinedSpark.task_type
      || (refinedSpark.card && refinedSpark.card.context_envelope ? refinedSpark.card.context_envelope.sub_domain : null)
      || null,
    contributor_chain: sanitized.contributor_chain || [],
    credibility: {
      internal: refinedSpark.credibility ? refinedSpark.credibility.internal : createCredibility().internal,
      external: createCredibility().external,
      composite: refinedSpark.credibility ? refinedSpark.credibility.composite : 0.5,
      trend: 'stable',
    },
    origin: {
      node_id: getNodeId(),
      agent_name: getAgentName(),
      bound: !!getBindingKey(),
    },
    pricing: o.pricing || { model: 'free', price: 0, currency: 'USD' },
    license: o.license || 'open',
    relations: refinedSpark.relations || [],
    citation_count: 0,
    upvotes: 0,
    downvotes: 0,
    status: 'candidate',
    published_at: now,
    valid_until: refinedSpark.valid_until || null,
    freshness_half_life_days: refinedSpark.freshness_half_life_days || 90,
    forge_eligible: false,
    asset_id: null,
  };

  ember.asset_id = computeAssetId(ember);
  return ember;
}

function extractKeywords(spark) {
  var keywords = [];
  if (spark.domain) keywords.push(spark.domain);
  if (Array.isArray(spark.tags)) keywords.push(...spark.tags);

  // Extract from six-dimension fields
  var textParts = [];
  if (spark.when && spark.when.trigger) textParts.push(spark.when.trigger);
  if (spark.where && spark.where.scenario) textParts.push(spark.where.scenario);
  if (spark.how && spark.how.summary) textParts.push(spark.how.summary);
  if (spark.why) textParts.push(spark.why);
  // Fallback to legacy fields
  if (spark.summary) textParts.push(spark.summary);
  if (spark.insight && spark.insight.rules) textParts.push(spark.insight.rules.join(' '));

  var text = textParts.join(' ');
  var words = text.split(/\s+/).filter(w => w.length >= 2);
  var seen = new Set(keywords);
  for (var i = 0; i < words.length && keywords.length < 10; i++) {
    if (!seen.has(words[i])) { keywords.push(words[i]); seen.add(words[i]); }
  }
  return keywords.slice(0, 15);
}

// --- Retry queue for failed remote operations ---

var RETRY_QUEUE_PATH = function () { return resolvePath('retry_queue.json'); };
var MAX_RETRIES = 3;

function readRetryQueue() {
  return readJson(RETRY_QUEUE_PATH(), []);
}

function writeRetryQueue(queue) {
  writeJson(RETRY_QUEUE_PATH(), queue);
}

function enqueueRetry(entry) {
  var queue = readRetryQueue();
  queue.push(Object.assign({
    retries: 0,
    max_retries: MAX_RETRIES,
    created_at: new Date().toISOString(),
    last_attempt: new Date().toISOString(),
  }, entry));
  writeRetryQueue(queue);
}

// Publish a RefinedSpark as Ember with state machine tracking
async function publishEmber(refinedSparkId, opts) {
  var o = opts || {};
  var refined = readRefinedSparks().find(s => s.id === refinedSparkId);
  if (!refined) return { ok: false, error: 'refined_spark_not_found' };

  var visibility = o.visibility || refined.visibility || 'public';
  if (visibility === 'private') visibility = 'public';

  var ember = createEmber(refined, o);
  if (ember.error) return { ok: false, error: ember.error, issues: ember.issues };

  // Store locally with pending_remote status (not yet confirmed by hub)
  ember.status = 'pending_remote';
  appendEmber(ember);

  // Do NOT mark refined as 'published' until hub confirms
  updateRefinedSpark(refinedSparkId, { status: 'publishing' });

  var transport = { ok: true, skipped: false };
  if (visibility !== 'private') {
    var publishOpts = { action: 'create' };
    if (o.category_id) publishOpts.category_id = o.category_id;
    if (o.category_path) publishOpts.category_path = o.category_path;
    var message = buildPublishMessage(ember, publishOpts);
    transport = await sendToHub(message);

    if (transport.ok) {
      updateEmber(ember.id, { status: 'synced', synced_at: new Date().toISOString() });
      updateRefinedSpark(refinedSparkId, { status: 'published' });
    } else {
      // Remote failed — keep ember as pending_remote and enqueue for retry
      process.stderr.write('[sparker] Hub publish failed for ' + ember.id + ': ' + (transport.error || 'unknown') + '. Queued for retry.\n');
      enqueueRetry({
        type: 'publish',
        ember_id: ember.id,
        refined_spark_id: refinedSparkId,
        publish_opts: publishOpts,
        error: transport.error || 'unknown',
      });
    }
  } else {
    updateEmber(ember.id, { status: 'synced' });
    updateRefinedSpark(refinedSparkId, { status: 'published' });
  }

  return {
    ok: true,
    ember: ember,
    transport: transport,
    visibility: visibility,
    remote_status: transport.ok ? 'synced' : 'pending_remote',
  };
}

// Process retry queue — called by `node index.js retry`
async function processRetryQueue() {
  var queue = readRetryQueue();
  if (queue.length === 0) return { ok: true, processed: 0, remaining: 0 };

  var remaining = [];
  var processed = 0;
  var succeeded = 0;

  for (var i = 0; i < queue.length; i++) {
    var entry = queue[i];
    if (entry.retries >= (entry.max_retries || MAX_RETRIES)) {
      // Exceeded max retries — mark as sync_failed
      if (entry.type === 'publish' && entry.ember_id) {
        updateEmber(entry.ember_id, { status: 'sync_failed' });
        if (entry.refined_spark_id) {
          updateRefinedSpark(entry.refined_spark_id, { status: 'publish_failed' });
        }
      }
      processed++;
      continue;
    }

    var success = false;
    if (entry.type === 'publish') {
      success = await retryPublish(entry);
    } else if (entry.type === 'vote') {
      success = await retryVote(entry);
    }

    if (success) {
      processed++;
      succeeded++;
    } else {
      entry.retries++;
      entry.last_attempt = new Date().toISOString();
      remaining.push(entry);
      processed++;
    }
  }

  writeRetryQueue(remaining);
  return { ok: true, processed: processed, succeeded: succeeded, remaining: remaining.length };
}

async function retryPublish(entry) {
  var embers = readEmbers();
  var ember = embers.find(function (e) { return e.id === entry.ember_id; });
  if (!ember) return true; // ember gone, nothing to retry

  var message = buildPublishMessage(ember, entry.publish_opts || {});
  var transport = await sendToHub(message);
  if (transport.ok) {
    updateEmber(ember.id, { status: 'synced', synced_at: new Date().toISOString() });
    if (entry.refined_spark_id) {
      updateRefinedSpark(entry.refined_spark_id, { status: 'published' });
    }
    return true;
  }
  return false;
}

async function retryVote(entry) {
  var { hubVote } = require('./hub-client');
  try {
    var result = await hubVote(entry.spark_id, entry.vote_type, { reason: entry.reason });
    return result && result.ok;
  } catch (e) { return false; }
}

module.exports = {
  createEmber,
  publishEmber,
  extractKeywords,
  processRetryQueue,
  readRetryQueue,
  enqueueRetry,
};
