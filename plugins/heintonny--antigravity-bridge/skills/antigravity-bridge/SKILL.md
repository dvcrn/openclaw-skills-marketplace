---
name: antigravity-bridge
description: "One-directional knowledge bridge from Google Antigravity IDE to OpenClaw. Keeps the OpenClaw agent informed about project development without replacing Antigravity as the primary coding agent. Antigravity has deep codebase awareness (IDE, LSP, vectors, code tracker, annotations) — OpenClaw has breadth (24/7 availability, cross-project awareness, business ops, monitoring, communications). The bridge syncs: Knowledge Items, tasks (.agent/tasks.md), lessons learned (.agent/memory/), rules, skills, workflows, and session handoffs. Use when: (1) syncing Antigravity knowledge to OpenClaw context, (2) analyzing tasks for next-task recommendations, (3) running cross-agent self-improve (updates both systems), (4) checking what Antigravity sessions produced, (5) user says \"sync antigravity\", \"pick task\", \"what did antigravity do\", \"bridge sync\", or \"antigravity status\". NOT for: primary coding (use Antigravity), model/provider config, or starting the IDE (use `agy` CLI)."
homepage: https://github.com/heintonny/antigravity-bridge
---

# Antigravity Bridge

Bidirectional knowledge bridge between OpenClaw and Google Antigravity IDE.
Both agents share the same knowledge, tasks, and learnings — no manual sync needed.

## Prerequisites

