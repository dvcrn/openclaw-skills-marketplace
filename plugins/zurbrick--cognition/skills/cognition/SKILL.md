---
name: cognition
description: "Seven biologically-inspired memory systems for OpenClaw agents. Gives your agent overnight learning (nightly consolidation), metacognition (confidence tracking), prospective memory (future intents), procedural memory (compiled skills), spreading activation (cross-references), knowledge gap detection, and weekly deep reflection. Use when setting up agent memory architecture, implementing long-term memory, adding overnight consolidation, enabling self-improvement, or building cognitive infrastructure. Based on SOAR, ACT-R, Global Workspace Theory, and hippocampal replay research."
---

# 🧠 Cognition — Seven Memory Systems for OpenClaw Agents

Give your agent a mind, not just memory.

## What It Does

Your agent forgets everything between sessions. Cognition fixes that with seven cognitive systems borrowed from neuroscience:

1. **Working Memory** — Context window management with GWT broadcasting
2. **Episodic Memory** — Session replay with importance tagging
3. **Semantic Memory** — Hierarchical knowledge with activation-weighted retrieval
4. **Procedural Memory** — Compiled skills with Bayesian success tracking
5. **Prospective Memory** — Structured future intents (never forget a commitment)
6. **Metamemory** — Confidence scoring and knowledge gap detection
7. **Causal-Temporal Reasoning** — Cross-references and spreading activation

## Quick Start

Run the install script to scaffold the full directory structure:

```bash
bash {baseDir}/scripts/install.sh
```

This creates all template files and directories. Then follow the 4-phase adoption guide below.

## Phase 1: Foundation (10 minutes)

### 1.1 Add FUTURE_INTENTS.md to workspace root

Copy from `{baseDir}/templates/FUTURE_INTENTS.md`. This is your agent's prospective memory — structured commitments with triggers, actions, and status tracking.

### 1.2 Create procedural memory

The install script creates `memory/procedures/` with `index.yaml`. After solving non-trivial problems, compile solutions here. Each procedure tracks preconditions, steps, failure modes, and success rate.

### 1.3 Set up nightly consolidation

Add a cron job using the prompt at `{baseDir}/references/consolidation-prompt.md`. Schedule: `0 2 * * *` (2 AM daily). Uses your agent's model to process the day's logs into durable knowledge.

**Recommended model:** Any model with reliable tool use (Sonnet 4+, GPT-5+). Small local models may narrate instead of executing — test tool reliability first.

### 1.4 Add Memory Protocol to AGENTS.md

Paste the protocol block from `{baseDir}/references/protocols.md` into your AGENTS.md.

## Phase 2: Consolidation Intelligence (10 minutes)

### 2.1 Add KNOWLEDGE_MAP.md

Copy from `{baseDir}/templates/KNOWLEDGE_MAP.md`. Customize domains for your use case. Confidence scores: 🟢 High (0.8+) | 🟡 Medium (0.5-0.8) | 🔴 Low (<0.5).

### 2.2 Enable importance tagging

Add the tagging protocol from `{baseDir}/references/protocols.md` to AGENTS.md. Tag daily log entries:
- `[REPLAY_PRIORITY: HIGH]` — Corrections, policy changes, decisions
- `[REPLAY_PRIORITY: MEDIUM]` — New facts, milestones, config changes
- LOW = default, no tag needed

### 2.3 Enable GWT Broadcasting

Add the broadcasting rules from `{baseDir}/references/protocols.md`. When important info enters a session, push it to the correct store immediately.

## Phase 3: Intelligence (15 minutes)

### 3.1 Create cross-references

Copy `{baseDir}/templates/cross-references.md` to `memory/bank/`. Customize with your person→file, project→resource, and domain→domain links. This enables spreading activation — retrieving one topic primes related topics.

### 3.2 Set up gap tracking

The install script creates `memory/meta/gap_tracker.json`. Failed searches are logged here. Gaps with 3+ misses are surfaced during weekly reflection.

### 3.3 Upgrade weekly reflection

Add a weekly cron using the prompt at `{baseDir}/references/weekly-reflection-prompt.md`. Schedule: `0 4 * * 0` (Sunday 4 AM). Performs 13-step deep cognitive maintenance.

### 3.4 Update Retrieval Protocol

Replace your basic retrieval protocol with the enhanced version from `{baseDir}/references/protocols.md` — adds cross-reference following and gap logging.

## Phase 4: Evolution (ongoing)

Phase 4 is emergent. As the other systems accumulate data:
- Weekly reflection recommends AGENTS.md rule changes
- Procedures compile automatically from solved problems
- Knowledge gaps drive proactive research
- Confidence scores guide when to act vs. when to ask

## Configuration

### Recommended openclaw.json settings

Read `{baseDir}/references/config.md` for copy-paste config blocks:
- `reserveTokensFloor`: 40000 (not the default 20K)
- `memoryFlush`: enabled with 4K-10K soft threshold
- Hybrid search: 0.7 vector / 0.3 BM25
- MMR diversity: lambda 0.7
- Temporal decay: halfLifeDays 30
- Embedding cache: 50K entries

## File Structure

After installation:
```
workspace/
├── FUTURE_INTENTS.md          # Prospective memory
├── KNOWLEDGE_MAP.md           # Metamemory
└── memory/
    ├── bank/
    │   └── cross-references.md  # Spreading activation
    ├── meta/
    │   ├── gap_tracker.json     # Knowledge gap detection
    │   └── retrieval_log.json   # Search quality tracking
    ├── procedures/
    │   └── index.yaml           # Compiled skills registry
    ├── consolidation/
    │   └── YYYY-MM-DD.md        # Nightly consolidation logs
    └── summaries/
        └── YYYY-WNN.md          # Weekly reflection summaries
```

## Cognitive Science Foundation

| Theory | Mechanism | System |
|--------|-----------|--------|
| SOAR | Procedural chunking | Procedural Memory |
| ACT-R | Activation-weighted retrieval | Semantic Memory |
| Global Workspace Theory | Broadcast to all stores | GWT Broadcasting |
| Hippocampal Replay | Overnight consolidation | Nightly Cron |
| Predictive Processing | Importance tagging | Episodic Memory |
| Metacognition | Confidence calibration | Metamemory |
