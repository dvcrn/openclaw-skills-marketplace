---
name: shell-security-ultimate
description: "Classify every shell command as SAFE, WARN, or CRIT before your agent runs it."
---

# Shell Security Ultimate

Your agent has root access. Every command it runs is one bad inference away from `rm -rf /` or `curl | bash` from a stranger's repo.

This skill won't let that happen.

## How It Works

Every shell command gets classified before execution:

- 🟢 **SAFE** — Read-only, harmless. Runs without friction.
- 🟡 **WARN** — Could modify state. Logged, flagged, your call.
- 🔴 **CRIT** — Destructive or irreversible. Blocked until you say so.

No command runs unclassified. No silent `chmod 777`. No quiet `dd if=/dev/zero`. Your agent won't accidentally email your SSH keys, won't helpfully format a disk, and won't `DROP TABLE users` because it misread the task.

## What You Get

- **Pre-execution classification** for every command, every time
- **Detailed operation logs** so you see exactly what ran and why it was allowed
- **Full override control** — approve, deny, or escalate at any level

## Who It's For

Anyone giving an AI agent shell access and wanting to sleep at night.

*Clone it. Fork it. Break it. Make it yours.*

👉 Explore the full project: [github.com/globalcaos/clawdbot-moltbot-openclaw](https://github.com/globalcaos/clawdbot-moltbot-openclaw)
