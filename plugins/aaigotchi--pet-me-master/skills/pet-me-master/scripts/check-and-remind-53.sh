#!/bin/bash
set -e

# Check if gotchis are ready and send reminder + schedule auto-pet fallback
# Updated for 53-gotchi squad

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
STATE_FILE="$SKILL_DIR/reminder-state.json"
REMINDER_FILE="$HOME/.openclaw/workspace/.gotchi-reminder.txt"
CONTRACT="0xA99c4B08201F2913Db8D28e71d020c4298F29dBF"
RPC_URL="https://mainnet.base.org"

# Check first gotchi as representative (they were all petted together)
FIRST_GOTCHI=9638
COOLDOWN=43260  # 12h 1min

echo "[$(date)] Checking gotchi #$FIRST_GOTCHI cooldown..."

# Get last pet time
DATA=$(cast call "$CONTRACT" "getAavegotchi(uint256)" "$FIRST_GOTCHI" --rpc-url "$RPC_URL" 2>/dev/null)

if [ -z "$DATA" ]; then
  echo "[$(date)] ❌ Failed to query blockchain"
  exit 1
fi

# Extract timestamp
LAST_PET_HEX=${DATA:2498:64}
LAST_PET_DEC=$((16#$LAST_PET_HEX))
NOW=$(date +%s)
TIME_SINCE=$((NOW - LAST_PET_DEC))
READY_IN=$((COOLDOWN - TIME_SINCE))

# Load state
if [ -f "$STATE_FILE" ]; then
  LAST_REMINDER=$(jq -r '.lastReminder // 0' "$STATE_FILE" 2>/dev/null || echo "0")
  FALLBACK_SCHEDULED=$(jq -r '.fallbackScheduled // false' "$STATE_FILE" 2>/dev/null || echo "false")
else
  LAST_REMINDER=0
  FALLBACK_SCHEDULED=false
  echo '{"lastReminder": 0, "fallbackScheduled": false}' > "$STATE_FILE"
fi

# If ready and no recent reminder
if [ $TIME_SINCE -ge $COOLDOWN ]; then
  TIME_SINCE_REMINDER=$((NOW - LAST_REMINDER))
  
  if [ $TIME_SINCE_REMINDER -gt 43200 ] && [ "$FALLBACK_SCHEDULED" = false ]; then
    echo "[$(date)] ✅ All 53 gotchis ready! Sending reminder..."
    
    # Create reminder message
    cat > "$REMINDER_FILE" << 'EOF'
👻 Gotchi time, fren!

All 53 gotchis are ready for petting! 🦞

Reply with "pet all my gotchis" or I'll auto-pet them in 1 hour if you're busy! 

LFGOTCHi! 💜
EOF
    
    # Update state
    jq '.lastReminder = '$(date +%s)' | .fallbackScheduled = true' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
    
    # Schedule auto-pet fallback in 1 hour
    echo "bash $SKILL_DIR/scripts/auto-pet-53.sh" | at now + 1 hour 2>/dev/null || {
      (sleep 3600 && bash "$SKILL_DIR/scripts/auto-pet-53.sh" >> ~/.openclaw/logs/auto-pet-53.log 2>&1) &
      echo "[$(date)] ⏰ Fallback scheduled via background process (PID $!)"
    }
    
    echo "[$(date)] ✅ Reminder sent + 1h fallback scheduled"
  else
    echo "[$(date)] ⏭️  Reminder already sent or fallback pending"
  fi
else
  echo "[$(date)] ⏰ Not ready yet (wait $((READY_IN / 60))m $((READY_IN % 60))s)"
  
  # Reset fallback if gotchis were petted
  if [ "$FALLBACK_SCHEDULED" = true ]; then
    echo "[$(date)] 🔄 Gotchis were petted, resetting state"
    echo '{"lastReminder": 0, "fallbackScheduled": false}' > "$STATE_FILE"
    rm -f "$REMINDER_FILE"
  fi
fi

exit 0
