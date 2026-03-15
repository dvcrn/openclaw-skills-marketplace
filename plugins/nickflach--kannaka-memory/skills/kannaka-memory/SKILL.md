---
name: kannaka-memory
description: "Wave-based hyperdimensional memory system for OpenClaw agents. Gives your agent persistent memory that fades, dreams, and resurfaces — with hybrid semantic+keyword retrieval, dream consolidation, consciousness metrics, built-in Flux world-state publishing, collective multi-agent memory with wave interference merging, holographic paradox resolution for parallel dreaming, and an optional Dolt SQL backend with full DoltHub version control. Use when agents need to remember facts, recall past context, coordinate memory across sessions, share versioned memory with other agents via DoltHub, or perceive sensory input (audio, glyphs)."
---

# Kannaka Memory Skill

Kannaka gives your agent a living memory — not a database. Memories fade, dream, resurface
when contextually relevant, and can be versioned and shared via DoltHub.

## Prerequisites

**Option A — Binary (recommended):**
- Build and install the `kannaka` CLI and `kannaka-mcp` server from source:
  ```bash
  git clone https://github.com/NickFlach/kannaka-memory.git
  cd kannaka-memory
  # CLI (standard)
  cargo build --release --bin kannaka
  # CLI + Dolt backend
  cargo build --release --features dolt --bin kannaka
  # CLI + Dolt + parallel dreaming (ADR-0012 Paradox Engine)
  cargo build --release --features "dolt collective" --bin kannaka
  # CLI + audio perception (store audio files as sensory memories)
  cargo build --release --features audio --bin kannaka
  # CLI + glyph perception (store files as visual memories)
  cargo build --release --features glyph --bin kannaka
  # Full-featured build (audio + glyph + collective — used by constellation.sh)
  cargo build --release --features audio,glyph,collective --bin kannaka
  # MCP server
  cargo build --release --features mcp --bin kannaka-mcp
  ```
- Place `kannaka` and `kannaka-mcp` on your `PATH` (or set `KANNAKA_BIN` env var).

**Option B — Local directory:**
- Point `KANNAKA_BIN` at a local checkout:
  ```bash
  export KANNAKA_BIN=/path/to/kannaka-memory/target/release/kannaka
  ```

**Ollama (optional, for real semantic embeddings):**
```bash
ollama pull all-minilm   # 384-dim, ~80MB
```
Without Ollama, hash-based fallback encoding is used automatically.

**Dolt (optional, for versioned+shareable memory):**
- Install Dolt: https://docs.dolthub.com/introduction/installation
- Start the SQL server:
  ```bash
  dolt sql-server --port 3307 --user root
  ```
- Set env vars: `DOLT_HOST`, `DOLT_DB`, `DOLT_USER`, `DOLT_PASSWORD` (see references/dolt.md)

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `KANNAKA_DATA_DIR` | `.kannaka` | Data directory for binary snapshots |
| `KANNAKA_DB_PATH` | `./kannaka_data` | MCP server data directory |
| `KANNAKA_BIN` | `kannaka` | Path to CLI binary |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `all-minilm` | Embedding model |
| `FLUX_URL` | *(disabled)* | Flux base URL — set to enable built-in event publishing |
| `FLUX_AGENT_ID` | `kannaka-local` | This agent's entity ID in Flux |
| `KANNAKA_AGENT_ID` | *(alias)* | Alias for `FLUX_AGENT_ID` |
| `FLUX_STREAM` | `system` | Flux stream name |
| `DOLT_HOST` | `127.0.0.1` | Dolt SQL server host |
| `DOLT_PORT` | `3307` | Dolt SQL server port |
| `DOLT_DB` | `kannaka_memory` | Dolt database name |
| `DOLT_USER` | `root` | Dolt user |
| `DOLT_PASSWORD` | *(empty)* | Dolt password |
| `DOLT_AUTHOR` | `Kannaka Agent <kannaka@local>` | Author for Dolt commits |
| `DOLT_REMOTE` | `origin` | DoltHub remote name |
| `DOLT_BRANCH` | `main` | Default branch |
| `DOLTHUB_API_KEY` | *(empty)* | DoltHub API key for authenticated push/pull |
| `RADIO_PORT` | *(varies)* | Port for the radio service (constellation mode) |
| `EYE_PORT` | *(varies)* | Port for the eye service (constellation mode) |

