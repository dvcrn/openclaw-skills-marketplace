#!/bin/bash
# Send pet reminder and schedule auto-pet fallback (1 hour later)

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="$SKILL_DIR/reminder-state.json"
REMINDER_FILE="$HOME/.openclaw/workspace/.gotchi-reminder.txt"

echo "[$(date)] Sending pet reminder"

# Send reminder
cat > "$REMINDER_FILE" << 'EOF'
fren, pet your gotchi(s)! 👻💜
EOF

# Mark reminder sent
jq '.reminderSent = true | .fallbackScheduled = true' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"

# Schedule auto-pet in 1 hour
echo "bash $SKILL_DIR/scripts/auto-pet-simple.sh" | at now + 1 hour 2>/dev/null || {
  (sleep 3600 && bash "$SKILL_DIR/scripts/auto-pet-simple.sh") &
}

echo "[$(date)] ✅ Reminder sent + auto-pet scheduled in 1 hour"
