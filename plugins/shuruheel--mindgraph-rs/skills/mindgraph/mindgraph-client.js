/**
 * mindgraph-client.js
 * Node.js client for mindgraph-server.
 * Implements the Extended API Endpoint Specification (18 Cognitive Layer Tools).
 */

const fs = require('fs');
const path = require('path');

// ─── Config ──────────────────────────────────────────────────────────────────

function loadConfig() {
  const configPath = process.env.MINDGRAPH_CONFIG_PATH || path.join(process.env.HOME, '.openclaw', 'mindgraph.json');
  let config = {};
  if (fs.existsSync(configPath)) {
    config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
  }

  return {
    baseUrl: process.env.MINDGRAPH_URL || `http://${config.bind || '127.0.0.1'}:${config.port || 18790}`,
    token: process.env.MINDGRAPH_TOKEN || config.token || '',
    defaultAgent: process.env.MINDGRAPH_AGENT || config.default_agent || 'jaadu',
  };
}

const CONFIG = loadConfig();

// ─── HTTP helper ─────────────────────────────────────────────────────────────

const MAX_RETRIES = 3;
const RETRY_DELAY_MS = 500;
const RETRYABLE_STATUSES = new Set([502, 503, 504]);

async function request(method, reqPath, body = null) {
  const { default: fetch } = await import('node-fetch').catch(() => {
    return { default: globalThis.fetch };
  });

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${CONFIG.token}`,
  };

  const opts = { method, headers };
  if (body !== null) opts.body = JSON.stringify(body);

  let lastError;
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      const res = await fetch(`${CONFIG.baseUrl}${reqPath}`, opts);
      const text = await res.text();

      if (!res.ok) {
        // Retry on transient server errors
        if (RETRYABLE_STATUSES.has(res.status) && attempt < MAX_RETRIES) {
          lastError = new Error(`mindgraph ${method} ${reqPath} → ${res.status}`);
          await new Promise(r => setTimeout(r, RETRY_DELAY_MS * attempt));
          continue;
        }
        let errBody = text;
        try { errBody = JSON.parse(text); } catch {}
        const msg = errBody.message || errBody.error || text;
        const error = new Error(`mindgraph ${method} ${reqPath} → ${res.status}: ${msg}`);
        error.status = res.status;
        error.details = errBody;
        throw error;
      }

      if (!text || text === 'null') return null;
      try { return JSON.parse(text); } catch { return text; }
    } catch (e) {
      // Retry on network errors (ECONNRESET, ECONNREFUSED, etc.)
      if (e.code && ['ECONNRESET', 'ECONNREFUSED', 'EPIPE', 'ETIMEDOUT'].includes(e.code) && attempt < MAX_RETRIES) {
        lastError = e;
        await new Promise(r => setTimeout(r, RETRY_DELAY_MS * attempt));
        continue;
      }
      throw e;
    }
  }
  throw lastError;
}

/**
 * Sanitise a node label for CozoDB FTS indexing.
 */
function sanitizeLabel(label) {
  if (!label || typeof label !== 'string') return label;
  return label
    .replace(/'/g, "'")
    .replace(/'/g, "'")
    .replace(/[:\\\/]/g, ' ')
    .replace(/\+/g, 'and')
    .replace(/\^/g, '')
    .replace(/~/g, '')
    .replace(/\*/g, '')
    .replace(/\?/g, '')
    .replace(/\s{2,}/g, ' ')
    .trim();
}

// ─── 1. Reality Layer (Ingest) ────────────────────────────────────────────────

async function ingest(label, content, action = 'observation', opts = {}) {
  return request('POST', '/reality/ingest', {
    action, // 'source', 'snippet', 'observation'
    label: sanitizeLabel(label),
    content,
    source_uid: opts.sourceUid,
    medium: opts.medium,
    url: opts.url,
    timestamp: opts.timestamp,
    confidence: opts.confidence,
    salience: opts.salience,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 2. Reality Layer (Entity) ────────────────────────────────────────────────

async function manageEntity(opts = {}) {
  return request('POST', '/reality/entity', {
    action: opts.action, // 'create', 'alias', 'resolve', 'fuzzy_resolve', 'merge', 'relate'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    text: opts.text,
    canonical_uid: opts.canonicalUid,
    alias_score: opts.aliasScore,
    keep_uid: opts.keepUid,
    merge_uid: opts.mergeUid,
    limit: opts.limit,
    source_uid: opts.sourceUid,
    target_uid: opts.targetUid,
    edge_type: opts.edgeType,
    // entity_type must live inside props (server reads it from props.entity_type for dedup)
    props: opts.entityType ? { entity_type: opts.entityType, ...opts.props } : opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 3. Epistemic Layer (Argument) ───────────────────────────────────────────

async function addArgument(opts = {}) {
  return request('POST', '/epistemic/argument', {
    claim: opts.claim ? { ...opts.claim, label: sanitizeLabel(opts.claim.label) } : undefined,
    evidence: opts.evidence,
    warrant: opts.warrant ? { ...opts.warrant, principle: opts.warrant.principle || opts.warrant.explanation } : undefined,
    argument: opts.argument,
    refutes_uid: opts.refutesUid,
    extends_uid: opts.extendsUid,
    source_uids: opts.sourceUids,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 4. Epistemic Layer (Inquiry) ────────────────────────────────────────────

async function addInquiry(label, content, action, opts = {}) {
  return request('POST', '/epistemic/inquiry', {
    action, // 'hypothesis', 'theory', 'paradigm', 'anomaly', 'assumption', 'question', 'open_question'
    label: sanitizeLabel(label),
    content,
    status: opts.status,
    anomalous_to_uid: opts.anomalousToUid,
    assumes_uid: opts.assumesUid,
    tests_uid: opts.testsUid,
    addresses_uid: opts.addressesUid,
    confidence: opts.confidence,
    salience: opts.salience,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 5. Epistemic Layer (Structure) ──────────────────────────────────────────

async function addStructure(label, content, action, opts = {}) {
  return request('POST', '/epistemic/structure', {
    action, // 'concept', 'pattern', 'mechanism', 'model', 'analogy', 'theorem', 'equation'
    label: sanitizeLabel(label),
    content,
    summary: opts.summary,
    analogous_to_uid: opts.analogousToUid,
    transfers_to_uid: opts.transfersToUid,
    evaluates_uid: opts.evaluatesUid,
    outperforms_uid: opts.outperformsUid,
    chain_steps: opts.chainSteps,
    derived_from_uid: opts.derivedFromUid,
    proven_by_uid: opts.provenByUid,
    confidence: opts.confidence,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 6. Intent Layer (Commitment) ────────────────────────────────────────────

async function addCommitment(label, description, action, opts = {}) {
  return request('POST', '/intent/commitment', {
    action, // 'goal', 'project', 'milestone'
    label: sanitizeLabel(label),
    description,
    priority: opts.priority,
    status: opts.status,
    parent_uid: opts.parentUid,
    due_date: opts.dueDate,
    motivated_by_uid: opts.motivatedByUid,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 7. Intent Layer (Deliberation) ──────────────────────────────────────────

async function deliberate(opts = {}) {
  return request('POST', '/intent/deliberation', {
    action: opts.action, // 'open_decision', 'add_option', 'add_constraint', 'resolve'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    description: opts.description,
    decision_uid: opts.decisionUid,
    chosen_option_uid: opts.chosenOptionUid,
    resolution_rationale: opts.resolutionRationale,
    constraint_type: opts.constraintType,
    blocks_uid: opts.blocksUid,
    informs_uid: opts.informsUid,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 8. Action Layer (Procedure) ─────────────────────────────────────────────

async function procedure(opts = {}) {
  return request('POST', '/action/procedure', {
    action: opts.action, // 'create_flow', 'add_step', 'add_affordance', 'add_control'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    description: opts.description,
    flow_uid: opts.flowUid,
    step_order: opts.stepOrder,
    previous_step_uid: opts.previousStepUid,
    affordance_type: opts.affordanceType,
    control_type: opts.controlType,
    uses_affordance_uids: opts.usesAffordanceUids,
    goal_uid: opts.goalUid,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 9. Action Layer (Risk) ──────────────────────────────────────────────────

async function risk(opts = {}) {
  return request('POST', '/action/risk', {
    action: opts.action, // 'assess', 'get_assessments'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    description: opts.description,
    assessed_uid: opts.assessedUid,
    severity: opts.severity,
    likelihood: opts.likelihood,
    mitigations: opts.mitigations,
    residual_risk: opts.residualRisk,
    filter_uid: opts.filterUid,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 10. Memory Layer (Session) ───────────────────────────────────────────────

async function sessionOp(opts = {}) {
  return request('POST', '/memory/session', {
    action: opts.action, // 'open', 'trace', 'close', 'journal'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    summary: opts.summary,
    session_uid: opts.sessionUid,
    relevant_node_uids: opts.relevantNodeUids,
    confidence: opts.confidence,
    salience: opts.salience,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 11. Memory Layer (Distill) ───────────────────────────────────────────────

async function distill(label, content, opts = {}) {
  return request('POST', '/memory/distill', {
    label: sanitizeLabel(label),
    content,
    session_uid: opts.sessionUid,
    summarizes_uids: opts.summarizesUids,
    importance: opts.importance,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 12. Memory Layer (Config) ───────────────────────────────────────────────

async function memoryConfig(opts = {}) {
  return request('POST', '/memory/config', {
    action: opts.action, // 'set_preference', 'set_policy', 'get_preferences', 'get_policies'
    type: opts.type,
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    key: opts.key,
    value: opts.value,
    policy_content: opts.policyContent,
    applies_to_layers: opts.appliesToLayers,
    decay_half_life: opts.decayHalfLife,
    privacy_default: opts.privacyDefault,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 13. Agent Layer (Plan) ──────────────────────────────────────────────────

async function plan(opts = {}) {
  // Field mapping by action:
  //   create_task  → label, description, goalUid, relatedUids, status, props
  //   create_plan  → label, description, taskUid, goalUid, props
  //   add_step     → label, planUid, stepOrder, dependsOnUids, props
  //   update_status → targetUid (the task/plan uid), status ('pending'|'in_progress'|'completed'|'cancelled')
  //                   NOTE: use targetUid, NOT taskUid, for update_status
  //   get_plan     → targetUid (the task uid to fetch plan for)
  return request('POST', '/agent/plan', {
    action: opts.action,
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    description: opts.description,
    goal_uid: opts.goalUid,
    task_uid: opts.taskUid,
    plan_uid: opts.planUid,
    step_order: opts.stepOrder,
    depends_on_uids: opts.dependsOnUids,
    // targetUid is used by update_status and get_plan — taskUid is a common mistake, support both
    target_uid: opts.targetUid || (opts.action === 'update_status' || opts.action === 'get_plan' ? opts.taskUid : undefined),
    status: opts.status,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 14. Agent Layer (Governance) ────────────────────────────────────────────

async function governance(opts = {}) {
  return request('POST', '/agent/governance', {
    action: opts.action, // 'create_policy', 'set_budget', 'request_approval', 'resolve_approval'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    policy_content: opts.policyContent,
    policy_scope: opts.policyScope,
    budget_type: opts.budgetType,
    budget_limit: opts.budgetLimit,
    governed_uid: opts.governedUid,
    approval_request: opts.approvalRequest,
    approval_uid: opts.approvalUid,
    approved: opts.approved,
    resolution_note: opts.resolutionNote,
    requires_plan_uid: opts.requiresPlanUid,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 15. Agent Layer (Execution) ─────────────────────────────────────────────

async function execution(opts = {}) {
  return request('POST', '/agent/execution', {
    action: opts.action, // 'start', 'complete', 'fail', 'register_agent'
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    plan_uid: opts.planUid,
    executor_uid: opts.executorUid,
    execution_uid: opts.executionUid,
    outcome: opts.outcome,
    produces_node_uid: opts.producesNodeUid,
    error_description: opts.errorDescription,
    agent_name: opts.agentName,
    agent_role: opts.agentRole,
    filter_plan_uid: opts.filterPlanUid,
    props: opts.props,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── 16. Connective Tissue (Retrieve) ────────────────────────────────────────

async function retrieve(action, opts = {}) {
  // For semantic action, embed client-side and use /embeddings/search
  // (server's semantic action requires inline embedding provider we don't have)
  if (action === 'semantic' && opts.query) {
    try {
      const queryVec = await embedQuery(opts.query);
      const k = opts.k || opts.limit || 10;
      const results = await request('POST', '/embeddings/search', { query: queryVec, k });
      const items = Array.isArray(results) ? results : (results?.results || results?.items || []);
      return { results: items };
    } catch (e) {
      // Fall back to server-side retrieve if embedding fails
      return request('POST', '/retrieve', { action, ...opts });
    }
  }

  return request('POST', '/retrieve', {
    action,
    query: opts.query,
    k: opts.k,
    threshold: opts.threshold,
    layer: opts.layer,
    node_types: opts.nodeTypes,
    confidence_min: opts.confidenceMin,
    salience_min: opts.salienceMin,
    limit: opts.limit,
    offset: opts.offset,
  });
}

// ─── 17. Connective Tissue (Traverse) ────────────────────────────────────────

async function traverse(mode, startUid, opts = {}) {
  return request('POST', '/traverse', {
    mode,
    start_uid: startUid,
    end_uid: opts.endUid,
    max_depth: opts.maxDepth,
    direction: opts.direction,
    edge_types: opts.edgeTypes,
    weight_threshold: opts.weightThreshold,
    include_tombstoned: opts.includeTombstoned,
  });
}

// ─── 18. Connective Tissue (Evolve) ──────────────────────────────────────────

async function evolve(action, uid, opts = {}) {
  return request('POST', '/evolve', {
    action, // 'update', 'tombstone', 'restore', 'decay', 'history', 'snapshot'
    uid,
    label: opts.label ? sanitizeLabel(opts.label) : undefined,
    summary: opts.summary,
    confidence: opts.confidence,
    salience: opts.salience,
    props_patch: opts.propsPatch,
    reason: opts.reason,
    cascade: opts.cascade,
    half_life_secs: opts.halfLifeSecs,
    min_salience: opts.minSalience,
    min_age_secs: opts.minAgeSecs,
    version: opts.version,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── Low-level CRUD (Backward Compatibility) ───────────────────────────────

async function addNode(label, props, opts = {}) {
  return request('POST', '/node', {
    label: sanitizeLabel(label),
    props,
    confidence: opts.confidence,
    salience: opts.salience,
    summary: opts.summary,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

async function getNode(uid) {
  return request('GET', `/node/${uid}`);
}

async function updateNode(uid, updates, opts = {}) {
  return request('PATCH', `/node/${uid}`, {
    ...updates,
    agent_id: opts.agentId || CONFIG.defaultAgent,
    reason: opts.reason || 'updated via client',
  });
}

async function deleteNode(uid, opts = {}) {
  const params = new URLSearchParams({
    reason: opts.reason || 'deleted via client',
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
  return request('DELETE', `/node/${uid}?${params}`);
}

async function link(fromUid, toUid, edgeType, opts = {}) {
  return request('POST', '/link', {
    from_uid: fromUid,
    to_uid: toUid,
    edge_type: edgeType,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

async function getEdges(fromUid, opts = {}) {
  const params = new URLSearchParams({ from_uid: fromUid });
  if (opts.edgeType) params.set('edge_type', opts.edgeType);
  const result = await request('GET', `/edges?${params}`);
  return Array.isArray(result) ? result : (result?.items ?? result ?? []);
}

async function edgesTo(uid, edgeType) {
  const params = new URLSearchParams({ to_uid: uid });
  if (edgeType) params.set('edge_type', edgeType);
  const result = await request('GET', `/edges?${params}`);
  return Array.isArray(result) ? result : (result?.items ?? result ?? []);
}

async function stats() {
  return request('GET', '/stats');
}

async function health() {
  return request('GET', '/health');
}

async function search(query, opts = {}) {
  return request('POST', '/search', {
    query: sanitizeLabel(query),
    node_type: opts.nodeType,
    layer: opts.layer,
    limit: opts.limit,
    min_score: opts.minScore,
  });
}

async function getNodes(opts = {}) {
  const params = new URLSearchParams();
  if (opts.layer) params.set('layer', opts.layer);
  if (opts.nodeType) params.set('node_type', opts.nodeType);
  if (opts.labelContains) params.set('label_contains', opts.labelContains);
  if (opts.agent) params.set('agent', opts.agent);
  params.set('limit', opts.limit || 100);
  params.set('offset', opts.offset || 0);
  return request('GET', `/nodes?${params}`);
}

// ─── Journal (Phase 0.5.6) ────────────────────────────────────────────────────

async function addJournal(label, content, opts = {}) {
  return request('POST', '/memory/session', {
    action: 'journal',
    label: sanitizeLabel(label),
    summary: opts.summary || content.slice(0, 300),
    session_uid: opts.sessionUid,
    relevant_node_uids: opts.relevantNodeUids,
    props: {
      content,
      journal_type: opts.journalType || 'note',
      tags: opts.tags || [],
    },
    confidence: opts.confidence,
    salience: opts.salience,
    agent_id: opts.agentId || CONFIG.defaultAgent,
  });
}

// ─── Hybrid Search (Phase 0.5.4 — client-side RRF) ───────────────────────────

/**
 * Embed a query string using OpenAI's text-embedding-3-small model.
 * Returns a 1536-dim vector.
 */
async function embedQuery(text) {
  // Try env var first; fall back to OpenClaw config for local installs
  let apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    try {
      const ocConfig = JSON.parse(fs.readFileSync(path.join(process.env.HOME, '.openclaw', 'openclaw.json'), 'utf8'));
      apiKey = ocConfig.env?.OPENAI_API_KEY;
    } catch {}
  }
  if (!apiKey) throw new Error('OPENAI_API_KEY not found — set the OPENAI_API_KEY environment variable');

  const { default: fetch } = await import('node-fetch').catch(() => ({ default: globalThis.fetch }));
  const res = await fetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiKey}` },
    body: JSON.stringify({ input: text, model: 'text-embedding-3-small' }),
  });
  if (!res.ok) throw new Error(`Embedding API error ${res.status}`);
  const data = await res.json();
  return data.data[0].embedding;
}

