/**
 * embedding-analysis.js
 * Analyzer for finding nodes missing embeddings.
 */

'use strict';

const mg = require('../mindgraph-client.js');

async function hasEmbedding(uid) {
  // Check if a vector is actually stored, even if embedding_ref is null.
  // Nodes embedded inline via embedNode() have vectors but embedding_ref stays null
  // (Rust server lock issue prevents the mark update). This prevents the dreamer
  // from re-embedding nodes that were already embedded in-session.
  try {
    const result = await mg.request('GET', `/node/${uid}/embedding`);
    // Server returns { embedding: [f32...] } or 404 (throws)
    return result && Array.isArray(result.embedding) && result.embedding.length > 0;
  } catch (e) {
    return false; // 404 or error = no embedding
  }
}

async function analyzeEmbeddings() {
  const proposals = [];
  const MAX_PER_SESSION = 25;

  try {
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

    // Filter out nodes that already have a stored vector (embedded inline this session)
    const trulyMissing = [];
    for (const n of missing) {
      const has = await hasEmbedding(n.uid);
      if (!has) trulyMissing.push(n);
    }

    for (const node of trulyMissing.slice(0, MAX_PER_SESSION)) {
      proposals.push({
        id: `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`,
        timestamp: new Date().toISOString(),
        auto_apply: true, // Tag as auto-apply since it's a non-destructive tech fix
        type: 'embedding_generate',
        impact: 'low',
        target: { uid: node.uid, label: node.label, node_type: node.node_type },
        action: `Generate embedding for "${node.label}"`,
        reason: 'Node is missing a vector embedding, which prevents it from being discovered via semantic search.',
        dream_session: 'direct_analysis',
        analyzer: 'embedding_analysis'
      });
    }
  } catch (e) {
    console.error('Embedding analysis failed:', e.message);
  }

  return proposals;
}

module.exports = { analyzeEmbeddings };
