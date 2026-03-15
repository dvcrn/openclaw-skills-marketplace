#!/usr/bin/env node
/**
 * MindGraph Quick Context — lightweight mid-conversation retrieval
 *
 * Usage:
 *   node mg-context.js "topic or question"
 *   node mg-context.js --fts "exact label"
 *   node mg-context.js --entity "person or org name"
 *   node mg-context.js --neighborhood <uid>
 *
 * Returns compact context suitable for injection into a conversation turn.
 * Designed to be fast (<3s). Returns full summaries — no truncation.
 *
 * v2 improvements:
 *  - entityLookup: uses traverse(neighborhood, depth=2) + parallel getNode batch
 *  - combinedQuery: expands top FTS/semantic hits with depth-1 subgraph
 *  - neighborhood: fixed traverse API (action= not mode=)
 *  - All node fetches parallelized via Promise.all
 */

'use strict';

const mg = require('./mindgraph-client.js');
const fsSync = require('fs');
const pathMod = require('path');
const http = require('http');

// ─── Paths ───────────────────────────────────────────────────────────────────

const WORKSPACE_ROOT = pathMod.resolve(__dirname, '..', '..');

// ─── Logging ─────────────────────────────────────────────────────────────────

const LOG_PATH = pathMod.join(WORKSPACE_ROOT, 'memory', 'retrieval-log.jsonl');
function logRetrieval(mode, query, resultCount, topScore) {
  try {
    const entry = JSON.stringify({
      ts: Date.now(),
      mode,
      query: query.slice(0, 200),
      results: resultCount,
      topScore: topScore ? +topScore.toFixed(3) : null,
    });
    fsSync.appendFileSync(LOG_PATH, entry + '\n');
  } catch {}
}

// ─── Formatting ───────────────────────────────────────────────────────────────

const NOISE_TYPES = new Set(['Source', 'Session', 'Trace', 'Warrant', 'Evidence']);

function nodeDesc(node) {
  return node.summary || node.props?.description || node.props?.content || '';
}

function formatNode(n, score) {
  const node = n.node || n;
  const s = score ?? n.score ?? node.score;
  const scoreStr = s ? ` (${Math.round(s * 100)}%)` : '';
  return `[${node.node_type}] ${node.label}${scoreStr}: ${nodeDesc(node)}`;
}

// ─── Raw traverse (correct API: action= not mode=) ───────────────────────────

const MG_CONFIG = JSON.parse(fsSync.readFileSync('/home/node/.openclaw/mindgraph.json', 'utf8'));

