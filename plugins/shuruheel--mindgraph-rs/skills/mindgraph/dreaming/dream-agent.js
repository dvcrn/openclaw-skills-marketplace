/**
 * dream-agent.js
 * Main dreaming agent for MindGraph
 * 
 * Usage:
 *   node dream-agent.js [options]
 */

'use strict';

const fs = require('fs');
const path = require('path');
const mg = require('../mindgraph-client.js');
const { 
  analyzers,
  getAnalyzersForSchedule,
  generateProposalId,
} = require('./dream-analysis.js');

// ─── Configuration ────────────────────────────────────────────────────────────

const CONFIG = {
  outputDir: path.join(__dirname, '.dream'),
  defaultAnalyzers: ['schema_compliance', 'contradictions', 'recency_salience', 'weak_claims'],
  lowRiskThreshold: 0.15,
  maxProposalsPerType: 20
};

// ─── Main Entry Point ─────────────────────────────────────────────────────────

async function runDreamSession(options = {}) {
  const sessionId = generateProposalId();
  const timestamp = new Date().toISOString();
  const sessionDate = timestamp.split('T')[0];
  
  console.log(`🌙 MindGraph Dream Session: ${sessionId}`);
  console.log(`   Time: ${timestamp}`);
  
  // ─── 1. Open Graph Session ───────────────────────────────────────────────────
  // Label includes HH:MM UTC to distinguish multiple runs on the same day
  const timeTag = new Date().toISOString().slice(11, 16); // "HH:MM"
  let mgSessionUid = null;
  try {
    const mgSession = await mg.sessionOp({ 
      action: 'open', 
      label: `Dream Session ${sessionDate} ${timeTag} UTC`, 
      focus: 'Nightly graph optimization and maintenance',
      agent_id: 'dreamer'
    });
    mgSessionUid = mgSession.uid;
  } catch (e) {
    console.error('Failed to open MindGraph session:', e.message);
  }

  // Collect all proposals
  const allProposals = [];
  const stats = {
    sessionId,
    timestamp,
    analyzersRun: [],
    totalProposals: 0,
    byType: {},
    byImpact: { high: 0, medium: 0, low: 0 },
    autoApplyCount: 0,
    requiresReviewCount: 0
  };
  
  // Get graph stats
  let graphStats;
  try {
    graphStats = await mg.stats();
    console.log(`📊 Graph State: ${graphStats.live_nodes} nodes, ${graphStats.live_edges} edges`);
  } catch (e) {
    console.error('Failed to get graph stats:', e.message);
    graphStats = { live_nodes: 0, live_edges: 0 };
  }
  
  // Run selected analyzers
  let runSet;
  if (options.analyzers) {
    runSet = options.analyzers.map(name => analyzers.find(a => a.name === name)).filter(Boolean);
  } else {
    runSet = options.all ? analyzers : getAnalyzersForSchedule();
  }
  const selectedAnalyzers = runSet.map(a => a.name);

  for (const analyzerName of selectedAnalyzers) {
    const analyzer = analyzers.find(a => a.name === analyzerName);
    if (!analyzer) continue;
    
    console.log(`🔍 Running: ${analyzerName}...`);
    if (mgSessionUid) {
      await mg.sessionOp({ 
        action: 'trace', 
        session_uid: mgSessionUid, 
        trace_content: `Running analyzer: ${analyzerName}`,
        trace_type: 'tool_call',
        agent_id: 'dreamer'
      }).catch(() => {});
    }
    
    try {
      const proposals = await analyzer.fn(analyzer.defaultOptions);
      for (const p of proposals) {
        p.dream_session = sessionId;
        p.analyzer = analyzerName;
      }
      allProposals.push(...proposals);
      stats.analyzersRun.push({ name: analyzerName, proposalsGenerated: proposals.length });
      console.log(`   ✓ ${proposals.length} proposals`);
    } catch (e) {
      console.error(`   ✗ Failed: ${e.message}`);
      stats.analyzersRun.push({ name: analyzerName, proposalsGenerated: 0, error: e.message });
    }
  }
  
  // AUTO-APPLY POLICY
  const AUTO_APPLY_TYPES = new Set(['schema_fix', 'data_enrichment', 'salience_boost', 'salience_decay', 'confidence_update', 'trending', 'embedding_generate']);

  for (const p of allProposals) {
    p.auto_apply = AUTO_APPLY_TYPES.has(p.type);
    p.auto_apply_reason = p.auto_apply ? `Low-risk type (${p.type})` : `Type "${p.type}" requires review`;
  }

  // Deduplicate — two passes:
  // Pass 1: same type + same target uid (exact dupe)
  // Pass 2: cross-type content collision — schema_fix and data_enrichment writing the same
  //         field+value to the same node. Keep schema_fix, drop data_enrichment.
  const contentByUid = {}; // uid → set of JSON(new_value) strings already queued
  for (const p of allProposals) {
    const uid = p.target?.uid || 'none';
    if (!contentByUid[uid]) contentByUid[uid] = new Set();
    contentByUid[uid].add(JSON.stringify(p.new_value || {}));
  }

  const seen = new Set();
  const seenContent = {}; // uid → Set of new_value JSON seen so far in pass
  for (const uid of Object.keys(contentByUid)) seenContent[uid] = new Set();

  const uniqueProposals = [];
  // Sort: schema_fix before data_enrichment so schema_fix wins content collisions
  allProposals.sort((a, b) => {
    if (a.type === 'schema_fix' && b.type === 'data_enrichment') return -1;
    if (a.type === 'data_enrichment' && b.type === 'schema_fix') return 1;
    return 0;
  });

  for (const p of allProposals) {
    const uid = p.target?.uid || 'none';
    const typeKey = `${p.type}:${uid}`;
    const contentKey = JSON.stringify(p.new_value || {});

    // Drop exact type+uid dupes
    if (seen.has(typeKey)) continue;
    // Drop cross-type content collisions (same uid, same new_value already queued by another type)
    if (uid !== 'none' && seenContent[uid]?.has(contentKey)) {
      continue; // schema_fix already covers this
    }

    seen.add(typeKey);
    if (uid !== 'none') seenContent[uid].add(contentKey);
    uniqueProposals.push(p);
  }
  
  stats.totalProposals = uniqueProposals.length;
  for (const p of uniqueProposals) {
    stats.byType[p.type] = (stats.byType[p.type] || 0) + 1;
    stats.byImpact[p.impact || 'low']++;
    if (p.auto_apply) stats.autoApplyCount++; else stats.requiresReviewCount++;
  }
  
  const output = {
    session: { id: sessionId, timestamp, date: sessionDate, mg_session_uid: mgSessionUid },
    graph: graphStats,
    stats,
    proposals: uniqueProposals.sort((a, b) => {
      const impactOrder = { high: 0, medium: 1, low: 2 };
      if (impactOrder[a.impact] !== impactOrder[b.impact]) return impactOrder[a.impact] - impactOrder[b.impact];
      return a.auto_apply ? 1 : -1;
    })
  };
  
  if (!options.dryRun) {
    if (!fs.existsSync(CONFIG.outputDir)) fs.mkdirSync(CONFIG.outputDir, { recursive: true });
    fs.writeFileSync(options.output || path.join(CONFIG.outputDir, `${sessionDate}.json`), JSON.stringify(output, null, 2));
  }
  
  if (options.report) {
    const reportMd = generateReport(output);
    if (!options.dryRun) fs.writeFileSync(path.join(CONFIG.outputDir, `${sessionDate}.md`), reportMd);
  }
  
  // Run description enrichment pass after main dream cycle (weekly on Sunday, or --enrich flag)
  const isEnrichDay = new Date().getDay() === 0; // Sunday
  if (isEnrichDay || options.enrich) {
    try {
      console.log('[dreamer] Running description enrichment pass...');
      const { execFileSync } = require('child_process');
      execFileSync('node', [path.join(__dirname, 'enrich-descriptions.js'), '--limit', '50'], {
        cwd: path.join(__dirname, '../../..'),
        timeout: 120000,
        stdio: 'inherit',
        env: { ...process.env },
      });
    } catch (e) {
      console.error('[dreamer] Enrichment pass failed:', e.message);
    }
  }

  if (mgSessionUid) {
    await mg.sessionOp({ 
      action: 'close', 
      session_uid: mgSessionUid, 
      agent_id: 'dreamer'
    }).catch(() => {});
  }

  return output;
}

