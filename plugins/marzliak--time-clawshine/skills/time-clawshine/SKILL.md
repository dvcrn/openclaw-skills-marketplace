---
name: time-clawshine
description: "Use this skill when the user asks to 'backup OpenClaw', 'restore a snapshot', 'roll back memory', 'check backup status', 'view backup history', 'undo agent changes', or 'set up time machine backup'."
---

# ⏱🦞 Time Clawshine

Hourly incremental backup for this OpenClaw instance — restic-powered, YAML-configured. Silent on success, Telegram notification on failure.

## Overview

Time Clawshine protects OpenClaw's runtime context (memory, sessions, credentials, config) with hourly snapshots. It runs automatically via cron. You can also trigger it manually or restore any point in the last 72 hours.

**Repository:** Configured in `{baseDir}/config.yaml` (default: `/var/backups/time-clawshine`)
**Log:** `/var/log/time-clawshine.log`
**Password file:** `/etc/time-clawshine.pass`

---

## When the user asks to set up or install Time Clawshine

1. Check if already set up:
   ```bash
   source {baseDir}/lib.sh && tc_load_config && restic_cmd snapshots 2>/dev/null && echo "Already initialized"
   ```
2. If not initialized, ask the user to fill in `{baseDir}/config.yaml` with their Telegram `bot_token` and `chat_id`, then run:
   ```bash
   sudo bash {baseDir}/bin/setup.sh
   ```
3. Confirm setup succeeded by tailing the log:
   ```bash
   tail -5 /var/log/time-clawshine.log
   ```

---

## When the user asks to run a manual backup

```bash
sudo bash {baseDir}/bin/backup.sh
```

Then confirm with:
```bash
tail -5 /var/log/time-clawshine.log
```

---

## When the user asks to check backup status or history

Show the last 10 log lines:
```bash
tail -20 /var/log/time-clawshine.log
```

List all snapshots (most recent first):
```bash
source {baseDir}/lib.sh && tc_load_config && restic_cmd snapshots
```

Show what changed between the two most recent snapshots:
```bash
source {baseDir}/lib.sh && tc_load_config
SNAPS=$(restic_cmd snapshots --json | jq -r '.[-2:][].id')
restic_cmd diff $SNAPS
```

---

## When the user asks to restore or roll back

**Interactive restore (recommended — always dry-runs first):**
```bash
sudo bash {baseDir}/bin/restore.sh
```

**Restore a specific file from the latest snapshot:**
```bash
sudo bash {baseDir}/bin/restore.sh latest --file /root/.openclaw/workspace/MEMORY.md --target /tmp/tc-restore
# Preview the result, then move manually:
# cp /tmp/tc-restore/root/.openclaw/workspace/MEMORY.md /root/.openclaw/workspace/MEMORY.md
```

**Restore a specific snapshot by ID:**
```bash
sudo bash {baseDir}/bin/restore.sh <snapshot_id>
```

Always confirm with the user before executing a full restore to `/`.

---

## When the user asks to check repo integrity

```bash
source {baseDir}/lib.sh && tc_load_config && restic_cmd check
```

---

## When the user asks to change configuration

Edit `{baseDir}/config.yaml` with the requested changes (schedule, retention, paths, Telegram credentials), then re-run setup to apply:
```bash
sudo bash {baseDir}/bin/setup.sh
```

---

## Important notes

- **Silent by design:** cron runs every hour at :05 and logs to `/var/log/time-clawshine.log`. No output unless there is a failure.
- **Telegram fires only on failure.** If the user has not configured `bot_token` and `chat_id`, failures are logged only.
- **This is the time machine layer.** It protects against "the agent broke something in the last 3 days." It is NOT a disaster recovery backup — that should be handled by an off-VM backup (e.g. restic to a remote server).
- **Password:** The restic repository is AES-256 encrypted. The password is at `/etc/time-clawshine.pass` (chmod 600). Losing it means losing access to all snapshots.
- **Never commit `secrets.env` or `.pass` files to git.** They are excluded via `.gitignore`.

---

## When the user asks to customize backup paths (whitelist/blacklist)

Run the AI-assisted customization helper:
```bash
sudo bash {baseDir}/bin/customize.sh
```

This will:
1. Scan the user's workspace
2. Ask the agent to suggest extra paths to include (whitelist) and patterns to exclude (blacklist)
3. Show all suggestions to the user for review
4. Apply to `config.yaml` only after explicit confirmation

Remind the user: the original `config.yaml` is saved as `config.yaml.bak` before any changes.

If the user wants to add paths manually instead:
- Edit `backup.extra_paths` in `{baseDir}/config.yaml` for extra inclusions
- Edit `backup.extra_excludes` in `{baseDir}/config.yaml` for extra exclusions
- Then re-run: `sudo bash {baseDir}/bin/setup.sh`
