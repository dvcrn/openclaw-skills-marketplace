# what-just-happened

**When the gateway comes back online, summarize what happened and deliver the response to the user’s TUI or Telegram.**

**ClawHub:** Update `clawhub install` and ClawHub links in this file when the new ClawHub instance is live.

Standalone OpenClaw skill with its own GitHub repo and [OpenClaw/ClawHub](https://clawhub.ai/skills/what-just-happened) page.

## What it does

After a gateway restart (force-kill, SIGUSR1, config reload, or reconnect), the skill:

1. Reads the last few minutes of `logs/gateway.log` and `logs/gateway-guard.restart.log`.
2. Produces a short plain-language summary (what happened, any errors).
3. Proposes a solution (e.g. [gateway-guard](https://clawhub.ai/skills/gateway-guard) for auth stability).
4. **Delivers that summary to the user in their TUI or Telegram** (announce).

## Trigger every time the gateway comes back online

Auto-trigger **only works if the gateway-back watcher is installed and loaded**. Otherwise nothing runs when the gateway comes back.

1. Install the skill (clone or `clawhub install what-just-happened`).
2. **Run the install script once** so the LaunchAgent is loaded:

   ```bash
   cd workspace/skills/what-just-happened
   ./scripts/install_gateway_back_watcher.sh
   ```

3. **Verify:** `launchctl list com.openclaw.what-just-happened` — you should see a PID. If it says "not loaded", run the install script again. Logs: `OPENCLAW_HOME/logs/what-just-happened.out.log` and `.err.log`.

   To stop: `launchctl unload ~/Library/LaunchAgents/com.openclaw.what-just-happened.plist`

You can also use the **cron job** (every 2 min) as a fallback, or ask **"what just happened?"** in chat for an immediate summary.

## Manual run

```bash
python3 workspace/skills/what-just-happened/scripts/report_recent_logs.py --minutes 5
```

Optional: `--json` for machine-readable output.

## Requirements

- OpenClaw with `openclaw.json` and `gateway.auth` (token or password).
- `openclaw` CLI on PATH (for the watcher’s `openclaw gateway health` and `openclaw agent --deliver`).

## Links

- **ClawHub:** https://clawhub.ai/skills/what-just-happened  
- **Gateway-guard (recommended follow-up):** https://clawhub.ai/skills/gateway-guard  
