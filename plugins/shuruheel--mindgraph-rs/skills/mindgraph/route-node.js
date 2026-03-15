/**
 * route-node.js — Shared node routing for MindGraph cognitive layer.
 *
 * Maps a node's type to the correct cognitive API endpoint.
 * Used by both import.js (extraction pipeline) and mindgraph-bridge.js (batch writes).
 *
 * Returns { result, skipped, fallback } where:
 *   - result: the API response (has .uid) or null on error
 *   - skipped: true if the type is intentionally not imported (Goal, Project, Source, Session)
 *   - fallback: true if the type was unknown and fell through to observation
 */

'use strict';

const mg = require('./mindgraph-client.js');

/**
 * Route a single node to the correct cognitive endpoint.
 *
 * @param {Object} node - { label, type, summary?, confidence?, props? }
 * @param {Object} [opts] - { agentId?, dryRun? }
 * @returns {Promise<{ result: Object|null, skipped: boolean, fallback: boolean }>}
 */
async function routeNode(node, opts = {}) {
  const { agentId, dryRun } = opts;
  const type = node.type.toLowerCase();
  const label = node.label;
  const content = node.props?.content || node.summary || '';
  const props = node.props || {};
  const summaryText = node.summary || content.slice(0, 300);

  if (dryRun) {
    return { result: { uid: `dry-${Math.random().toString(36).slice(2, 10)}`, label }, skipped: false, fallback: false };
  }

  let result = null;
  let skipped = false;
  let fallback = false;

  switch (type) {
    // ── Reality layer ──────────────────────────────────────────────────────
    case 'observation':
    case 'snippet':
      result = await mg.ingest(label, content, type, { confidence: node.confidence, agentId });
      break;
    case 'source':
      skipped = true;
      break;

    // ── Entity (dedup-safe) ──────────────────────────────────────────────
    case 'entity':
    case 'person':
    case 'organization':
    case 'service':
    case 'product':
    case 'location':
      result = await mg.findOrCreateEntity(label, node.type);
      break;

    // ── Epistemic layer ──────────────────────────────────────────────────
    case 'claim':
      result = await mg.addNode(label, {
        _type: 'Claim',
        content,
        truth_status: props.truth_status || 'asserted',
        certainty_degree: props.certainty_degree || 0.7,
      }, { summary: summaryText, confidence: node.confidence, agentId });
      break;
    case 'evidence':
      result = await mg.addNode(label, {
        _type: 'Evidence',
        description: content,
        evidence_type: props.evidence_type || 'qualitative',
        quantitative_value: props.quantitative_value,
      }, { summary: summaryText, confidence: node.confidence, agentId });
      break;
    case 'warrant':
      result = await mg.addNode(label, {
        _type: 'Warrant',
        principle: props.principle || content,
        warrant_type: props.warrant_type || 'general',
        strength: props.strength,
      }, { summary: summaryText, confidence: node.confidence, agentId });
      break;
    case 'argument':
      result = await mg.addArgument({
        claim: { label, content },
        evidence: props.evidence || [],
        warrant: props.warrant || null,
      });
      break;
    case 'hypothesis':
    case 'anomaly':
    case 'assumption':
    case 'question':
    case 'openquestion':
      result = await mg.addInquiry(label, content, type, props);
      break;
    case 'concept':
    case 'pattern':
    case 'mechanism':
    case 'model':
    case 'theory':
    case 'paradigm':
    case 'analogy':
    case 'theorem':
    case 'equation':
      result = await mg.addStructure(label, content, type, props);
      break;
    case 'method':
      result = await mg.addNode(label, {
        _type: 'Method', name: label, description: content,
        method_type: props.method_type, domain: props.domain,
        parameters: props.parameters, limitations: props.limitations,
      }, { summary: summaryText, confidence: node.confidence, agentId });
      break;
    case 'experiment':
      result = await mg.addNode(label, {
        _type: 'Experiment', description: content,
        status: props.status || 'proposed',
      }, { summary: summaryText, confidence: node.confidence, agentId });
      break;
    case 'modelevaluation':
      result = await mg.addNode(label, {
        _type: 'ModelEvaluation',
        evaluation_type: props.evaluation_type, metrics: props.metrics,
        failure_domains: props.failure_domains, comparison_to: props.comparison_to,
        evaluation_date: props.evaluation_date,
      }, { summary: summaryText, confidence: node.confidence, agentId });
      break;
    case 'inferencechain':
      result = await mg.addNode(label, {
        _type: 'InferenceChain', summary: content,
      }, { summary: summaryText, confidence: node.confidence, agentId });
      break;
    case 'sensitivityanalysis':
      result = await mg.addNode(label, {
        _type: 'SensitivityAnalysis',
        analysis_type: props.analysis_type, sensitivity_map: props.sensitivity_map,
        critical_inputs: props.critical_inputs, robustness_score: props.robustness_score,
      }, { summary: summaryText, confidence: node.confidence, agentId });
      break;
    case 'reasoningstrategy':
      result = await mg.addNode(label, {
        _type: 'ReasoningStrategy', name: label, description: content,
        strategy_type: props.strategy_type, applicable_contexts: props.applicable_contexts,
        limitations: props.limitations,
      }, { summary: summaryText, confidence: node.confidence, agentId });
      break;

    // ── Intent layer ─────────────────────────────────────────────────────
    case 'goal':
    case 'project':
      // Human-managed — never auto-created
      skipped = true;
      break;
    case 'milestone':
      result = await mg.addCommitment(label, content, 'milestone', props);
      break;
    case 'decision':
      result = await mg.deliberate({ action: 'open_decision', label, description: content, props });
      break;
    case 'option':
      result = await mg.deliberate({ action: 'add_option', label, description: content, props });
      break;
    case 'constraint':
      result = await mg.deliberate({
        action: 'add_constraint', label, description: content,
        props: { hard: props.hard ?? true, ...props },
      });
      break;

    // ── Action layer ─────────────────────────────────────────────────────
    case 'flow':
      result = await mg.procedure({ action: 'create_flow', label, description: content, props });
      break;
    case 'flowstep':
      result = await mg.procedure({ action: 'add_step', label, description: content, props });
      break;
    case 'affordance':
      result = await mg.procedure({ action: 'add_affordance', label, description: content, props });
      break;
    case 'control':
      result = await mg.procedure({ action: 'add_control', label, description: content, props });
      break;
    case 'riskassessment':
    case 'risk':
      result = await mg.risk({ action: 'assess', label, description: content, props });
      break;
    case 'execution':
      result = await mg.ingest(label, content, 'observation', {
        observed_at: props.completed_at || props.started_at, agentId,
      });
      break;

    // ── Memory layer ─────────────────────────────────────────────────────
    case 'session':
      skipped = true;
      break;
    case 'trace':
      result = await mg.sessionOp({ action: 'trace', label, note: content });
      break;
    case 'summary':
      result = await mg.distill(label, content, props);
      break;
    case 'preference':
      result = await mg.memoryConfig({
        action: 'set_preference', label,
        value: content || props.value, key: props.key || label,
      });
      break;
    case 'memorypolicy':
      result = await mg.memoryConfig({
        action: 'set_policy', label,
        policyText: content || props.policy_text, scope: props.scope || 'global',
      });
      break;
    case 'journal':
      result = await mg.addJournal(label, content, {
        summary: node.summary, journalType: props.journal_type || 'note',
        tags: props.tags || [], sessionUid: props.session_uid,
      });
      break;

    // ── Agent layer ──────────────────────────────────────────────────────
    case 'task':
      result = await mg.plan({
        action: 'create_task', label, description: content,
        priority: props.priority || 'medium', status: props.status || 'pending',
      });
      break;
    case 'plan':
      result = await mg.plan({ action: 'create_plan', label, description: content, props });
      break;
    case 'policy':
      result = await mg.governance({
        action: 'create_policy', label,
        policyContent: content || props.description, props,
      });
      break;

    default:
      // Unknown type — ingest as observation
      fallback = true;
      result = await mg.ingest(label, content, 'observation', { agentId });
  }

  return { result, skipped, fallback };
}

module.exports = { routeNode };
