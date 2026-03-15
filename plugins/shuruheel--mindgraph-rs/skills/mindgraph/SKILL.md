---
name: mindgraph
description: "Structured knowledge graph with 18 cognitive tools for agent memory and reasoning (server v0.8.0)"
---

# MindGraph Skill

MindGraph is a **structured knowledge graph index** for sub-agents, cross-file constraint lookups, and semantic search. Files (MEMORY.md, daily notes) are canonical — MindGraph provides structured relationships and search on top of them.

---

## Setup: Cloud vs Local

MindGraph can run as a **cloud API** or a **local self-hosted server**. Set two env vars to choose:

### Cloud API (recommended — no server, no binary, embeddings included)
```bash
export MINDGRAPH_URL=https://api.mindgraph.cloud
export MINDGRAPH_TOKEN=your-api-key   # from mindgraph.cloud/signup
```
- No binary to install or start
- Embeddings handled server-side — no `OPENAI_API_KEY` needed
- `start.sh` is a no-op when `MINDGRAPH_URL` starts with `https://`

### Local Server (self-hosted)
```bash
bash install.sh       # downloads pre-built binary from GitHub Releases
bash start.sh         # starts server on port 18790
export OPENAI_API_KEY=sk-...   # required for semantic/hybrid search
```
- Runs at `http://127.0.0.1:18790` by default
- Token auto-generated and saved to `data/mindgraph.json` on first start
- `MINDGRAPH_TOKEN` is read from `data/mindgraph.json` automatically

### Environment Variables
| Variable | Required | Description |
|---|---|---|
| `MINDGRAPH_TOKEN` | Always | Bearer token / API key |
| `MINDGRAPH_URL` | Cloud only | Set to `https://api.mindgraph.cloud` |
| `OPENAI_API_KEY` | Local only | Required for semantic/hybrid search |

---

## File Map

All paths relative to skill root (`skills/mindgraph/`):

| File | Purpose |
|---|---|
| `mindgraph-client.js` | **Canonical** client library. All scripts import from here. Workspace root has a symlink. |
| `mindgraph-bridge.js` | CLI bridge + batch writer for OpenClaw sessions. Workspace root has a symlink. |
| `mg-context.js` | Quick mid-conversation retrieval (FTS + semantic + subgraph). Workspace root has a symlink. |
| `entity-resolution.js` | 5-step entity dedup module (cache → aliases → fuzzy_resolve → FTS → semantic) |
| `extract.js` | LLM-powered extraction from text → structured JSON (nodes + edges) |
| `import.js` | Import extracted JSON into graph via cognitive layer endpoints |
| `re-embed.js` | Graph-aware re-embedding (label + summary + neighborhood context) |
| `dedup.js` | Merge duplicate nodes (case-insensitive label + type grouping) |
| `flatten_transcript.py` | Flatten JSONL session transcripts to plain text for extraction |
| `SCHEMA.md` | Full node type + edge type reference (53 node types, 16+ edge types) |
| `start.sh` / `install.sh` | Server lifecycle management |
| `dreaming/` | Nightly analysis pipeline (dream-analysis.js, apply-proposals.js, etc.) |

---

## Design Conventions

1.  **Agent Identity:** Always pass `agent_id: 'jaadu'` (or context-appropriate id) for `changed_by` provenance.
2.  **Atomic Bundling:** Use bundle endpoints (`/epistemic/argument`, `/action/procedure`, `/agent/plan`) to create related nodes and edges in a single transaction.
3.  **Narration:** Narrate before writing to `/memory/config` or `/agent/governance` as these modify behavioral rules.
4.  **Session Framing:** Call `POST /memory/session (action: open)` at the start of each conversation and use the `session_uid` for trace entries and distillation.
5.  **`props` deep-merge (v0.8.0):** All cognitive endpoints accept an optional `props` field. The server deep-merges user-provided props over its handler-constructed defaults.
6.  **Entity `entity_type` in `props` (v0.8.0):** For entity creation, pass `entity_type` inside the `props` object. `mg.manageEntity({ action: 'create', label, entityType })` handles this automatically.
7.  **Retry logic (v5.0.6):** The client automatically retries on 502/503/504 and transient network errors (ECONNRESET, ECONNREFUSED) up to 3 times with exponential backoff.