/**
 * Hybrid search using server-side RRF (Phase 0.5.4).
 * Uses /retrieve with action:"hybrid" — server fuses FTS (BM25) + vector (HNSW)
 * with Reciprocal Rank Fusion (k=60). Falls back to FTS-only if no embeddings.
 */
async function hybridSearch(query, opts = {}) {
  const limit = opts.limit || 10;
  const result = await request('POST', '/retrieve', {
    action: 'hybrid',
    query,
    k: opts.k || limit,
    node_types: opts.nodeTypes,
    layer: opts.layer,
    limit,
  });
  const items = result?.results || result?.items || (Array.isArray(result) ? result : []);
  return items.map(item => {
    const node = item.node || item;
    return { node, score: item.score || 0 };
  });
}

// ─── Find or Create Entity (Phase 0.5.3 — client wrapper) ────────────────────

/**
 * Dedup-safe entity creation via server-side find_or_create_entity (Phase 0.5.3).
 * The /reality/entity create action now checks alias + case-insensitive label
 * match before creating. Returns {node, created: bool}.
 */
async function findOrCreateEntity(label, entityType = 'Person', opts = {}) {
  return manageEntity({
    action: 'create',
    label,
    entityType,
    ...opts,
  });
}

// ─── Follows Edge Helper (Phase 0.5.5) ───────────────────────────────────────

