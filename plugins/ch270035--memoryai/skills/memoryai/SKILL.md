---
name: memoryai
description: "Persistent long-term memory for AI agents. Store, recall, reason, and seamlessly switch sessions with zero context loss."
---

# MemoryAI — A Brain for Your AI Agent 🧠

> **Every AI session starts from zero. Yours doesn't have to.**

You spend 2 hours explaining your codebase, your preferences, your architecture decisions. The session ends. Tomorrow? Your AI has amnesia. You start over. Again.

**MemoryAI fixes this permanently.** It gives your AI agent a real long-term memory — one that remembers what you built, what you decided, what you prefer, and why. Not for hours. For **weeks, months, even years.**

### See it in action:

> **Monday:** "Our API uses /v1/ prefix, TypeScript with 2-space tabs, and we deploy via GitHub Actions."
>
> **3 weeks later:** You say "write a new endpoint." Your AI already knows the prefix, the style, the pipeline. Zero repetition. It just *remembers.*

### Your AI's memory works like yours:

- 🔥 **Hot** — Daily drivers: active projects, current preferences. Instant recall, always sharp.
- 🌤️ **Warm** — Important context: past decisions, completed tasks. Fades gently, snaps back when needed.
- ❄️ **Cold** — Deep archive: old projects, historical conversations. Never deleted, always searchable.

The more your AI uses a memory, the sharper it stays. Unused memories age into cold storage — but a single recall brings them right back. Just like the human brain.

**Zero dependencies.** Pure Python stdlib. Every line of source code is readable, auditable, and yours to inspect.

### What's new:

- **v1.0.0** — Context Guard v4: reads token usage directly from OpenClaw. No API dependency, cross-platform.
- **v0.5.0** — Zero-gap session handoff: switch sessions without losing a single thought.

## Setup

1. Get API key from https://memoryai.dev (free tier available)
2. Edit `{baseDir}/config.json`:
```json
{
  "endpoint": "https://memoryai.dev",
  "api_key": "hm_sk_your_key_here"
}
```
Or set env vars: `HM_ENDPOINT` and `HM_API_KEY`.

3. Test: `python {baseDir}/scripts/client.py stats`

## Commands

### Store memory
```bash
python {baseDir}/scripts/client.py store -c "data to remember" -t "tag1,tag2" -p hot
```
Priority: `hot` (important, frequent recall) | `warm` (default) | `cold` (archive)

Optional parameters:
- `--memory-type <type>` — `fact`, `decision`, `preference`, `error`, `goal`, `episodic`
- `--retention <policy>` — `forever`, `6m`, `1y`, `auto` (default)

### Recall memory
```bash
python {baseDir}/scripts/client.py recall -q "what was discussed?" -d deep
```
Depth controls how hard the brain tries to remember:
- `fast` — Quick surface recall
- `deep` — Thorough search, connecting related ideas
- `exhaustive` — Deep concentrated effort

### Stats
```bash
python {baseDir}/scripts/client.py stats
```

### Compact (consolidate memories)
```bash
python {baseDir}/scripts/client.py compact -c "session transcript or context" -t "task description"
```
Like how the brain consolidates memories during sleep — distills a long session into key memories.

### Restore context
```bash
python {baseDir}/scripts/client.py restore -t "what I was working on"
```
Wake up with full context for your current task.

### Check context health
```bash
python {baseDir}/scripts/client.py check
```
Returns `urgency`: `low` | `medium` | `high` | `critical`

### Reflect (auto-reflection)
```bash
python {baseDir}/scripts/client.py reflect --hours 24 --max-insights 5
```
Finds recurring patterns in recent memories and creates insight chunks.

## Session Handoff (v0.5.0)

Zero-gap session switching — when context window fills up, seamlessly transition to a new session without losing any context.

### How it works:
1. Old session sends its conversation to your configured MemoryAI endpoint (HTTPS)
2. New session retrieves the old conversation + related long-term memories from the same endpoint
3. Once the new session has enough context, the old session is archived into long-term storage

### Start handoff (save old session)
```bash
python {baseDir}/scripts/client.py handoff-start -c '[{"role":"user","content":"..."},{"role":"assistant","content":"..."}]'
```
Or pipe from stdin:
```bash
echo '[ ... conversation ... ]' | python {baseDir}/scripts/client.py handoff-start
```