---

## When to Use Each Tool (Decision Guide)

### Retrieval: Reading from the Graph

| Situation | Tool | Example |
|---|---|---|
| Person/company mentioned mid-conversation | `mg-context.js --entity "name"` | `node mg-context.js --entity "Aaron Goh"` |
| General topic lookup | `mg-context.js "topic"` | `node mg-context.js "Iran regime"` |
| Exact label search | `mg-context.js --fts "label"` | `node mg-context.js --fts "Income Generation"` |
| Explore a node's neighborhood | `mg-context.js --neighborhood <uid>` | `node mg-context.js --neighborhood 01HRX...` |
| Programmatic search (in scripts) | `mg.search(query)` or `mg.hybridSearch(query)` | — |
| Semantic similarity | `mg.retrieve('semantic', { query })` | — |
| Active goals/tasks/questions | `mg.retrieve('active_goals')` etc. | — |

**Rule:** When a named person or company is mentioned, always retrieve before responding. It's cheap (<2s).

### Writing: Updating the Graph

| Trigger | Tool | Code |
|---|---|---|
| Decision made/confirmed | `mg.deliberate` | `mg.deliberate({ action: 'open_decision', label, description })` then `mg.deliberate({ action: 'resolve', decisionUid, resolutionRationale })` |
| Hard rule stated ("never X") | `mg.governance` | `mg.governance({ action: 'create_policy', label, policyContent })` |
| Task committed | `mg.plan` | `mg.plan({ action: 'create_task', label, description })` |
| Preference expressed | `mg.memoryConfig` | `mg.memoryConfig({ action: 'set_preference', label, value })` |
| New person/org/tool | `mg.manageEntity` | `mg.manageEntity({ action: 'create', label, entityType })` — dedup-safe |
| Observation worth preserving | `mg.ingest` | `mg.ingest(label, content, 'observation')` |
| Evidence-backed claim | `mg.addArgument` | `mg.addArgument({ claim: { label, content }, evidence: [...], warrant: { label, explanation } })` |
| Anomaly/bug discovered | `mg.addInquiry` | `mg.addInquiry(label, details, 'anomaly')` |
| Goal progress updated | `mg.evolve` | `mg.evolve('update', uid, { propsPatch: { progress: 0.5 } })` |
| Structural pattern/concept | `mg.addStructure` | `mg.addStructure(label, content, 'pattern')` |

**Write threshold:** Would this still be useful in 7 days without the chat context? If yes, write it.

**Label discipline:** Short noun-phrase, max 60 chars. Think Wikipedia article titles.
- ✅ "MindGraph Port Decision"
- ❌ "Decision MindGraph UI Port 8766. Status made..."

**Don't write:** Routine messages, heartbeat acks, search results, anything already in MEMORY.md verbatim.

### Session Framing (main sessions)

```javascript
// At session start:
const { session_uid } = await mg.sessionOp({ action: 'open', label: 'Session 2026-03-08 20:00', focus: '...' });

// During session — trace key reasoning/decisions:
await mg.sessionOp({ action: 'trace', session_uid, note: 'Decided X because Y' });

// At session end:
await mg.sessionOp({ action: 'close', session_uid, agent_id: 'jaadu' });
```

### Significant Judgments (Arguments)

For market assessments, product framing decisions, job opportunity evaluations:

```javascript
await mg.addArgument({
  claim: { label: 'Iran Regime Fall underpriced at 37%', content: 'Fair value ~50%...' },
  evidence: [{ label: 'IRGC interim council = short-term stability', description: '...' }],
  warrant: { label: 'Succession contests increase instability', explanation: '...' }
});
```

---

## Cognitive Layer Endpoints (The 18 Tools)

