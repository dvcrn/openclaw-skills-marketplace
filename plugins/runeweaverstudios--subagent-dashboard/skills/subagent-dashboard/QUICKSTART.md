# Quick Start Guide

## Start the Dashboard

```bash
cd workspace/skills/subagent-dashboard/scripts
./start_dashboard.sh
```

Then open **http://localhost:8080** in your browser.

## What You'll See

- **Agent Cards** - One card per active subagent showing:
  - Model name (e.g., "google/gemini-2.5-flash")
  - Age (how long it's been running)
  - Token usage (input/output)
  - Task progress (if available, e.g., "Task 2/5")
  - Task description

- **Status Indicators**:
  - 🟢 Green = Active
  - 🟠 Orange = Stalled (>30 min inactive)

- **Actions**:
  - **📋 Transcript** - View recent activity
  - **🔄 Refresh** - Update status
  - **⚡ Restart** - Restart stalled agents

## Auto-Refresh

The dashboard refreshes every 3 seconds automatically. Click "Pause" to stop, "Resume" to restart.

## Troubleshooting

**Port already in use?**
```bash
PORT=9000 python3 dashboard.py
```

**Dependencies missing?**
```bash
pip install Flask flask-cors
```

**No agents showing?**
- Check that subagents are actually running
- Verify `~/.openclaw/agents/main/sessions/sessions.json` exists
- Ensure subagent-tracker skill is installed
