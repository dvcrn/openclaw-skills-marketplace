---
name: agent-conductor
description: "Orchestrate coding sub-agents (Claude Code, Codex, Cursor, Gemini Code, or any CLI-based coding agent) for maximum throughput on implementation tasks. Use when: (1) writing or modifying code files, (2) running scripts or data pipelines, (3) batch processing large datasets, (4) multi-stage workflows requiring parallel execution. Covers agent-agnostic dispatch templates, task decomposition, parallel coordination, and acceptance criteria. NOT for: simple file reads, config-only changes, or sending messages. Core principle — the orchestrator plans; the coding agents execute."
---

# Agent Conductor 🎼

**You conduct. Agents perform.**

Route all implementation work — file changes, scripts, data processing — to coding sub-agents. The orchestrating session stays lean: it plans, decides, and validates. Agents do the execution.

## Supported Agents

Agent-agnostic. Set your invoke command once:

| Agent | Invoke Command |
|-------|---------------|
| Claude Code | `claude '<task>'` |
| OpenAI Codex | `codex '<task>'` |
| Cursor Agent | `cursor-agent '<task>'` |
| Gemini Code | `gemini-code '<task>'` |
| Any other | `your-agent-cmd '<task>'` |

Use `AGENT_CMD` as a placeholder in the examples below.

## When to Dispatch

Dispatch when the task involves **any** of:
- Writing or modifying files (even one line)
- Running scripts or processing data
- Execution time > 10 seconds
- Batch operations over multiple items

*If it produces file changes → dispatch it.*

## Dispatch Template

```
## Task: [name]

### Requirement
[One sentence: what to produce and where]

### Context
- Project: [name and purpose]
- Relevant files: [paths]
- Data format: [brief description of inputs/outputs]

### Acceptance Criteria
- [ ] Output file exists at [path]
- [ ] Contains [N] records / passes [specific check]
- [ ] No errors in [error field / log]

### Gotchas
- [Known pitfall 1]
- [Known pitfall 2]

### Environment
- Language/runtime: [python3 / node / go / etc.]
- Working directory: [path]
- Special config: [proxy, auth, env vars if needed]

When done, notify with:
[your completion notification command]
```

## Execution Mechanism

| Duration | Mechanism |
|----------|-----------|
| < 5 min | Foreground: `exec pty:true command:"AGENT_CMD '...'"` |
| 5–30 min | Background: `exec pty:true background:true timeout:1800 command:"AGENT_CMD '...'"` |
| > 30 min | Agent writes script → run in `screen` / `tmux` |

> Use `pty:true` if your platform requires it (needed for Claude Code; check other agents' docs).

## Task Decomposition

Split large projects by **stage**, not by feature. Each stage must be independently verifiable.

**Split when any of these apply:**
- Runtime > 30 minutes
- More than one script needed
- Batch > 100 items
- Output of one step feeds the next

```
Stage 1: Prepare data  →  clean_data.csv        (< 2 min)
Stage 2: Process       →  results.json           (needs Stage 1)
Stage 3: Report        →  report.md              (needs Stage 2)
```

See [references/patterns.md](references/patterns.md) for parallel coordination, checkpoint/resume, and domain examples.

## Acceptance Checklist

After any "done" signal, always verify:

1. **File exists** — confirm output path
2. **Count correct** — expected N vs. actual N records  
3. **Non-empty** — spot-check 2–3 outputs
4. **No silent errors** — check error fields and null rates

*A completion signal ≠ acceptance. Run the checklist.*

## Error Handling

| Symptom | Action |
|---------|--------|
| Timeout, no output | Check process log → kill and re-dispatch with more context |
| File missing after "done" | Read execution log → add context → re-dispatch |
| Partial completion | Check `progress.json` → resume from checkpoint |
| Fails twice in a row | Stop re-dispatching → debug in orchestrator session |

## What NOT to Dispatch

- Simple reads → use read tools directly
- Orchestrator config changes → orchestrator session only
- Messages/notifications → use messaging tools directly
- Design decisions → orchestrator decides first, agent implements