- Google Antigravity IDE installed (with `~/.gemini/antigravity/` directory)
- A project with `.agent/` directory (Antigravity's standard agent config)
- Python 3.10+ (for sync scripts)

## Configuration

Before first use, create a config file:

```bash
python3 "$(dirname "$0")/scripts/configure.py"
```

Or create `~/.openclaw/antigravity-bridge.json` manually:

```json
{
  "knowledge_dir": "~/.gemini/antigravity/knowledge",
  "project_dir": "~/path/to/your/project",
  "agent_dir": "~/path/to/your/project/.agent",
  "gemini_md": "~/path/to/your/project/.gemini/GEMINI.md",
  "auto_commit": false
}
```

## Sync Command — The Core Workflow

### Running the sync

```bash
python3 scripts/sync_knowledge.py
```

This outputs **structured JSON to stdout** with two sections:
- `diff` — what changed since last sync (or "first sync" if no previous state)
- `current` — full snapshot of current Antigravity state

State is tracked in `~/.openclaw/workspace/antigravity-sync-state.json`.

### Agent responsibilities after sync

**The agent (not the script) is responsible for updating OpenClaw memory.**

After running the sync script, the agent MUST:

1. **Read the JSON output**, focusing on the `diff` section
2. **If `diff.is_first_sync` is true or `diff.summary` shows changes:**
   - Update `MEMORY.md` with significant changes:
     - Task count changes (done/todo deltas)
     - New or removed KI topics
     - New active tasks or phase changes
     - New lessons learned (from memory files)
   - Append a sync log entry to `memory/YYYY-MM-DD.md`:
     ```
     HH:MM — Antigravity Bridge sync: <diff.summary>
     ```
3. **If `diff.summary` is "No changes since last sync":**
   - No updates needed. Optionally log the sync attempt.

### What goes where

| Change type | Target | What to write |
|---|---|---|
| Task count deltas | `MEMORY.md` → CodePact section | Update done/todo counts |
| New active `[>]` tasks | `MEMORY.md` → Current Phase | Replace active task info |
| New KI topics | `MEMORY.md` → CodePact section | Note new topic names |
| New memory/lessons files | `MEMORY.md` → relevant section | Summarize key lessons |
| New rules/skills/workflows | `MEMORY.md` → CodePact section | Update inventory counts |
| Session handoff changes | `MEMORY.md` → CodePact section | Note current handoff context |
| Any sync event | `memory/YYYY-MM-DD.md` | Timestamped log entry |

### What NOT to do

- Do NOT create standalone reference docs (no ANTIGRAVITY.md, no antigravity-sync.md)
- Do NOT dump raw sync data into files — distill into MEMORY.md
- Do NOT ask the user whether to update MEMORY.md — just do it

## Other Commands

### Diff Tasks (`diff`)

Show what changed in tasks since last sync:

```bash
python3 scripts/diff_tasks.py
```

### Next Task (`pick-task`) — mirrors Antigravity's /next-task

Gather project context for intelligent task selection:

```bash
python3 scripts/pick_task.py
```

This outputs **structured JSON context** (does NOT modify tasks.md). The agent uses this to reason.

**Agent workflow after running pick-task:**

1. Read the JSON output (tasks, git log, sessions, memory)
2. Analyze:
   - Active `[>]` tasks that need finishing
   - Session handoffs (continuation prompts from Antigravity)
   - Recent commits (what was just worked on)
   - Phase dependencies (what's unblocked)
3. Recommend **2-3 tasks** to the user with:
   - Context: why this task now
   - Scope: what's involved
   - Effort: Small / Medium / Large
4. Present as numbered options:
   ```
   🎯 Recommended Next Tasks — Reply 1, 2, or 3

   ### Option 1: [Task Name] ⭐
   - Context: ...
   - Scope: ...
   - Effort: Medium

   ### Option 2: [Task Name]
   ...
   ```
5. User picks → agent marks task `[>]` in tasks.md
6. Agent spawns coding sub-agent with task brief (rules + relevant memory + KIs)
7. After completion: mark `[x]`, run self-improve

**Priority criteria (in order):**
1. Active but incomplete (`[>]` tasks)
2. Unblocking (enables other work)
3. Quick wins (low effort, high value)
4. Technical debt (flagged in audits/lessons)
5. Natural progression (next step in current phase)

**The script gathers data. The agent thinks. The user decides.**

### Self-Improve (`self-improve`)

Update BOTH knowledge systems with session learnings:

```bash
python3 scripts/self_improve.py --topic "<topic>" --lesson "<what was learned>"
```

What it does:
1. **OpenClaw side:** Updates `MEMORY.md` and `memory/YYYY-MM-DD.md`
2. **Antigravity side:**
   - Creates/updates `.agent/memory/lessons-learned-<topic>.md`
   - Creates/updates KI artifacts in `knowledge/<topic>/artifacts/`
   - Updates `metadata.json` and `timestamps.json`
3. Optionally commits changes

### Write Knowledge Item (`write-ki`)

Write directly to Antigravity's native Knowledge Item system:

```bash
python3 scripts/write_ki.py \
  --topic "my_topic" \
  --title "My Topic" \
  --summary "What this knowledge covers" \
  --artifact "pattern_name" \
  --content "# Pattern\n\nDetailed content here..."
```

### Create Antigravity Skill (`create-agy-skill`)

Generate the reverse-direction Antigravity skill:

```bash
python3 scripts/create_agy_skill.py --project-dir ~/path/to/project
```

## Architecture

```
┌─────────────────────┐       ┌─────────────────────┐
│    Antigravity       │       │    OpenClaw          │
│    (Gemini)          │       │    (Any LLM)         │
│                      │       │                      │
│  knowledge/       ◄──┼───────┼──► MEMORY.md         │
│  .agent/tasks.md  ◄──┼───────┼──► MEMORY.md (tasks) │
│  .agent/memory/   ◄──┼───────┼──► MEMORY.md (lessons)│
│  .agent/sessions/ ◄──┼───────┼──► MEMORY.md (handoff)│
│  .agent/rules/    ───┼───────┼──► MEMORY.md (counts) │
│  .agent/skills/   ───┼───────┼──► MEMORY.md (counts) │
│  .agent/workflows/───┼───────┼──► MEMORY.md (counts) │
└─────────────────────┘       └─────────────────────┘
         │                              │
         └──── state.json ◄─────────────┘
              (diff tracking)
```

## State File

`~/.openclaw/workspace/antigravity-sync-state.json` tracks:
- Last sync timestamp
- KI topic hashes and artifact counts
- Task file hash and counts
- Memory/rules/skills/workflows file hashes

This enables precise change detection without markdown diffing.

## Security & Privacy

- **All data stays local.** No external API calls. No cloud sync.
- Scripts only read/write files within configured directories.
- No credentials or tokens are required.
- The skill never modifies code — only knowledge/task/memory files.

## External Endpoints

None. This skill operates entirely on local files.

## Trust Statement

This skill reads and writes files within your Antigravity knowledge directory
(`~/.gemini/antigravity/`) and your project's `.agent/` directory. It does not
send any data to external services. Only install if you trust the skill to
modify these directories.