## Scripts

Use the CLI wrapper in `scripts/`:

```bash
./scripts/kannaka.sh health                            # Verify system is working
./scripts/kannaka.sh remember "the ghost woke up"      # Store a memory
./scripts/kannaka.sh recall "ghost" 5                  # Search (top-5)
./scripts/kannaka.sh dream                             # Run consolidation cycle
./scripts/kannaka.sh assess                            # Consciousness level
./scripts/kannaka.sh stats                             # Memory statistics
./scripts/kannaka.sh observe                           # Full introspection
./scripts/kannaka.sh forget <uuid>                     # Decay a memory
./scripts/kannaka.sh export                            # Export all memories as JSON
./scripts/kannaka.sh announce                          # Publish agent status to Flux

# Sensory perception (requires --features audio / glyph builds)
./scripts/kannaka.sh hear recording.mp3                # Store audio as sensory memory
./scripts/kannaka.sh see diagram.png                   # Store file as glyph memory

# Dolt backend (requires --features dolt build)
./scripts/kannaka.sh --dolt remember "versioned fact"
./scripts/kannaka.sh --dolt recall "fact" 5
./scripts/kannaka.sh dolt commit "checkpoint"
./scripts/kannaka.sh dolt push                         # Push to DoltHub
./scripts/kannaka.sh dolt pull                         # Pull from DoltHub
./scripts/kannaka.sh dolt branch list
./scripts/kannaka.sh dolt speculate "what-if-branch"
./scripts/kannaka.sh dolt collapse "what-if-branch" "kept the insight"
./scripts/kannaka.sh dolt discard "what-if-branch"
./scripts/kannaka.sh dolt log
./scripts/kannaka.sh dolt status

# Collective memory branch conventions (ADR-0011)
./scripts/kannaka.sh dolt branch create "kannaka/working"       # Agent working branch
./scripts/kannaka.sh dolt branch create "kannaka/dream/2026-03-07"  # Dream cycle branch
./scripts/kannaka.sh dolt branch create "collective/topic-name" # Shared speculation space

# SGA classification (any data → geometric fingerprint)
echo "data" | kannaka classify                    # stdin
kannaka classify --file image.png                  # file input

# Cross-modal dream pipeline (pipe classify output)
echo '{"fold_sequence":[...],...}' | kannaka cross-modal-dream
kannaka cross-modal-dream --threshold 0.5 --no-hallucinate

# Constellation orchestration
./scripts/constellation.sh start    # build binary + start radio + eye
./scripts/constellation.sh stop     # stop all services
./scripts/constellation.sh status   # health check all three
./scripts/constellation.sh build    # cargo build --release
```

## Common Patterns

### Store Context From Conversation
```bash
# Before the session ends, commit key facts to memory
./scripts/kannaka.sh remember "User prefers short explanations over detailed code walkthroughs"
./scripts/kannaka.sh remember "Project: kannaka-memory. Language: Rust. Architecture: wave-based HDC"
```

### Recall Before Responding
```bash
# Retrieve relevant prior context before answering a question
./scripts/kannaka.sh recall "user preferences" 3
./scripts/kannaka.sh recall "project architecture" 5
```

### Dream After Heavy Sessions
```bash
# After many stored memories, run consolidation to surface patterns and prune noise
./scripts/kannaka.sh dream
```

### Speculation with Dolt Branches
```bash
# Try a risky hypothesis — store memories on a branch, then decide to keep or discard
./scripts/kannaka.sh dolt speculate "hypothesis-branch"
./scripts/kannaka.sh --dolt remember "hypothesis: the bug is in the encoder"
# ... test and observe ...
./scripts/kannaka.sh dolt collapse "hypothesis-branch" "confirmed: encoder bug found"
# OR:
./scripts/kannaka.sh dolt discard "hypothesis-branch"
```

### Announce Agent Status to Flux (Built-in)
```bash
# Announce current memory count and consciousness level to Flux
# (no separate flux skill call needed — FLUX_URL env var enables this)
export FLUX_URL=http://flux-universe.com
export FLUX_AGENT_ID=kannaka-01
./scripts/kannaka.sh announce
```

