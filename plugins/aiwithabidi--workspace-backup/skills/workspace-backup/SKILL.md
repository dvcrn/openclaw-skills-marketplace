---
name: workspace-backup
description: "Automated workspace backup to GitHub — git-based with auto-generated commit messages, proper .gitignore, and restore procedures. Cron-friendly for hands-free backup. Use for backing up your OpenClaw workspace, skills, memory, and configuration."
homepage: https://www.agxntsix.ai
---

# 💾 Workspace Backup

Automated git-based backup of your OpenClaw workspace to GitHub. Designed to run as a cron job or on-demand.

## Features

- One-command backup with auto-generated commit messages
- Smart `.gitignore` for OpenClaw workspaces
- Timestamp + changed files summary in commits
- Restore from any point in history
- Cron-friendly (no TTY required)

## Setup

### 1. Initialize the backup repo

```bash
cd ~/.openclaw/workspace
git init
git remote add origin git@github.com:YOUR_USER/YOUR_REPO.git
```

### 2. Ensure SSH keys are configured

The script uses SSH for push. Make sure your deploy key or SSH key is available.

### 3. Run the backup

```bash
bash {baseDir}/scripts/backup.sh
```

### 4. Schedule as cron job

In OpenClaw, create a cron job:

```json
{
  "name": "workspace-backup",
  "schedule": "0 */6 * * *",
  "command": "bash /home/node/.openclaw/workspace/skills/workspace-backup/{baseDir}/scripts/backup.sh",
  "description": "Backup workspace to GitHub every 6 hours"
}
```

Or via system crontab:
```
0 */6 * * * cd /home/node/.openclaw/workspace && bash skills/workspace-backup/{baseDir}/scripts/backup.sh >> /tmp/backup.log 2>&1
```

## Restore Procedures

### Restore entire workspace to latest backup
```bash
cd ~/.openclaw/workspace
git fetch origin
git reset --hard origin/main
```

### Restore a specific file from history
```bash
git log --oneline -- path/to/file          # find the commit
git checkout <commit-hash> -- path/to/file  # restore it
```

### Restore to a specific point in time
```bash
git log --oneline --before="2026-02-01"    # find commit near that date
git checkout <commit-hash>                  # detached HEAD at that point
# Copy what you need, then: git checkout main
```

### View what changed between backups
```bash
git log --oneline -10
git diff <older-hash> <newer-hash> --stat
```

## .gitignore

The backup script auto-creates a `.gitignore` if missing, excluding:

- `.venv/` — Python virtual environments
- `.data/` — Local databases and data files
- `.env` — Secret environment variables
- `node_modules/` — Node.js dependencies
- `__pycache__/` — Python bytecode
- `*.pyc` — Compiled Python files
- `.DS_Store` — macOS metadata

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/backup.sh` | Main backup script — add, commit, push |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
