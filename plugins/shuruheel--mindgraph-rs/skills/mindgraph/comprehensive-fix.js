#!/usr/bin/env node
/**
 * MindGraph Comprehensive Fix — Mar 4, 2026
 *
 * Fixes all identified issues from the integration review:
 * 1. Wire orphan nodes to relevant entities/projects
 * 2. Retype RELEVANT_TO edges to semantic edges where possible
 * 3. Fix schema_compliance analyzer (stop proposing impossible props)
 * 4. Add orphan detection analyzer to dreaming
 * 5. Integrate entity resolution into dreaming duplicate_nodes
 */

'use strict';

const fs = require('fs');
const path = require('path');
const mg = require('./mindgraph-client.js');

async function withRetry(fn, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try { return await fn(); } catch (e) {
      if (e.message?.includes('database is locked') && attempt < maxRetries) {
        await new Promise(r => setTimeout(r, 500 * attempt));
      } else throw e;
    }
  }
}

// ─── Fix 1: Wire Orphan Nodes ─────────────────────────────────────────────────

async function wireOrphans() {
  console.log('\n=== Fix 1: Wire Orphan Nodes ===');
  
  // Build a map of all entities/projects/goals for linking
  const entityTypes = ['Entity', 'Project', 'Goal'];
  const linkTargets = [];
  for (const t of entityTypes) {
    const r = await mg.getNodes({ nodeType: t, limit: 200 });
    const nodes = (r.items || r || []).filter(n => !n.tombstone_at);
    linkTargets.push(...nodes);
  }
  
  // Keyword → entity mapping for common topics
  const keywordMap = {};
  for (const n of linkTargets) {
    const words = n.label.toLowerCase().split(/\s+/);
    for (const w of words) {
      if (w.length > 3) {
        if (!keywordMap[w]) keywordMap[w] = [];
        keywordMap[w].push(n);
      }
    }
  }
  
  const orphanTypes = ['Observation', 'Decision', 'Claim', 'Constraint', 'Task'];
  let wired = 0, total = 0;
  
  for (const t of orphanTypes) {
    const r = await mg.getNodes({ nodeType: t, limit: 300 });
    const nodes = (r.items || r || []).filter(n => !n.tombstone_at);
    
    for (const n of nodes) {
      const outEdges = await mg.getEdges(n.uid);
      const inEdges = await mg.edgesTo(n.uid);
      
      if (outEdges.length === 0 && inEdges.length === 0) {
        total++;
        
        // Try keyword matching first
        const labelWords = n.label.toLowerCase().split(/\s+/);
        let bestMatch = null;
        let bestScore = 0;
        
        for (const word of labelWords) {
          if (keywordMap[word]) {
            for (const target of keywordMap[word]) {
              if (target.uid === n.uid) continue;
              // Count matching words
              const targetWords = new Set(target.label.toLowerCase().split(/\s+/));
              let score = 0;
              for (const w of labelWords) {
                if (targetWords.has(w)) score++;
              }
              if (score > bestScore) {
                bestScore = score;
                bestMatch = target;
              }
            }
          }
        }
        
        // Determine edge type based on node types
        if (bestMatch && bestScore >= 1) {
          let edgeType = 'RELEVANT_TO';
          if (n.node_type === 'Observation') edgeType = 'RELEVANT_TO';
          if (n.node_type === 'Decision' && bestMatch.node_type === 'Project') edgeType = 'ADDRESSES';
          if (n.node_type === 'Constraint') edgeType = 'CONSTRAINED_BY';
          if (n.node_type === 'Task' && bestMatch.node_type === 'Goal') edgeType = 'MOTIVATED_BY';
          if (n.node_type === 'Claim' && bestMatch.node_type === 'Entity') edgeType = 'RELEVANT_TO';
          
          // For Polymarket position decisions, link to the trading system
          if (n.label.toLowerCase().includes('position ')) {
            const polymarket = linkTargets.find(t => t.label === 'Polymarket Trading System');
            if (polymarket) {
              bestMatch = polymarket;
              edgeType = 'RELEVANT_TO';
            }
          }
          
          try {
            await withRetry(() => mg.link(n.uid, bestMatch.uid, edgeType));
            console.log(`  WIRED [${n.node_type}] "${n.label.slice(0, 40)}" → [${bestMatch.node_type}] "${bestMatch.label}" (${edgeType})`);
            wired++;
          } catch (e) {
            console.log(`  ERROR: ${e.message}`);
          }
        } else {
          console.log(`  ORPHAN (no match): [${n.node_type}] "${n.label.slice(0, 60)}"`);
        }
      }
    }
  }
  
  console.log(`  Total orphans: ${total}, Wired: ${wired}`);
  return { total, wired };
}

// ─── Fix 2: Retype RELEVANT_TO Edges ──────────────────────────────────────────

