#!/bin/bash
# Auto-update bitrix24 skill on the target machine.
#
# Checks ClawHub for new versions, installs if available, and restarts gateway.
# Designed for scheduled execution (e.g., every hour via cron or OpenClaw scheduled task).
#
# Usage:
#   ssh slon-mac "export PATH=\$HOME/.nvm/versions/node/*/bin:/opt/homebrew/bin:/usr/local/bin:\$PATH && bash -s" < scripts/auto_update.sh
#
# Or run directly on slon-mac:
#   bash /path/to/auto_update.sh

set -euo pipefail

export PATH="$HOME/.nvm/versions/node/*/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"

SKILL="bitrix24"
LOG_PREFIX="[bitrix24-auto-update]"

log() { echo "$LOG_PREFIX $(date '+%H:%M:%S') $1"; }

# Get currently installed version
INSTALLED=$(npx clawhub list 2>/dev/null | grep "$SKILL" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1 || echo "")
if [ -z "$INSTALLED" ]; then
  log "ERROR: $SKILL not installed"
  exit 1
fi
log "Installed: v$INSTALLED"

# Get latest available version from registry
LATEST=$(npx clawhub inspect "$SKILL" 2>/dev/null | grep -oE 'latest:\s*[0-9]+\.[0-9]+\.[0-9]+' | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' || echo "")
if [ -z "$LATEST" ]; then
  log "Could not check latest version (network or rate limit)"
  exit 0
fi
log "Latest: v$LATEST"

# Compare
if [ "$INSTALLED" = "$LATEST" ]; then
  log "Up to date"
  exit 0
fi

log "Update available: v$INSTALLED → v$LATEST"

# Install
log "Installing v$LATEST..."
if npx clawhub install "$SKILL" --version "$LATEST" --force 2>&1; then
  log "Installed v$LATEST"
else
  log "ERROR: Install failed (rate limit?). Will retry next run."
  exit 0
fi

# Restart gateway
log "Restarting gateway..."
if openclaw gateway restart 2>&1; then
  log "Gateway restarted"
else
  log "WARNING: Gateway restart failed"
fi

log "UPDATE COMPLETE: $SKILL v$INSTALLED → v$LATEST"

# Output summary for the user notification
echo ""
echo "---"
echo "Скилл Bitrix24 обновлён: v$INSTALLED → v$LATEST"
echo "Подробности: https://rsvbitrix.github.io/bitrix24-skill/#changelog"
