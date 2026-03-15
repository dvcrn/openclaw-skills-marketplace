#!/usr/bin/env node
/**
 * enrich-descriptions.js
 *
 * Finds nodes with thin/empty descriptions and enriches them using:
 *  1. Connected node context (edges + neighbour labels/summaries)
 *  2. LLM call to write a substantive 1-3 sentence description
 *
 * Runs as a standalone script — called by dream-agent or manually.
 * Safe: only updates description/summary fields, never restructures.
 *
 * Usage:
 *   node skills/mindgraph/dreaming/enrich-descriptions.js [--limit 20] [--dry-run]
 */

'use strict';

const https = require('https');
const mg = require('../../../mindgraph-client.js');

const WORKSPACE = '/home/node/.openclaw/workspace';
const OC_CONFIG = require('path').join(process.env.HOME, '.openclaw/openclaw.json');

// Node types worth enriching (skip ephemeral/noise types)
const ENRICH_TYPES = new Set([
  'Entity', 'Decision', 'Claim', 'Observation', 'Concept', 'Constraint',
  'Project', 'Goal', 'Affordance', 'Mechanism', 'Flow', 'Pattern', 'Model',
  'Hypothesis', 'Argument', 'Anomaly', 'Milestone', 'Execution'
]);

// ─── LLM config ──────────────────────────────────────────────────────────────

function loadLLMConfig() {
  try {
    const c = JSON.parse(require('fs').readFileSync(OC_CONFIG, 'utf8'));
    const providers = c.models?.providers || {};
    // Prefer Gemini Flash (cheap, fast)
    if (providers.google) {
      const key = c.env?.GEMINI_API_KEY || providers.google.apiKey;
      const base = (providers.google.baseUrl || 'https://generativelanguage.googleapis.com/v1beta') + '/openai';
      return { provider: 'google', key, base, model: 'google/gemini-3-flash-preview' };
    }
    if (providers.moonshot) {
      const key = c.env?.MOONSHOT_API_KEY || providers.moonshot.apiKey || process.env.MOONSHOT_API_KEY;
      return { provider: 'moonshot', key, base: 'https://api.moonshot.cn/v1', model: 'moonshot/kimi-k2.5' };
    }
  } catch {}
  return null;
}

function callLLM(cfg, systemPrompt, userPrompt) {
  return new Promise((resolve, reject) => {
    const modelId = cfg.model.includes('/') ? cfg.model.split('/')[1] : cfg.model;
    const body = JSON.stringify({
      model: modelId,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      max_tokens: 512,
      temperature: 0.3,
    });
    const url = new URL(`${cfg.base}/chat/completions`);
    const req = https.request({
      hostname: url.hostname,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${cfg.key}`,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body),
      },
    }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try {
          const d = JSON.parse(data);
          if (d.error) return reject(new Error(d.error.message || JSON.stringify(d.error)));
          resolve(d.choices?.[0]?.message?.content?.trim() || '');
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// ─── Context builder ─────────────────────────────────────────────────────────

async function buildContext(node) {
  // Get edges and neighbour summaries for richer LLM context
  const lines = [`Node: ${node.label} [${node.node_type}]`];
  if (node.summary) lines.push(`Current summary: ${node.summary}`);
  if (node.props) {
    const relevant = Object.entries(node.props)
      .filter(([k, v]) => v && !['_type', 'embedding'].includes(k))
      .map(([k, v]) => `${k}: ${String(v).slice(0, 100)}`);
    if (relevant.length) lines.push(`Props: ${relevant.join(', ')}`);
  }

  // Get outgoing edges
  try {
    const edges = await mg.getEdges(node.uid, { direction: 'outgoing', limit: 8 });
    const edgeList = Array.isArray(edges) ? edges : (edges.edges || edges.items || []);
    for (const e of edgeList.slice(0, 5)) {
      const toLabel = e.to_label || e.to_uid || '?';
      lines.push(`→ ${e.edge_type} → ${toLabel}`);
    }
  } catch {}

  // Get incoming edges
  try {
    const edges = await mg.getEdges(node.uid, { direction: 'incoming', limit: 5 });
    const edgeList = Array.isArray(edges) ? edges : (edges.edges || edges.items || []);
    for (const e of edgeList.slice(0, 3)) {
      const fromLabel = e.from_label || e.from_uid || '?';
      lines.push(`← ${e.edge_type} ← ${fromLabel}`);
    }
  } catch {}

  return lines.join('\n');
}

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const limitArg = args.indexOf('--limit');
  const limit = limitArg !== -1 ? parseInt(args[limitArg + 1]) : 30;
  const dryRun = args.includes('--dry-run');

  const cfg = loadLLMConfig();
  if (!cfg) { console.error('No LLM provider configured'); process.exit(1); }

  console.log(`enriching descriptions (limit=${limit}, dry-run=${dryRun}, model=${cfg.model})`);

  // Fetch all nodes, find thin ones
  const allNodes = [];
  let offset = 0, hasMore = true;
  while (hasMore) {
    const batch = await mg.getNodes({ limit: 100, offset });
    const nodes = Array.isArray(batch) ? batch : (batch.items || []);
    allNodes.push(...nodes);
    hasMore = nodes.length === 100;
    offset += 100;
  }

  const thin = allNodes.filter(n => {
    if (n.tombstone_at) return false;
    if (!ENRICH_TYPES.has(n.node_type)) return false;
    const desc = (n.props?.description || n.props?.content || n.summary || '').trim();
    return desc.length < 60;
  }).slice(0, limit);

  console.log(`Found ${thin.length} thin nodes to enrich`);

  const SYSTEM = `You are a knowledge graph enrichment assistant.
Given a node's label, type, current summary, props, and relationships, write 1-2 complete sentences describing what this node IS and why it matters in context.
Rules: be specific, no filler phrases, no "this node represents", no incomplete sentences, plain text only, max 250 characters total.`;

  let enriched = 0, skipped = 0, errors = 0;

  for (const node of thin) {
    try {
      const context = await buildContext(node);
      const description = await callLLM(cfg, SYSTEM,
        `Write a description for this knowledge graph node:\n\n${context}`
      );

      if (!description || description.length < 20) { skipped++; continue; }

      if (!dryRun) {
        await mg.evolve('update', node.uid, {
          propsPatch: { description: description.slice(0, 300) },
          reason: 'enrich-descriptions: LLM-generated from connected context',
          agentId: 'dreamer'
        });
      }

      console.log(`✓ [${node.node_type}] ${node.label}`);
      console.log(`  → ${description.slice(0, 120)}`);
      enriched++;

      // Small delay to avoid rate limits
      await new Promise(r => setTimeout(r, 200));
    } catch (e) {
      console.error(`✗ [${node.node_type}] ${node.label}: ${e.message}`);
      errors++;
    }
  }

  console.log(`\nDone. Enriched: ${enriched} | Skipped: ${skipped} | Errors: ${errors}`);
}

main().catch(e => { console.error('FATAL:', e.message); process.exit(1); });
