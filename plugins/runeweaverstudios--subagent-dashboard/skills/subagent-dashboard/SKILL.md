---
name: subagent-dashboard
description: "Web dashboard for real-time monitoring and management of OpenClaw subagents. Use when monitoring or managing subagents."
---

# Subagent Dashboard Skill

Web dashboard for real-time monitoring and management of OpenClaw subagents.


## Installation

```bash
cd workspace/skills/subagent-dashboard/scripts
./start_dashboard.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
python3 dashboard.py
```


## Usage

Start the dashboard and open http://localhost:8080 in your browser.

The dashboard shows:
- **All sessions** from sessions.json: main (orchestrator), subagents, and optionally cron jobs
- Real-time updates (auto-refresh every 3 seconds)
- Agent details: model, age, tokens, task progress; role badges (Main / Subagent / Cron)
- Transcript viewing for each agent
- Stalled agent detection (>30 min inactive)


## Purpose

Provides a web UI to:
- Monitor active subagents in real-time
- View agent transcripts and activity
- Detect and manage stalled agents
- Track task progress and token usage


## Dependencies

- Flask (web server)
- flask-cors (CORS support)
- Subagent-tracker skill (for data)


## Configuration

Set `PORT` environment variable to change the server port (default: 8080).


## Integration

The dashboard uses the subagent-tracker skill to fetch data. It reads:
- `~/.openclaw/agents/main/sessions/sessions.json` - Session list
- `~/.openclaw/agents/main/sessions/*.jsonl` - Transcript files
- `~/.openclaw/agents/main/subagents/runs.json` - Task mapping (and legacy `~/.openclaw/subagents/runs.json`)

**Completed column:** For finished tasks to appear in the Completed column, the run in `runs.json` must have `endedAt` (timestamp) and `outcome.status` set to `"ok"`, `"completed"`, or `"success"` when the sub-agent finishes. The dashboard appends "recently completed" runs (within 24h) even if the session was removed from sessions.json.
