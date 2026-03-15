/**
 * dream-analysis.js
 * Core analysis framework for MindGraph Dreaming System
 *
 * SAFETY RULE: auto_apply is ALWAYS false.
 * No proposal is ever applied without explicit human approval.
 *
 * Each analyzer is a pure read-only function that returns proposals.
 * Analyzers never mutate the graph.
 *
 * DOMAIN CONVENTIONS: See CONVENTIONS.md in this directory for:
 *   - Valid status values per node type (Goal, Decision, Project)
 *   - project_type values (active / portfolio / internal)
 *   - Decision modeling rules (decided_at, decision_rationale, description)
 *   - How to handle status normalization (locked/decided/implemented/completed → made)
 *   - Proposal grouping guidelines (flat list, not per-type columns)
 */

'use strict';

const mg = require('../mindgraph-client.js');

const { analyzeEmbeddings } = require('./embedding-analysis.js');
const { analyzeRichEnrichment } = require('./rich-enrichment.js');

// ─── ULID ────────────────────────────────────────────────────────────────────

let ulid;
try { ({ ulid } = require('ulidx')); } catch {}

function generateProposalId() {
  if (ulid) return ulid();
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function now() { return new Date().toISOString(); }

function daysBetween(ms1, ms2) {
  return Math.abs(ms2 - ms1) / (24 * 60 * 60 * 1000);
}

function calculateImpact(delta) {
  const abs = Math.abs(delta || 0);
  if (abs >= 0.3) return 'high';
  if (abs >= 0.1) return 'medium';
  return 'low';
}

/**
 * SAFETY: every proposal must go through this wrapper.
 * auto_apply is always false — no exceptions.
 */
function proposal(base) {
  return {
    id: generateProposalId(),
    timestamp: now(),
    auto_apply: false,
    auto_apply_reason: 'All proposals require human review (global safety policy)',
    impact: 'medium',
    ...base,
  };
}

// ─── Analyzer 1: Schema Compliance ──────────────────────────────────────────

async function analyzeSchemaCompliance() {
  const proposals = [];

  // NOTE: 'description' is NOT a valid server prop for Decision/Goal nodes.
  // The server enforces strict schemas and strips unknown fields.
  // ONLY list props that the server actually accepts per node type.
  // Verified server schemas (2026-03-05):
  //   Decision:    _type, question, status, decided_option_uid, decided_at, decision_rationale, reversibility
  //   Project:     _type, name, description, status, started_at, target_completion
  //   Question:    _type, text, question_type, scope, status, importance, tractability, blocking_factors
  //   Goal:        _type, deadline, description, goal_type, priority, progress, status, success_criteria
  //   Task:        _type, assigned_to, created_by, deadline, depends_on_task_uids, description, parent_goal_uid, priority, result_summary, status, task_type
  //   Constraint:  _type, constraint_type, description, hard, unit, value
  //   Observation: _type, content, observation_type, session_uid, timestamp
  //   Entity:      _type, entity_type (+ varies)
  //
  // Fields that DON'T exist and get silently stripped:
  //   - project_type (not in Project schema — use description or tags)
  //   - question_text (not in Question schema — use 'text')
  //   - description on Decision (not in schema — use summary or decision_rationale)
  const requiredProps = {
    Claim:        ['content'],
    Constraint:   ['description'],
    Goal:         ['status'],           // description is in Goal props schema
    Decision:     ['status'],           // no description prop — use summary (top-level) or decision_rationale
    Project:      ['description'],      // description IS in Project props schema; project_type is NOT
    Entity:       ['entity_type'],
    Preference:   ['key', 'value'],
    Observation:  ['content'],
    Evidence:     ['description'],
    Question:     ['text'],             // server uses 'text', NOT 'question_text'
    OpenQuestion: ['text'],             // same — 'text' not 'question_text'
  };

  // Additional check: nodes that need a non-empty summary for FTS searchability
  const needsSummary = new Set([
    'Decision', 'Goal', 'Project', 'Constraint', 'Entity',
    'Observation', 'Claim', 'Pattern', 'Task'
  ]);

  const validPriorities   = ['low', 'medium', 'high', 'critical'];
  // Decision statuses use a different vocabulary from Goal/Project:
  //   'open'        = still being deliberated (options exist, no conclusion yet)
  //   'made'        = decision has been made and is in force (steady state)
  //   'superseded'  = replaced by another decision (link to new one)
  //   'reversed'    = explicitly undone
  // Goal/Project statuses: active, archived, on_hold, live, completed
  // Do NOT use 'completed' for Decisions — use 'made'.
  const validDecisionStatuses = ['open', 'made', 'superseded', 'reversed'];
  const validStatuses     = ['active', 'completed', 'archived', 'on_hold', 'open', 'closed', 'live'];
  // project_type distinguishes what a project is used for:
  //   'active'    = currently being worked on together (Thumos, Elys, Polymarket, MindGraph etc.)
  //   'portfolio' = past/archived work to mention in job applications and outreach
  //   'internal'  = infrastructure/tooling not relevant to external audiences
  const validProjectTypes = ['active', 'portfolio', 'internal'];

  try {
    let offset = 0, hasMore = true;
    const allNodes = [];
    while (hasMore) {
      const batch = await mg.getNodes({ limit: 100, offset });
      const nodes = batch.items || batch || [];
      allNodes.push(...nodes);
      hasMore = nodes.length === 100;
      offset += 100;
    }

    for (const node of allNodes) {
      const required = requiredProps[node.node_type] || [];
      const missing = [];
      const invalid = [];

      for (const prop of required) {
        const val = node.props?.[prop] ?? node[prop];
        if (val === undefined || val === null || val === '') {
          missing.push(prop);
        }
      }

      if (node.node_type === 'Goal' && node.props?.priority &&
          !validPriorities.includes(node.props.priority)) {
        invalid.push({ prop: 'priority', current: node.props.priority, expected: validPriorities });
      }
      const statusList = node.node_type === 'Decision' ? validDecisionStatuses : validStatuses;
      if (['Goal','Decision','Project'].includes(node.node_type) && node.props?.status &&
          !statusList.includes(node.props.status)) {
        invalid.push({ prop: 'status', current: node.props.status, expected: statusList });
      }
      // NOTE: project_type is not in server schema — skip validation (2026-03-05)
      // Decision: flag when status=made but decided_at is null (data quality gap)
      if (node.node_type === 'Decision' &&
          node.props?.status === 'made' &&
          !node.props?.decided_at &&
          !node.props?.decision_rationale) {
        // Only flag if we have no rationale either — both missing is a real gap
        missing.push('decision_rationale');
      }

      // Check summary (top-level, not in props) for FTS searchability
      if (needsSummary.has(node.node_type) && (!node.summary || node.summary.length < 10)) {
        const fallback =
          node.props?.description ||
          node.props?.decision_rationale ||
          node.props?.content ||
          node.props?.policy_text ||
          null;
        if (fallback && fallback.length > 10) {
          missing.push('summary');
        }
      }

      if (missing.length || invalid.length) {
        // ── Synthesize suggested values from available sibling fields ──
        const suggested = {};

        for (const prop of missing) {
          if (prop === 'summary') {
            // summary is a top-level field — evolve('update') can set it directly
            const fallback =
              node.props?.description ||
              node.props?.decision_rationale ||
              node.props?.content ||
              node.props?.policy_text ||
              null;
            if (fallback) suggested.summary = fallback.slice(0, 300);
          }
          if (prop === 'description') {
            // Only for types where description IS a valid server prop (Constraint, Evidence)
            const fallback =
              node.props?.decision_rationale ||
              node.props?.content ||
              node.props?.policy_text ||
              node.summary ||
              null;
            if (fallback) suggested.description = fallback.slice(0, 500);
          }
          if (prop === 'content') {
            const fallback = node.props?.description || node.summary || null;
            if (fallback) suggested.content = fallback.slice(0, 500);
          }
          if (prop === 'text') {
            // For Question/OpenQuestion: 'text' is the server field name (NOT 'question_text')
            const fallback =
              node.props?.question ||
              (node.label && (node.label.includes('?') || node.label.split(' ').length > 3) ? node.label : null) ||
              node.summary ||
              null;
            if (fallback) suggested.text = fallback.slice(0, 500);
          }
          if (prop === 'status') {
            suggested.status = 'active'; // safe default for Goal/Decision
          }
          if (prop === 'entity_type') {
            // Infer from label patterns
            const lbl = node.label.toLowerCase();
            if (lbl.includes('company') || lbl.includes('inc') || lbl.includes('ai') || lbl.includes('care')) suggested.entity_type = 'Organization';
            else if (lbl.match(/\b(shan|rizvi|jeff|vishal|dr\.)\b/i)) suggested.entity_type = 'Person';
            else suggested.entity_type = 'Organization'; // safe default
          }
          if (prop === 'decision_rationale') {
            // Already have summary or label sometimes
            const fallback = node.summary || null;
            if (fallback) suggested.decision_rationale = fallback;
          }
        }

        // For invalid props, suggest the normalized value
        for (const inv of invalid) {
          if (inv.prop === 'status') {
            const cur = (inv.current || '').toLowerCase();
            const normalize = node.node_type === 'Decision'
              ? { locked: 'made', decided: 'made', implemented: 'made', completed: 'made',
                  finalized: 'made', final: 'made', active: 'open', 'in-progress': 'open' }
              : { locked: 'completed', decided: 'completed', implemented: 'completed',
                  finalized: 'completed', final: 'completed', 'in-progress': 'active', open: 'active' };
            suggested.status = normalize[cur] || (node.node_type === 'Decision' ? 'made' : 'active');
          }
          // project_type is not in the server schema — skip
        }

        // If we have suggested values, this is an actionable schema_fix (auto-apply).
        // If no suggested values, it's a data_gap — flagged for review, not auto-applied.
        // This prevents the dreamer from re-generating the same empty proposal every night.
        const hasSuggestions = Object.keys(suggested).length > 0;
        proposals.push(proposal({
          type: hasSuggestions ? 'schema_fix' : 'data_gap',
          target: { uid: node.uid, label: node.label, node_type: node.node_type },
          action: hasSuggestions 
            ? `Fix ${missing.length + invalid.length} schema issue(s)` 
            : `Data gap: ${missing.length + invalid.length} field(s) need manual input`,
          reason: [
            missing.length ? `Missing: ${missing.join(', ')}` : null,
            invalid.length ? `Invalid: ${invalid.map(i => `${i.prop}="${i.current}"`).join(', ')}` : null,
          ].filter(Boolean).join(' · '),
          impact: missing.length > 2 ? 'high' : 'medium',
          schema_violation: { missing_props: missing, invalid_props: invalid },
          new_value: hasSuggestions ? suggested : undefined,
        }));
      }
    }
  } catch (e) {
    console.error('Schema compliance failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 1b: Data Quality ───────────────────────────────────────────────
// Catches domain-specific modeling issues beyond raw schema compliance.
// Derived from cockpit UI feedback (Feb 2026):
//   - Decisions where description is missing but decision_rationale exists → copy it
//   - Projects missing project_type (can't distinguish active vs portfolio)
//   - Decision dates: completed decisions with no decided_at (dates lost at import)
//   - Status normalization catches: locked/decided/implemented/finalized/final/completed → made (Decision); → completed (Goal/Project)

async function analyzeDataQuality() {
  const proposals = [];

  try {
    const allNodes = [];
    let offset = 0, hasMore = true;
    while (hasMore) {
      const batch = await mg.getNodes({ limit: 100, offset });
      const nodes = batch.items || batch || [];
      allNodes.push(...nodes);
      hasMore = nodes.length === 100;
      offset += 100;
    }

    for (const node of allNodes) {
      // Decision: summary is missing/short but decision_rationale has content → copy to summary
      // NOTE: Decision schema does NOT have 'description' prop — use 'summary' (top-level field)
      if (node.node_type === 'Decision') {
        const hasSummary = node.summary && node.summary.trim().length > 20;
        const hasRat = node.props?.decision_rationale && node.props.decision_rationale.trim();
        if (!hasSummary && hasRat) {
          proposals.push(proposal({
            type: 'data_enrichment',
            target: { uid: node.uid, label: node.label, node_type: node.node_type },
            action: 'Copy decision_rationale → summary',
            reason: 'Summary is missing/short but decision_rationale has content. Use rationale as summary for FTS and discoverability.',
            impact: 'low',
            new_value: { summary: node.props.decision_rationale.slice(0, 500) },
          }));
        }

        // Completed decisions with no decided_at and no rationale — genuinely incomplete
        if (node.props?.status === 'completed' && !node.props?.decided_at && !hasRat && !hasSummary) {
          proposals.push(proposal({
            type: 'data_gap',
            target: { uid: node.uid, label: node.label, node_type: node.node_type },
            action: 'Add decision_rationale and decided_at',
            reason: 'Completed decision has no rationale, description, or decided_at. Original context is lost.',
            impact: 'medium',
          }));
        }
      }

      // NOTE: project_type is NOT in the server schema for Project nodes.
      // It gets silently stripped on write. Removed this proposal generator (2026-03-05).

      // Goal: missing success_criteria — suggest generic baseline
      // NOTE: success_criteria is in Goal schema but NOT in Project schema
      if (node.node_type === 'Goal' && 
          (!node.props?.success_criteria || node.props.success_criteria.length === 0)) {
        const type = node.node_type;
        proposals.push(proposal({
          type: 'data_enrichment',
          target: { uid: node.uid, label: node.label, node_type: node.node_type },
          action: `Define baseline success criteria for ${type}`,
          reason: `${type} "${node.label}" is missing success criteria. Proposing a baseline to track progress.`,
          impact: 'low',
          new_value: { 
            success_criteria: [
              `Core objectives in "${node.label}" description are achieved.`,
              `Stakeholder expectations for "${node.label}" are met.`
            ]
          },
        }));
      }
    }
  } catch (e) {
    console.error('Data quality check failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 2: Contradiction Patrol ────────────────────────────────────────

async function analyzeContradictions() {
  const proposals = [];

  const NEWS_KEYWORDS = [
    'iran', 'protest', 'strike', 'election', 'war', 'ceasefire', 'geneva',
    'polymarket', 'trump', 'regime', 'attack', 'starmer', 'xi jinping',
    'tim cook', 'ukraine', 'taiwan', 'treaty', 'nuclear',
  ];

  function isTimeSensitive(node) {
    const text = `${node.label} ${node.summary || ''} ${node.props?.content || ''}`.toLowerCase();
    return NEWS_KEYWORDS.some(kw => text.includes(kw));
  }

  try {
    // Server exposes GET /contradictions — returns edges of type CONTRADICTS with resolution_status=unresolved
    const contradictions = await mg.retrieve('contradictions').catch(() => []);

    for (const c of contradictions) {
      const [nodeA, nodeB] = await Promise.all([
        mg.getNode(c.node_a_uid),
        mg.getNode(c.node_b_uid),
      ]);
      if (!nodeA || !nodeB) continue;

      const timeSensitive = isTimeSensitive(nodeA) || isTimeSensitive(nodeB);
      const newer = (nodeA.created_at || 0) >= (nodeB.created_at || 0) ? nodeA : nodeB;
      const older = newer === nodeA ? nodeB : nodeA;
      const ageDays = daysBetween((older.created_at || 0) * 1000, (newer.created_at || 0) * 1000);

      // Always propose explicit REFUTES edge to make contradiction visible
      proposals.push(proposal({
        type: 'edge_addition',
        target: { uid: newer.uid, label: newer.label, node_type: newer.node_type },
        action: `Add REFUTES edge: "${newer.label}" → "${older.label}"`,
        reason: `Contradiction detected. Adding REFUTES edge makes this explicit in the graph and ensures both claims surface together in context retrieval.`,
        edge_details: {
          from_uid: newer.uid,
          to_uid: older.uid,
          edge_type: 'REFUTES',
          confidence: 0.75,
        },
        impact: 'medium',
        contradiction_details: {
          contradicting_uid: older.uid,
          contradicting_label: older.label,
          age_diff_days: Math.round(ageDays),
          time_sensitive: timeSensitive,
          resolution_strategy: timeSensitive && ageDays < 60 ? 'favor_newer' : 'manual_review',
        },
      }));

      // For time-sensitive events, also suggest confidence adjustment on newer claim
      if (timeSensitive && ageDays < 60 && (newer.confidence || 0.5) < 0.75) {
        proposals.push(proposal({
          type: 'confidence_update',
          target: { uid: newer.uid, label: newer.label, node_type: newer.node_type },
          action: `Boost confidence of newer claim (time-sensitive, ${Math.round(ageDays)}d newer)`,
          reason: `"${newer.label}" contradicts older claim "${older.label}" (${Math.round(ageDays)} days older). For ongoing news events, recency is strong signal — consider raising confidence.`,
          old_value: { confidence: newer.confidence },
          new_value: { confidence: Math.min(0.85, (newer.confidence || 0.5) + 0.15) },
          delta: 0.15,
          impact: 'medium',
          contradiction_details: {
            contradicting_uid: older.uid,
            contradicting_label: older.label,
            resolution_strategy: 'favor_newer',
          },
        }));
      }
    }
  } catch (e) {
    console.error('Contradiction patrol failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 3: Recency-Salience Calibration ────────────────────────────────

async function analyzeRecencySalience() {
  const proposals = [];

  try {
    // Active goals → keep salience high
    const goals = await mg.retrieve('active_goals', { limit: 100 });
    for (const node of goals) {
      if ((node.salience || 0.5) < 0.8) {
        proposals.push(proposal({
          type: 'salience_boost',
          target: { uid: node.uid, label: node.label, node_type: node.node_type },
          action: 'Boost salience — active goal below visibility threshold (0.8)',
          reason: `Active goal salience is ${node.salience?.toFixed(2) || '?'}. Active goals should always surface in context.`,
          old_value: { salience: node.salience },
          new_value: { salience: Math.min(1.0, (node.salience || 0.5) + 0.1) },
          delta: 0.1,
          impact: 'low',
        }));
      }
    }

    // Hard constraints → keep salience high
    const constraints = await mg.getNodes({ nodeType: 'Constraint', limit: 100 });
    for (const node of (constraints.items || constraints || [])) {
      if (node.props?.hard === true && (node.salience || 0.5) < 0.75) {
        proposals.push(proposal({
          type: 'salience_boost',
          target: { uid: node.uid, label: node.label, node_type: node.node_type },
          action: 'Boost salience — hard constraint below visibility threshold (0.75)',
          reason: `Hard constraint has salience ${node.salience?.toFixed(2) || '?'}. Hard constraints must surface in context retrieval.`,
          old_value: { salience: node.salience },
          new_value: { salience: 0.75 },
          delta: 0.75 - (node.salience || 0.5),
          impact: 'low',
        }));
      }
    }

    // Batch nightly decay (server-side)
    proposals.push(proposal({
      type: 'salience_decay',
      target: { uid: '__batch__', label: 'All nodes — nightly half-life decay', node_type: 'system' },
      action: 'Apply nightly half-life salience decay (30-day half-life, server-side)',
      reason: 'Gradual decay prevents stale nodes from dominating context. Nodes touched in sessions will regain salience naturally.',
      new_value: { half_life_secs: 2592000 },
      impact: 'low',
    }));

  } catch (e) {
    console.error('Recency-salience failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 4: Weak Claim Triage ──────────────────────────────────────────

async function analyzeWeakClaims() {
  const proposals = [];
  const MAX = 20;

  try {
    const weak = await mg.retrieve('weak_claims', { limit: 100 });
    const now_ts = Date.now();

    for (const claim of weak) {
      if (proposals.length >= MAX) break;
      const daysOld = daysBetween((claim.created_at || 0) * 1000, now_ts);
      if (daysOld < 3) continue; // Ignore brand-new nodes

      proposals.push(proposal({
        type: 'belief_revision',
        target: { uid: claim.uid, label: claim.label, node_type: claim.node_type },
        action: `Review weak claim (confidence ${claim.confidence?.toFixed(2) || '?'}, ${Math.round(daysOld)}d old)`,
        reason: `"${claim.label}" has been below confidence 0.5 for ${Math.round(daysOld)} days. Options: add supporting evidence, lower further, or tombstone if no longer relevant.`,
        old_value: { confidence: claim.confidence },
        impact: 'medium',
      }));
    }
  } catch (e) {
    console.error('Weak claims failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 5: Inference Chain Completion ──────────────────────────────────
// Only follows SUPPORTS and IMPLIES edges — DERIVED_FROM is not transitive.
// Starts from any node type, not just Claims.

async function analyzeInferenceChains() {
  const proposals = [];
  const MAX = 10;
  // Only genuinely transitive edge types — NOT DERIVED_FROM
  const CHAIN_TYPES = ['SUPPORTS', 'IMPLIES'];

  try {
    // Sample broadly across node types, not just Claims
    const allNodes = await mg.getNodes({ limit: 80 });

    for (const nodeA of (allNodes.items || allNodes || [])) {
      if (proposals.length >= MAX) break;

      const edgesA = await mg.getEdges(nodeA.uid);
      const hopA = edgesA.filter(e => CHAIN_TYPES.includes(e.edge_type));

      for (const e1 of hopA) {
        if (proposals.length >= MAX) break;

        const edgesB = await mg.getEdges(e1.to_uid);
        const hopB = edgesB.filter(e => CHAIN_TYPES.includes(e.edge_type));

        for (const e2 of hopB) {
          // Avoid self-loops and back-edges to start node
          if (e2.to_uid === nodeA.uid) continue;
          if (e1.to_uid === nodeA.uid) continue;
          if (proposals.length >= MAX) break;

          // Only suggest A→C if it doesn't exist in either direction
          // (mg.edgeBetween removed in Phase 0.5 — use getEdges + filter instead)
          const [fwdEdges, revEdges] = await Promise.all([
            mg.getEdges(nodeA.uid).catch(() => []),
            mg.getEdges(e2.to_uid).catch(() => []),
          ]);
          const fwd = fwdEdges.filter(e => e.to_uid === e2.to_uid);
          const rev = revEdges.filter(e => e.to_uid === nodeA.uid);
          if (fwd.length || rev.length) continue;

          // Fetch middle and end node labels for readable proposal text
          const [nodeB, nodeC] = await Promise.all([
            mg.getNode(e1.to_uid),
            mg.getNode(e2.to_uid),
          ]);

          proposals.push(proposal({
            type: 'edge_addition',
            target: { uid: nodeA.uid, label: nodeA.label, node_type: nodeA.node_type },
            action: `Add transitive IMPLIES: "${nodeA.label}" → "${nodeC?.label || e2.to_uid.slice(0,8)}"`,
            reason: `Chain: "${nodeA.label}" -[${e1.edge_type}]→ "${nodeB?.label || e1.to_uid.slice(0,8)}" -[${e2.edge_type}]→ "${nodeC?.label || e2.to_uid.slice(0,8)}" but no direct link. Review whether the transitive implication holds.`,
            edge_details: {
              from_uid: nodeA.uid,
              to_uid: e2.to_uid,
              edge_type: 'IMPLIES',
              // Confidence degrades through the chain
              confidence: Math.min(nodeA.confidence || 1, e1.confidence || 1, e2.confidence || 1) * 0.85,
            },
            impact: 'medium',
          }));
        }
      }
    }
  } catch (e) {
    console.error('Inference chains failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 6: Belief Revision ─────────────────────────────────────────────

async function analyzeBeliefRevision() {
  const proposals = [];

  try {
    const claims = await mg.getNodes({ nodeType: 'Claim', limit: 100 });

    for (const claim of (claims.items || claims || [])) {
      const incoming = await mg.edgesTo(claim.uid);
      const supports = incoming.filter(e => e.edge_type === 'SUPPORTS');
      const refutes  = incoming.filter(e => e.edge_type === 'REFUTES');
      const conf = claim.confidence ?? 0.5;

      // Determine dominant signal — if both supports and refutes exist, net wins
      const netSignal = supports.length - refutes.length;

      if (supports.length >= 2 && refutes.length === 0 && conf < 0.65) {
        // Clear support, no counter-evidence → boost
        const avgSupConf = supports.reduce((s, e) => s + (e.confidence ?? 0.5), 0) / supports.length;
        const newConf = Math.min(0.9, conf + 0.1);
        proposals.push(proposal({
          type: 'confidence_update',
          target: { uid: claim.uid, label: claim.label, node_type: claim.node_type },
          action: `Raise confidence (${supports.length} SUPPORTS, avg ${avgSupConf.toFixed(2)})`,
          reason: `"${claim.label}" has ${supports.length} supporting edges (avg confidence ${avgSupConf.toFixed(2)}) but claim confidence is only ${conf.toFixed(2)}. No counter-evidence. A boost is warranted.`,
          old_value: { confidence: conf },
          new_value: { confidence: newConf },
          delta: newConf - conf,
          impact: calculateImpact(newConf - conf),
        }));
      } else if (refutes.length > 0 && conf > 0.65 && netSignal < 0) {
        // More refutation than support → lower confidence
        const newConf = Math.max(0.3, conf - 0.15);
        proposals.push(proposal({
          type: 'confidence_update',
          target: { uid: claim.uid, label: claim.label, node_type: claim.node_type },
          action: `Lower confidence (${refutes.length} REFUTES vs ${supports.length} SUPPORTS, conf=${conf.toFixed(2)})`,
          reason: `"${claim.label}" has more refuting edges (${refutes.length}) than supporting (${supports.length}) but confidence is still ${conf.toFixed(2)}. Net signal is negative.`,
          old_value: { confidence: conf },
          new_value: { confidence: newConf },
          delta: newConf - conf,
          impact: 'high',
        }));
      } else if (supports.length >= 1 && refutes.length >= 1) {
        // Mixed signals — flag for manual review without suggesting a direction
        proposals.push(proposal({
          type: 'belief_revision',
          target: { uid: claim.uid, label: claim.label, node_type: claim.node_type },
          action: `Mixed evidence — review manually (${supports.length} SUPPORTS, ${refutes.length} REFUTES)`,
          reason: `"${claim.label}" has both supporting and refuting edges. Net signal is ambiguous. Human review needed to determine whether confidence (${conf.toFixed(2)}) should change.`,
          old_value: { confidence: conf },
          impact: 'medium',
        }));
      }
    }
  } catch (e) {
    console.error('Belief revision failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 7: Edge Type Consistency ───────────────────────────────────────
// Only enforces a small set of clearly wrong combinations — not an exhaustive
// schema check. The graph was built organically so many legitimate edges won't
// match a strict canonical map. We only flag truly anomalous patterns.

async function analyzeEdgeTypeConsistency() {
  const proposals = [];

  // Only flag combinations that are clearly semantically wrong.
  // These are DISALLOWED source→edge→target patterns (not an exhaustive allowlist).
  // A→[EDGE_TYPE]→B is flagged if B's node_type is in the disallowed set for that edge.
  const disallowedTargets = {
    // A Source node can't SUPPORT or REFUTE a claim (it DERIVED_FROM or is evidence for)
    SUPPORTS:        new Set(['Source', 'Session']),
    REFUTES:         new Set(['Source', 'Session']),
    // AUTHORED_BY should point to a person/org, not another claim or project
    AUTHORED_BY:     new Set(['Claim', 'Project', 'Goal', 'Decision', 'Constraint']),
    // DECOMPOSES_INTO should stay within task/plan hierarchy
    DECOMPOSES_INTO: new Set(['Claim', 'Constraint', 'Entity', 'Source', 'Session']),
  };

  const MAX_PROPOSALS = 15;

  try {
    // Paginate through all nodes
    let offset = 0, hasMore = true;
    const allNodes = [];
    while (hasMore) {
      const batch = await mg.getNodes({ limit: 100, offset });
      const nodes = batch.items || batch || [];
      allNodes.push(...nodes);
      hasMore = nodes.length === 100;
      offset += 100;
    }

    for (const node of allNodes) {
      if (proposals.length >= MAX_PROPOSALS) break;
      const outgoing = await mg.getEdges(node.uid);

      for (const edge of outgoing) {
        if (proposals.length >= MAX_PROPOSALS) break;
        const disallowed = disallowedTargets[edge.edge_type];
        if (!disallowed) continue; // Not a monitored edge type

        const target = await mg.getNode(edge.to_uid);
        if (!target) continue;

        if (disallowed.has(target.node_type)) {
          proposals.push(proposal({
            type: 'schema_fix',
            target: { uid: node.uid, label: node.label, node_type: node.node_type },
            action: `Suspicious edge: "${node.label}" -[${edge.edge_type}]→ "${target.label}" [${target.node_type}]`,
            reason: `${edge.edge_type} edges pointing to ${target.node_type} nodes are unusual. This may be a misclassified edge type or node type. Review and correct if needed.`,
            schema_violation: {
              missing_props: [],
              invalid_props: [{
                prop: 'edge_target_type',
                current: `${edge.edge_type} → ${target.node_type}`,
                note: `${target.node_type} is an unexpected target for ${edge.edge_type}`,
              }],
            },
            impact: 'low',
          }));
        }
      }
    }
  } catch (e) {
    console.error('Edge type consistency failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 8: Bridge Node Detection ───────────────────────────────────────
// Finds the top-N structurally important nodes by connection count × type diversity.
// Returns at most 5 proposals (the most important bridges only).
// Note: true betweenness centrality is too expensive; this is a heuristic approximation.

async function analyzeBridgeNodes() {
  const proposals = [];
  const TOP_N = 5;
  const MIN_DISTINCT_TYPES = 6;  // Raised from 4 — only flag genuinely cross-cutting nodes
  const MIN_CONNECTIONS = 8;     // Raised from 5 — must be a real hub

  try {
    // Paginate through all nodes
    let offset = 0, hasMore = true;
    const allNodes = [];
    while (hasMore) {
      const batch = await mg.getNodes({ limit: 100, offset });
      const nodes = batch.items || batch || [];
      allNodes.push(...nodes);
      hasMore = nodes.length === 100;
      offset += 100;
    }

    // Score each node by connection count
    const candidates = [];
    for (const node of allNodes) {
      const [out, inc] = await Promise.all([mg.getEdges(node.uid), mg.edgesTo(node.uid)]);
      const totalConns = out.length + inc.length;
      if (totalConns < MIN_CONNECTIONS) continue;
      candidates.push({ node, out, inc, totalConns });
    }

    // Sort by connection count descending, take top 20 for type-diversity check
    candidates.sort((a, b) => b.totalConns - a.totalConns);
    const toCheck = candidates.slice(0, 20);

    const bridges = [];
    for (const { node, out, inc, totalConns } of toCheck) {
      if ((node.salience || 0.5) >= 0.8) continue; // Already salient, skip

      // Fetch connected node types (sample up to 20 neighbors)
      const connectedUids = [...new Set([
        ...out.map(e => e.to_uid),
        ...inc.map(e => e.from_uid),
      ].filter(Boolean))].slice(0, 20);

      const connectedTypes = new Set();
      for (const uid of connectedUids) {
        const n = await mg.getNode(uid);
        if (n?.node_type) connectedTypes.add(n.node_type);
      }

      if (connectedTypes.size >= MIN_DISTINCT_TYPES) {
        bridges.push({ node, totalConns, connectedTypes, typeCount: connectedTypes.size });
      }
    }

    // Sort by type diversity × connection count, take top N
    bridges.sort((a, b) => (b.typeCount * b.totalConns) - (a.typeCount * a.totalConns));

    for (const { node, totalConns, connectedTypes } of bridges.slice(0, TOP_N)) {
      proposals.push(proposal({
        type: 'salience_boost',
        target: { uid: node.uid, label: node.label, node_type: node.node_type },
        action: `Boost salience — structural bridge (${totalConns} edges, ${connectedTypes.size} node types)`,
        reason: `"${node.label}" connects ${totalConns} nodes across ${connectedTypes.size} distinct types: ${[...connectedTypes].join(', ')}. This node bridges multiple clusters and should surface readily in context retrieval.`,
        old_value: { salience: node.salience },
        new_value: { salience: Math.min(0.9, (node.salience || 0.5) + 0.15) },
        delta: 0.15,
        impact: 'low',
      }));
    }
  } catch (e) {
    console.error('Bridge node detection failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 9: Goal Staleness ───────────────────────────────────────────────

async function analyzeGoalStaleness() {
  const proposals = [];
  const STALE_DAYS = 30;

  try {
    const goals = await mg.retrieve('active_goals', { limit: 100 });
    const now_ts = Date.now();

    for (const goal of goals) {
      const lastTouched = (goal.updated_at || goal.created_at || 0) * 1000;
      const daysStale = daysBetween(lastTouched, now_ts);

      if (daysStale > STALE_DAYS) {
        proposals.push(proposal({
          type: 'goal_review',
          target: { uid: goal.uid, label: goal.label, node_type: goal.node_type },
          action: `Review stale goal — no update in ${Math.round(daysStale)} days`,
          reason: `Goal "${goal.label}" last updated ${Math.round(daysStale)} days ago. Is it still active? Achieved? Consider archiving or adding a progress note.`,
          old_value: { status: goal.props?.status, updated_at: goal.updated_at },
          impact: 'medium',
        }));
      }
    }
  } catch (e) {
    console.error('Goal staleness failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 10: Decision Expiration ────────────────────────────────────────

async function analyzeDecisionExpiration() {
  const proposals = [];

  try {
    // mg.openDecisions() removed in Phase 0.5 — fetch all Decision nodes and filter by status
    const allDecNodes = await mg.getNodes({ nodeType: 'Decision', limit: 200 });
    const decItems = Array.isArray(allDecNodes) ? allDecNodes : (allDecNodes?.items || []);
    const decisions = decItems.filter(d => d.props?.status === 'open');
    const now_ts = Date.now();

    for (const dec of decisions) {
      const reviewAfter = dec.props?.review_after;
      if (!reviewAfter) continue;

      const reviewTs = new Date(reviewAfter).getTime();
      if (now_ts > reviewTs) {
        const daysOverdue = daysBetween(reviewTs, now_ts);
        proposals.push(proposal({
          type: 'decision_expired',
          target: { uid: dec.uid, label: dec.label, node_type: dec.node_type },
          action: `Review overdue decision — ${Math.round(daysOverdue)}d past review date (${reviewAfter})`,
          reason: `Decision "${dec.label}" had review_after=${reviewAfter}, now ${Math.round(daysOverdue)} days overdue. Should be reaffirmed, revised, or closed.`,
          old_value: { review_after: reviewAfter, status: dec.props?.status },
          impact: 'high',
        }));
      }
    }
  } catch (e) {
    console.error('Decision expiration failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 11: Source Drift Detection ─────────────────────────────────────

async function analyzeSourceDrift() {
  const proposals = [];
  const fs = require('fs');

  try {
    const sources = await mg.getNodes({ nodeType: 'Source', limit: 100 });

    for (const node of (sources.items || sources || [])) {
      const sourcePath = node.props?.source_path || node.props?.path;
      if (!sourcePath) continue;

      let stat;
      try { stat = fs.statSync(sourcePath); } catch { continue; }

      const fileMtimeMs  = stat.mtimeMs;
      const nodeUpdateMs = (node.updated_at || node.created_at || 0) * 1000;

      if (fileMtimeMs > nodeUpdateMs) {
        const daysDrift = daysBetween(nodeUpdateMs, fileMtimeMs);
        proposals.push(proposal({
          type: 'source_drift',
          target: { uid: node.uid, label: node.label, node_type: node.node_type },
          action: `Re-extract "${sourcePath}" — file changed ${Math.round(daysDrift)}d after node`,
          reason: `Source file "${sourcePath}" modified ${new Date(fileMtimeMs).toISOString().split('T')[0]} but node last updated ${new Date(nodeUpdateMs).toISOString().split('T')[0]}. Nodes derived from this source may be stale.`,
          old_value: { node_updated: new Date(nodeUpdateMs).toISOString() },
          new_value: { file_mtime: new Date(fileMtimeMs).toISOString() },
          impact: daysDrift > 7 ? 'high' : 'medium',
        }));
      }
    }
  } catch (e) {
    console.error('Source drift failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 12: Trending Detection ─────────────────────────────────────────
// Uses updated_at (not created_at) as the recency signal — nodes touched in
// recent sessions are "active." created_at reflects extraction batch time and
// is misleading as a trending proxy.

async function analyzeTrending() {
  const proposals = [];
  const WINDOW = 7; // days

  try {
    // Paginate to get all nodes
    let offset = 0, hasMore = true;
    const allNodes = [];
    while (hasMore) {
      const batch = await mg.getNodes({ limit: 100, offset });
      const nodes = batch.items || batch || [];
      allNodes.push(...nodes);
      hasMore = nodes.length === 100;
      offset += 100;
    }

    const now_ts = Date.now();
    const wordCount = { recent: {}, prior: {} };

    for (const node of allNodes) {
      // Use updated_at as activity signal; fall back to created_at only if no update exists
      const activityTs = (node.updated_at || node.created_at || 0) * 1000;
      const ageDays = (now_ts - activityTs) / (24 * 60 * 60 * 1000);

      // Skip nodes that have never been touched (updated_at === created_at within 60s)
      const wasUpdated = node.updated_at && node.created_at &&
        Math.abs(node.updated_at - node.created_at) > 60;
      if (!node.updated_at || !wasUpdated) continue;

      const bucket = ageDays <= WINDOW ? 'recent' : ageDays <= WINDOW * 2 ? 'prior' : null;
      if (!bucket) continue;

      const words = `${node.label} ${node.summary || ''}`.toLowerCase()
        .split(/\W+/).filter(w => w.length > 4 && w.length < 30);

      for (const word of words) {
        wordCount[bucket][word] = (wordCount[bucket][word] || 0) + 1;
      }
    }

    // Find words trending up in recently-touched nodes vs prior week
    const trending = [];
    for (const [word, recent] of Object.entries(wordCount.recent)) {
      const prior = wordCount.prior[word] || 0;
      if (recent >= 2 && recent > prior + 1) {
        trending.push({ word, recent, prior, delta: recent - prior });
      }
    }

    trending.sort((a, b) => b.delta - a.delta);

    for (const t of trending.slice(0, 5)) {
      proposals.push(proposal({
        type: 'trending',
        target: { uid: '__trending__', label: `Topic: "${t.word}"`, node_type: 'system' },
        action: `Trending topic: "${t.word}" (${t.recent} active nodes this week vs ${t.prior} prior)`,
        reason: `"${t.word}" appears in ${t.recent} recently-updated nodes this week vs ${t.prior} the week prior. This indicates active engagement — check if related goals or projects need attention.`,
        impact: 'low',
        trending_details: {
          word: t.word,
          active_nodes_recent: t.recent,
          active_nodes_prior: t.prior,
          percent_change: t.prior > 0 ? Math.round((t.delta / t.prior) * 100) : null,
          window_days: WINDOW,
          signal: 'updated_at',
        },
      }));
    }
  } catch (e) {
    console.error('Trending detection failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 13: Question Answering ─────────────────────────────────────────
// Flags open questions for human + agent follow-up. Does NOT attempt web search
// directly (the Brave API is not accessible from this context). Instead, it
// produces proposals with a `requires_web_search: true` flag so the cron agent
// can use its own web_search tool to research answers before presenting them.

async function analyzeQuestionAnswering() {
  const proposals = [];

  try {
    const questions = await mg.retrieve('open_questions', { limit: 100 });
    if (!questions.length) return proposals;

    const now_ts = Date.now();

    for (const q of questions.slice(0, 10)) { // Cap at 10
      const questionText = q.props?.question_text || q.label;
      const daysOld = daysBetween((q.created_at || 0) * 1000, now_ts);

      proposals.push(proposal({
        type: 'answer_question',
        target: { uid: q.uid, label: q.label, node_type: q.node_type },
        action: `Research open question (${Math.round(daysOld)}d old): "${questionText}"`,
        reason: `This question has been open for ${Math.round(daysOld)} days without an answer node. The cron agent should web-search for an answer, then either: (1) create an answer node and link it, or (2) confirm the question is still unanswerable.`,
        requires_web_search: true,
        search_query: questionText,
        impact: daysOld > 14 ? 'high' : 'medium',
      }));
    }
  } catch (e) {
    console.error('Question answering failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 14: Task Suggestion ────────────────────────────────────────────
// Looks at active Goals and Projects, finds recent momentum signals (Decisions,
// Observations, Claims updated recently), and proposes up to 3 concrete next
// tasks for the most active work areas.

async function analyzeTaskSuggestions() {
  const proposals = [];
  const MAX_TASKS = 8;

  try {
    const now_ts = Date.now();
    const RECENT_DAYS = 7;

    // Get all nodes we need
    const [goalBatch, projectBatch, taskBatch, recentBatch] = await Promise.all([
      mg.getNodes({ nodeType: 'Goal',    limit: 50 }),
      mg.getNodes({ nodeType: 'Project', limit: 50 }),
      mg.getNodes({ nodeType: 'Task',    limit: 100 }),
      mg.getNodes({ limit: 250 }),  // for recency signals
    ]);

    const goals    = (goalBatch.items    || goalBatch    || []).filter(g => !g.tombstone_at && g.props?.status === 'active');
    const projects = (projectBatch.items || projectBatch || []).filter(p => !p.tombstone_at && ['active', 'live'].includes(p.props?.status));
    const tasks    = (taskBatch.items    || taskBatch    || []).filter(t => !t.tombstone_at);
    const allNodes = (recentBatch.items  || recentBatch  || []);

    // Find recently-touched nodes as momentum signals
    const recentNodes = allNodes.filter(n => {
      const ageDays = (now_ts - (n.updated_at || n.created_at || 0) * 1000) / 86400000;
      return ageDays <= RECENT_DAYS;
    });

    // Build set of existing task labels (normalized) to avoid proposing duplicates in the graph
    const existingTaskLabels = new Set(tasks.map(t => t.label.toLowerCase().trim()));

    // Also load recent dream files (last 7 days) to avoid re-proposing tasks
    // that were already suggested but not yet actioned
    const recentlyProposedForUids = new Set();
    try {
      const dreamDir = require('path').join(__dirname, '.dream');
      const fs = require('fs');
      const cutoff = Date.now() - 7 * 86400000;
      fs.readdirSync(dreamDir)
        .filter(f => f.endsWith('.json'))
        .filter(f => {
          const dateMs = new Date(f.replace('.json', '')).getTime();
          return dateMs >= cutoff && f !== `${new Date().toISOString().split('T')[0]}.json`;
        })
        .forEach(f => {
          try {
            const d = JSON.parse(fs.readFileSync(require('path').join(dreamDir, f), 'utf8'));
            (d.proposals || [])
              .filter(p => p.type === 'task_suggestion' && !p.rejected)
              .forEach(p => recentlyProposedForUids.add(p.target?.uid));
          } catch {}
        });
    } catch {}

    // Score each goal+project by recency signal strength (momentum)
    const scored = [];

    for (const goal of goals) {
      // GoalProps has a progress field; ProjectProps does not — use status as proxy
      const progress = typeof goal.props?.progress === 'number' ? goal.props.progress : 0;
      if (progress >= 1.0) continue;
      const keywords = goal.label.toLowerCase().split(/\s+/).filter(w => w.length > 3);
      const momentum = recentNodes.filter(n =>
        keywords.some(kw =>
          n.label.toLowerCase().includes(kw) ||
          (n.summary || '').toLowerCase().includes(kw)
        )
      ).length;
      scored.push({ node: goal, type: 'Goal', progress, momentum });
    }

    for (const project of projects) {
      // Projects use status rather than numeric progress.
      // 'live' = shipped/operational, skip unless specific action needed.
      // Only suggest tasks for projects with recent momentum (actively being worked on).
      const status = project.props?.status || 'active';
      const keywords = project.label.toLowerCase().split(/\s+/).filter(w => w.length > 3);
      const momentum = recentNodes.filter(n =>
        keywords.some(kw =>
          n.label.toLowerCase().includes(kw) ||
          (n.summary || '').toLowerCase().includes(kw)
        )
      ).length;

      // Skip 'live' projects unless there's active momentum (they're operational, not blocked)
      if (status === 'live' && momentum < 3) continue;
      // Use momentum as a proxy for "needs attention" — only surface if actively discussed
      if (momentum === 0) continue;

      // Use a status-based pseudo-progress (live=0.7, active=0.3, flagged=0.1)
      const pseudoProgress = status === 'live' ? 0.7 : status === 'active' ? 0.3 : 0.1;
      scored.push({ node: project, type: 'Project', progress: pseudoProgress, momentum });
    }

    // Sort: highest momentum first
    scored.sort((a, b) => b.momentum - a.momentum || a.progress - b.progress);

    // Generate one task suggestion per top work area, up to MAX_TASKS
    for (const { node, type, progress, momentum } of scored.slice(0, MAX_TASKS)) {
      // Skip if we already proposed a task for this node in the last 7 days (pending review)
      if (recentlyProposedForUids.has(node.uid)) continue;

      // Derive a concrete task from context
      const contextNodes = recentNodes
        .filter(n => {
          const kws = node.label.toLowerCase().split(/\s+/).filter(w => w.length > 3);
          return kws.some(kw => n.label.toLowerCase().includes(kw) || (n.summary||'').toLowerCase().includes(kw));
        })
        .filter(n => ['Decision', 'Observation', 'Claim', 'Anomaly'].includes(n.node_type))
        .sort((a, b) => (b.updated_at || 0) - (a.updated_at || 0))
        .slice(0, 3);

      const contextStr = contextNodes.map(n => `${n.node_type}: "${n.label}"`).join('; ');
      const progressPct = Math.round(progress * 100);

      // Build a concrete task label — not generic "Review blockers"
      const shortName = node.label.split(/\s+/).slice(0, 4).join(' ') + (node.label.split(/\s+/).length > 4 ? '…' : '');
      let suggestedLabel, suggestedDescription;

      if (type === 'Project' && progress >= 0.6) {
        // Live/near-complete project with momentum — surface what's being worked on
        suggestedLabel = `Next step: ${shortName}`;
        suggestedDescription = `"${node.label}" is active and operational. Recent graph activity: ${contextStr || 'none'}. What's the concrete next milestone?`;
      } else if (contextStr) {
        // There's recent activity — make the task specific to it
        const firstContext = contextNodes[0];
        suggestedLabel = firstContext
          ? `Follow up: ${firstContext.label.slice(0, 45)}`
          : `Next step: ${shortName}`;
        suggestedDescription = `"${node.label}" has recent activity — ${contextStr}. What action does this require?`;
      } else {
        suggestedLabel = `Review status: ${shortName}`;
        suggestedDescription = `"${node.label}" has no recent graph activity in the past ${RECENT_DAYS} days. Is it still active?`;
      }

      // Skip if very similar task already exists in the graph
      const labelNorm = suggestedLabel.toLowerCase();
      if (existingTaskLabels.has(labelNorm)) continue;
      const tooSimilar = [...existingTaskLabels].some(el =>
        node.label.toLowerCase().split(/\s+/).filter(w=>w.length>4).some(kw => el.includes(kw))
      );
      if (tooSimilar) continue;

      proposals.push(proposal({
        type: 'task_suggestion',
        target: { uid: node.uid, label: node.label, node_type: node.node_type },
        action: `Create task: "${suggestedLabel}"`,
        reason: suggestedDescription,
        new_value: {
          task_label: suggestedLabel,
          task_description: suggestedDescription,
          parent_uid: node.uid,
          parent_type: type,
          momentum_signals: momentum,
        },
        impact: momentum > 3 ? 'high' : 'medium',
      }));
    }
  } catch (e) {
    console.error('Task suggestion failed:', e.message);
  }

  return proposals;
}

async function analyzeTrivialDecisions() {
  const proposals = [];
  const TRIVIAL_LENGTH = 30; // chars

  try {
    const batch = await mg.getNodes({ nodeType: 'Decision', limit: 100 });
    const decisions = batch.items || batch || [];

    for (const node of decisions) {
      const p = node.props || {};
      const rationale = (p.decision_rationale || node.summary || '').trim();
      const description = (p.description || '').trim();
      
      // If it's very short and not already low priority
      if (rationale.length < TRIVIAL_LENGTH && description.length < TRIVIAL_LENGTH && p.priority !== 'low') {
        proposals.push(proposal({
          type: 'schema_fix', // using schema_fix as it's a metadata update
          target: { uid: node.uid, label: node.label, node_type: node.node_type },
          action: 'Mark decision as low priority (trivial)',
          reason: `Decision "${node.label}" has very brief rationale (${rationale.length} chars). It may be too trivial for a full Decision node. Marking as low priority to hide from default timeline view.`,
          impact: 'low',
          new_value: { priority: 'low' },
        }));
      }
    }
  } catch (e) {
    console.error('Trivial decisions check failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 15: Duplicate Node Detection ────────────────────────────────────
// Finds nodes with identical (normalized) labels and proposes merging the
// shell/empty duplicate into the richer one.

async function analyzeDuplicateNodes() {
  const proposals = [];

  try {
    // Paginate all nodes
    let offset = 0, hasMore = true;
    const allNodes = [];
    while (hasMore) {
      const batch = await mg.getNodes({ limit: 250, offset });
      const nodes = batch.items || batch || [];
      allNodes.push(...nodes);
      hasMore = nodes.length === 250;
      offset += 250;
    }

    // Group by normalized label
    const byLabel = {};
    for (const n of allNodes) {
      const key = n.label.trim().toLowerCase();
      if (!byLabel[key]) byLabel[key] = [];
      byLabel[key].push(n);
    }

    for (const [, nodes] of Object.entries(byLabel)) {
      if (nodes.length < 2) continue;

      // Sort richest first: salience desc, summary length desc, version desc
      nodes.sort((a, b) => {
        if (b.salience !== a.salience) return b.salience - a.salience;
        const aLen = (a.summary || '').length, bLen = (b.summary || '').length;
        if (bLen !== aLen) return bLen - aLen;
        return b.version - a.version;
      });

      const keep = nodes[0];
      for (const dupe of nodes.slice(1)) {
        // Only flag true duplicates: same node_type required.
        // Different types with the same label are intentional schema distinctions
        // (e.g. Entity "Aaron Goh" + Source "[Email] Aaron Goh" are NOT duplicates).
        if (dupe.node_type !== keep.node_type) continue;

        const isShell = !dupe.summary && dupe.salience <= 0.5;
        const impact = isShell ? 'low' : 'medium';

        proposals.push(proposal({
          type: 'dedup',
          target: { uid: dupe.uid, label: dupe.label, node_type: dupe.node_type },
          action: `Tombstone duplicate [${dupe.node_type}] "${dupe.label}" — keep ${keep.uid.slice(0, 8)} ([${keep.node_type}])`,
          reason: `"${dupe.label}" appears ${nodes.length}x. Duplicate [${dupe.node_type}] (sal=${dupe.salience.toFixed(2)}, ${isShell ? 'no summary' : 'has summary'}) is weaker than keep target [${keep.node_type}] (sal=${keep.salience.toFixed(2)}).`,
          old_value: { uid: dupe.uid, node_type: dupe.node_type, salience: dupe.salience },
          new_value: { merge_into: keep.uid, keep_label: keep.label, keep_type: keep.node_type },
          impact,
        }));
      }
    }
  } catch (e) {
    console.error('Duplicate detection failed:', e.message);
  }

  return proposals;
}

// ─── Analyzer 16: Orphan Node Detection ────────────────────────────────────────
// Finds nodes with zero edges (both directions) and proposes wiring them.

async function analyzeOrphanNodes() {
  const proposals = [];

  try {
    const checkTypes = ['Observation', 'Decision', 'Claim', 'Constraint', 'Task', 'Entity'];
    
    for (const t of checkTypes) {
      const r = await mg.getNodes({ nodeType: t, limit: 200 });
      const nodes = (r.items || r || []).filter(n => !n.tombstone_at);
      
      for (const n of nodes) {
        const outEdges = await mg.getEdges(n.uid);
        const inEdges = (await mg.request('GET', `/edges?to_uid=${n.uid}`)) || [];
        const liveOut = Array.isArray(outEdges) ? outEdges.filter(e => !e.tombstone_at) : [];
        const liveIn = Array.isArray(inEdges) ? inEdges.filter(e => !e.tombstone_at) : [];
        
        if (liveOut.length === 0 && liveIn.length === 0) {
          proposals.push(proposal({
            type: 'orphan_wire',
            target: { uid: n.uid, label: n.label, node_type: n.node_type },
            action: `Wire orphan [${n.node_type}] "${n.label}" to a relevant entity or project`,
            reason: `Node has 0 edges — invisible to graph traversal. Created ${new Date(n.created_at * 1000).toISOString().slice(0, 10)}.`,
            impact: 'medium',
          }));
        }
      }
    }
  } catch (e) {
    console.error('Orphan detection failed:', e.message);
  }

  return proposals;
}

// ─── Registry & Exports ───────────────────────────────────────────────────────

const analyzers = [
  { name: 'schema_compliance',      fn: analyzeSchemaCompliance,     schedule: 'daily' },
  { name: 'data_quality',           fn: analyzeDataQuality,           schedule: 'daily' },
  { name: 'contradictions',         fn: analyzeContradictions,        schedule: 'daily' },
  { name: 'recency_salience',       fn: analyzeRecencySalience,       schedule: 'daily' },
  { name: 'weak_claims',            fn: analyzeWeakClaims,            schedule: 'daily' },
  { name: 'source_drift',           fn: analyzeSourceDrift,           schedule: 'daily' },
  { name: 'inference_chains',       fn: analyzeInferenceChains,       schedule: 'mon_thu' },
  { name: 'belief_revision',        fn: analyzeBeliefRevision,        schedule: 'mon_thu' },
  { name: 'edge_type_consistency',  fn: analyzeEdgeTypeConsistency,   schedule: 'mon_thu' },
  { name: 'bridge_nodes',           fn: analyzeBridgeNodes,           schedule: 'wed_sat' },
  { name: 'trending',               fn: analyzeTrending,              schedule: 'daily' },
  { name: 'goal_staleness',         fn: analyzeGoalStaleness,         schedule: 'sunday' },
  { name: 'decision_expiration',    fn: analyzeDecisionExpiration,    schedule: 'sunday' },
  { name: 'question_answering',     fn: analyzeQuestionAnswering,     schedule: 'mon_thu' },
  { name: 'duplicate_nodes',        fn: analyzeDuplicateNodes,        schedule: 'daily' },
  { name: 'task_suggestions',       fn: analyzeTaskSuggestions,       schedule: 'daily' },
  { name: 'trivial_decisions',      fn: analyzeTrivialDecisions,      schedule: 'mon_thu' },
  { name: 'embedding_analysis',     fn: analyzeEmbeddings,            schedule: 'daily' },
  { name: 'rich_enrichment',        fn: analyzeRichEnrichment,        schedule: 'daily' },
  { name: 'orphan_detection',       fn: analyzeOrphanNodes,           schedule: 'daily' },
];

// Which analyzers to run by schedule
function getAnalyzersForSchedule(schedule) {
  const day = new Date().getDay(); // 0=Sun, 1=Mon ... 6=Sat
  const isMon = day === 1, isThu = day === 4;
  const isWed = day === 3, isSat = day === 6;
  const isSun = day === 0;

  return analyzers.filter(a => {
    switch (a.schedule) {
      case 'daily':   return true;
      case 'mon_thu': return isMon || isThu;
      case 'wed_sat': return isWed || isSat;
      case 'sunday':  return isSun;
      default:        return schedule === 'all';
    }
  });
}

module.exports = {
  analyzers,
  getAnalyzersForSchedule,
  generateProposalId,
  calculateImpact,
  proposal,
  // Named exports for testing
  analyzeSchemaCompliance,
  analyzeDataQuality,
  analyzeContradictions,
  analyzeRecencySalience,
  analyzeWeakClaims,
  analyzeInferenceChains,
  analyzeBeliefRevision,
  analyzeEdgeTypeConsistency,
  analyzeBridgeNodes,
  analyzeGoalStaleness,
  analyzeDecisionExpiration,
  analyzeSourceDrift,
  analyzeTrending,
  analyzeQuestionAnswering,
  analyzeDuplicateNodes,
  analyzeTaskSuggestions,
  analyzeTrivialDecisions,
  analyzeOrphanNodes,
};