async function addFollowsEdge(fromUid, toUid, opts = {}) {
  return link(fromUid, toUid, 'Follows', opts);
}

// ─── Exports ──────────────────────────────────────────────────────────────────

module.exports = {
  health,
  stats,
  search,
  getNodes,
  // 1. Reality
  ingest,
  // 2. Entity
  manageEntity,
  // 3. Argument
  addArgument,
  // 4. Inquiry
  addInquiry,
  // 5. Structure
  addStructure,
  // 6. Commitment
  addCommitment,
  // 7. Deliberation
  deliberate,
  // 8. Procedure
  procedure,
  // 9. Risk
  risk,
  // 10. Session
  sessionOp,
  // 11. Distill
  distill,
  // 12. Config
  memoryConfig,
  // 13. Plan
  plan,
  // 14. Governance
  governance,
  // 15. Execution
  execution,
  // 16. Retrieve
  retrieve,
  // 17. Traverse
  traverse,
  // 18. Evolve
  evolve,
  // Phase 0.5 additions
  addJournal,
  hybridSearch,
  findOrCreateEntity,
  addFollowsEdge,
  // Low-level & Compat
  addNode,
  getNode,
  updateNode,
  deleteNode,
  link,
  getEdges,
  edgesTo,
  sanitizeLabel,
};
