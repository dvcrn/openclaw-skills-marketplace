#!/bin/bash
# Hook to run AFTER petting - resets state and schedules next reminder

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="$SKILL_DIR/reminder-state.json"
REMINDER_FILE="$HOME/.openclaw/workspace/.gotchi-reminder.txt"

echo "[$(date)] Post-pet hook: resetting state and scheduling next reminder"

# Reset state
echo '{"reminderSent": false, "fallbackScheduled": false}' > "$STATE_FILE"

# Clear any pending reminder
rm -f "$REMINDER_FILE"

# Schedule next reminder check (12h 5m from now based on blockchain timestamp)
bash "$SKILL_DIR/scripts/schedule-next-check.sh" &

echo "[$(date)] ✅ Ready for next cycle"
