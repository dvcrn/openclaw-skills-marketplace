#!/usr/bin/env node
/**
 * MindGraph Extraction Script
 *
 * Reads a text/memory file + SCHEMA.md, calls LLM to extract structured nodes/edges.
 * If the file exceeds the SUMMARIZE_THRESHOLD, it first summarizes via a Flash call,
 * then extracts from the summary. This handles large session transcripts gracefully.
 *
 * Usage:
 *   node skills/mindgraph/extract.js <file_path> [--model <model>] [--output <path>]
 *
 * Model defaults:
 *   Files < 20KB  → google/gemini-3-flash-preview  (fast, cheap)
 *   Files >= 20KB → google/gemini-3-pro-preview    (larger output capacity)
 *   Override with --model <model>
 *
 * Auto-summarize:
 *   Files > 40KB are summarized via Flash first, then extracted from the summary.
 *   Override threshold with --summarize-threshold <bytes>
 */

'use strict';

const fs     = require('fs');
const path   = require('path');
const crypto = require('crypto');

// ─── Entity Resolution ────────────────────────────────────────────────────────
const { resolveEntity, normalizeLabel, loadAliasesFromGraph } = require('./entity-resolution.js');

// ─── Config ───────────────────────────────────────────────────────────────────

const SCHEMA_PATH        = path.join(__dirname, 'SCHEMA.md');
const EXTRACTED_DIR      = path.join(__dirname, 'extracted');
const OC_CONFIG          = path.join(process.env.HOME, '.openclaw/openclaw.json');

const LARGE_FILE_THRESHOLD  = 20 * 1024;  // 20 KB  → switch to Pro model
const SUMMARIZE_THRESHOLD   = 40 * 1024;  // 40 KB  → summarize first, then extract

const MODELS = {
  flash: 'google/gemini-3-flash-preview',
  pro:   'google/gemini-3-pro-preview',
};

// ─── Provider config ──────────────────────────────────────────────────────────

function loadConfig() {
  const c = JSON.parse(fs.readFileSync(OC_CONFIG, 'utf8'));
  const providers = c.models?.providers || {};
  const providerMap = {};

  if (providers.google) {
    providerMap.google = {
      apiKey:  c.env?.GEMINI_API_KEY || providers.google.apiKey,
      baseUrl: (providers.google.baseUrl || 'https://generativelanguage.googleapis.com/v1beta') + '/openai',
    };
  }
  if (providers.moonshot) {
    providerMap.moonshot = {
      apiKey:  c.env?.MOONSHOT_API_KEY || providers.moonshot.apiKey || process.env.MOONSHOT_API_KEY,
      baseUrl: providers.moonshot.baseUrl || 'https://api.moonshot.cn/v1',
    };
  }
  if (providers.anthropic) {
    providerMap.anthropic = {
      apiKey:  providers.anthropic.apiKey || c.env?.ANTHROPIC_API_KEY,
      baseUrl: (providers.anthropic.baseUrl || 'https://api.anthropic.com') + '/v1',
    };
  }
  if (!providerMap.google) {
    providerMap.google = {
      apiKey:  c.env?.GEMINI_API_KEY || '',
      baseUrl: 'https://generativelanguage.googleapis.com/v1beta/openai',
    };
  }
  return { providers: providerMap };
}

// ─── LLM call (returns parsed JSON) ──────────────────────────────────────────

