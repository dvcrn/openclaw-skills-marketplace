#!/bin/bash
# Simple pet reminder system - exactly 3 rules:
# 1. Pet all gotchis (wallet + delegated)
# 2. Reminder at 12h 5m after last pet
# 3. Auto-pet 1h after reminder if no response

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="$SKILL_DIR/reminder-state.json"
REMINDER_FILE="$HOME/.openclaw/workspace/.gotchi-reminder.txt"
CONTRACT="0xA99c4B08201F2913Db8D28e71d020c4298F29dBF"
RPC_URL="https://mainnet.base.org"

# Use first gotchi as reference (they're all petted together)
FIRST_GOTCHI=9638

# Get last pet time from blockchain
DATA=$(cast call "$CONTRACT" "getAavegotchi(uint256)" "$FIRST_GOTCHI" --rpc-url "$RPC_URL" 2>/dev/null)

if [ -z "$DATA" ]; then
  echo "[$(date)] Failed to check blockchain"
  exit 1
fi

LAST_PET_HEX=${DATA:2498:64}
LAST_PET=$(( 16#$LAST_PET_HEX ))
NOW=$(date +%s)
TIME_SINCE=$(( $NOW - $LAST_PET ))
REMINDER_TIME=$(( $LAST_PET + 43500 ))  # 12h 5m

# Load state
if [ ! -f "$STATE_FILE" ]; then
  echo '{"reminderSent": false, "fallbackScheduled": false}' > "$STATE_FILE"
fi

REMINDER_SENT=$(jq -r '.reminderSent' "$STATE_FILE")
FALLBACK_SCHEDULED=$(jq -r '.fallbackScheduled' "$STATE_FILE")

# Rule 2: Send reminder at 12h 5m
if [ $NOW -ge $REMINDER_TIME ] && [ "$REMINDER_SENT" = "false" ]; then
  echo "[$(date)] Sending reminder (12h 5m reached)"
  
  cat > "$REMINDER_FILE" << 'EOF'
fren, pet your gotchi(s)! 👻💜
EOF
  
  # Update state
  jq '.reminderSent = true | .fallbackScheduled = true' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
  
  # Rule 3: Schedule auto-pet in 1 hour
  echo "bash $SKILL_DIR/scripts/auto-pet-simple.sh" | at now + 1 hour 2>/dev/null || {
    (sleep 3600 && bash "$SKILL_DIR/scripts/auto-pet-simple.sh") &
  }
  
  echo "[$(date)] Reminder sent + auto-pet scheduled in 1h"
  
# Reset if gotchis were petted manually
elif [ $TIME_SINCE -lt 43500 ] && [ "$REMINDER_SENT" = "true" ]; then
  echo "[$(date)] Gotchis petted manually - resetting"
  echo '{"reminderSent": false, "fallbackScheduled": false}' > "$STATE_FILE"
  rm -f "$REMINDER_FILE"
fi

exit 0
