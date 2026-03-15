#!/usr/bin/env node
/**
 * MindGraph Import Script
 * 
 * Updated to use the 18 Cognitive Layer Tools API for all writes.
 * 
 * Usage:
 *   node skills/mindgraph/import.js <extracted.json>
 */

'use strict';

const fs = require('fs');
const path = require('path');
const https = require('https');

const mg = require('./mindgraph-client.js');
const { resolveEntity, normalizeLabel, loadAliasesFromGraph } = require('./entity-resolution.js');
const { routeNode } = require('./route-node.js');

// ─── Deduplication & Cache ────────────────────────────────────────────────────

const nodeCache = new Map(); // label → uid

async function findExisting(label, nodeType = 'Entity') {
  if (nodeCache.has(label)) return nodeCache.get(label);
  
  // Use the entity resolution module for consistent deduplication
  const resolvedUid = await resolveEntity(label, nodeType, { createIfMissing: false });
  
  if (resolvedUid) {
    nodeCache.set(label, resolvedUid);
    return resolvedUid;
  }
  
  return null;
}

// ─── Node Writer (Cognitive Mapping) ──────────────────────────────────────────

async function writeNode(node, opts) {
  const { dryRun, noDedup } = opts;

  if (!node.label || !node.type) {
    console.error(`  SKIP: missing label or type`, JSON.stringify(node).slice(0, 100));
    return null;
  }

  if (!noDedup) {
    const existingUid = await findExisting(node.label, node.type || 'Entity');
    if (existingUid) {
      console.log(`  DEDUP: ${node.label} → ${existingUid}`);
      nodeCache.set(node.label, existingUid);
      return existingUid;
    }
  }

  try {
    const { result, skipped, fallback } = await routeNode(node, { dryRun });

    if (skipped) {
      console.error(`  SKIP [${node.type}]: "${node.label}" — not auto-imported`);
      return null;
    }
    if (fallback) {
      console.error(`  FALLBACK [${node.type}]: "${node.label}" → ingest as observation`);
    }

    const uid = result?.uid;
    if (uid) {
      nodeCache.set(node.label, uid);
      console.log(`  ${dryRun ? 'DRY-RUN' : 'CREATED'} [${node.type}]: ${node.label} → ${uid}`);
    }
    return uid;
  } catch (e) {
    console.error(`  ERROR creating "${node.label}": ${e.message}`);
    return null;
  }
}

// ─── Main Logic (Refactored) ──────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('Usage: node import.js <extracted.json> [--dry-run] [--no-dedup] [--session-label "..."] [--session-focus "..."]');
    process.exit(0);
  }

  const sessionLabelIdx = args.indexOf('--session-label');
  const sessionFocusIdx = args.indexOf('--session-focus');

  const opts = {
    dryRun: args.includes('--dry-run'),
    noDedup: args.includes('--no-dedup'),
    sessionLabel: sessionLabelIdx !== -1 ? args[sessionLabelIdx + 1] : null,
    sessionFocus: sessionFocusIdx !== -1 ? args[sessionFocusIdx + 1] : null,
  };

  const inputArg = args.find(a => !a.startsWith('--'));
  const raw = inputArg === '-' ? fs.readFileSync('/dev/stdin', 'utf8') : fs.readFileSync(inputArg, 'utf8');
  const data = JSON.parse(raw);
  const { meta, nodes, edges } = data;

  console.log(`\n=== MindGraph Cognitive Import ===`);
  console.log(`Source: ${meta?.source_path || 'unknown'}`);
  console.log(`Nodes: ${nodes?.length || 0}, Edges: ${edges?.length || 0}\n`);

  // Pre-load graph for dedup
  const allLive = await mg.getNodes({ limit: 1000 });
  for (const n of (allLive.items || [])) {
    nodeCache.set(n.label, n.uid);
    nodeCache.set(n.label.toLowerCase(), n.uid);
  }

  // Phase 1: Nodes
  let created = 0, deduped = 0, failed = 0;
  for (const node of (nodes || [])) {
    const sizeBefore = nodeCache.size;
    const uid = await writeNode(node, opts);
    if (uid) {
      if (nodeCache.size > sizeBefore) created++;
      else deduped++;
    } else failed++;
  }

  // Phase 2: Edges
  console.log('\n--- Phase 2: Writing edges ---');
  for (const edge of (edges || [])) {
    const fromUid = nodeCache.get(edge.from) || nodeCache.get(edge.from.toLowerCase());
    const toUid = nodeCache.get(edge.to) || nodeCache.get(edge.to.toLowerCase());

    if (fromUid && toUid) {
      try {
        if (!opts.dryRun) await mg.link(fromUid, toUid, edge.type.toUpperCase());
        console.log(`  EDGE [${edge.type}]: ${edge.from.slice(0, 20)} → ${edge.to.slice(0, 20)}`);
      } catch (e) {
        console.error(`  ERROR edge: ${e.message}`);
      }
    }
  }

  // Phase 3: Session provenance node
  // If --session-label is provided, create a Session node and wire all imported nodes to it
  // via EXTRACTED_FROM edges. This gives every extraction run an audit trail.
  let sessionUid = null;
  if (opts.sessionLabel && !opts.dryRun) {
    console.log('\n--- Phase 3: Creating Session provenance node ---');
    try {
      const sessionResult = await mg.sessionOp({
        action: 'open',
        label: opts.sessionLabel,
        focus: opts.sessionFocus || `Extraction from ${meta?.source_path || 'unknown'}`,
        agent_id: 'writeback'
      });
      sessionUid = sessionResult?.uid;
      if (sessionUid) {
        console.log(`  SESSION: ${opts.sessionLabel} → ${sessionUid}`);
        // Close immediately — this is a record of a past session, not an active one
        await mg.sessionOp({
          action: 'close',
          session_uid: sessionUid,
          agent_id: 'writeback'
        }).catch(() => {});
      }
    } catch (e) {
      console.error(`  ERROR creating session node: ${e.message}`);
    }
  }

  // Phase 4: Auto-wiring EXTRACTED_FROM edges
  // Wire all imported nodes to the Session provenance node (preferred) or Source node (fallback)
  const provenanceUid = sessionUid;
  const sourceLabel = (!provenanceUid && meta?.source_path) ? `Source: ${path.basename(meta.source_path)}` : null;
  const wireTargetUid = provenanceUid || (sourceLabel ? nodeCache.get(sourceLabel) : null);

  if (wireTargetUid && !opts.dryRun) {
    console.log(`\n--- Phase 4: Wiring EXTRACTED_FROM → ${provenanceUid ? 'Session' : 'Source'} ---`);
    for (const node of (nodes || [])) {
      const nodeUid = nodeCache.get(node.label);
      if (nodeUid && nodeUid !== wireTargetUid) {
        await mg.link(nodeUid, wireTargetUid, 'EXTRACTED_FROM').catch(() => {});
      }
    }
  }

  console.log(`\n=== DONE ===`);
}

main().catch(e => {
  console.error('FATAL:', e.message);
  process.exit(1);
});
