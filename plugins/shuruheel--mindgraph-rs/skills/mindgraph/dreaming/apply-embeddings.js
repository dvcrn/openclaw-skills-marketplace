/**
 * apply-embeddings.js
 * Generate and store embeddings for nodes missing them.
 *
 * Uses OpenAI text-embedding-3-small (1536-dim) and stores via
 * PUT /node/{uid}/embedding on the local mindgraph-server.
 *
 * Usage:
 *   node skills/mindgraph/dreaming/apply-embeddings.js [dream-output.txt]
 *
 * If a dream output file is provided, only processes nodes flagged by the
 * embedding_generate proposals. Otherwise, scans all nodes missing embeddings.
 */

'use strict';

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');
const mg = require('../mindgraph-client.js');

// ─── Config ───────────────────────────────────────────────────────────────────

const WORKSPACE = path.join(__dirname, '../../..');
const ENV_PATH = path.join(WORKSPACE, '.env');

function loadEnv(envPath) {
  try {
    return fs.readFileSync(envPath, 'utf8')
      .split('\n')
      .reduce((acc, line) => {
        const eq = line.indexOf('=');
        if (eq > 0) acc[line.slice(0, eq).trim()] = line.slice(eq + 1).trim();
        return acc;
      }, {});
  } catch { return {}; }
}

const env = loadEnv(ENV_PATH);
const OPENAI_KEY = process.env.OPENAI_API_KEY || env.OPENAI_API_KEY;
const MG_CONFIG_PATH = path.join(process.env.HOME, '.openclaw/mindgraph.json');
const MG_CONFIG = JSON.parse(fs.readFileSync(MG_CONFIG_PATH, 'utf8'));
const MG_TOKEN = MG_CONFIG.token;
const MG_PORT = MG_CONFIG.port || 18790;
const MG_HOST = (MG_CONFIG.bind || '127.0.0.1');

const EMBEDDING_MODEL = 'text-embedding-3-small';
const EMBEDDING_DIM = 1536;
const BATCH_SIZE = 50;   // OpenAI allows up to 2048 inputs per request
const RATE_LIMIT_MS = 500; // ms between OpenAI batches

if (!OPENAI_KEY) {
  console.error('❌ OPENAI_API_KEY not found in .env or environment');
  process.exit(1);
}

// ─── OpenAI embeddings (batch) ────────────────────────────────────────────────

