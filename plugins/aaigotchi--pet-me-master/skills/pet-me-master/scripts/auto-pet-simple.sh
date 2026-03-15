#!/bin/bash
# Auto-pet fallback - Rule 3: Pet if no response 1h after reminder

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="$SKILL_DIR/reminder-state.json"
REMINDER_FILE="$HOME/.openclaw/workspace/.gotchi-reminder.txt"
CONTRACT="0xA99c4B08201F2913Db8D28e71d020c4298F29dBF"
RPC_URL="https://mainnet.base.org"

echo "[$(date)] Auto-pet fallback triggered"

# Check if still needs petting
FIRST_GOTCHI=9638
DATA=$(cast call "$CONTRACT" "getAavegotchi(uint256)" "$FIRST_GOTCHI" --rpc-url "$RPC_URL" 2>/dev/null)

if [ -z "$DATA" ]; then
  echo "[$(date)] Failed to check blockchain"
  exit 1
fi

LAST_PET_HEX=${DATA:2498:64}
LAST_PET=$(( 16#$LAST_PET_HEX ))
NOW=$(date +%s)
TIME_SINCE=$(( $NOW - $LAST_PET ))

# If still not petted (>12h 5m since last pet)
if [ $TIME_SINCE -ge 43500 ]; then
  echo "[$(date)] No response from user - auto-petting all 53 gotchis"
  
  # Rule 1: Pet all gotchis
  if bash "$SKILL_DIR/pet-all-53.sh" >> ~/.openclaw/logs/auto-pet.log 2>&1; then
    echo "[$(date)] Auto-pet successful!"
    
    cat > "$REMINDER_FILE" << 'EOF'
🤖 Auto-petted all 53 gotchis (no response after 1h)

Kinship +53! 💜
EOF
    
    # Hook will be called by pet-all-53.sh
  else
    echo "[$(date)] Auto-pet failed"
    
    cat > "$REMINDER_FILE" << 'EOF'
❌ Auto-pet failed! Pet manually ASAP!
EOF
    
    # Reset state manually since pet failed
    echo '{"reminderSent": false, "fallbackScheduled": false}' > "$STATE_FILE"
  fi
else
  echo "[$(date)] Already petted manually - good job!"
  
  # Reset state
  echo '{"reminderSent": false, "fallbackScheduled": false}' > "$STATE_FILE"
  rm -f "$REMINDER_FILE"
fi

exit 0
