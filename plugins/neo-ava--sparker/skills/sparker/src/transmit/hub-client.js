// SparkHub HTTP/file client — handles STP-A2A message transport.
// Sends binding key on all HTTP requests for user identity resolution.

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { STP_SCHEMA_VERSION, getNodeId } = require('../core/asset-id');
const { getStpAssetsDir, ensureDir } = require('../core/storage');
const { getBindingKey, getHubUrl, getAgentName } = require('./auth');

const PROTOCOL_NAME = 'stp-a2a';
const PROTOCOL_VERSION = '1.0.0';

function generateMessageId() {
  return 'msg_' + Date.now() + '_' + crypto.randomBytes(4).toString('hex');
}

function buildMessage(params) {
  return {
    protocol: PROTOCOL_NAME,
    protocol_version: PROTOCOL_VERSION,
    schema_version: STP_SCHEMA_VERSION,
    message_type: params.messageType,
    message_id: generateMessageId(),
    sender_id: params.senderId || getNodeId(),
    agent_name: params.agentName || getAgentName(),
    timestamp: new Date().toISOString(),
    payload: params.payload || {},
  };
}

// Normalize server response — handles both {payload: {...}} and flat response formats
function unwrapResponse(httpResult) {
  if (!httpResult || !httpResult.ok) return httpResult;
  var data = httpResult.response || {};
  if (data.payload && typeof data.payload === 'object') {
    return Object.assign({}, httpResult, { response: data.payload });
  }
  return httpResult;
}

function buildPublishMessage(ember, opts) {
  var o = opts || {};
  var payload = { spark: ember, action: o.action || 'create' };
  if (o.category_id) payload.category_id = o.category_id;
  if (o.category_path) payload.category_path = o.category_path;
  return buildMessage({
    messageType: 'spark_publish',
    payload: payload,
  });
}

function buildSearchMessage(query, opts) {
  var o = opts || {};
  return buildMessage({
    messageType: 'spark_search',
    payload: {
      query_text: query,
      domain: o.domain || null,
      threshold: typeof o.threshold === 'number' ? o.threshold : 0.25,
      top_k: typeof o.topK === 'number' ? o.topK : 20,
    },
  });
}

function buildFeedbackMessage(emberId, feedbackType, opts) {
  var o = opts || {};
  var voteTypeMap = { upvote: 'upvote', downvote: 'downvote', positive: 'upvote', negative: 'downvote', cite: 'cite' };
  return buildMessage({
    messageType: 'spark_feedback',
    payload: {
      spark_id: emberId,
      vote_type: voteTypeMap[feedbackType] || feedbackType,
      reason: o.reason || null,
      context: o.context || null,
      voter_reputation: o.voterReputation || 1.0,
    },
  });
}

function buildForgeRequestMessage(emberId) {
  return buildMessage({
    messageType: 'spark_forge_request',
    payload: { ember_id: emberId },
  });
}

function buildRelateMessage(sourceId, targetId, relationType, opts) {
  var o = opts || {};
  return buildMessage({
    messageType: 'spark_relate',
    payload: {
      source_id: sourceId,
      target_id: targetId,
      relation_type: relationType,
      evidence: o.evidence || null,
    },
  });
}

function buildSyncMessage(opts) {
  var o = opts || {};
  return buildMessage({
    messageType: 'spark_sync',
    payload: {
      since: o.since || null,
      domain: o.domain || null,
      limit: o.limit || 100,
    },
  });
}

// --- HTTP transport ---

function buildHttpHeaders() {
  var headers = { 'Content-Type': 'application/json' };
  var bindingKey = getBindingKey();
  if (bindingKey) {
    headers['X-Sparkland-Binding-Key'] = bindingKey;
  }
  var nodeId = getNodeId();
  if (nodeId) {
    headers['X-Node-Id'] = nodeId;
  }
  return headers;
}

var TYPE_TO_ENDPOINT = {
  spark_publish: '/spark/spark_publish',
  spark_search: '/spark/spark_search',
  spark_feedback: '/spark/spark_vote',
  spark_fetch: '/spark/spark_fetch',
  spark_forge_request: '/spark/spark_fetch',
  spark_relate: '/spark/spark_relate',
  spark_sync: '/spark/spark_sync',
  spark_domain: '/spark/spark_domain',
};

async function httpTransportSend(message) {
  var hubUrl = getHubUrl();
  if (!hubUrl) return { ok: false, error: 'STP_HUB_URL not set' };

  var endpoint = hubUrl.replace(/\/+$/, '') + (TYPE_TO_ENDPOINT[message.message_type] || '/stp/' + message.message_type);

  try {
    var res = await fetch(endpoint, {
      method: 'POST',
      headers: buildHttpHeaders(),
      body: JSON.stringify(message),
      signal: AbortSignal.timeout(15000),
    });
    var data = await res.json();
    return { ok: res.ok, status: res.status, response: data };
  } catch (err) {
    return { ok: false, error: err.message };
  }
}

// Transport is always HTTP. When hub URL is not configured, send() returns error.
// Failed sends are handled by the retry queue in publisher.js.
function getTransport() {
  return { send: httpTransportSend };
}

async function sendToHub(message) {
  var transport = getTransport();
  return transport.send(message);
}

// --- High-level hub operations ---