async function callLLM(model, config, messages, { maxTokens, raw } = {}) {
  const { default: fetch } = await import('node-fetch')
    .catch(() => ({ default: globalThis.fetch }));

  const providerPrefix = model.includes('/') ? model.split('/')[0] : 'google';
  const provider = config.providers[providerPrefix] || config.providers.google;
  const { apiKey, baseUrl } = provider;
  const cleanModel = model.replace(/^(google|moonshot|anthropic)\//, '');

  const body = {
    model:       cleanModel,
    messages,
    temperature: providerPrefix === 'moonshot' ? 1 : 0.1,
    max_tokens:  maxTokens || (cleanModel.includes('gemini-3-flash') ? 32000 : 16000),
  };

  const response = await fetch(`${baseUrl}/chat/completions`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${apiKey}` },
    body:    JSON.stringify(body),
    timeout: 300000,
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`API error ${response.status}: ${err.slice(0, 400)}`);
  }

  const parsed  = await response.json();
  const msg     = parsed.choices?.[0]?.message;
  const content = msg?.content || msg?.reasoning_content;
  if (!content) throw new Error(`Empty response. Raw: ${JSON.stringify(parsed).slice(0, 300)}`);

  if (raw) return content; // For summarization pass — plain text

  // Strip markdown fences (handle both ``` and ```json, with or without leading newline)
  let jsonStr = content.trim();
  const fenceMatch = jsonStr.match(/^```(?:json)?\s*([\s\S]*?)\s*```\s*$/);
  if (fenceMatch) {
    jsonStr = fenceMatch[1].trim();
  }
  try {
    return JSON.parse(jsonStr);
  } catch (e) {
    throw new Error(`JSON parse failed: ${e.message}\nContent start: ${content.slice(0, 400)}`);
  }
}

// ─── Summarization pass ───────────────────────────────────────────────────────

async function summarize(content, config) {
  console.error(`  → File too large (${Math.round(Buffer.byteLength(content) / 1024)}KB). Summarizing first...`);

  const summary = await callLLM(MODELS.flash, config, [
    {
      role:    'system',
      content: 'You are a knowledge distillation assistant. Summarize the conversation or document below, focusing on: decisions made, tasks agreed, facts stated, constraints identified, goals discussed, and any anomalies or new information worth preserving. Be thorough but concise. Plain text only, no JSON.',
    },
    {
      role:    'user',
      content: `Summarize this for knowledge graph extraction:\n\n${content}`,
    },
  ], { raw: true });

  console.error(`  → Summary: ${Math.round(Buffer.byteLength(summary) / 1024)}KB`);
  return summary;
}

// ─── Known entities for canonical label reuse ─────────────────────────────────

const STATIC_KNOWN_ENTITIES = `People/Orgs: Shan Rizvi
Goals: Income Generation`;

/**
 * Fetch live entities, projects, and goals from the graph to build the KNOWN_ENTITIES block.
 * Falls back to static list if graph is unavailable.
 */
async function buildKnownEntities() {
  try {
    const mg = require('./mindgraph-client.js');
    
    const [entities, projects, goals] = await Promise.all([
      mg.getNodes({ nodeType: 'Entity', limit: 50 }).then(r => (r.items || r || []).filter(n => !n.tombstone_at)),
      mg.getNodes({ nodeType: 'Project', limit: 20 }).then(r => (r.items || r || []).filter(n => !n.tombstone_at)),
      mg.getNodes({ nodeType: 'Goal', limit: 10 }).then(r => (r.items || r || []).filter(n => !n.tombstone_at)),
    ]);

    const entityLabels = entities.map(n => n.label).sort().join(', ');
    const projectLabels = projects.map(n => n.label).sort().join(', ');
    const goalLabels = goals.map(n => n.label).sort().join(', ');

    const parts = [];
    if (entityLabels) parts.push(`People/Orgs: ${entityLabels}`);
    if (projectLabels) parts.push(`Projects: ${projectLabels}`);
    if (goalLabels) parts.push(`Goals: ${goalLabels}`);

    if (parts.length === 0) return STATIC_KNOWN_ENTITIES;
    return parts.join('\n');
  } catch (e) {
    console.error(`  → Could not fetch live entities from graph: ${e.message}. Using static list.`);
    return STATIC_KNOWN_ENTITIES;
  }
}

// ─── Extraction prompt ────────────────────────────────────────────────────────

function buildPrompt(schema, fileContent, knownEntities) {
  return `You are a knowledge graph extraction agent. Extract structured knowledge from the content below.

## SCHEMA — use ONLY the types defined here
${schema}

## KNOWN ENTITIES — reuse these EXACT labels when the concept appears
${knownEntities}

Use EXACT labels above. Do NOT create variants.

## TYPE SELECTION GUIDE

### Reality layer — use for raw facts and events
- \`Observation\` — something that HAPPENED or was REPORTED at a specific time ("IDF struck Tehran", "Tim Cook said X at WWDC"). Has \`observed_at\` timestamp in props.
- \`Entity\` — a named person, organization, product, or tool. Use for people and orgs mentioned by name.
- \`Snippet\` — a quoted passage worth preserving verbatim. Rare — only for exact quotes with evidential value.
- \`Source\` — DO NOT CREATE. File/session references have no graph value.

### Epistemic layer — use for reasoning, beliefs, patterns
- \`Claim\` — a currently-held belief or factual assertion that may change ("Iran regime at 33%", "Tim Cook is overpriced"). Has \`truth_status\` and \`certainty_degree\` in props.
- \`Evidence\` — a specific data point or measurement that SUPPORTS or REFUTES a Claim. Use with SUPPORTS/REFUTES edges. Has \`quantitative_value\` prop.
- \`Warrant\` — a reasoning principle connecting evidence to a claim ("Historical precedent: IRGC controls succession"). Part of an Argument bundle.
- \`Argument\` — a full reasoning chain (claim + evidence + warrant). Use for structured analytical arguments.
- \`Hypothesis\` — an unconfirmed proposed explanation ("may", "could", "possibly"). Has \`status: open\` prop.
- \`Anomaly\` — a surprising finding or contradiction ("Bug: propsPatch silently ignored"). Has \`severity\` prop.
- \`Pattern\` — a generalizable lesson learned ("Axum 0.8 uses {param} syntax, not :param"). Key prop: \`summary\` is the lesson itself.
- \`Concept\` — an abstract idea being defined ("Peace Architecture", "Deep Psychological Profiling").
- \`Mechanism\` — a causal or functional process ("Heartbeat watchdog restarts server on PID death").
- \`Model\` — an ML model or computational model ("Gemini 3 Flash", "Kimi K2.5"). NOT a general concept.
- \`Question\` — an open question needing resolution. Has \`status: open\` prop.
- \`Constraint\` → see Intent layer below (also epistemic in nature but lives in intent layer).

### Intent layer — use for decisions, constraints, commitments
- \`Decision\` — a made choice with rationale ("Use Gemini Flash for briefings"). Key props: \`question\`, \`decision_rationale\`, \`reversibility\`. NOT for facts — for deliberate choices.
- \`Constraint\` — a binding must/must-not rule ("Never give salary preemptively", "No EHR integration"). Has \`hard: true\` for non-negotiable rules.
- \`Milestone\` — a specific deliverable within a known Project ("mindgraph-rs v0.6.1 Release").
- \`Option\` — an alternative considered in a Decision (use only within Decision context, rarely standalone).
- \`Goal\` — NEVER create. See Rules 10 below.
- \`Project\` — NEVER create unless explicitly requested. See Rule 11 below.

### Action layer — use for workflows and agent actions
- \`Flow\` — a multi-step process or workflow ("Job Application Workflow", "X Listening Workflow"). Has \`step_count\` prop.
- \`FlowStep\` — a single step within a Flow. Has \`order\` prop.
- \`Affordance\` — a specific executable action available to the agent ("xapi post reply", "Telegram Card Delivery"). Has \`risk_level\` and \`reversible\` props.
- \`Execution\` — a record of an agent action that actually ran ("Dreaming Pipeline Verification", "Cron Schedule Update"). Use for past completed actions.
- \`RiskAssessment\` — an evaluation of risk. Use sparingly, only when risk was explicitly assessed.

### Memory layer — use for meta/behavioral rules
- \`Preference\` — how Shan wants things done ("Concrete Before Abstract", "Coworker Vibe"). Has \`key\` and \`value\` props.
- \`MemoryPolicy\` — a rule governing Jaadu's behavior ("No Internal Narration", "Anti-Compaction Strategy"). Has \`policy_text\` prop.
- \`Session\` — a conversation session node. The import script creates these automatically — do NOT extract.
- \`Trace\` — a log of a specific agent action within a session. Extract only for significant auditable agent actions.
- \`Journal\` — narrative reasoning prose. Use for debugging arcs, investigation notes, multi-step reasoning chains.

### Agent layer — use for tasks and plans
- \`Task\` — see Rule 12 below (strict). Has \`status: pending\` and \`priority\` props.
- \`Plan\` — a proposed sequence of steps. Rare — only when a full multi-step plan was explicitly described.
- \`Policy\` — an agent behavioral policy with explicit rules (distinct from MemoryPolicy — use for operational rules like "Fallback Chain", "Salary Negotiation Rule").

## EDGE SELECTION GUIDE

Choose the most semantically precise edge. RELEVANT_TO is a last resort.

| Situation | Correct edge |
|-----------|-------------|
| Evidence backs a Claim | SUPPORTS (Evidence → Claim) |
| Evidence contradicts a Claim | REFUTES (Evidence → Claim) |
| Two Claims oppose each other | CONTRADICTS |
| Decision serves a Goal | MOTIVATED_BY (Decision → Goal) |
| Decision chose an Option | DECIDED_ON (Decision → Option) |
| Node is limited by a Constraint | CONSTRAINED_BY |
| Project breaks into Milestones | DECOMPOSES_INTO |
| Claim B builds on Claim A | EXTENDS (B → A) |
| Argument justifies a Claim | JUSTIFIES (Argument → Claim) |
| Claim addresses a Question | ADDRESSES (Claim → Question) |
| One event followed another | FOLLOWS |
| Work belongs to a person/org | AUTHORED_BY |
| Sub-component belongs to whole | PART_OF |

## OUTPUT RULES
1. Use the TYPE SELECTION GUIDE above, not just "most specific."
2. Every node MUST have a non-empty \`summary\` field (max 300 chars).
3. Edge \`from\` and \`to\` values are node LABELS (not UIDs).
4. Edge types use SCREAMING_SNAKE_CASE.
5. Do NOT create DERIVED_FROM or PART_OF edges — the import script handles provenance.
6. RELEVANT_TO is last resort — only when no edge in the EDGE GUIDE applies.
7. Output valid JSON only — no markdown, no explanation.
8. Do NOT create Source or Session nodes — handled automatically.
9. LABEL RULES (critical):
   - Labels must be SHORT and NOUN-PHRASE style: max 60 characters.
   - Labels identify the thing, not describe it. "MindGraph Port Decision" not "Decision MindGraph UI Port 8766. Status made..."
   - All descriptive content goes in \`summary\` or \`props\`, never in the label.
   - Labels should be reusable as graph node names — imagine them as Wikipedia article titles.
10. GOAL rules (CRITICAL):
   - NEVER create a Goal node. Goals are owned by the human and managed manually.
   - If a goal is mentioned, reference it by label in edges only (e.g. MOTIVATED_BY → "Income Generation").
   - Exception: only if the human explicitly says "add this as a goal."
11. PROJECT rules (CRITICAL):
   - NEVER create a new Project node unless the human explicitly says "start a new project."
   - Reference existing projects in edges only. Known projects are listed in the KNOWN ENTITIES section above.
12. TASK rules (CRITICAL):
   - Only create a Task for a CONCRETE, SPECIFIC, ONE-TIME action explicitly agreed upon (e.g. "send the email", "fix the bug in X").
   - NEVER create Tasks for: recurring ops (crons, briefings), vague intentions, or things already completed.
   - A Task must be completable and archivable. If unsure, use Observation instead.

## OUTPUT FORMAT
{ "nodes": [{ "label": "...", "type": "...", "summary": "...", "props": {} }], "edges": [{ "from": "...", "to": "...", "type": "..." }] }

## CONTENT
${fileContent}`;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const args        = process.argv.slice(2);
  const filePathArg = args.find(a => !a.startsWith('--'));

  if (!filePathArg) {
    console.error('Usage: node extract.js <file_path> [--model <model>] [--output <path>] [--summarize-threshold <bytes>]');
    process.exit(1);
  }

  const filePath = path.resolve(filePathArg);
  if (!fs.existsSync(filePath)) {
    console.error(`File not found: ${filePath}`);
    process.exit(1);
  }

  let fileContent    = fs.readFileSync(filePath, 'utf8');
  const fileSize     = Buffer.byteLength(fileContent, 'utf8');
  const fileHash     = crypto.createHash('sha256').update(fileContent).digest('hex').slice(0, 16);
  const config       = loadConfig();
  const schema       = fs.readFileSync(SCHEMA_PATH, 'utf8');

  // ── Summarize threshold (default 40KB, overridable) ──
  const sumThreshIdx   = args.indexOf('--summarize-threshold');
  const sumThreshold   = sumThreshIdx !== -1 ? parseInt(args[sumThreshIdx + 1]) : SUMMARIZE_THRESHOLD;

  // ── Model selection ──
  const modelIdx = args.indexOf('--model');
  const model    = modelIdx !== -1
    ? args[modelIdx + 1]
    : (fileSize >= LARGE_FILE_THRESHOLD ? MODELS.pro : MODELS.flash);

  const outputIdx  = args.indexOf('--output');
  const explicitOut = outputIdx !== -1 ? args[outputIdx + 1] : null;

  console.error(`Extracting [${model}] (${Math.round(fileSize / 1024)}KB): ${path.basename(filePath)}`);

  // ── Stage 0: Fetch live entities from graph for canonical label reuse ──
  const knownEntities = await buildKnownEntities();

  // ── Stage 1: Summarize if too large ──
  let summarized = false;
  if (fileSize > sumThreshold) {
    fileContent = await summarize(fileContent, config);
    summarized  = true;
  }

  // ── Stage 2: Extract structured nodes ──
  const extracted = await callLLM(model, config, [
    { role: 'system', content: 'You are a knowledge graph extraction agent. Output valid JSON only.' },
    { role: 'user',   content: buildPrompt(schema, fileContent, knownEntities) },
  ]);

  // ── Stage 3: Entity Resolution ───────────────────────────────────────────────
  let entityResolutionStats = { checked: 0, resolved: 0, canonicalized: 0 };
  const entityTypeMap = new Map(); // label -> canonical label

  // Load aliases from graph for better resolution
  await loadAliasesFromGraph().catch(() => {});

  // Resolve Entity nodes
  for (const node of extracted.nodes || []) {
    if (node.type === 'Entity' || node.type === 'Person' || node.type === 'Organization') {
      entityResolutionStats.checked++;
      const resolvedUid = await resolveEntity(node.label, node.type || 'Entity', { 
        createIfMissing: false 
      });
      
      if (resolvedUid) {
        // Found existing entity — store mapping for edge updates
        const normalized = normalizeLabel(node.label);
        try {
          const mg = require('./mindgraph-client.js');
          const graphNode = await mg.getNode(resolvedUid);
          if (graphNode && graphNode.label && graphNode.label !== node.label) {
            console.error(`  ENTITY-RESOLVE: "${node.label}" → "${graphNode.label}"`);
            entityTypeMap.set(normalized, graphNode.label);
            entityResolutionStats.resolved++;
          }
        } catch (e) {
          // Fallback: just use the existing label
        }
      }
    }
  }

  // Update edges to use canonical labels
  for (const edge of extracted.edges || []) {
    const fromNormalized = normalizeLabel(edge.from);
    const toNormalized = normalizeLabel(edge.to);
    
    if (entityTypeMap.has(fromNormalized)) {
      edge.from = entityTypeMap.get(fromNormalized);
      entityResolutionStats.canonicalized++;
    }
    if (entityTypeMap.has(toNormalized)) {
      edge.to = entityTypeMap.get(toNormalized);
      entityResolutionStats.canonicalized++;
    }
  }

  if (entityResolutionStats.resolved > 0) {
    console.error(`  → Entity resolution: ${entityResolutionStats.resolved} duplicates found, ${entityResolutionStats.canonicalized} edges updated`);
  }

  const result = {
    meta: {
      source_path:  filePath,
      extracted_at: new Date().toISOString(),
      model,
      summarized,
      file_hash:    fileHash,
      file_size:    fileSize,
      node_count:   extracted.nodes?.length || 0,
      edge_count:   extracted.edges?.length || 0,
      entity_resolution: entityResolutionStats,
    },
    nodes: extracted.nodes || [],
    edges: extracted.edges || [],
  };

  if (!fs.existsSync(EXTRACTED_DIR)) fs.mkdirSync(EXTRACTED_DIR, { recursive: true });

  const datestamp  = new Date().toISOString().slice(0, 10);
  const outputPath = explicitOut
    || path.join(EXTRACTED_DIR, `${path.basename(filePath)}.${datestamp}.json`);

  fs.writeFileSync(outputPath, JSON.stringify(result, null, 2));
  console.error(`✓ Saved ${result.meta.node_count} nodes, ${result.meta.edge_count} edges → ${outputPath}${summarized ? ' (via summary)' : ''}`);
  process.stdout.write(JSON.stringify(result, null, 2) + '\n');
}

main().catch(e => {
  console.error('FATAL:', e.message);
  process.exit(1);
});
