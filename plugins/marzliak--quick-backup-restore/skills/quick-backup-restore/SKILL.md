---
name: quick-backup-restore
description: "Use this skill when the user asks to 'backup OpenClaw', 'restore a snapshot', 'roll back memory', 'check backup status', 'view backup history', 'undo agent changes', or 'set up time machine backup'."
---

# ⏱🦞 Quick Backup and Restore (time machine)

Your OpenClaw agent builds memory, preferences, and context over time — and agents make mistakes. They overwrite things. They corrupt their own context. When that happens, you want to go back to *exactly* 2 hours ago, not yesterday's backup, not a full system restore.

This skill gives your agent hourly snapshots of its own brain. Restic-powered, encrypted, silent on success — and it pings you on Telegram only when something breaks.

## Overview

Quick Backup and Restore protects OpenClaw's runtime context (memory, sessions, credentials, config) with hourly snapshots. It runs automatically via cron. You can also trigger it manually or restore any point in the last 72 hours.

**Repository:** `{baseDir}/../../../var/backups/quick-backup-restore` (or as configured in `{baseDir}/config.yaml`)
**Log:** `/var/log/quick-backup-restore.log`
**Password file:** `/etc/quick-backup-restore.pass`

---

## When the user asks to set up or install Quick Backup and Restore (time machine)

1. Check if already set up:
   ```bash
   restic -r /var/backups/quick-backup-restore --password-file /etc/quick-backup-restore.pass snapshots 2>/dev/null && echo "Already initialized"
   ```
2. If not initialized, ask the user to fill in `{baseDir}/config.yaml` with their Telegram `bot_token` and `chat_id`, then run:
   ```bash
   sudo bash {baseDir}/bin/setup.sh
   ```
3. Confirm setup succeeded by tailing the log:
   ```bash
   tail -5 /var/log/quick-backup-restore.log
   ```

---

## When the user asks to run a manual backup

```bash
sudo bash {baseDir}/bin/backup.sh
```

Then confirm with:
```bash
tail -5 /var/log/quick-backup-restore.log
```

---

## When the user asks to check backup status or history

Show the last 10 log lines:
```bash
tail -20 /var/log/quick-backup-restore.log
```

List all snapshots (most recent first):
```bash
restic -r /var/backups/quick-backup-restore --password-file /etc/quick-backup-restore.pass snapshots
```

Show what changed between the two most recent snapshots:
```bash
SNAPS=$(restic -r /var/backups/quick-backup-restore --password-file /etc/quick-backup-restore.pass snapshots --json | jq -r '.[-2:][].id')
restic -r /var/backups/quick-backup-restore --password-file /etc/quick-backup-restore.pass diff $SNAPS
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
restic -r /var/backups/quick-backup-restore --password-file /etc/quick-backup-restore.pass check
```

---

## When the user asks to change configuration

Edit `{baseDir}/config.yaml` with the requested changes (schedule, retention, paths, Telegram credentials), then re-run setup to apply:
```bash
sudo bash {baseDir}/bin/setup.sh
```

---

## Important notes

- **Silent by design:** cron runs every hour at :05 and logs to `/var/log/quick-backup-restore.log`. No output unless there is a failure.
- **Telegram fires only on failure.** If the user has not configured `bot_token` and `chat_id`, failures are logged only.
- **This is the time machine layer.** It protects against "the agent broke something in the last 3 days." It is NOT a disaster recovery backup — that should be handled by an off-VM backup (e.g. restic to a remote server).
- **Password:** The restic repository is AES-256 encrypted. The password is at `/etc/quick-backup-restore.pass` (chmod 600). Losing it means losing access to all snapshots.
- **Never commit `secrets.env` or `.pass` files to git.** They are excluded via `.gitignore`.