async function hubSearch(query, opts) {
  var hubUrl = getHubUrl();
  if (!hubUrl) return { ok: false, error: 'Hub not configured', results: [] };

  var message = buildSearchMessage(query, opts);
  var result = await httpTransportSend(message);

  if (!result.ok) {
    if (result.status === 402) {
      var errResp = result.response || {};
      return {
        ok: false,
        error: 'insufficient_balance',
        message: errResp.message || 'Points balance is insufficient for search.',
        balance: typeof errResp.balance === 'number' ? errResp.balance : null,
        results: [],
      };
    }
    return { ok: false, error: result.error || 'Hub search failed', network_error: !result.status, results: [] };
  }

  var payload = result.response && result.response.payload ? result.response.payload : result.response;
  var sparks = payload.sparks || [];

  return {
    ok: true,
    results: sparks.map(normalizeHubSpark),
    total: payload.total || sparks.length,
    threshold: payload.threshold_applied,
    purchased_spark_ids: payload.purchased_spark_ids || [],
    already_owned_ids: payload.already_owned_ids || [],
    insufficient_at: payload.insufficient_at || null,
    balance: typeof payload.balance === 'number' ? payload.balance : null,
  };
}

// Normalize a Hub spark into the same structure as local sparks (B2 fix)
function normalizeHubSpark(s) {
  var insight = parseInsight(s.insight);
  var result = {
    id: s.id,
    type: 'HubSpark',
    domain: s.domain_id || s.domain,
    summary: s.how_summary || extractSummary(s),
    score: s._score || s._effective_score || 0,
    credibility: s.credibility_score || s._effective_score || 0,
    source: 'hub',
  };

  // Extract six-dimension fields from Hub spark columns or insight JSON
  if (s.when_trigger || s.when_data) {
    result.when = { trigger: s.when_trigger || '' };
    if (s.when_data) {
      try { Object.assign(result.when, typeof s.when_data === 'string' ? JSON.parse(s.when_data) : s.when_data); } catch (e) {}
    }
  } else if (insight.when) {
    result.when = insight.when;
  }

  if (s.how_summary || s.how_detail) {
    result.how = { summary: s.how_summary || '', detail: s.how_detail || '' };
  } else if (insight.how) {
    result.how = insight.how;
  }

  if (s.why) {
    result.why = s.why;
  } else if (insight.why) {
    result.why = insight.why;
  }

  if (s.not_data) {
    try { result.not = typeof s.not_data === 'string' ? JSON.parse(s.not_data) : s.not_data; } catch (e) {}
  } else if (insight.not) {
    result.not = insight.not;
  }

  if (!result.summary && result.when && result.when.trigger && result.how && result.how.summary) {
    result.summary = result.when.trigger + ' → ' + result.how.summary;
  }

  return result;
}

function parseInsight(insight) {
  if (!insight) return {};
  if (typeof insight === 'string') {
    try { return JSON.parse(insight); } catch (e) { return {}; }
  }
  return insight;
}

function extractSummary(spark) {
  var insight = parseInsight(spark.insight);
  return insight.summary || insight.detail
    || (spark.how_summary ? spark.how_summary : '')
    || spark.summary || '';
}

async function hubPublish(ember) {
  var message = buildPublishMessage(ember);
  return httpTransportSend(message);
}

async function hubVote(sparkId, voteType, opts) {
  var message = buildFeedbackMessage(sparkId, voteType, opts);
  return httpTransportSend(message);
}

async function hubFetch(sparkId) {
  var message = buildMessage({
    messageType: 'spark_fetch',
    payload: { spark_id: sparkId },
  });
  return httpTransportSend(message);
}

async function hubSync(opts) {
  var message = buildSyncMessage(opts);
  return httpTransportSend(message);
}

async function hubGetCategoryTree() {
  var hubUrl = getHubUrl();
  if (!hubUrl) return { ok: false, error: 'Hub not configured', tree: [] };

  var endpoint = hubUrl.replace(/\/+$/, '') + '/api/categories/tree';
  try {
    var res = await fetch(endpoint, {
      method: 'GET',
      headers: buildHttpHeaders(),
      signal: AbortSignal.timeout(10000),
    });
    var data = await res.json();
    return { ok: res.ok, tree: data.tree || [], level_semantics: data.level_semantics || null };
  } catch (err) {
    return { ok: false, error: err.message, tree: [] };
  }
}

function formatCategoryTree(tree, indent, levelSemantics) {
  indent = indent || 0;
  var lines = [];
  if (indent === 0 && levelSemantics) {
    lines.push('层级说明: L1=' + (levelSemantics.L1 || '') + ', L2=' + (levelSemantics.L2 || '') + ', L3=' + (levelSemantics.L3 || ''));
    lines.push('---');
  }
  for (var i = 0; i < tree.length; i++) {
    var node = tree[i];
    var prefix = '';
    for (var j = 0; j < indent; j++) prefix += '  ';
    lines.push(prefix + '- ' + node.display_name + ' [id=' + node.id + ']');
    if (node.children && node.children.length > 0) {
      lines.push(formatCategoryTree(node.children, indent + 1));
    }
  }
  return lines.join('\n');
}

module.exports = {
  PROTOCOL_NAME,
  PROTOCOL_VERSION,
  buildMessage,
  buildPublishMessage,
  buildSearchMessage,
  buildFeedbackMessage,
  buildForgeRequestMessage,
  buildRelateMessage,
  buildSyncMessage,
  unwrapResponse,
  normalizeHubSpark,
  getTransport,
  sendToHub,
  getHubUrl,
  hubSearch,
  hubPublish,
  hubVote,
  hubFetch,
  hubSync,
  hubGetCategoryTree,
  formatCategoryTree,
  buildHttpHeaders,
};
