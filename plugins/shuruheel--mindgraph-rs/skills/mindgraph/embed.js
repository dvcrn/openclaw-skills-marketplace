#!/usr/bin/env node
/**
 * Populate MindGraph embeddings for all live nodes using OpenAI text-embedding-3-small.
 * 
 * Usage: node skills/mindgraph/embed.js [--force]
 *   --force: Reconfigure embedding dimension if already set to a different value
 */

const mg = require('./mindgraph-client.js');
const https = require('https');

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const EMBEDDING_MODEL = 'text-embedding-3-small';
const EMBEDDING_DIM = 1536;
const BATCH_SIZE = 50; // OpenAI allows up to 2048 inputs per request

if (!OPENAI_API_KEY) {
  console.error('OPENAI_API_KEY not set');
  process.exit(1);
}

// ─── OpenAI embedding API ─────────────────────────────────────────────────────

function getEmbeddings(texts) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: EMBEDDING_MODEL,
      input: texts,
    });
    const opts = {
      hostname: 'api.openai.com',
      path: '/v1/embeddings',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
      },
    };
    const req = https.request(opts, (res) => {
      let data = '';
      res.on('data', d => data += d);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.error) return reject(new Error(parsed.error.message));
          resolve(parsed.data.map(d => d.embedding));
        } catch (e) {
          reject(new Error(`Parse error: ${e.message}, body: ${data.slice(0, 200)}`));
        }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// ─── Build embedding text for a node ──────────────────────────────────────────

function nodeToText(node) {
  const parts = [node.label];
  if (node.summary) parts.push(node.summary);
  // Include relevant props
  const props = node.props || {};
  if (props.content) parts.push(props.content);
  if (props.description) parts.push(props.description);
  if (props.entity_type) parts.push(`Type: ${props.entity_type}`);
  if (props.value) parts.push(props.value);
  return parts.join('. ').slice(0, 8000); // OpenAI limit is ~8K tokens per input
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const forceFlag = process.argv.includes('--force');

  // Step 1: Configure embeddings
  console.log(`Configuring embeddings (dim=${EMBEDDING_DIM})...`);
  try {
    await mg.configureEmbeddings(EMBEDDING_DIM);
    console.log('Configured ✅');
  } catch (e) {
    if (e.message.includes('mismatch') && forceFlag) {
      console.log('Dimension mismatch — force reconfiguring...');
      const http = require('http');
      const config = require('/home/node/.openclaw/mindgraph.json');
      await new Promise((resolve, reject) => {
        const body = JSON.stringify({ dimension: EMBEDDING_DIM, force: true });
        const req = http.request({
          hostname: '127.0.0.1', port: 18790, path: '/embeddings/configure',
          method: 'POST',
          headers: { 'Authorization': 'Bearer ' + config.token, 'Content-Type': 'application/json' },
        }, (res) => {
          let data = '';
          res.on('data', d => data += d);
          res.on('end', () => resolve(data));
        });
        req.on('error', reject);
        req.write(body);
        req.end();
      });
      console.log('Reconfigured ✅');
    } else {
      throw e;
    }
  }

  // Step 2: Get all live nodes
  const all = await mg.getNodes({ limit: 500 });
  const nodes = all.items || [];
  console.log(`Found ${nodes.length} nodes to embed`);

  // Step 3: Embed in batches
  let embedded = 0;
  let errors = 0;

  for (let i = 0; i < nodes.length; i += BATCH_SIZE) {
    const batch = nodes.slice(i, i + BATCH_SIZE);
    const texts = batch.map(nodeToText);

    console.log(`Batch ${Math.floor(i / BATCH_SIZE) + 1}: embedding ${batch.length} nodes...`);

    try {
      const embeddings = await getEmbeddings(texts);

      // Store each embedding
      for (let j = 0; j < batch.length; j++) {
        try {
          await mg.setEmbedding(batch[j].uid, embeddings[j]);
          embedded++;
        } catch (e) {
          console.error(`  Error storing ${batch[j].label}: ${e.message}`);
          errors++;
        }
      }
    } catch (e) {
      console.error(`  Batch error: ${e.message}`);
      errors += batch.length;
    }
  }

  console.log(`\nDone: ${embedded} embedded, ${errors} errors`);

  // Step 4: Verify
  const stats = await mg.stats();
  console.log(`Graph stats: ${stats.embedding_count} embeddings, dim=${stats.embedding_dimension}`);

  // Step 5: Test semantic search
  console.log('\n=== Semantic Search Test ===');
  const testQueries = ['outreach email writing', 'prediction markets trading', 'job application'];
  for (const q of testQueries) {
    const [queryVec] = await getEmbeddings([q]);
    const results = await mg.embeddingSearch(queryVec, { k: 5 });
    console.log(`"${q}" → ${results.length} results:`);
    for (const r of results.slice(0, 3)) {
      const node = r.node || r;
      console.log(`  ${(r.score || 0).toFixed(4)} ${node.label} [${node.node_type}]`);
    }
  }
}

main().catch(e => {
  console.error('Fatal:', e.message);
  process.exit(1);
});