### Reality Layer (Raw Input)
- **POST /reality/ingest:** Capture `source` (web/paper/book), `snippet` (auto-links to source), or `observation`. Accepts optional `props` to deep-merge.
- **POST /reality/entity:** `create` (dedup-safe via `find_or_create_entity` — checks alias + case-insensitive match, returns `{node, created: bool}`; pass `entity_type` inside `props`), `alias`, `resolve`, `fuzzy_resolve`, `merge`, or `relate` (creates edge between `source_uid` and `target_uid` with `edge_type`).

### Epistemic Layer (Reasoning)
- **POST /epistemic/argument:** Atomic Toulmin bundle. Creates `Claim` + `Evidence` + `Warrant` + `Argument` nodes and wires edges.
- **POST /epistemic/inquiry:** Record `hypothesis`, `anomaly`, `assumption`, `question`, or `open_question`.
- **POST /epistemic/structure:** Crystallize `concept`, `pattern`, `mechanism`, `model`, `paradigm`, `analogy`, `theorem`, or `equation`.

### Intent Layer (Commitments)
- **POST /intent/commitment:** Declare `goal`, `project`, or `milestone`.
- **POST /intent/deliberation:** Manage `open_decision`, `add_option`, `add_constraint`, or `resolve` (creates `DecidedOn` edge).

### Action Layer (Workflows)
- **POST /action/procedure:** Design `create_flow`, `add_step`, `add_affordance`, or `add_control`.
- **POST /action/risk:** `assess` a node (severity/likelihood) or `get_assessments`.

### Memory Layer (Persistence)
- **POST /memory/session:** `open`, `trace` (real-time recording), `close` (sets `ended_at`), or `journal` (creates a `Journal` node, auto-linked to session).
- **POST /memory/distill:** Synthesis of a session into a durable `Summary` node.
- **POST /memory/config:** `set_preference`, `set_policy`, `get_preferences`, or `get_policies`.

### Agent Layer (Control)
- **POST /agent/plan:** `create_task`, `create_plan`, `add_step`, `update_status`, or `get_plan`. Note: `update_status` uses `targetUid` (not `taskUid`).
- **POST /agent/governance:** `create_policy`, `set_budget`, `request_approval`, or `resolve_approval`.
- **POST /agent/execution:** `start`, `complete`, `fail`, or `register_agent`.

### Connective Tissue
- **POST /retrieve:** Unified search: `text`, `semantic`, `hybrid` (RRF fusion, k=60), `active_goals`, `open_questions`, `weak_claims`, `pending_approvals`, `layer`, `recent`.
- **POST /traverse:** Navigation: `chain`, `neighborhood`, `path`, `subgraph`.
- **POST /evolve:** Mutation: `update`, `tombstone` (with cascade), `restore`, `decay`, `history`, `snapshot`.

---

## Client API (mindgraph-client.js)

```javascript
const mg = require('./mindgraph-client.js');

// Reality
await mg.ingest(label, content, 'observation', { confidence, props });
await mg.manageEntity({ action: 'create', label, entityType: 'Person' });
await mg.manageEntity({ action: 'relate', sourceUid, targetUid, edgeType: 'WorksAt' });
await mg.findOrCreateEntity("Aaron Goh", "Person");  // Dedup-safe wrapper

// Epistemic
await mg.addArgument({ claim: { label, content }, evidence: [...], warrant: { label, explanation } });
await mg.addInquiry(label, content, 'anomaly', { status: 'open' });
await mg.addStructure(label, content, 'pattern', { summary: 'the lesson' });

// Intent
await mg.addCommitment(label, description, 'milestone', { parentUid, dueDate });
await mg.deliberate({ action: 'open_decision', label, description });
await mg.deliberate({ action: 'resolve', decisionUid, resolutionRationale });

// Action
await mg.procedure({ action: 'create_flow', label, description });
await mg.risk({ action: 'assess', label, assessedUid, severity: 'high', likelihood: 'medium' });

// Memory
await mg.sessionOp({ action: 'open', label, focus });
await mg.sessionOp({ action: 'trace', sessionUid, note: '...' });
await mg.sessionOp({ action: 'journal', label, summary, props: { content, journal_type: 'investigation', tags: [] } });
await mg.distill(label, content, { sessionUid });
await mg.memoryConfig({ action: 'set_preference', label, value });

// Agent
await mg.plan({ action: 'create_task', label, description, status: 'pending' });
await mg.plan({ action: 'update_status', targetUid: taskUid, status: 'completed' });
await mg.governance({ action: 'create_policy', label, policyContent });

// Search & Navigate
await mg.search(query, { limit: 10 });                    // FTS
await mg.retrieve('semantic', { query, limit: 10 });       // Vector search
await mg.hybridSearch(query, { limit: 10 });               // RRF fusion (best quality)
await mg.traverse('neighborhood', uid, { maxDepth: 2 });   // Graph walk
await mg.retrieve('active_goals');                          // Structured queries

// Mutate
await mg.evolve('update', uid, { label, summary, propsPatch: { status: 'active' } });
await mg.evolve('tombstone', uid, { reason: 'completed', cascade: true });

// Low-level (backward compat)
await mg.addNode(label, props, { summary, confidence });
await mg.getNode(uid);
await mg.updateNode(uid, updates, { reason });
await mg.link(fromUid, toUid, 'SUPPORTS');
await mg.getEdges(uid);
await mg.edgesTo(uid, 'SUPPORTS');
```