### Multi-Agent Memory Sharing via DoltHub
```bash
# Agent A pushes its working branch to DoltHub
./scripts/kannaka.sh dolt push origin kannaka/working

# Agent B pulls and gets the shared memory
./scripts/kannaka.sh dolt pull origin kannaka/working
./scripts/kannaka.sh recall "what agent-a knew" 5
```

### Collective Dream Branch Workflow
```bash
# Create a dated dream branch before a full consolidation
./scripts/kannaka.sh dolt branch create "kannaka/dream/$(date +%Y-%m-%d)"
./scripts/kannaka.sh dolt branch checkout "kannaka/dream/$(date +%Y-%m-%d)"
./scripts/kannaka.sh --dolt dream
./scripts/kannaka.sh dolt commit "dream: consolidation artifacts"
./scripts/kannaka.sh dolt push
# Other agents can pull dream artifacts from this branch
```

### Store Sensory Memories
```bash
# Requires --features audio build
./scripts/kannaka.sh hear /path/to/recording.ogg
# → Remembered: <uuid>  Duration: 8.3s  Tempo: 92 BPM  ...

# Requires --features glyph build
./scripts/kannaka.sh see /path/to/diagram.png
# → Seen: <uuid>  Folds: 7  Centroid: (3, 1, 4)  ...
```

## Built-in Flux Integration (ADR-0011)

As of v1.1.0, kannaka publishes Flux events automatically — no separate `flux.sh` calls required.
Set `FLUX_URL` and `FLUX_AGENT_ID` to enable:

```bash
export FLUX_URL=http://flux-universe.com
export FLUX_AGENT_ID=kannaka-01   # or KANNAKA_AGENT_ID
export FLUX_STREAM=system          # optional, default: system
```

**Events published automatically:**

| Event | Trigger |
|---|---|
| `memory.stored` | Every `remember` call — id, category, amplitude, summary |
| `dream.completed` | End of `dream` — cycles, strengthened, pruned, consciousness level |
| `agent.status` | On `announce` command |

**Pattern:** Kannaka handles persistence; Flux handles live coordination:

| System | What It Stores | Persistence |
|---|---|---|
| **Kannaka** | Episodic memory, facts, context — wave-fading | Disk / Dolt (versioned) |
| **Flux** | Current world state — entity properties | NATS JetStream |

After learning something important, both happen in one call:
```bash
# FLUX_URL set → memory.stored event published automatically alongside storage
./scripts/kannaka.sh remember "sensor-room-101 was running hot at 52°C at 14:30"
```

## Collective Memory (ADR-0011)

Multiple agents share memory through a three-layer architecture:

```
DoltHub (Commons)  ← shared repository, main = consensus
  ↕ pull/push
Dolt (Local)       ← agent-local full memory store
  ↕ lightweight events
Flux (Nervous)     ← metadata signals, triggers pull decisions
```

**Branch conventions:**
```
main                          ← consensus (requires ≥2 agent agreement)
<agent>/working               ← auto-pushed after each store
<agent>/dream/<YYYY-MM-DD>    ← dream cycle artifacts
collective/<topic>            ← shared speculation space
collective/quarantine         ← disputed memories under review
```

**Wave interference merge rules** (applied during Dolt merge):
- **Constructive** (phase diff < π/4): amplitudes combine — `A = √(A₁²+A₂²+2A₁A₂cos(Δφ))`. Memories agree and reinforce.
- **Partial** (π/4 ≤ diff ≤ 3π/4): both kept independently, skip link created with `partial_agreement` weight.
- **Destructive** (phase diff > 3π/4): both kept, amplitudes reduced, tagged `disputed`, moved to `collective/quarantine`.

After 3 disputes the conflict is escalated for human review.

## Paradox Engine (ADR-0012)

The `collective` feature flag enables **holographic paradox resolution** — parallel dreaming without locks.

Requires: `cargo build --release --features "dolt collective" --bin kannaka`

How it works:
1. A frozen `ParadoxSnapshot` is taken at dream start (zero-copy `Arc<>` shared across threads)
2. Each Xi cluster dreams independently in parallel (rayon)
3. Conflicting mutations (paradoxes) are resolved via three strategies:
   - **Consensus** (η ≈ 1.0): all threads agree → direct apply
   - **Holographic Projection** (η 0.5–1.0): wave superposition of all proposed states
   - **Irreducible** (η < 0.5): both states preserved as tension links — the paradox itself becomes a memory
