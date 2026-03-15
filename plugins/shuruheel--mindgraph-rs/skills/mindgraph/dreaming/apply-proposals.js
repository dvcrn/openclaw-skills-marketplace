/**
 * apply-proposals.js
 * Apply proposals from a dream session JSON file.
 *
 * Updated to use the 18 Cognitive Layer Tools API exclusively.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const https = require('https');
const mg = require('../mindgraph-client.js');

const DREAM_DIR = path.join(__dirname, '.dream');

// ─── Embedding helper ─────────────────────────────────────────────────────────

function getOpenAIKey() {
  try {
    const env = fs.readFileSync(path.join(__dirname, '../../../.env'), 'utf8');
    const m = env.match(/OPENAI_API_KEY\s*=\s*(.+)/);
    return m ? m[1].trim() : process.env.OPENAI_API_KEY;
  } catch { return process.env.OPENAI_API_KEY; }
}

function getMgToken() {
  if (process.env.MINDGRAPH_TOKEN) return process.env.MINDGRAPH_TOKEN;
  try {
    return JSON.parse(fs.readFileSync(path.join(process.env.HOME, '.openclaw/mindgraph.json'), 'utf8')).token;
  } catch { return null; }
}

async function embedText(text) {
  const key = getOpenAIKey();
  if (!key) throw new Error('No OPENAI_API_KEY');
  const body = JSON.stringify({ input: text, model: 'text-embedding-3-small' });
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'api.openai.com', path: '/v1/embeddings', method: 'POST',
      headers: { 'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
    }, res => { let d = ''; res.on('data', c => d += c); res.on('end', () => { try { resolve(JSON.parse(d).data[0].embedding); } catch(e) { reject(e); } }); });
    req.on('error', reject); req.write(body); req.end();
  });
}

async function putEmbedding(uid, vector) {
  const token = getMgToken();
  const body = JSON.stringify({ embedding: vector });
  return new Promise((resolve, reject) => {
    const req = require('http').request({
      hostname: '127.0.0.1', port: 18790, path: '/node/' + uid + '/embedding', method: 'PUT',
      headers: { 'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
    }, res => { res.resume(); res.on('end', () => resolve(res.statusCode)); });
    req.on('error', reject); req.write(body); req.end();
  });
}

// ─── Load Proposals ────────────────────────────────────────────────────────────

function loadDreamFile(dateStr) {
  const filePath = path.join(DREAM_DIR, `${dateStr}.json`);
  if (!fs.existsSync(filePath)) {
    throw new Error(`No dream file for ${dateStr}: ${filePath}`);
  }
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function saveDreamFile(dateStr, data) {
  const filePath = path.join(DREAM_DIR, `${dateStr}.json`);
  fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
}

function todayDate() {
  return new Date().toISOString().split('T')[0];
}

// ─── Apply a Single Proposal ───────────────────────────────────────────────────

async function applyProposal(proposal) {
  switch (proposal.type) {
    case 'salience_boost':
    case 'confidence_update': {
      if (proposal.target?.uid === '__batch__') break;
      const updates = {};
      if (proposal.new_value?.salience != null) updates.salience = proposal.new_value.salience;
      if (proposal.new_value?.confidence != null) updates.confidence = proposal.new_value.confidence;
      if (Object.keys(updates).length > 0) {
        await mg.evolve('update', proposal.target.uid, { 
          ...updates, 
          reason: `dream: ${proposal.reason}`,
          agent_id: 'dreamer'
        });
      }
      break;
    }

    case 'salience_decay': {
      if (proposal.target?.uid === '__batch__' && proposal.new_value?.half_life_secs) {
        // Server requires a uid even for batch decay (ignored server-side) — pass placeholder
        await mg.evolve('decay', '__batch__', { 
          half_life_secs: proposal.new_value.half_life_secs,
          agent_id: 'dreamer' 
        });
      } else if (proposal.target?.uid !== '__batch__') {
        if (proposal.new_value?.salience != null) {
          await mg.evolve('update', proposal.target.uid, {
            salience: proposal.new_value.salience,
            reason: `dream: ${proposal.reason}`,
            agent_id: 'dreamer'
          });
        }
      }
      break;
    }

    case 'edge_addition': {
      const e = proposal.edge_details;
      if (!e?.from_uid || !e?.to_uid || !e?.edge_type) {
        throw new Error('edge_addition missing required edge_details fields');
      }
      // Check edge doesn't already exist
      const existing = await mg.getEdges(e.from_uid, { edgeType: e.edge_type });
      if (existing && existing.find(edge => edge.to_uid === e.to_uid)) {
        console.log(`   ⏭ Edge already exists: ${e.edge_type}`);
        return;
      }
      await mg.link(e.from_uid, e.to_uid, e.edge_type);
      break;
    }

    case 'task_suggestion': {
      const nv = proposal.new_value;
      if (!nv?.task_label) break;
      await mg.plan({
        action: 'create_task',
        label: nv.task_label,
        description: nv.task_description || '',
        goal_uid: nv.parent_uid,
        agent_id: 'dreamer'
      });
      break;
    }

    case 'schema_fix':
    case 'data_enrichment': {
      const nv = proposal.new_value;
      if (!nv) break;
      const uid = proposal.target.uid;
      
      // Read current node to get existing props
      const currentNode = await mg.getNode(uid);
      if (!currentNode) break;
      
      // Separate top-level fields (summary, label, confidence, salience)
      // from props fields. The server's evolve endpoint can update summary/label/etc
      // but propsPatch is silently ignored — we must use PATCH with full merged props.
      const topLevelFields = ['summary', 'label', 'confidence', 'salience'];
      const evolveUpdate = {};
      const propsUpdate = {};
      
      for (const [key, value] of Object.entries(nv)) {
        if (topLevelFields.includes(key)) {
          evolveUpdate[key] = value;
        } else if (key === 'description' || key === 'content') {
          // 'description' and 'content' should map to summary for FTS searchability
          // AND to props if the server schema allows it
          if (!currentNode.summary || currentNode.summary.length < (value).length) {
            evolveUpdate.summary = value;
          }
          propsUpdate[key] = value;
        } else {
          propsUpdate[key] = value;
        }
      }
      
      // Apply top-level updates via evolve (these work)
      if (Object.keys(evolveUpdate).length > 0) {
        await mg.evolve('update', uid, {
          ...evolveUpdate,
          reason: `dream: ${proposal.reason}`,
          agent_id: 'dreamer'
        });
      }
      
      // Apply props updates via PATCH with full merged props (must include _type)
      if (Object.keys(propsUpdate).length > 0 && currentNode.props?._type) {
        const mergedProps = { ...currentNode.props, ...propsUpdate };
        try {
          await mg.updateNode(uid, { props: mergedProps }, { 
            reason: `dream: ${proposal.reason}` 
          });
        } catch (e) {
          // If PATCH fails (strict schema), the summary update above is the fallback
          // This is expected for node types that don't accept arbitrary props
        }
      }
      break;
    }

    case 'dedup': {
      if (!proposal.target?.uid) break;
      const mergeInto = proposal.new_value?.merge_into;
      if (mergeInto) {
        await mg.manageEntity({
          action: 'merge',
          keepUid: mergeInto,
          mergeUid: proposal.target.uid,
          agentId: 'dreamer'
        });
      } else {
        await mg.evolve('tombstone', proposal.target.uid, {
          reason: `dedup: duplicate of unknown`,
          agent_id: 'dreamer'
        });
      }
      break;
    }

    case 'trending': {
      console.log(`   ✓ Insight acknowledged: Topic "${proposal.target?.label || 'unknown'}"`);
      break;
    }

    case 'embedding_generate': {
      const uid = proposal.target?.uid;
      if (!uid) break;
      const node = await mg.getNode(uid);
      if (!node) break;
      const text = [node.label, node.props?.description || node.summary].filter(Boolean).join('. ');
      const vector = await embedText(text);
      const status = await putEmbedding(uid, vector);
      if (status !== 204) throw new Error(`PUT /node/${uid}/embedding returned ${status}`);
      break;
    }

    // ── Review-only proposals (informational, not auto-applied) ──────────────
    // These surface in the dream report for human/agent review; no graph mutation.
    case 'answer_question':   // Open question needs web research
    case 'belief_revision':   // Weak claim needs manual evidence review
    case 'data_gap':          // Missing required info (decided_at, rationale)
    case 'decision_expired':  // Decision past its review_after date
    case 'goal_review':       // Stale goal needs status check
    case 'source_drift':      // Source file changed since node was extracted
    case 'system':            // System-level observations
    case 'orphan_wire':       // Orphan node needs wiring — requires review
      console.log(`   ⏭ review-only (${proposal.type}): ${proposal.target?.label || '?'}`);
      return;

    default:
      throw new Error(`Apply not implemented for type: ${proposal.type}`);
  }
}

// ─── Apply Batch ───────────────────────────────────────────────────────────────

async function applyBatch(proposals, { dryRun = false, dreamData = null } = {}) {
  let applied = 0;
  let skipped = 0;
  let failed = 0;

  // Use the dream SESSION start time (not individual proposal timestamps) as the staleness
  // cutoff. Individual proposal timestamps are all set at dream generation time — but
  // schema_fix runs first and bumps updated_at by a few seconds, causing data_enrichment
  // (same session, same node, same timestamp) to be falsely marked stale.
  // Grace window: 60s after session start, to accommodate same-session schema_fix writes.
  const sessionStart = dreamData?.session?.timestamp
    ? new Date(dreamData.session.timestamp).getTime()
    : null;
  const SAME_SESSION_GRACE_MS = 60 * 1000; // 60 seconds

  // Build a set of node UIDs already written in this batch (same-session writes)
  // so we can skip the staleness check for those — they were updated by us, not externally.
  const writtenThisSession = new Set();

  for (const p of proposals) {
    if (p.applied || p.rejected) {
      skipped++;
      continue;
    }

    if (dryRun) {
      console.log(`  [dry-run] Would apply: ${p.type} on ${p.target?.label || p.target?.uid}`);
      applied++;
      continue;
    }

    try {
      // ─── STALENESS CHECK ───────────────────────────────────────────────────
      // Skip check for: batch targets, nodes already written this session, embedding_generate
      const uid = p.target?.uid;
      const skipStalenessTypes = new Set(['embedding_generate', 'salience_decay', 'trending']);
      
      if (uid && uid !== '__batch__' && uid !== '__trending__' && !skipStalenessTypes.has(p.type) && !writtenThisSession.has(uid)) {
        const current = await mg.getNode(uid);
        const nodeTime = current?.updated_at ? current.updated_at * 1000 : 0;

        // Stale = node was updated AFTER the dream session started AND outside our grace window
        // (i.e. updated by something external, not by this dream run's earlier proposals)
        const cutoff = sessionStart ? sessionStart - SAME_SESSION_GRACE_MS : new Date(p.timestamp || 0).getTime();

        if (nodeTime > cutoff + SAME_SESSION_GRACE_MS * 2) {
          // Only skip if updated more than 2 grace periods after session start
          // (catches genuine external updates, ignores same-session schema_fix writes)
          console.log(`   ⏭ Stale: ${p.target.label} (updated ${Math.round((nodeTime - cutoff)/1000)}s after dream start)`);
          p.skipped = true;
          p.skip_reason = `Stale: node updated ${Math.round((nodeTime - cutoff)/1000)}s after dream session start`;
          skipped++;
          continue;
        }
      }

      await applyProposal(p);
      p.applied = true;
      p.applied_at = new Date().toISOString();
      if (uid) writtenThisSession.add(uid); // Track so subsequent proposals for same node skip staleness check
      applied++;
      console.log(`   ✓ ${p.type}: ${p.target?.label || p.target?.uid}`);
    } catch (e) {
      p.apply_error = e.message;
      failed++;
      console.error(`   ✗ ${p.type} on ${p.target?.label}: ${e.message}`);
    }
  }

  return { applied, skipped, failed };
}

// ─── Morning Review Summary ────────────────────────────────────────────────────

function buildReviewSummary(dreamData) {
  const { proposals, stats, session, graph } = dreamData;
  const pendingReview = proposals.filter(p => !p.auto_apply && !p.applied && !p.rejected);
  const autoApply = proposals.filter(p => p.auto_apply && !p.applied);

  const lines = [
    `🌙 **Dream Report — ${session.date}**`,
    `Graph: ${graph.live_nodes} nodes / ${graph.live_edges} edges`,
    '',
    `📋 **${stats.totalProposals} proposals** (${stats.autoApplyCount} auto, ${stats.requiresReviewCount} need review)`,
    ''
  ];

  if (pendingReview.length > 0) {
    lines.push(`🔍 **Needs your review (${pendingReview.length}):**`);
    for (const p of pendingReview.slice(0, 5)) {
      const impact = p.impact === 'high' ? '🔴' : p.impact === 'medium' ? '🟡' : '🟢';
      lines.push(`${impact} **${p.target?.label}**: ${p.action}`);
      lines.push(`   _${p.reason.slice(0, 120)}_`);
    }
    if (pendingReview.length > 5) {
      lines.push(`_...and ${pendingReview.length - 5} more — see .dream/${session.date}.json_`);
    }
    lines.push('');
  }

  if (autoApply.length > 0) {
    lines.push(`⚡ **Auto-applying ${autoApply.length} low-risk changes**`);
  }

  return lines.join('\n');
}

// ─── CLI ───────────────────────────────────────────────────────────────────────

async function cli() {
  const args = process.argv.slice(2);

  let dateStr = todayDate();
  let autoOnly = false;
  let specificIds = null;
  let rejectId = null;
  let dryRun = false;
  let review = false;

  let typeFilter = null;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--auto-only') autoOnly = true;
    else if (args[i] === '--dry-run') dryRun = true;
    else if (args[i] === '--review') review = true;
    else if (args[i] === '--ids') specificIds = args[++i].split(',').map(s => s.trim());
    else if (args[i] === '--reject') rejectId = args[++i];
    else if (args[i] === '--type') typeFilter = args[++i].split(',').map(s => s.trim());
    else if (/^\d{4}-\d{2}-\d{2}$/.test(args[i])) dateStr = args[i];
  }

  let dreamData;
  try {
    dreamData = loadDreamFile(dateStr);
  } catch (e) {
    console.error(e.message);
    process.exit(1);
  }

  if (rejectId) {
    const proposal = dreamData.proposals.find(p => p.id === rejectId);
    if (!proposal) {
      console.error(`Proposal ${rejectId} not found`);
      process.exit(1);
    }
    proposal.rejected = true;
    proposal.rejected_at = new Date().toISOString();
    saveDreamFile(dateStr, dreamData);
    console.log(`✓ Rejected: ${proposal.type} on ${proposal.target?.label}`);
    return;
  }

  if (review) {
    console.log(buildReviewSummary(dreamData));
    return;
  }

  let toApply = dreamData.proposals;

  if (specificIds) {
    toApply = dreamData.proposals.filter(p => specificIds.includes(p.id));
    console.log(`Applying ${toApply.length} specific proposals...`);
  } else if (autoOnly) {
    toApply = dreamData.proposals.filter(p => p.auto_apply);
    console.log(`Applying ${toApply.length} auto-approved proposals...`);
  } else if (typeFilter) {
    toApply = dreamData.proposals.filter(p => typeFilter.includes(p.type));
    console.log(`Applying ${toApply.length} proposals of type(s): ${typeFilter.join(', ')}`);
  } else {
    // Safety: never apply review-only types without explicit --type or --ids flag
    const REVIEW_ONLY = new Set(['answer_question', 'belief_revision', 'data_gap', 'decision_expired', 'goal_review', 'source_drift', 'system']);
    const skippedReviewOnly = toApply.filter(p => REVIEW_ONLY.has(p.type)).length;
    if (skippedReviewOnly > 0) {
      toApply = toApply.filter(p => !REVIEW_ONLY.has(p.type));
      console.log(`(skipping ${skippedReviewOnly} review-only proposals — use --type to apply explicitly)`);
    }
    console.log(`Applying all ${toApply.length} proposals...`);
  }

  const result = await applyBatch(toApply, { dryRun, dreamData });

  if (!dryRun) {
    saveDreamFile(dateStr, dreamData);
  }

  console.log('');
  console.log(`✅ Applied: ${result.applied}  ⏭ Skipped: ${result.skipped}  ✗ Failed: ${result.failed}`);
}

module.exports = { applyProposal, applyBatch, buildReviewSummary, loadDreamFile };

if (require.main === module) {
  cli().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
  });
}
