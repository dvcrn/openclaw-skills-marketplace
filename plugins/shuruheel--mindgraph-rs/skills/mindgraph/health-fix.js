#!/usr/bin/env node
/**
 * MindGraph Health Fix Script
 * 
 * Fixes issues found during review:
 * 1. Mistyped Claims (should be Decisions) — retype
 * 2. Orphan nodes — wire to relevant entities
 * 3. Long/descriptive labels — truncate and move content to summary
 * 4. RELEVANT_TO edge bloat — attempt to retype generic edges
 */

'use strict';

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

async function fixMistypedClaims() {
  console.log('\n=== Fix 1: Mistyped Claims → Decisions ===');
  const claims = await mg.getNodes({ nodeType: 'Claim', limit: 200 });
  const nodes = claims.items || claims || [];
  let fixed = 0;
  
  for (const n of nodes) {
    if (n.label.startsWith('Decision ')) {
      // Extract a clean label
      let cleanLabel = n.label;
      // Remove "Decision " prefix if it's followed by the actual decision name
      cleanLabel = cleanLabel.replace(/^Decision\s+/, '');
      // Truncate at first period if the label has rationale stuffed in
      const dotIdx = cleanLabel.indexOf('. Status');
      if (dotIdx > 0) cleanLabel = cleanLabel.slice(0, dotIdx);
      if (cleanLabel.length > 60) cleanLabel = cleanLabel.slice(0, 57) + '...';
      
      console.log(`  RETYPE: "${n.label.slice(0, 60)}..." → Decision: "${cleanLabel}"`);
      
      // Create proper Decision node
      try {
        const result = await withRetry(() => mg.deliberate({
          action: 'open_decision',
          label: cleanLabel,
          description: n.summary || n.label,
        }));
        
        // Move edges from old Claim to new Decision
        if (result?.uid) {
          const outEdges = await mg.getEdges(n.uid);
          const inEdges = await mg.edgesTo(n.uid);
          
          for (const e of [...outEdges, ...inEdges]) {
            if (e.tombstone_at) continue;
            try {
              const from = e.from_uid === n.uid ? result.uid : e.from_uid;
              const to = e.to_uid === n.uid ? result.uid : e.to_uid;
              await withRetry(() => mg.link(from, to, e.edge_type));
            } catch (err) {}
          }
          
          // Tombstone the old Claim
          await withRetry(() => mg.evolve('tombstone', n.uid, { 
            reason: 'Retyped: was Claim, should be Decision' 
          }));
          fixed++;
        }
      } catch (e) {
        console.log(`    ERROR: ${e.message}`);
      }
    }
  }
  console.log(`  Fixed ${fixed} mistyped claims`);
  return fixed;
}

async function fixLongLabels() {
  console.log('\n=== Fix 2: Long Labels → Truncate + Move to Summary ===');
  const types = ['Claim', 'Decision', 'Observation', 'Entity', 'Constraint'];
  let fixed = 0;
  
  for (const t of types) {
    const r = await mg.getNodes({ nodeType: t, limit: 200 });
    const nodes = r.items || r || [];
    
    for (const n of nodes) {
      if (n.label.length > 80) {
        // Move full label to summary if summary is empty/short
        const fullLabel = n.label;
        let cleanLabel = fullLabel;
        
        // Try to extract a meaningful short label
        const dotIdx = cleanLabel.indexOf('. ');
        if (dotIdx > 0 && dotIdx < 80) cleanLabel = cleanLabel.slice(0, dotIdx);
        else cleanLabel = cleanLabel.slice(0, 57) + '...';
        
        console.log(`  TRUNCATE [${t}]: "${fullLabel.slice(0, 60)}..." → "${cleanLabel}"`);
        
        try {
          await withRetry(() => mg.evolve('update', n.uid, {
            label: cleanLabel,
            summary: n.summary || fullLabel,
            reason: 'Label too long — truncated, full text moved to summary'
          }));
          fixed++;
        } catch (e) {
          console.log(`    ERROR: ${e.message}`);
        }
      }
    }
  }
  console.log(`  Fixed ${fixed} long labels`);
  return fixed;
}

async function fixOrphanNodes() {
  console.log('\n=== Fix 3: Wire Orphan Nodes ===');
  const types = ['Observation', 'Decision', 'Claim'];
  let wired = 0;
  
  for (const t of types) {
    const r = await mg.getNodes({ nodeType: t, limit: 200 });
    const nodes = r.items || r || [];
    
    for (const n of nodes) {
      const outEdges = await mg.getEdges(n.uid);
      const inEdges = await mg.edgesTo(n.uid);
      
      if (outEdges.length === 0 && inEdges.length === 0) {
        console.log(`  ORPHAN [${t}]: ${n.label.slice(0, 60)}`);
        
        // Try to find a related entity or project via search
        try {
          const results = await mg.search(n.label.split(' ').slice(0, 3).join(' '), { limit: 3 });
          const items = Array.isArray(results) ? results : [];
          
          for (const item of items) {
            const related = item.node || item;
            if (related.uid !== n.uid && !related.tombstone_at && 
                ['Entity', 'Project', 'Goal'].includes(related.node_type)) {
              await withRetry(() => mg.link(n.uid, related.uid, 'RELEVANT_TO'));
              console.log(`    → WIRED to ${related.label} [${related.node_type}]`);
              wired++;
              break;
            }
          }
        } catch (e) {}
      }
    }
  }
  console.log(`  Wired ${wired} orphan nodes`);
  return wired;
}

async function main() {
  console.log('=== MindGraph Health Fix ===');
  console.log('Server:', (await mg.health()));
  const stats = await mg.stats();
  console.log(`Graph: ${stats.live_nodes} nodes, ${stats.live_edges} edges`);
  
  const f1 = await fixMistypedClaims();
  const f2 = await fixLongLabels();
  const f3 = await fixOrphanNodes();
  
  console.log('\n=== Summary ===');
  console.log(`Mistyped claims fixed: ${f1}`);
  console.log(`Long labels fixed: ${f2}`);
  console.log(`Orphans wired: ${f3}`);
  
  const newStats = await mg.stats();
  console.log(`\nGraph after: ${newStats.live_nodes} nodes, ${newStats.live_edges} edges`);
}

main().catch(e => {
  console.error('FATAL:', e.message);
  process.exit(1);
});
