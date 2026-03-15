/**
 * embedding-worker.js
 * Explicitly generates embeddings for nodes missing them.
 * Updated to use the 18 Cognitive Layer Tools API.
 */

'use strict';

const mg = require('../mindgraph-client.js');

async function run() {
  console.log('📡 Fetching nodes missing embeddings...');
  const stats = await mg.stats();
  console.log(`📊 Current coverage: ${stats.embedding_count} / ${stats.live_nodes} nodes`);

  let offset = 0, hasMore = true;
  const missing = [];
  
  while (hasMore) {
    const batch = await mg.getNodes({ limit: 100, offset });
    const nodes = batch.items || batch || [];
    for (const n of nodes) {
      if (!n.embedding_ref) missing.push(n);
    }
    hasMore = nodes.length === 100;
    offset += 100;
  }

  console.log(`🔍 Identified ${missing.length} nodes for indexing.`);

  let count = 0;
  for (const node of missing) {
    try {
      // Use evolve('update') to trigger re-indexing
      await mg.evolve('update', node.uid, { 
        summary: node.summary || node.label,
        reason: 'system: periodic embedding refresh'
      });
      
      count++;
      if (count % 20 === 0) console.log(`   Indexed ${count}/${missing.length}...`);
    } catch (err) {
      console.error(`   ✗ ${node.label}: ${err.message}`);
    }
  }

  const finalStats = await mg.stats();
  console.log(`✅ Finished. Final coverage: ${finalStats.embedding_count} / ${finalStats.live_nodes}`);
}

run().catch(console.error);