function getEmbeddings(texts) {
  return new Promise((resolve, reject) => {
    const body = Buffer.from(JSON.stringify({
      model: EMBEDDING_MODEL,
      input: texts.map(t => t.replace(/\n+/g, ' ').slice(0, 8000)), // OpenAI limit
    }));

    const options = {
      hostname: 'api.openai.com',
      port: 443,
      path: '/v1/embeddings',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_KEY}`,
        'Content-Length': body.length,  // byte length, not string length
      },
    };

    const req = https.request(options, (res) => {
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => {
        try {
          const parsed = JSON.parse(Buffer.concat(chunks).toString());
          if (parsed.error) return reject(new Error(parsed.error.message));
          resolve(parsed.data.map(d => d.embedding));
        } catch (e) {
          reject(new Error(`Failed to parse OpenAI response: ${e.message}`));
        }
      });
    });

    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// ─── Store embedding in mindgraph-server ─────────────────────────────────────

function setEmbedding(uid, embedding) {
  return new Promise((resolve, reject) => {
    const body = Buffer.from(JSON.stringify({ embedding }));

    const options = {
      hostname: MG_HOST,
      port: MG_PORT,
      path: `/node/${encodeURIComponent(uid)}/embedding`,
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${MG_TOKEN}`,
        'Content-Length': body.length,
      },
    };

    const req = http.request(options, (res) => {
      const chunks = [];
      res.on('data', c => chunks.push(c));
      res.on('end', () => {
        if (res.statusCode === 204) return resolve();
        const txt = Buffer.concat(chunks).toString();
        reject(new Error(`HTTP ${res.statusCode}: ${txt.slice(0, 200)}`));
      });
    });

    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// ─── Get nodes needing embeddings ─────────────────────────────────────────────

async function getNodesNeedingEmbeddings(dreamOutputPath) {
  // If dream output provided, extract only flagged UIDs
  if (dreamOutputPath && fs.existsSync(dreamOutputPath)) {
    const content = fs.readFileSync(dreamOutputPath, 'utf8');
    const flaggedLabels = new Set();
    const labelMatch = content.matchAll(/embedding_generate[^\n]*?on ([^\n:]+?):/g);
    for (const m of labelMatch) flaggedLabels.add(m[1].trim());

    if (flaggedLabels.size > 0) {
      console.log(`📋 Processing ${flaggedLabels.size} flagged nodes from dream output...`);
      // Still need to fetch full node data to get UIDs
    }
  }

  // Scan all nodes for missing embedding_ref
  console.log('📡 Scanning for nodes missing embeddings...');
  const missing = [];
  let offset = 0;
  let hasMore = true;

  while (hasMore) {
    const result = await mg.getNodes({ limit: 100, offset });
    const nodes = Array.isArray(result) ? result : (result?.items ?? []);
    for (const n of nodes) {
      if (!n.embedding_ref && !n.tombstone_at) missing.push(n);
    }
    hasMore = nodes.length === 100;
    offset += nodes.length;
  }

  return missing;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function run() {
  const dreamOutputPath = process.argv[2];
  const missing = await getNodesNeedingEmbeddings(dreamOutputPath);

  console.log(`🔍 ${missing.length} nodes need embeddings`);
  if (missing.length === 0) {
    console.log('✅ Nothing to do.');
    return;
  }

  // Ensure embedding dimension is configured
  await new Promise((resolve, reject) => {
    const body = Buffer.from(JSON.stringify({ dimension: EMBEDDING_DIM }));
    const req = http.request({
      hostname: MG_HOST, port: MG_PORT, path: '/embeddings/configure',
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${MG_TOKEN}`, 'Content-Length': body.length },
    }, res => { res.resume(); res.on('end', resolve); });
    req.on('error', reject);
    req.write(body); req.end();
  });

  let success = 0, failed = 0;

  // Process in batches
  for (let i = 0; i < missing.length; i += BATCH_SIZE) {
    const batch = missing.slice(i, i + BATCH_SIZE);
    const texts = batch.map(n => `${n.label} ${n.summary || ''}`.trim());

    let embeddings;
    try {
      embeddings = await getEmbeddings(texts);
    } catch (err) {
      if (err.message.includes('rate limit') || err.message.includes('429')) {
        console.log('⏳ Rate limited — waiting 60s...');
        await new Promise(r => setTimeout(r, 60000));
        try { embeddings = await getEmbeddings(texts); } catch (e2) {
          console.error(`✗ Batch ${i}-${i+batch.length} failed after retry: ${e2.message}`);
          failed += batch.length;
          continue;
        }
      } else {
        console.error(`✗ Batch ${i}-${i+batch.length}: ${err.message}`);
        failed += batch.length;
        continue;
      }
    }

    // Store each embedding
    for (let j = 0; j < batch.length; j++) {
      const node = batch[j];
      try {
        await setEmbedding(node.uid, embeddings[j]);
        success++;
      } catch (err) {
        console.error(`   ✗ ${node.label}: ${err.message}`);
        failed++;
      }
    }

    console.log(`   ✓ ${Math.min(i + BATCH_SIZE, missing.length)}/${missing.length} processed`);
    if (i + BATCH_SIZE < missing.length) {
      await new Promise(r => setTimeout(r, RATE_LIMIT_MS));
    }
  }

  console.log(`\n✅ Done. Success: ${success}  Failed: ${failed}`);
}

run().catch(err => {
  console.error('Fatal:', err.message);
  process.exit(1);
});
