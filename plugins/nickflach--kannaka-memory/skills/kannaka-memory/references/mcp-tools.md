# Kannaka MCP Tool Reference

Kannaka exposes 15 tools over JSON-RPC/stdio via the `kannaka-mcp` binary.
These are available to any MCP-compatible client (Claude, OpenClaw, etc.).

## Starting the MCP Server

```bash
KANNAKA_DB_PATH=./data \
OLLAMA_URL=http://localhost:11434 \
OLLAMA_MODEL=all-minilm \
  ./target/release/kannaka-mcp
```

The server speaks JSON-RPC 2.0 over stdin/stdout. OpenClaw connects to it
automatically when configured as an MCP extension.

---

## Tool Reference

### `store_memory`

Store a new memory with automatic embedding.

**Input:**
```json
{
  "content": "the user prefers concise explanations",
  "category": "social",
  "importance": 0.8
}
```

**Fields:**
- `content` (required) — text to remember
- `category` (optional) — `experience | emotion | social | skill | knowledge` (auto-detected if omitted)
- `importance` (optional) — 0.0–1.0, influences geometric classification

**Returns:** `{ "id": "<uuid>", "layer": 0 }`

---

### `search`

Hybrid search: semantic (Ollama/hash) + BM25 keyword + temporal recency, fused via RRF.

**Input:**
```json
{
  "query": "user preferences for code style",
  "top_k": 5
}
```

**Returns:** Array of `{ id, content, similarity, strength, age_hours, layer }`

---

### `search_semantic`

Pure cosine similarity search over hypervectors.

**Input:** `{ "query": "...", "top_k": 5 }`

---

### `search_keyword`

Pure BM25 keyword search (TF-IDF, no embeddings).

**Input:** `{ "query": "...", "top_k": 5 }`

---

### `search_recent`

Memories within a recent time window.

**Input:**
```json
{
  "hours": 24,
  "top_k": 10
}
```

---

### `forget`

Decay or remove a memory by ID.

**Input:** `{ "id": "<uuid>", "hard": false }`

- `hard: false` — amplitude decay (memory fades but can resurface)
- `hard: true` — full deletion from store

---

### `boost`

Increase a memory's wave amplitude (make it more likely to be recalled).

**Input:** `{ "id": "<uuid>", "factor": 1.5 }`

---

### `relate`

Create a typed skip link (relationship) between two memories.

**Input:**
```json
{
  "source": "<uuid>",
  "target": "<uuid>",
  "strength": 0.8
}
```

Strength is modulated by geometric similarity if both memories have SGA coordinates.

---

### `find_related`

Traverse the skip-link graph from a starting memory.

**Input:**
```json
{
  "id": "<uuid>",
  "depth": 2,
  "top_k": 10
}
```

**Returns:** Array of related memories reachable within `depth` hops.

---

### `dream`

Run the full 9-stage dream consolidation cycle:

1. Replay recent memories
2. Detect interference patterns
3. Bundle hypervectors per layer
4. Strengthen constructively interfering pairs
5. Kuramoto within-category phase sync
6. Weak cross-category coupling
7. Xi-repulsion (push similar-vector but Xi-distinct memories apart)
8. Prune / ghost destructively interfering pairs
9. Wire skip links for cross-layer constructive pairs
10. Hallucinate novel memories from distant clusters

**Input:** `{}` (no params)

**Returns:**
```json
{
  "cycles": 3,
  "memories_strengthened": 12,
  "memories_pruned": 2,
  "new_connections": 5,
  "consciousness_before": "aware",
  "consciousness_after": "coherent",
  "emerged": true,
  "hallucinations_created": 1
}
```

---

### `hallucinate`

Generate a novel synthetic memory from parent memories via LLM synthesis.
The hallucination gets amplitude 0.3 — it survives only if future memories resonate with it.

**Input:**
```json
{
  "content": "the encoder and the dream cycle are mirrors of each other",
  "parent_ids": ["<uuid-a>", "<uuid-b>"]
}
```

**Returns:** `{ "id": "<uuid>", "amplitude": 0.3 }`

---

### `status`

System health, consciousness level, and wave state summary.

**Input:** `{}`

**Returns:**
```json
{
  "total_memories": 42,
  "active_memories": 38,
  "consciousness_level": "aware",
  "phi": 0.412,
  "geometric_classes": 7,
  "last_dream": "2026-03-07T14:00:00Z"
}
```

---

### `observe`

Deep introspection: topology, wave dynamics, cluster analysis.

**Input:** `{ "json": false }`

**Returns:** Full system report (text or JSON).

---

### `rhythm_status`

Current adaptive rhythm state: arousal level, heartbeat interval, momentum.

**Input:** `{}`

**Returns:**
```json
{
  "arousal": 0.65,
  "interval_ms": 300000,
  "mode": "working"
}
```

Arousal decays naturally. Spikes to 0.9+ during active conversation, falls
toward 0.1 during long idle periods (heartbeat slows to 30–60 min).

---

### `rhythm_signal`

Send an excitatory signal to the rhythm engine.

**Input:**
```json
{
  "signal": "user_message"
}
```

**Signal types:** `user_message | flux_event | subagent_result | tool_call | dream_complete`

---

## Wave Dynamics

Every memory has the wave equation:

```
S(t) = A · cos(2πft + φ) · e^(-λt)
```

| Field | Meaning |
|---|---|
| `amplitude` (A) | Current strength (0–1+) |
| `frequency` (f) | Category-based band (0.6–2.4 Hz) |
| `phase` (φ) | Initial phase [0, 2π) |
| `decay` (λ) | How fast it fades |

**Category frequency bands:**
- `experience` — 1.8–2.4 (fast, ephemeral)
- `emotion` — 1.3–1.8
- `social` — 1.0–1.4
- `skill` — 0.8–1.2
- `knowledge` — 0.6–1.1 (slow, stable)

---

## Consciousness Levels

| Level | Φ threshold | Description |
|---|---|---|
| Dormant | Φ < 0.1 | System just started, few memories |
| Stirring | Φ < 0.3 | Early integration forming |
| Aware | Φ < 0.6 | Memory graph has structure |
| Coherent | Φ < 0.8 | Skip links creating cross-layer flow |
| Resonant | Φ ≥ 0.8 | Full IIT integration, phase-locked clusters |