function rawPost(path, body) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const req = http.request({
      host: '127.0.0.1', port: 18790, path, method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + MG_CONFIG.token,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(data),
      },
    }, (r) => {
      let s = '';
      r.on('data', d => s += d);
      r.on('end', () => {
        try { resolve({ status: r.statusCode, body: JSON.parse(s) }); }
        catch { resolve({ status: r.statusCode, body: s }); }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

/**
 * Traverse neighborhood around a UID. Returns steps[] with
 * { depth, edge_type, label, node_type, node_uid, parent_uid }.
 * Does NOT include summaries — call batchGetNodes for those.
 */
async function traverseNeighborhood(uid, maxDepth = 2) {
  const r = await rawPost('/traverse', { action: 'neighborhood', start_uid: uid, max_depth: maxDepth });
  if (r.status !== 200) return [];
  return r.body.steps || [];
}

/**
 * Batch-fetch node summaries in parallel for a list of UIDs.
 * Returns Map<uid, node>.
 */
async function batchGetNodes(uids) {
  const results = await Promise.all(
    uids.map(uid => mg.getNode(uid).catch(() => null))
  );
  const map = new Map();
  results.forEach((node, i) => {
    if (node && !node.tombstone_at) map.set(uids[i], node);
  });
  return map;
}

// ─── Entity lookup (subgraph-aware) ──────────────────────────────────────────

async function entityLookup(name) {
  const { resolveEntity } = require('./entity-resolution.js');
  const uid = await resolveEntity(name, 'Entity', { createIfMissing: false });

  if (!uid) {
    logRetrieval('entity', name, 0, null);
    // Fallback: FTS search
    return ftsQuery(name);
  }

  // Traverse depth-2 neighborhood
  const steps = await traverseNeighborhood(uid, 2);

  // Collect all unique UIDs (root + neighbors)
  const allUids = [uid, ...steps.map(s => s.node_uid)];
  const uniqueUids = [...new Set(allUids)];

  // Batch-fetch summaries in parallel
  const nodeMap = await batchGetNodes(uniqueUids);
  const rootNode = nodeMap.get(uid);
  if (!rootNode) {
    logRetrieval('entity', name, 0, null);
    return ['Entity not found: ' + name];
  }

  logRetrieval('entity', name, steps.length + 1, null);

  const lines = [formatNode(rootNode)];

  // Group steps by depth, filter noise, deduplicate
  const seen = new Set([uid]);
  const depth1 = steps.filter(s => s.depth === 1 && !seen.has(s.node_uid));
  const depth2 = steps.filter(s => s.depth === 2 && !seen.has(s.node_uid));

  // Depth-1: show all non-noise neighbors with summaries
  for (const step of depth1.slice(0, 6)) {
    if (NOISE_TYPES.has(step.node_type)) continue;
    const n = nodeMap.get(step.node_uid);
    const summary = n ? nodeDesc(n) : '';
    lines.push(`  ${step.edge_type} → [${step.node_type}] ${step.label}: ${summary}`);
    seen.add(step.node_uid);
  }

  // Depth-2: show high-value nodes (Goals, Projects, Decisions, Policies)
  const HIGH_VALUE = new Set(['Goal', 'Project', 'Decision', 'Policy', 'Task', 'Claim']);
  for (const step of depth2) {
    if (!HIGH_VALUE.has(step.node_type)) continue;
    if (seen.has(step.node_uid)) continue;
    const n = nodeMap.get(step.node_uid);
    const summary = n ? nodeDesc(n) : '';
    lines.push(`    ↳ [${step.node_type}] ${step.label}: ${summary}`);
    seen.add(step.node_uid);
    if (lines.length > 12) break;
  }

  return lines;
}

// ─── FTS query ────────────────────────────────────────────────────────────────

async function ftsQuery(query) {
  const results = await mg.search(query, { limit: 8 });
  const items = Array.isArray(results) ? results : [];
  const filtered = items
    .map(n => n.node || n)
    .filter(n => !n.tombstone_at && !NOISE_TYPES.has(n.node_type))
    .slice(0, 5);
  const topScore = filtered.length > 0 ? Math.max(...filtered.map(n => n.score || 0)) : null;
  logRetrieval('fts', query, filtered.length, topScore);
  return filtered.map(n => formatNode(n));
}

// ─── Semantic query ───────────────────────────────────────────────────────────

async function semanticQuery(query) {
  const results = await mg.retrieve('semantic', { query, limit: 8 });
  const items = Array.isArray(results) ? results : [];
  const seen = new Set();
  const relevant = items.filter(n => {
    const node = n.node || n;
    if ((n.score || 0) < 0.38) return false;
    if (NOISE_TYPES.has(node.node_type)) return false;
    if (node.tombstone_at) return false;
    if (seen.has(node.uid)) return false;
    seen.add(node.uid);
    return true;
  }).slice(0, 5);
  const topScore = items.length > 0 ? Math.max(...items.map(n => n.score || 0)) : null;
  logRetrieval('semantic', query, relevant.length, topScore);
  return relevant.map(n => formatNode(n.node || n, n.score));
}

// ─── Neighborhood (by UID) ────────────────────────────────────────────────────

async function neighborhood(uid) {
  const steps = await traverseNeighborhood(uid, 2);
  const allUids = [uid, ...steps.map(s => s.node_uid)];
  const nodeMap = await batchGetNodes([...new Set(allUids)]);

  const rootNode = nodeMap.get(uid);
  if (!rootNode) return ['Node not found: ' + uid];

  const lines = [formatNode(rootNode)];
  const seen = new Set([uid]);

  for (const step of steps) {
    if (seen.has(step.node_uid)) continue;
    if (NOISE_TYPES.has(step.node_type)) continue;
    const n = nodeMap.get(step.node_uid);
    const indent = '  '.repeat(step.depth);
    const summary = n ? nodeDesc(n) : '';
    lines.push(`${indent}${step.edge_type} → [${step.node_type}] ${step.label}: ${summary}`);
    seen.add(step.node_uid);
    if (lines.length > 12) break;
  }

  return lines;
}

// ─── Combined query (FTS + semantic + subgraph expansion) ────────────────────

async function combinedQuery(query) {
  // Run FTS and semantic in parallel
  const [ftsItems, semItems] = await Promise.all([
    mg.search(query, { limit: 6 }).catch(() => []),
    mg.retrieve('semantic', { query, limit: 6 }).catch(() => []),
  ]);

  // Merge and deduplicate
  const seen = new Set();
  const candidates = [];
  for (const raw of [...(ftsItems || []), ...(semItems || [])]) {
    const node = raw.node || raw;
    if (!node?.uid || node.tombstone_at || NOISE_TYPES.has(node.node_type)) continue;
    if (seen.has(node.uid)) continue;
    seen.add(node.uid);
    candidates.push({ node, score: raw.score || 0 });
  }

  // Log top-level results
  const topScore = candidates.length > 0 ? Math.max(...candidates.map(c => c.score)) : null;
  logRetrieval('combined', query, candidates.length, topScore);

  if (candidates.length === 0) return [];

  // Top candidates get subgraph expansion (depth-1), rest are flat
  const TOP_N = 2;
  const topCandidates = candidates.slice(0, TOP_N);
  const restCandidates = candidates.slice(TOP_N, 6);

  // Expand top candidates with depth-1 neighborhood in parallel
  const expansions = await Promise.all(
    topCandidates.map(async ({ node, score }) => {
      const lines = [formatNode(node, score)];
      try {
        const steps = await traverseNeighborhood(node.uid, 1);
        // Batch-fetch neighbors
        const neighborUids = [...new Set(steps.map(s => s.node_uid).filter(u => !seen.has(u)))];
        const neighborMap = await batchGetNodes(neighborUids);

        for (const step of steps.slice(0, 4)) {
          if (NOISE_TYPES.has(step.node_type)) continue;
          if (seen.has(step.node_uid)) continue;
          const n = neighborMap.get(step.node_uid);
          const summary = n ? nodeDesc(n) : '';
          lines.push(`  ${step.edge_type} → [${step.node_type}] ${step.label}: ${summary}`);
          seen.add(step.node_uid);
        }
      } catch {}
      return lines;
    })
  );

  const lines = expansions.flat();

  // Add remaining flat results
  for (const { node, score } of restCandidates) {
    if (seen.has(node.uid)) continue;
    lines.push(formatNode(node, score));
    seen.add(node.uid);
    if (lines.length > 14) break;
  }

  return lines;
}

// ─── Server auto-start ────────────────────────────────────────────────────────

async function ensureServerUp() {
  const token = MG_CONFIG.token;
  try {
    const res = require('child_process').execSync(
      `curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${token}" http://127.0.0.1:18790/health`,
      { timeout: 3000 }
    ).toString().trim();
    if (res === '200') return;
  } catch {}

  // Don't try to auto-start in cloud mode
  const url = process.env.MINDGRAPH_URL || '';
  if (url.startsWith('https://')) {
    console.error('[mg-context] Cloud mode — skipping local server auto-start');
    return;
  }

  console.error('[mg-context] Server down — auto-starting...');
  const PID_FILE = '/tmp/mindgraph-server.pid';
  try { fsSync.unlinkSync(PID_FILE); } catch {}
  const START_SH = pathMod.join(__dirname, 'start.sh');
  const { spawn } = require('child_process');
  const child = spawn('bash', [START_SH], { detached: true, stdio: 'ignore', env: { ...process.env } });
  child.unref();

  for (let i = 0; i < 10; i++) {
    await new Promise(r => setTimeout(r, 500));
    try {
      const res = require('child_process').execSync(
        `curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${token}" http://127.0.0.1:18790/health`,
        { timeout: 2000 }
      ).toString().trim();
      if (res === '200') { console.error('[mg-context] Server up.'); return; }
    } catch {}
  }
  console.error('[mg-context] Warning: server may not be ready, proceeding anyway.');
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('Usage: node mg-context.js "query" | --fts "label" | --entity "name" | --neighborhood <uid>');
    process.exit(0);
  }

  await ensureServerUp();

  let results;
  if (args[0] === '--fts') {
    results = await ftsQuery(args.slice(1).join(' '));
  } else if (args[0] === '--entity') {
    results = await entityLookup(args.slice(1).join(' '));
  } else if (args[0] === '--neighborhood') {
    results = await neighborhood(args[1]);
  } else {
    results = await combinedQuery(args.join(' '));
  }

  if (results.length === 0) {
    console.log('No relevant context found.');
  } else {
    console.log(results.join('\n'));
  }
}

main().catch(e => {
  console.error('Error:', e.message);
  process.exit(1);
});
