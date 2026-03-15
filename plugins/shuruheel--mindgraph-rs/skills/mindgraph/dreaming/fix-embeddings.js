/**
 * fix-embeddings.js
 * Analyzes the graph for nodes missing embeddings and generates them.
 * Updated to use the 18 Cognitive Layer Tools API.
 */

'use strict';

const mg = require('../mindgraph-client.js');

async function fixEmbeddings() {
  console.log('🔍 Checking for nodes missing embeddings...');
  
  try {
    let offset = 0, hasMore = true;
    const missingUids = [];
    
    while (hasMore) {
      const batch = await mg.getNodes({ limit: 100, offset });
      const nodes = batch.items || batch || [];
      
      for (const node of nodes) {
        if (!node.embedding_ref) {
          missingUids.push(node.uid);
        }
      }
      
      hasMore = nodes.length === 100;
      offset += 100;
    }
    
    console.log(`📊 Found ${missingUids.length} nodes missing embeddings.`);
    
    if (missingUids.length === 0) {
      console.log('✅ All nodes have embeddings.');
      return;
    }
    
    console.log('🏗️ Generating embeddings (this may take a minute)...');
    
    let successCount = 0;
    for (const uid of missingUids) {
      try {
        // Use evolve('update') to trigger re-indexing
        await mg.evolve('update', uid, { reason: 'system: trigger missing embedding generation' });
        successCount++;
        if (successCount % 10 === 0) {
          console.log(`   Processed ${successCount}/${missingUids.length}...`);
        }
      } catch (err) {
        console.error(`   ✗ Failed to index node ${uid}:`, err.message);
      }
    }
    
    console.log(`✅ Successfully triggered indexing for ${successCount} nodes.`);
    
  } catch (e) {
    console.error('❌ Embedding fix failed:', e.message);
  }
}

if (require.main === module) {
  fixEmbeddings().catch(console.error);
}
