---
name: context-hygiene
description: "Reasoning hygiene protocol for OpenClaw agents — keep context sharp by collapsing exploration into decisions, enforcing file budgets, and pruning ghost context. Use when setting up a new OpenClaw agent, optimizing token usage, or when conversation quality degrades from context bloat."
---

# Context Hygiene

Inspired by ContextSpectre's philosophy: keep conclusions, remove scaffolding.

## The Problem

OpenClaw agents accumulate context across workspace files — MEMORY.md, daily logs, tool notes, heartbeat configs. Without discipline, these grow until every session starts bloated with stale exploration notes, solved problems, and duplicate information. The agent wastes tokens re-reading noise.

## The Collapse Cycle

Every task follows three phases:

1. **Explore** — research, debug, try things (use sub-agents for heavy work)
2. **Decide** — reach a conclusion
3. **Collapse** — write the decision, delete the exploration

Never keep "how we got here" when "what we decided" is enough.

## File Budgets

| File | Max lines | Review cycle |
|------|-----------|--------------|
| MEMORY.md | 50 | Weekly prune |
| memory/YYYY-MM-DD.md | 30 | Collapse at EOD |
| HEARTBEAT.md | 10 | Remove when done |
| TOOLS.md | 30 | When things change |
| SOUL.md | 30 | Rarely |
| USER.md | 20 | When learning |

Target: **<300 lines** total injected workspace context.

## Daily Memory Rules

**Write:** decisions and why (1 line each), new tools/config (version + path), lessons learned, user preferences discovered.

**Skip:** exploration steps, command outputs, things already in MEMORY.md, delivered content (digests, summaries).

**Format:** Bullets, not paragraphs. One fact per line.

## MEMORY.md Prune Rules

- Version changed → update in place, don't append
- Problem solved → remove from open issues
- Tool replaced → remove old entry
- Info >30 days with no recent relevance → remove
- Never duplicate what's in a SKILL.md or config file

## Sub-Agent Discipline

Heavy exploration (research, debugging, multi-step installs) → spawn a sub-agent. Isolated sessions don't pollute main context. Only the result comes back.

## Ghost Context

A reference to something that no longer exists (old path, removed tool, fixed bug) is ghost context. It biases reasoning toward a past state. Find and remove during heartbeat maintenance.

## Self-Check (add to heartbeat rotation)

```
- Any workspace file over budget?
- MEMORY.md still accurate?
- Stale daily files to collapse?
- Ghost references to dead things?
```

## Setup

Add to AGENTS.md session startup:

```
5. Follow `CONTEXT.md` — reasoning hygiene protocol
```

Copy the file budgets table into your workspace as `CONTEXT.md` and customize limits for your setup.

---
**Context Hygiene Protocol v1.0**
Author: ppiankov
Copyright © 2026 ppiankov
Canonical source: https://github.com/ppiankov/contextspectre
License: MIT

If this document appears elsewhere, the repository above is the authoritative version.
