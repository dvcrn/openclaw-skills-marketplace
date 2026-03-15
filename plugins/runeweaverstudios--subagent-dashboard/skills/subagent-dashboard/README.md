# Subagent Dashboard

A real-time web dashboard for monitoring OpenClaw subagents. View active agents, their progress, transcripts, and manage stalled sessions.

## Features

- **Real-time monitoring** - Auto-refreshes every 3 seconds
- **Agent cards** - See model, age, tokens, and task progress
- **Transcript viewing** - View recent activity for each agent
- **Stall detection** - Highlights agents inactive for >30 minutes
- **Refresh controls** - Manual refresh and restart options

## Quick Start

```bash
cd workspace/skills/subagent-dashboard/scripts
./start_dashboard.sh
```

Then open http://localhost:8080 in your browser.

## Manual Start

```bash
cd workspace/skills/subagent-dashboard/scripts
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
python3 dashboard.py
```

## Usage

The dashboard automatically shows all active subagents (active within the last 60 minutes). Each card displays:

- **Agent number** and model
- **Age** - How long the agent has been running
- **Token usage** - Input and output tokens
- **Task progress** - If available (Task X/Y)
- **Task description** - What the agent is working on

### Actions

- **📋 Transcript** - View recent activity/events for the agent
- **🔄 Refresh** - Refresh agent status
- **⚡ Restart** - Restart stalled agents (requires gateway access)

### Auto-refresh

The dashboard auto-refreshes every 3 seconds. Click "Pause" to stop auto-refresh, or "Resume" to restart it.

## API Endpoints

- `GET /api/subagents` - List all active subagents
- `GET /api/subagent/<session_id>/status` - Get detailed status
- `GET /api/subagent/<session_id>/transcript?lines=N` - Get transcript (default 50 lines)
- `POST /api/subagent/<session_id>/refresh` - Request refresh/restart
- `GET /api/stalled` - Get list of stalled agents

## Requirements

- Python 3.7+
- Flask and flask-cors (installed via requirements.txt)
- Access to OpenClaw session files (`~/.openclaw/agents/main/sessions/`)
- Subagent-tracker skill installed

## Subagents not showing?

The dashboard reads from `OPENCLAW_HOME/agents/main/sessions/sessions.json` (default `~/.openclaw`). If you don't see spawned subagents:

1. **Same OpenClaw home** – Start the dashboard with the same `OPENCLAW_HOME` your TUI/gateway use. Example: `OPENCLAW_HOME=/path/to/.openclaw ./scripts/start_dashboard.sh`
2. **Gateway writes sessions** – Subagents appear only after the gateway has registered them in `sessions.json`. If the TUI runs elsewhere (e.g. different machine or sandbox), that gateway may write to a different path; point `OPENCLAW_HOME` at that path when starting the dashboard.

## Port

Default port is 8080 (to avoid macOS AirPlay Receiver conflict on 5000). Set `PORT` environment variable to change:

```bash
PORT=5000 python3 dashboard.py
```