// ─── Proposal Application ───
// DEPRECATED: This logic moved to apply-proposals.js
async function applyProposal(proposal) {
  const { applyProposal: realApply } = require('./apply-proposals.js');
  return realApply(proposal);
}

// ─── Report Generation ────────────────────────────────────────────────────────

function generateReport(output) {
  const { session, graph, stats, proposals } = output;
  
  const lines = [
    `# MindGraph Dream Report — ${session.date}`,
    '',
    `**Session:** ${session.id}  `,
    `**Generated:** ${session.timestamp}`,
    '',
    '## Summary',
    `- **Nodes analyzed:** ${graph.live_nodes}`,
    `- **Edges analyzed:** ${graph.live_edges}`,
    `- **Proposals generated:** ${stats.totalProposals}`,
    `  - Auto-apply: ${stats.autoApplyCount}`,
    `  - Needs review: ${stats.requiresReviewCount}`,
    '',
    '## Proposals by Impact',
    `- 🔴 High: ${stats.byImpact.high}`,
    `- 🟡 Medium: ${stats.byImpact.medium}`,
    `- 🟢 Low: ${stats.byImpact.low}`,
    ''
  ];
  
  const byImpact = { high: [], medium: [], low: [] };
  for (const p of proposals) byImpact[p.impact || 'low'].push(p);
  
  if (byImpact.high.length > 0) {
    lines.push('## 🔴 High Impact (Manual Review Required)');
    for (const p of byImpact.high) {
      lines.push(`### ${p.target?.label || 'Unknown'} [${p.type}]`);
      lines.push(`**Action:** ${p.action}`);
      lines.push(`**Reason:** ${p.reason}`);
      lines.push('');
    }
  }
  
  const autoApply = proposals.filter(p => p.auto_apply);
  if (autoApply.length > 0) {
    lines.push('## 🟢 Auto-Apply Proposals');
    for (const p of autoApply) lines.push(`- **${p.target?.label}**: ${p.action} (${p.type})`);
  }
  
  return lines.join('\n');
}

async function cli() {
  const args = process.argv.slice(2);
  const options = { analyzers: null, all: false, output: null, report: false, dryRun: false };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--analyzers') options.analyzers = args[++i].split(',').map(s => s.trim());
    else if (args[i] === '--all') options.all = true;
    else if (args[i] === '--output') options.output = args[++i];
    else if (args[i] === '--report') options.report = true;
    else if (args[i] === '--dry-run') options.dryRun = true;
  }
  
  try { await runDreamSession(options); } catch (e) {
    console.error('Dream session failed:', e.message);
    process.exit(1);
  }
}

module.exports = { runDreamSession, applyProposal, generateReport, CONFIG };
if (require.main === module) cli();
