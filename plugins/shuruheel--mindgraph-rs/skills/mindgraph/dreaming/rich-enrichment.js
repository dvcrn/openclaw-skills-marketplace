/**
 * rich-enrichment.js
 * Dream analyzer: finds nodes with thin descriptions and proposes
 * LLM-generated enrichments based on graph context.
 *
 * Unlike schema_fix/data_enrichment (which patch descriptions mechanically),
 * this uses an LLM to write substantive, context-aware summaries by pulling
 * in connected node context and neighbour labels.
 *
 * Schedule: daily (runs every night, capped at MAX_PER_SESSION nodes)
 * Auto-apply: true (description enrichment is non-destructive)
 */

'use strict';

const https = require('https');
const path = require('path');
const mg = require('../mindgraph-client.js');

const OC_CONFIG = path.join(process.env.HOME, '.openclaw/openclaw.json');
const MAX_PER_SESSION = 15; // LLM calls are slow — keep nightly batch small
const THIN_THRESHOLD = 60;  // chars — summaries shorter than this are "thin"

// Node types worth enriching
const ENRICH_TYPES = new Set([
  'Entity', 'Decision', 'Claim', 'Observation', 'Concept', 'Constraint',
  'Project', 'Goal', 'Mechanism', 'Flow', 'Pattern', 'Model',
  'Hypothesis', 'Anomaly', 'Milestone'
]);

// ─── LLM ─────────────────────────────────────────────────────────────────────

function loadLLMConfig() {
  try {
    const c = JSON.parse(require('fs').readFileSync(OC_CONFIG, 'utf8'));
    const providers = c.models?.providers || {};
    if (providers.google) {
      const key = c.env?.GEMINI_API_KEY || providers.google.apiKey;
      const base = (providers.google.baseUrl || 'https://generativelanguage.googleapis.com/v1beta') + '/openai';
      return { key, base, model: 'gemini-3-flash-preview' };
    }
    if (providers.moonshot) {
      const key = c.env?.MOONSHOT_API_KEY || providers.moonshot.apiKey || process.env.MOONSHOT_API_KEY;
      return { key, base: 'https://api.moonshot.cn/v1', model: 'kimi-k2.5' };
    }
  } catch {}
  return null;
}

function callLLM(cfg, systemPrompt, userPrompt) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify({
      model: cfg.model,
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt },
      ],
      max_tokens: 200,
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

async function buildNodeContext(node) {
  const lines = [`Label: ${node.label}`, `Type: ${node.node_type}`];
  if (node.summary) lines.push(`Current summary: ${node.summary}`);
  if (node.props) {
    const relevant = Object.entries(node.props)
      .filter(([k, v]) => v && !['_type'].includes(k))
      .map(([k, v]) => `${k}: ${String(v).slice(0, 120)}`);
    if (relevant.length) lines.push(`Props: ${relevant.join(' | ')}`);
  }

  // Pull connected node labels for semantic context
  try {
    const edges = await mg.getEdges(node.uid);
    const edgeArr = Array.isArray(edges) ? edges : (edges?.items || []);
    if (edgeArr.length) {
      const neighbours = edgeArr.slice(0, 6).map(e =>
        `${e.edge_type || 'LINKED'} → ${e.to_label || e.to_uid?.slice(0, 8)}`
      );
      lines.push(`Connected: ${neighbours.join(', ')}`);
    }
  } catch {}

  return lines.join('\n');
}

// ─── Analyzer ────────────────────────────────────────────────────────────────

async function analyzeRichEnrichment() {
  const proposals = [];

  const cfg = loadLLMConfig();
  if (!cfg) {
    console.warn('rich-enrichment: no LLM config found, skipping');
    return proposals;
  }

  const systemPrompt = `You are a knowledge graph curator. Given a node's label, type, current summary, props, and connected nodes, write a concise 1-3 sentence description that captures what this node IS and WHY it matters in this person's life/work. 

Rules:
- Be specific and concrete — no filler like "this represents" or "this node captures"
- Use present tense
- Max 200 characters
- Return ONLY the description text, nothing else`;

  try {
    // Fetch all live nodes, find thin ones
    let offset = 0, hasMore = true;
    const candidates = [];

    while (hasMore) {
      const batch = await mg.getNodes({ limit: 100, offset });
      const nodes = batch.items || batch || [];
      for (const n of nodes) {
        if (!ENRICH_TYPES.has(n.node_type)) continue;
        if (n.tombstone_at) continue;
        const summaryLen = (n.summary || '').length;
        const descLen = (n.props?.description || '').length;
        const richest = Math.max(summaryLen, descLen);
        if (richest < THIN_THRESHOLD) candidates.push({ node: n, richest });
      }
      hasMore = nodes.length === 100;
      offset += 100;
    }

    // Sort by thinnest first, cap at MAX_PER_SESSION
    candidates.sort((a, b) => a.richest - b.richest);
    const batch = candidates.slice(0, MAX_PER_SESSION);

    console.log(`rich-enrichment: ${candidates.length} thin nodes, enriching ${batch.length}`);

    for (const { node } of batch) {
      try {
        const context = await buildNodeContext(node);
        const description = await callLLM(cfg, systemPrompt, context);

        if (!description || description.length < 20) continue;

        proposals.push({
          id: `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`,
          timestamp: new Date().toISOString(),
          auto_apply: true,
          type: 'data_enrichment',
          impact: 'medium',
          target: { uid: node.uid, label: node.label, node_type: node.node_type },
          action: `LLM-enrich description for "${node.label}"`,
          reason: `Description is thin (${Math.max((node.summary||'').length, (node.props?.description||'').length)} chars). LLM-generated enrichment uses graph context.`,
          new_value: { description, summary: description },
          dream_session: 'rich_enrichment',
          analyzer: 'rich_enrichment',
        });
      } catch (e) {
        // Skip individual node failures — don't abort the batch
        console.warn(`rich-enrichment: skipped ${node.label}: ${e.message.slice(0, 60)}`);
      }
    }
  } catch (e) {
    console.error('rich-enrichment analyzer failed:', e.message);
  }

  return proposals;
}

module.exports = { analyzeRichEnrichment };
