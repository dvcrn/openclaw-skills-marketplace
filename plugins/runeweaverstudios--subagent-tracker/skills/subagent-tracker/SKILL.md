---
name: subagent-tracker
description: "Say \"agent status\" and get updates on all subagent progress. Track subagent actions while they run; list active subagents, status, and tail transcripts. Install for power users using the agent swarm."
---

# Subagent Tracker

## Description

Say "agent status" and get updates on all subagent progress. Track subagent actions while they run; list active subagents, status, and tail transcripts. Install for power users using the agent swarm.

# Subagent Tracker

Say **“agent status”** and get an update on **all subagent progress**—who’s running, what they’re doing, and when tasks complete. The TUI doesn’t show a live “sub-agent working…” indicator; subagent-tracker is how you see what your agent swarm is doing.

---


## Installation

**ClawHub:** Update `clawhub install` and ClawHub links when the new ClawHub instance is live.

```bash
npm install -g clawhub
clawhub install subagent-tracker
```

Or clone: `git clone https://github.com/RuneweaverStudios/subagent-tracker.git workspace/skills/subagent-tracker`

---


## Usage

- User says: **"agent status"**, "track subagents", "see what the sub-agent is doing", "show progress", "show subagent progress", "why didn't the agent come back", "sub-agent never responded"
- After delegation: user wants a **progress/loading-style** view — run the tracker and summarize active subagents and recent tool calls
- Debugging: sub-agent was assigned (e.g. "Using: Kimi k2.5") but no result showed in chat — list runs and sessions, tail transcripts, report what the sub-agent is doing or did

| You say | What happens |
|--------|----------------|
| **"agent status"** | Orchestrator runs tracker, reports active subagents (Agent 1, Agent 2, … with Task X/Y and model). |
| "track subagents" / "show subagent progress" | Same: list active subagents and optional status/tail for detail. |
| "what's the sub-agent doing?" | Tracker list + summary; optionally status for a specific session. |
| "why didn't the agent come back?" | Tracker shows what ran or is running; orchestrator can tail transcript and report. |


## Examples

**List subagents active in the last 30 minutes:**
```bash
python3 /Users/ghost/.openclaw/workspace/skills/subagent-tracker/scripts/subagent_tracker.py list --active 30
```

**Status for a session (ID from list or runs.json):**
```bash
python3 /Users/ghost/.openclaw/workspace/skills/subagent-tracker/scripts/subagent_tracker.py status e1e51315-9766-4604-85b4-58b9e96c39ef
```

**Tail last 15 transcript events:**
```bash
python3 /Users/ghost/.openclaw/workspace/skills/subagent-tracker/scripts/subagent_tracker.py tail e1e51315-9766-4604-85b4-58b9e96c39ef --lines 15
```

**Run all tracker checks locally (list + status + tail on first active subagent):**
```bash
/Users/ghost/.openclaw/workspace/skills/subagent-tracker/scripts/test-subagent-tracker.sh
```


## Commands

From any cwd (e.g. TUI exec), use the skill path:

```bash
python3 /Users/ghost/.openclaw/workspace/skills/subagent-tracker/scripts/subagent_tracker.py list [--active MINUTES] [--json] [--summary]
```
 (Use `--summary` for a single "Here are your active subagents" block with Agent 1, Agent 2, … and Task X/Y when available; report it once, do not duplicate.)

```bash
python3 /Users/ghost/.openclaw/workspace/skills/subagent-tracker/scripts/subagent_tracker.py status <session-id|key> [--json]
```

```bash
python3 /Users/ghost/.openclaw/workspace/skills/subagent-tracker/scripts/subagent_tracker.py tail <session-id> [--lines N]
```

**Prevent duplicate subagent tasks (run before sessions_spawn):**
```bash
python3 /Users/ghost/.openclaw/workspace/skills/subagent-tracker/scripts/subagent_tracker.py check-duplicate --task "<task string>" --json
```
If output has `"duplicate": true`, do not call sessions_spawn; reply that the task is already running. The orchestrator rule runs this automatically before spawning.

Session IDs come from `list` or from `subagents/runs.json` (extract from `childSessionKey`, e.g. `agent:main:subagent:UUID` → use UUID).


## Pain point

When you queue multiple tasks (poem, bug fix, research), you have no built-in view of which subagents are active or how far along they are. Without this skill, “agent status” or “what’s the sub-agent doing?” can’t be answered.

---


## Benefits

- **One phrase:** Say **“agent status”**, **“track subagents”**, or **“show subagent progress”** and the orchestrator runs the tracker and reports (Agent 1, Agent 2, … with Task X/Y and model).
- **Full visibility** — List active subagents, view status and tokens, tail transcript events (tool calls, thinking).
- **Works with the swarm** — Map task → session via `subagents/runs.json`; when runs include `taskIndex` and `totalTasks`, the tracker shows “Task X/Y” per agent.
- **Duplicate prevention** — `check-duplicate` runs before `sessions_spawn` so the same task isn’t run twice (saves tokens and lag).

**Encouraged for power users:** If you use Agent Swarm and handle multiple queued tasks, **download subagent-tracker** so you can say “agent status” and stay updated.

---


## Chat visibility and "agents never come back"

**Why results sometimes don't appear:** The orchestrator must **wait** for `sessions_spawn` to return before replying. If it replies with "I'll let you know once it has findings!" and ends the turn, the sub-agent result never gets into the chat. The rule **"Wait for spawn before replying"** in the orchestrator delegate rule addresses this.

**Progress/loading:** The TUI does **not** show a live "Sub-agent working…" indicator. To see progress, the user must ask (e.g. "show subagent progress", "what's the sub-agent doing?", "track subagents"). The orchestrator then runs the tracker and reports. Use `list --active 30 --summary` for a single block (e.g. "Here are your active subagents:" with "Agent 1 (Task 2/5): model (age)" per line). The orchestrator must output this block **once** only—never repeat it. Optionally `list --active 30` then `status <session-id>` / `tail <session-id>` for detail.


## Features

- **List active subagents** – Sessions with status (recent activity, model, tokens)
- **View subagent details** – Tool calls, tokens, transcript line count
- **Tail subagent logs** – Recent transcript events (tool calls, thinking)
- **Map task → session** – `subagents/runs.json` has `task`, `childSessionKey`, `runId`; when entries include `taskIndex` and `totalTasks`, the tracker shows "Task X/Y" (e.g. Task 3/5) per agent.


## Orchestrator behavior

When the user asks to **track** or **see progress** of subagents:
1. Run `subagent_tracker.py list --active 30 --summary` (absolute path above). The output is a single block with "Here are your active subagents:" and one line per agent (Agent 1, Agent 2, … with Task X/Y when in runs.json).
2. Paste that block **once** in your reply; do not repeat it or add a second copy of the list. Optionally run `status <sessionId>` for detail.
3. If you add a line about completed subagents, do it once at the end. Optionally summarize in plain language: e.g. "One sub-agent is running (Kimi k2.5). It’s been active for 2m; last actions: write, exec (npm install)."

When the user says **sub-agents never come back** or **no results in chat**:
1. Acknowledge the issue (orchestrator should wait for `sessions_spawn` before replying; see delegate rule).
2. Run the tracker to show what *is* running or what recently ran: `list`, then `status`/`tail` for recent sessions, and report.


## Integration with heartbeats

In `HEARTBEAT.md` you can add:

```markdown


## Subagent checks

- Check for stalled subagents (>30 min inactive)
- Notify when subagents complete
```


## How it works

The tracker reads OpenClaw's session store (`agents/main/sessions/`) and JSONL transcripts. It does not require extra dependencies (Python standard library).