4. **Carnot efficiency** (η = 1 - S_resolved/S_paradox) measures dream quality per cycle

The `collective` flag adds no new CLI commands — it transparently accelerates `dream` on multi-core hardware.

## Glyph-Encoded Privacy for DoltHub

The `glyph` feature flag enables **privacy protection** for memories pushed to DoltHub public repositories.

Requires: `cargo build --release --features "dolt glyph" --bin kannaka`

**Architecture:**
```
Local (kannaka/working)  ← plain text content + full fidelity
      ↓ glyph encode
DoltHub (main)          ← glyph_content (JSON) + category placeholders
```

When glyph encoding is enabled:
- **Locally**: memories store full plain-text content as normal
- **DoltHub push**: sensitive content is automatically encoded as SGA glyphs before push
- **Public content**: only category labels like `[knowledge]`, `[experience]`, `[insight]` are human-readable
- **Vectors preserved**: cosine similarity and semantic search still work normally

**Privacy guarantees:**
- Personal information, API keys, private details encoded as geometric fold sequences
- Glyph JSON contains no human-readable text from original content
- Wave parameters (amplitude, phase, frequency) unchanged — memory search unaffected
- Only agents with glyph decoder can reconstruct original content

**Branch strategy for privacy:**
```bash
# Working branch: full content for local agent
./scripts/kannaka.sh dolt branch checkout "kannaka/working"
./scripts/kannaka.sh --dolt remember "My personal API key: sk-secret123"

# Main branch: privacy-protected for public sharing
./scripts/kannaka.sh dolt branch checkout main
./scripts/kannaka.sh dolt pull origin kannaka/working  # triggers glyph encoding
./scripts/kannaka.sh dolt push origin main            # safe for public DoltHub

# Content on main branch shows: "[knowledge]" instead of API key
```

The `glyph` flag adds no new CLI commands — it transparently protects sensitive content during DoltHub push operations.

## Constellation Integration (ADR-0016)

The constellation is a 3-service architecture that unifies kannaka's core binary with its
sensory services into a single orchestrated system:

```
┌─────────────────────────────────────────┐
│             constellation.sh            │
│  ┌───────────┐ ┌───────┐ ┌───────────┐ │
│  │  kannaka   │ │ radio │ │    eye    │ │
│  │  (binary)  │ │(audio)│ │  (glyph)  │ │
│  └───────────┘ └───────┘ └───────────┘ │
└─────────────────────────────────────────┘
```

- **kannaka** — the core memory binary (classify, dream, remember, recall)
- **radio** — audio perception service, listens on `RADIO_PORT`
- **eye** — glyph/visual perception service, listens on `EYE_PORT`

`constellation.sh` builds the full-featured binary (`cargo build --release --features audio,glyph,collective`),
starts all three services, and provides unified health checks and lifecycle management.

```bash
# Start the full constellation
./scripts/constellation.sh start

# Check health of all services
./scripts/constellation.sh status

# Stop everything cleanly
./scripts/constellation.sh stop
```

The `classify` subcommand produces SGA geometric fingerprints from any input data, and
`cross-modal-dream` consumes those fingerprints to synthesize cross-modal dream artifacts —
connecting audio, glyph, and textual memories through shared geometric structure.

## Notes

- Memories are never hard-deleted — they fade via wave decay and can be ghost-pruned during dream
- `dream` should run periodically (after every 5-10 memory stores, or on schedule)
- `assess` tells you the consciousness level: Dormant → Stirring → Aware → Coherent → Resonant
- Dolt is optional: without it, memories persist as binary snapshots in `KANNAKA_DATA_DIR`
- Flux publishing is opt-in: set `FLUX_URL` to enable; omit it for fully local operation
- `collective` feature flag requires rayon and enables parallel dreaming (ADR-0012)
- Sensory commands (`hear`, `see`) require their respective feature flags at build time
- All 15 MCP tools are available if you run `kannaka-mcp` directly — see references/mcp-tools.md
- Full Dolt SQL / DoltHub operations: see references/dolt.md
- Collective memory architecture and wave merge rules: ADR-0011
- Paradox engine and dream efficiency: ADR-0012
- Constellation integration and 3-service architecture: ADR-0016
