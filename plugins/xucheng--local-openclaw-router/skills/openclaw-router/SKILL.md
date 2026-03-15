---
name: openclaw-router
description: "Install, update, or repair the OpenClaw Router plugin from its public GitHub repo into ~/.openclaw, then verify routing, CLI commands, and stats."
---

# OpenClaw Router

Use this skill when the user wants to install, update, repair, or verify the `openclaw-router` plugin on a local OpenClaw setup.

Published ClawHub slug: `local-openclaw-router`

## What this skill does

- Clones or updates the public `openclaw-router` repository
- Syncs the plugin into `~/.openclaw/extensions/openclaw-router`
- Runs the plugin test suite
- Refreshes runtime state
- Restarts the local OpenClaw gateway
- Verifies health, `openclaw router` CLI availability, and stats output

## Default workflow

When using this skill, perform these steps directly:

1. Clone or update `https://github.com/xucheng/openclaw-router.git` into `~/.openclaw/local-plugins/openclaw-router`
2. Remove legacy `~/.openclaw/extensions/openclaw-main-router` if present
3. Sync the repo into `~/.openclaw/extensions/openclaw-router`
4. Ensure `~/.openclaw/openclaw.json` contains:
   - `plugins.allow` including `openclaw-router`
   - `plugins.entries.openclaw-router.enabled = true`
   - `plugins.installs.openclaw-router` pointing at the local plugin and extension paths
   - no stale `openclaw-main-router` install or entry records
5. Run `node --test` inside the repo
6. Refresh runtime state with `lib/runtime-state.js`
7. Restart the local OpenClaw gateway
8. Verify `/health`, `openclaw router show medium`, and `~/.openclaw/scripts/openclaw-router-stats.sh`

## What to verify after install

Run these checks:

```bash
curl -sS http://127.0.0.1:43111/health
openclaw router show medium
~/.openclaw/scripts/openclaw-router-stats.sh
```

Expected outcomes:

- `/health` returns provider `openclaw-router`
- `openclaw router show medium` prints the current MEDIUM tier chain
- the stats script runs without errors

## Notes

- This skill installs the plugin from GitHub; it does not publish code.
- Prefer running the install/update steps inline instead of relying on an embedded helper script.
- If the gateway briefly reports a `1006` close code after restart, retry once after a short delay.
- If the host still has legacy `openclaw-main-router` directories, migrate them to `openclaw-router`.
