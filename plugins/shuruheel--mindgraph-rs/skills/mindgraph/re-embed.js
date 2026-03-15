#!/usr/bin/env node
/**
 * MindGraph Re-Embedding Script
 * 
 * Re-generates embeddings for all nodes using enriched text:
 * label + summary + connected node labels + props description/content
 * 
 * This produces richer embeddings that capture graph neighborhood context,
 * dramatically improving semantic retrieval quality.
 * 
 * Usage:
 *   node re-embed.js [--limit 50] [--type Entity] [--force]
 */

'use strict';

const fs = require('fs');
const path = require('path');
const https = require('https');
const mg = require('./mindgraph-client.js');

function getOpenAIKey() {
  try {
    const env = fs.readFileSync(path.join(__dirname, '.env'), 'utf8');
    const m = env.match(/OPENAI_API_KEY\s*=\s*(.+)/);
    return m ? m[1].trim() : process.env.OPENAI_API_KEY;
  } catch { return process.env.OPENAI_API_KEY; }
}

function getMgToken() {
  try {
    return JSON.parse(fs.readFileSync(path.join(process.env.HOME, '.openclaw/mindgraph.json'), 'utf8')).token;
  } catch { return null; }
}

async function embedText(text, apiKey) {
  const body = JSON.stringify({ input: text.slice(0, 8000), model: 'text-embedding-3-small' });
  return new Promise((resolve, reject) => {
    const req = https.request({
      hostname: 'api.openai.com', path: '/v1/embeddings', method: 'POST',
      headers: { 'Authorization': 'Bearer ' + apiKey, 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) }
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

async function buildEmbeddingText(node) {
  const parts = [node.label];
  
  // Add summary (primary FTS field)
  if (node.summary) parts.push(node.summary);

  // Add all semantically meaningful props — aligned with FTS indexed fields
  const p = node.props || {};
  // Narrative / descriptive
  if (p.description)          parts.push(p.description);
  if (p.content)              parts.push(p.content);
  // Decision nodes
  if (p.decision_rationale)   parts.push(p.decision_rationale);
  if (p.question)             parts.push(p.question);
  // Constraint / policy nodes
  if (p.policy_text)          parts.push(p.policy_text);
  if (p.policyContent)        parts.push(p.policyContent);
  // Argument / epistemic nodes
  if (p.claim_text)           parts.push(p.claim_text);
  if (p.evidence)             parts.push(typeof p.evidence === 'string' ? p.evidence : JSON.stringify(p.evidence));
  if (p.warrant)              parts.push(typeof p.warrant === 'string' ? p.warrant : JSON.stringify(p.warrant));
  if (p.rebuttal)             parts.push(p.rebuttal);
  // Task / goal nodes
  if (p.task_description)     parts.push(p.task_description);
  if (p.outcome)              parts.push(p.outcome);
  if (p.focus)                parts.push(p.focus);
  // Entity / observation nodes
  if (p.bio)                  parts.push(p.bio);
  if (p.notes)                parts.push(p.notes);
  if (p.text)                 parts.push(p.text);

  // Add type context
  parts.push(`Type: ${node.node_type}`);
  
  // Add connected node labels for graph-aware embeddings
  try {
    const edges = await mg.getEdges(node.uid);
    const inEdges = await mg.edgesTo(node.uid);
    const allEdges = [...(edges || []), ...(inEdges || [])].filter(e => !e.tombstone_at);
    
    const connectedLabels = [];
    for (const e of allEdges.slice(0, 6)) {
      const otherUid = e.from_uid === node.uid ? e.to_uid : e.from_uid;
      try {
        const other = await mg.getNode(otherUid);
        if (other && !other.tombstone_at) {
          connectedLabels.push(`${e.edge_type}: ${other.label}`);
        }
      } catch {}
    }
    
    if (connectedLabels.length > 0) {
      parts.push('Connected: ' + connectedLabels.join('; '));
    }
  } catch {}
  
  return parts.filter(Boolean).join('. ');
}

async function main() {
  const args = process.argv.slice(2);
  const limit = args.includes('--limit') ? parseInt(args[args.indexOf('--limit') + 1]) : 100;
  const typeFilter = args.includes('--type') ? args[args.indexOf('--type') + 1] : null;
  const force = args.includes('--force');
  
  const apiKey = getOpenAIKey();
  if (!apiKey) { console.error('No OPENAI_API_KEY'); process.exit(1); }
  
  console.log(`Re-embedding up to ${limit} nodes${typeFilter ? ` (type: ${typeFilter})` : ''}${force ? ' (force)' : ''}`);
  
  // Get all live nodes
  let allNodes = [];
  let offset = 0, hasMore = true;
  const opts = typeFilter ? { nodeType: typeFilter, limit: 250, offset: 0 } : { limit: 250, offset: 0 };
  
  while (hasMore) {
    const batch = await mg.getNodes({ ...opts, offset });
    const nodes = batch.items || batch || [];
    allNodes.push(...nodes.filter(n => !n.tombstone_at));
    hasMore = nodes.length === 250;
    offset += 250;
  }
  
  console.log(`Found ${allNodes.length} live nodes`);
  
  // Sort by importance: high salience first
  allNodes.sort((a, b) => (b.salience || 0) - (a.salience || 0));
  
  let embedded = 0, errors = 0;
  
  for (const node of allNodes.slice(0, limit)) {
    try {
      const text = await buildEmbeddingText(node);
      const vector = await embedText(text, apiKey);
      const status = await putEmbedding(node.uid, vector);
      
      if (status === 204) {
        embedded++;
        if (embedded % 10 === 0) {
          console.log(`  ${embedded}/${Math.min(limit, allNodes.length)} embedded...`);
        }
      } else {
        console.error(`  ERROR [${node.label}]: PUT returned ${status}`);
        errors++;
      }
      
      // Rate limit: 500 req/min for OpenAI embeddings
      await new Promise(r => setTimeout(r, 150));
    } catch (e) {
      console.error(`  ERROR [${node.label}]: ${e.message}`);
      errors++;
    }
  }
  
  console.log(`\nDone: ${embedded} embedded, ${errors} errors`);
}

main().catch(e => {
  console.error('FATAL:', e.message);
  process.exit(1);
});