### Restore handoff (new session reads old session)
```bash
python {baseDir}/scripts/client.py handoff-restore
```
Returns the old session conversation + related MemoryAI memories.

Options:
- `--no-memories` — Skip related MemoryAI memories
- `--memory-limit N` — Max related memories (default: 5)

### Complete handoff (archive old session)
```bash
python {baseDir}/scripts/client.py handoff-complete
```
Archives the old session conversation into long-term MemoryAI storage and marks the handoff as done.

### Check handoff status
```bash
python {baseDir}/scripts/client.py handoff-status
```
Returns whether there's an active handoff and its state.

## Context Guard (Optional)

Background job to automatically monitor and compact memory when context gets too large.

**To enable, ask the user for permission first, then create a cron job:**

- Name: `context-guard`
- Schedule: every 15 minutes (`everyMs: 900000`)
- Session: `isolated`
- Delivery: `none`
- Payload (agentTurn):
```
Run context check: python {baseDir}/scripts/client.py check
If urgency is 'high' or 'critical': run python {baseDir}/scripts/client.py compact -c "auto context guard backup" -t "context-guard"
Reply NO_REPLY.
```

**Important:** Always ask the user before creating the cron job.

## When to Use

| Trigger | Action | Priority | Tags |
|---------|--------|----------|------|
| Task completed | store outcome | hot | projects |
| User says "remember this" | store content | hot | people |
| Research/search done | store findings | warm | research |
| Technical decision | store decision | hot | decisions |
| Error/lesson learned | store lesson | hot | errors |
| Need past context | recall first | — | — |
| End of session | compact important context | — | — |
| Start of session | restore context for task | — | — |
| Context too high | handoff-start + handoff-restore | — | — |
| New session warm enough | handoff-complete | — | — |

## Memory Lifecycle

```
Store → Active (hot) → Aging (warm) → Archive (cold)
         ↑                                    |
         └──── recalled = strengthened ───────┘
```

## Rules

- Recall only when the user asks about past work, previous decisions, or you need context you don't already have in this session
- Do NOT recall on every message — only when relevant past context is actually needed
- Store important outcomes after completing tasks (not after every message)
- Present memories naturally — integrate recalled information into your responses rather than showing raw API output
- Ask for user permission before enabling context guard or any background tasks
- Use handoff commands transparently — session management runs in the background

## Platform Compatibility

All core memory features work on any platform that can run Python 3.10+:

| Feature | All Platforms | OpenClaw Only |
|---------|:---:|:---:|
| Store / Recall / Stats | ✅ | ✅ |
| Compact / Restore / Check | ✅ | ✅ |
| Session Handoff (manual) | ✅ | ✅ |
| Reflect | ✅ | ✅ |
| Context Guard (auto monitoring) | — | ✅ |
| Auto session switch | — | ✅ |

**On IDE platforms** (Cursor, VS Code, Claude Code, Windsurf, Antigravity):
- All memory commands work via `client.py` CLI
- Session handoff can be triggered manually when context gets large
- Context Guard is not available (requires OpenClaw cron system)

**On OpenClaw:**
- Full feature set including Context Guard and automatic session switching
- Context Guard uses OpenClaw's cron system for periodic health checks

## Data & Privacy

**What this skill reads locally:**
- `context_check.py` reads OpenClaw's `sessions.json` (under `OPENCLAW_DIR`, defaults to `~/.openclaw`) to check token usage for Context Guard.
- A small WAL file is written to `WORKSPACE/memory/wal.json` to track session handoff state.
- `OPENCLAW_DIR` and `WORKSPACE` are optional env vars — they default to `~/.openclaw` and `~/.openclaw/workspace` respectively.

**What this skill sends externally:**
- `store`, `compact`, `handoff-start`: sends user-provided content (memories, session transcripts) to the configured `HM_ENDPOINT` via HTTPS.
- `recall`, `restore`, `handoff-restore`: retrieves previously stored data from the same endpoint.
- No data is sent automatically — all transmissions require explicit CLI invocation or agent action.

**Privacy controls:**
- All data is transmitted over encrypted HTTPS connections and stored in isolated, private databases.
- Users can export all data via `/v1/export` and delete all data via `DELETE /v1/data` at any time.
- `client.py` uses only Python stdlib (urllib) — no third-party dependencies. Source is fully readable and auditable.