---

## Extraction Pipeline

### Full pipeline (used by heartbeat and end-of-session writeback):
```bash
# 1. Flatten transcript to plain text
python3 flatten_transcript.py <session.jsonl> --since-minutes 60 --output /tmp/conv.txt

# 2. Extract structured nodes/edges via LLM
node extract.js /tmp/conv.txt --output /tmp/extracted.json

# 3. Import into graph via cognitive layer
node import.js /tmp/extracted.json
```

### Extract model selection:
- Files < 20KB → `gemini-3-flash-preview` (fast, cheap)
- Files ≥ 20KB → `gemini-3-pro-preview` (larger output)
- Files > 40KB → Auto-summarized via Flash first, then extracted

### Entity resolution (during extraction):
The pipeline resolves entities post-extraction via `entity-resolution.js`:
1. Known aliases map → 2. `fuzzy_resolve` API → 3. FTS exact match → 4. Semantic similarity (0.85 threshold)

---

## Maintenance Scripts

| Script | What it does | When to run |
|---|---|---|
| `dedup.js` | Merge nodes with identical labels (grouped by `node_type::label`) | After bulk imports |
| `re-embed.js` | Regenerate graph-aware embeddings for all nodes | After schema changes, periodically |
| `reindex-search.js` | Rebuild FTS index | After server upgrades |
| `maintenance.js` | Batch watchdog + extraction trigger | Via heartbeat |

---

## Sub-agent Usage

Sub-agents should NOT receive MEMORY.md. Instead:
- Use `mg.retrieve` and `mg.traverse` for context
- Use `mg.search` for quick lookups
- Always pass `agentId` to track provenance

---

## Full Schema Reference

See `SCHEMA.md` for complete node type definitions (53 types), edge type definitions, and key distinction rules.

### Key Distinctions (most common errors):
1. **Claim vs Observation:** "X happened on date Y" → Observation. "X is currently true" → Claim.
2. **Claim vs Decision:** "BCG X is top priority" → Decision. "BCG X is a consulting firm" → Claim.
3. **Claim vs Constraint:** "Never give salary preemptively" → Constraint (hard=true).
4. **Claim vs Preference:** "Shan prefers concise replies" → Preference.
5. **Claim vs Pattern:** "Axum 0.7 uses :param syntax" → Pattern (generalizable lesson).

### FTS Searchability
FTS indexes **all user-authored text** across 35+ string fields — not just label and summary. Use `mg.search()` or `mg.hybridSearch()`.

### Entity Dedup
Use `mg.findOrCreateEntity(label, entityType)` for all entity creation. Checks alias + case-insensitive match before creating.

### Hybrid Retrieval
`mg.hybridSearch(query, opts)` performs Reciprocal Rank Fusion of FTS + vector results. Use this instead of separate `search()` + `retrieve()` calls.
