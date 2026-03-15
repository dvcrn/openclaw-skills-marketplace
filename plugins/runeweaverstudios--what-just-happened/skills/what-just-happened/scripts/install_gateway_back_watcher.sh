#!/usr/bin/env bash
# Install the what-just-happened gateway-back watcher as a LaunchAgent.
# When the gateway comes back online, the watcher triggers an agent turn and
# the user sees the summary in TUI or Telegram.
# Expands OPENCLAW_HOME and script path; installs to ~/Library/LaunchAgents.

set -e
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WATCHER_SCRIPT="$SCRIPT_DIR/gateway_back_watcher.py"
PLIST_SRC="$SCRIPT_DIR/com.openclaw.what-just-happened.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.openclaw.what-just-happened.plist"

if [[ ! -f "$WATCHER_SCRIPT" ]]; then
  echo "Error: gateway_back_watcher.py not found at $WATCHER_SCRIPT"
  exit 1
fi
if [[ ! -f "$PLIST_SRC" ]]; then
  echo "Error: plist not found at $PLIST_SRC"
  exit 1
fi

OPENCLAW_BIN="${OPENCLAW_BIN:-$(which openclaw 2>/dev/null || echo '/opt/homebrew/bin/openclaw')}"
PATH_FOR_PLIST="${PATH:-/usr/bin:/bin:/usr/sbin:/sbin}:/usr/local/bin:/opt/homebrew/bin"
mkdir -p "$OPENCLAW_HOME/logs"
sed -e "s|OPENCLAW_HOME|$OPENCLAW_HOME|g" \
    -e "s|OPENCLAW_WATCHER_SCRIPT|$WATCHER_SCRIPT|g" \
    -e "s|OPENCLAW_BIN|$OPENCLAW_BIN|g" \
    -e "s|PATH_PLACEHOLDER|$PATH_FOR_PLIST|g" \
    "$PLIST_SRC" > "$PLIST_DEST"
echo "Installed $PLIST_DEST (openclaw: $OPENCLAW_BIN)"
launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load "$PLIST_DEST"
echo "Loaded. Gateway-back watcher runs every 15s. When the gateway goes from down to up, you'll get a what-just-happened summary in TUI or Telegram."
echo "To stop: launchctl unload $PLIST_DEST"
echo "Logs: $OPENCLAW_HOME/logs/what-just-happened.out.log and .err.log"
echo "Verify: launchctl list com.openclaw.what-just-happened"
echo ""
echo "Tip: For one combined daemon (gateway-back + continue-on-error), use gateway-guard instead: bash \$OPENCLAW_HOME/workspace/skills/gateway-guard/scripts/install_watcher.sh"
