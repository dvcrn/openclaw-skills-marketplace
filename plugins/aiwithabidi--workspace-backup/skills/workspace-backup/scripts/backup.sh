#!/usr/bin/env bash
# Workspace Backup — git add, commit, push with auto-generated message
# Designed to run unattended (cron-friendly, no TTY needed)
set -euo pipefail

WORKSPACE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}"
BRANCH="${BACKUP_BRANCH:-main}"
REMOTE="${BACKUP_REMOTE:-origin}"

cd "$WORKSPACE"

# Ensure git repo exists
if [ ! -d .git ]; then
  echo "ERROR: $WORKSPACE is not a git repository. Run 'git init' first."
  exit 1
fi

# Ensure remote is configured
if ! git remote get-url "$REMOTE" &>/dev/null; then
  echo "ERROR: Remote '$REMOTE' not configured. Run 'git remote add $REMOTE <url>' first."
  exit 1
fi

# Auto-create .gitignore if missing
GITIGNORE="$WORKSPACE/.gitignore"
if [ ! -f "$GITIGNORE" ]; then
  cat > "$GITIGNORE" << 'EOF'
# OpenClaw workspace defaults
.venv/
.data/
.env
.env.*
node_modules/
__pycache__/
*.pyc
*.pyo
.DS_Store
Thumbs.db
*.log
*.tmp
*.swp
*~
EOF
  echo "Created .gitignore with workspace defaults"
fi

# Stage all changes
git add -A

# Check if there's anything to commit
if git diff --cached --quiet; then
  echo "$(date -Iseconds) — No changes to backup"
  exit 0
fi

# Build commit message with timestamp and changed files summary
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S %Z')
CHANGED_FILES=$(git diff --cached --stat --no-color | tail -1)
FILE_LIST=$(git diff --cached --name-only | head -20)
FILE_COUNT=$(git diff --cached --name-only | wc -l)

MSG="backup: $TIMESTAMP

$CHANGED_FILES

Changed files:"

if [ "$FILE_COUNT" -le 20 ]; then
  MSG="$MSG
$FILE_LIST"
else
  MSG="$MSG
$FILE_LIST
... and $((FILE_COUNT - 20)) more"
fi

# Commit
git commit -m "$MSG" --no-verify

# Push
if git push "$REMOTE" "$BRANCH" 2>&1; then
  echo "$(date -Iseconds) — Backup pushed successfully ($CHANGED_FILES)"
else
  echo "$(date -Iseconds) — Push failed. Commit saved locally."
  exit 1
fi
