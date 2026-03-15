#!/bin/sh
# Warning Bot Cron Wrapper
# Runs every 5 minutes

# Get script directory (works regardless of CWD)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/../data"
LOG_FILE="${DATA_DIR}/warning-bot.log"
ALERT_FILE="${DATA_DIR}/alert-pending.txt"
LOCK_FILE="${DATA_DIR}/warning-bot.lock"
ALERT_SENT_FLAG="${DATA_DIR}/alert-sent.flag"

# Cleanup function
cleanup() {
    rm -rf "$LOCK_FILE"
}
trap 'cleanup' EXIT

# Atomic lock check (using mkdir which is atomic on POSIX)
if ! mkdir "$LOCK_FILE" 2>/dev/null; then
    echo "$(date '+%Y-%m-%d %H:%M'): Already running, skipping" >> "$LOG_FILE"
    exit 0
fi

# Run the bot
OUTPUT=$(python3 "${SCRIPT_DIR}/warning-bot.py" 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -eq 1 ] && [ -n "$OUTPUT" ]; then
    # Alert for your address - save to file for notification
    echo "$OUTPUT" > "$ALERT_FILE"
    echo "$(date '+%Y-%m-%d %H:%M'): ALERT FOUND - saved to $ALERT_FILE" >> "$LOG_FILE"
    
    # Also create a flag that OpenClaw can check
    touch "$ALERT_SENT_FLAG"
else
    echo "$(date '+%Y-%m-%d %H:%M'): No warnings for address" >> "$LOG_FILE"
fi

exit 0