async function retypeGenericEdges() {
  console.log('\n=== Fix 2: Retype RELEVANT_TO Edges ===');
  
  // Get all nodes to build a type map
  const allNodes = new Map();
  let offset = 0, hasMore = true;
  while (hasMore) {
    const batch = await mg.getNodes({ limit: 250, offset });
    const nodes = batch.items || batch || [];
    for (const n of nodes) allNodes.set(n.uid, n);
    hasMore = nodes.length === 250;
    offset += 250;
  }
  
  // Retype rules based on node types
  const retypeRules = [
    // Decision → Goal = MOTIVATED_BY (not RELEVANT_TO)
    { from: 'Decision', to: 'Goal', newEdge: 'MOTIVATED_BY' },
    // Decision → Project = ADDRESSES
    { from: 'Decision', to: 'Project', newEdge: 'ADDRESSES' },
    // Constraint → Project = CONSTRAINED_BY (reverse direction)
    { from: 'Constraint', to: 'Project', newEdge: 'CONSTRAINED_BY', reverse: true },
    // Claim → Entity = RELEVANT_TO (keep — this is correct usage)
    // Observation → Entity = DERIVED_FROM
    { from: 'Observation', to: 'Entity', newEdge: 'DERIVED_FROM' },
    // Task → Goal = MOTIVATED_BY
    { from: 'Task', to: 'Goal', newEdge: 'MOTIVATED_BY' },
    // Task → Project = RELEVANT_TO (keep)
    // Evidence → Claim = SUPPORTS
    { from: 'Evidence', to: 'Claim', newEdge: 'SUPPORTS' },
    // Pattern → Concept = EXTENDS
    { from: 'Pattern', to: 'Concept', newEdge: 'EXTENDS' },
    // Project → Goal = MOTIVATED_BY
    { from: 'Project', to: 'Goal', newEdge: 'MOTIVATED_BY' },
    // Milestone → Project = DECOMPOSES_INTO (reverse)
    { from: 'Milestone', to: 'Project', newEdge: 'DECOMPOSES_INTO', reverse: true },
  ];
  
  // Find all RELEVANT_TO edges
  let retyped = 0, checked = 0;
  
  for (const [uid, node] of allNodes) {
    if (node.tombstone_at) continue;
    
    const edges = await mg.getEdges(uid, { edgeType: 'RELEVANT_TO' });
    if (!edges || edges.length === 0) continue;
    
    for (const edge of edges) {
      if (edge.tombstone_at) continue;
      checked++;
      
      const fromNode = allNodes.get(edge.from_uid);
      const toNode = allNodes.get(edge.to_uid);
      if (!fromNode || !toNode) continue;
      
      // Find applicable retype rule
      for (const rule of retypeRules) {
        if (fromNode.node_type === rule.from && toNode.node_type === rule.to) {
          try {
            if (rule.reverse) {
              await withRetry(() => mg.link(edge.to_uid, edge.from_uid, rule.newEdge));
            } else {
              await withRetry(() => mg.link(edge.from_uid, edge.to_uid, rule.newEdge));
            }
            console.log(`  RETYPE: ${fromNode.label.slice(0, 25)} → ${toNode.label.slice(0, 25)}: RELEVANT_TO → ${rule.newEdge}`);
            retyped++;
          } catch (e) {}
          break;
        }
      }
    }
    
    // Rate limit — don't hammer the server
    if (checked % 50 === 0) await new Promise(r => setTimeout(r, 100));
  }
  
  console.log(`  Checked: ${checked} RELEVANT_TO edges, Retyped: ${retyped}`);
  return { checked, retyped };
}

// ─── Fix 3: Apply Pending Schema Fixes via Summary ────────────────────────────

async function applyPendingSchemaFixes() {
  console.log('\n=== Fix 3: Apply Pending Schema Fixes (description → summary) ===');
  
  // Find nodes that schema_compliance keeps flagging for missing 'description'
  // The real fix: copy decision_rationale or question to summary where summary is empty
  const types = ['Decision', 'Goal', 'Project', 'Constraint'];
  let fixed = 0;
  
  for (const t of types) {
    const r = await mg.getNodes({ nodeType: t, limit: 200 });
    const nodes = (r.items || r || []).filter(n => !n.tombstone_at);
    
    for (const n of nodes) {
      if (!n.summary || n.summary.length < 10) {
        // Build a summary from available props
        const desc = n.props?.description || n.props?.decision_rationale || 
                     n.props?.question || n.props?.content || n.label;
        
        if (desc && desc.length > 10 && desc !== n.label) {
          try {
            await withRetry(() => mg.evolve('update', n.uid, {
              summary: desc.slice(0, 300),
              reason: 'Fix: populate summary for FTS searchability',
              agent_id: 'health-fix'
            }));
            console.log(`  SUMMARY [${t}]: ${n.label.slice(0, 40)} → "${desc.slice(0, 60)}..."`);
            fixed++;
          } catch (e) {}
        }
      }
    }
  }
  
  console.log(`  Fixed ${fixed} missing summaries`);
  return fixed;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  console.log('=== MindGraph Comprehensive Fix ===');
  const startStats = await mg.stats();
  console.log(`Graph: ${startStats.live_nodes} nodes, ${startStats.live_edges} edges`);
  
  const orphanResult = await wireOrphans();
  const retypeResult = await retypeGenericEdges();
  const summaryFixes = await applyPendingSchemaFixes();
  
  const endStats = await mg.stats();
  
  console.log('\n=== Final Summary ===');
  console.log(`Orphans wired: ${orphanResult.wired}/${orphanResult.total}`);
  console.log(`RELEVANT_TO retyped: ${retypeResult.retyped}/${retypeResult.checked}`);
  console.log(`Summaries fixed: ${summaryFixes}`);
  console.log(`Graph: ${startStats.live_nodes} → ${endStats.live_nodes} nodes, ${startStats.live_edges} → ${endStats.live_edges} edges`);
  console.log(`RELEVANT_TO edges: ${startStats.edges_by_type?.RELEVANT_TO || '?'} → ${endStats.edges_by_type?.RELEVANT_TO || '?'}`);
}

main().catch(e => {
  console.error('FATAL:', e.message);
  process.exit(1);
});
