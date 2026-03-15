---
name: what-just-happened
description: "When the gateway comes back online, check recent logs and post a short message about what happened (restart, SIGUSR1, auth change, reconnect). User sees the response in TUI or Telegram."
---

# What Just Happened

## Description

When the gateway comes back online, check recent logs and post a short message about what happened (restart, SIGUSR1, auth change, reconnect). User sees the response in TUI or Telegram.

# What Just Happened

Standalone skill with its own **GitHub repo** and **OpenClaw/ClawHub page**. After a gateway restart or reconnect, it summarizes what happened by reading recent gateway logs (and optionally gateway-guard restart logs) and posts a short, user-facing message. **The user should see the response in their TUI or Telegram.**


## Usage

- Gateway just came back online and you want the user to see what happened (use watcher or cron).
- User asks "what happened to the gateway?" or "why did it reconnect?"
- You want a brief summary of recent restarts/errors and a proposed solution (e.g. gateway-guard).


## Commands

```bash
python3 <workspace>/skills/what-just-happened/scripts/report_recent_logs.py [--minutes N] [--json]
```

- **--minutes N** — Look at log lines from the last N minutes (default 5).
- **--json** — Emit a single JSON object with keys like `summary`, `restart`, `reason`, `suggestGatewayGuard`.

Output is a short paragraph suitable for posting. When the cause is auth/config, the script includes a tip with the ClawHub link: `clawhub install gateway-guard` — https://clawhub.ai/skills/gateway-guard. **ClawHub:** Update this link when the new instance is live.


## Two ways to run

1. **Every time the gateway comes back online (recommended)**  
   You **must install** the **gateway-back watcher** or it will never auto-trigger. Run once (from the skill dir):

   ```bash
   cd workspace/skills/what-just-happened
   ./scripts/install_gateway_back_watcher.sh
   ```

   The install script loads a LaunchAgent that runs every 15s. When it sees the gateway go from down → up, it triggers the summary to TUI or Telegram. **Verify it's loaded:** `launchctl list com.openclaw.what-just-happened` (should show a PID). If you see "not loaded", run the install script again.

   To stop: `launchctl unload ~/Library/LaunchAgents/com.openclaw.what-just-happened.plist`

2. **Cron (periodic)**  
   A cron job runs every 2 minutes. When it runs, the agent checks the last 5 minutes of logs and, if a restart happened, announces to the user. Good as a fallback; for immediate feedback on reconnect, use the watcher above.

3. **Manual**  
   User says **"what just happened?"** or "I restarted the gateway" and the orchestrator runs the script and replies in chat.


## How it works

Reads `OPENCLAW_HOME/logs/gateway.log` and optionally `gateway-guard.restart.log`. Looks for recent shutdown/restart/SIGUSR1/reload lines and produces a plain-language summary. Suggests gateway-guard (with ClawHub install link) when the cause was auth or config change.


## Delivery (TUI or Telegram)

- **Gateway-back watcher** and **cron** both trigger an agent turn with **announce** (deliver). The OpenClaw gateway delivers that to the configured channel(s)—typically the last-used channel (TUI webchat) and/or Telegram if configured. The user sees the summary in their TUI or Telegram.
- Manual "what just happened?" is replied to in the current chat (TUI).


## Integration summary

| Trigger | How | User sees response |
|--------|-----|---------------------|
| **Gateway comes back online** | Install `install_gateway_back_watcher.sh` (LaunchAgent every 15s) | TUI or Telegram (announce) |
| **Cron every 2 min** | OpenClaw cron job with announce | TUI or Telegram (announce) |
| **Manual** | User says "what just happened?" | Current chat (TUI) |
