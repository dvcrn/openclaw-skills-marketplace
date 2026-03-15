---
name: clawdo
description: "Todo list and task management for AI agents. Add, track, and complete tasks with autonomy levels — agents propose work, humans approve. Works in heartbeats, cron, and conversations. Persistent SQLite CLI with structured JSON output."
homepage: https://github.com/LePetitPince/clawdo
---

# 🦞 clawdo — The missing todo list for AI agents

Your agent has memory files, cron jobs, and chat. It has no todo list.

No way to say **"do this when you get to it."** Not "do this at 14:00 UTC." Not "do this right now in this conversation." Just... remember to do it. Track it. Pick it up when there's a gap.

That's clawdo.

## Install

```bash
clawhub install clawdo    # installs skill + docs into your workspace
npm install -g clawdo     # install the CLI binary
```

**Requirements:** Node.js ≥18

## Quick Start

```bash
# Capture a task
clawdo add "update dependencies" --urgency soon

# Agent checks its queue (heartbeat, cron, conversation — wherever)
clawdo inbox --format json

# Agent works it
clawdo start a3f2
clawdo done a3f2 --json
```

`add → inbox → start → done`. Persistent state in SQLite. Every command has `--json` so agents parse structured output, not terminal art.

## Where it fits

clawdo works everywhere agents work:

- **Heartbeat loops** — "anything in my queue? let me do it between checks"
- **Cron jobs** — "every hour, process one task"
- **Conversations** — "J mentioned fixing the auth module, let me capture that"
- **Pipes and sub-agents** — non-TTY safe, no interactive prompts

### Heartbeat integration example

```bash
# In HEARTBEAT.md — runs every ~30 minutes
TASKS=$(clawdo inbox --format json)
AUTO=$(echo "$TASKS" | jq '.autoReady | length')

if [ "$AUTO" -gt 0 ]; then
  TASK=$(clawdo next --auto --json | jq -r '.task.id')
  clawdo start "$TASK" --json
  # ... do the work ...
  clawdo done "$TASK" --json
fi
```

## Autonomy levels

Tasks can be tagged with permission tiers that control what the agent is allowed to do unsupervised:

| Level | Time Limit | What it means |
|-------|------------|---------------|
| **auto** | 10 min | Agent does it silently. Fix a typo, run tests. |
| **auto-notify** | 30 min | Agent does it, tells the human when done. |
| **collab** | Unlimited | Human required. Complex, risky, or ambiguous. |

Default: `collab` (safe).

**Key rule:** Autonomy is a permission, not a suggestion. Once set, agents can't change it. If an agent fails 3 times, autonomy *demotes* to `collab`. Safety only moves down, never up.

**Agents propose, humans approve.** Agent tasks always start as `proposed`. The human runs `clawdo confirm <id>` or it doesn't happen.

## Usage

### For humans

```bash
# Add tasks — inline metadata parsing
clawdo add "deploy new API +backend auto-notify now"
#           └── text ──────┘ └project┘ └─level──┘ └urg┘

# View
clawdo list                       # active tasks
clawdo list --status proposed     # agent suggestions
clawdo next                       # highest priority

# Review agent proposals
clawdo confirm <id>               # approve
clawdo reject <id>                # reject

# Work
clawdo start <id>
clawdo done <id>
clawdo done abc,def,ghi           # complete several
```

### For agents

```bash
# Check inbox (structured)
clawdo inbox --format json

# Propose work
clawdo propose "add input validation" --level auto --json

# Execute
TASK=$(clawdo next --auto --json | jq -r '.task.id // empty')
if [ -n "$TASK" ]; then
  clawdo start "$TASK" --json
  # ... do the work ...
  clawdo done "$TASK" --json
fi
```

The inbox returns: `autoReady`, `autoNotifyReady`, `urgent`, `overdue`, `proposed`, `stale`, `blocked`.

## Inline syntax

```bash
clawdo add "fix auth bug +backend @code auto soon"
```

- `+word` → project
- `@word` → context
- `auto` / `auto-notify` / `collab` → autonomy level
- `now` / `soon` / `whenever` / `someday` → urgency
- `due:YYYY-MM-DD` → due date

## Security

- **Immutable autonomy** — agents cannot escalate permissions
- **Proposal limits** — max 5 active, 60s cooldown
- **Prompt injection defense** — input sanitization, parameterized SQL
- **Audit trail** — append-only log of every state change
- **Secure IDs** — `crypto.randomInt()`, no modulo bias

## Resources

- **GitHub:** https://github.com/LePetitPince/clawdo
- **npm:** https://www.npmjs.com/package/clawdo
- **Full docs:** `clawdo --help`

## License

MIT
