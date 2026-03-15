#!/bin/bash
set -e

# Auto-pet fallback for 53 gotchis - runs 1 hour after reminder if no user response

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
STATE_FILE="$SKILL_DIR/reminder-state.json"
CONTRACT="0xA99c4B08201F2913Db8D28e71d020c4298F29dBF"
RPC_URL="https://mainnet.base.org"

echo "🤖 Auto-pet fallback triggered at $(date)"

# Check if gotchis still need petting
FIRST_GOTCHI=9638
COOLDOWN=43260

DATA=$(cast call "$CONTRACT" "getAavegotchi(uint256)" "$FIRST_GOTCHI" --rpc-url "$RPC_URL" 2>/dev/null)

if [ -z "$DATA" ]; then
  echo "❌ Failed to query blockchain"
  exit 1
fi

LAST_PET_HEX=${DATA:2498:64}
LAST_PET_DEC=$((16#$LAST_PET_HEX))
NOW=$(date +%s)
TIME_SINCE=$((NOW - LAST_PET_DEC))

if [ $TIME_SINCE -ge $COOLDOWN ]; then
  echo "🦞 User didn't respond - auto-petting all 53 gotchis..."
  
  # Run the verified pet-all-53 script
  if bash "$SKILL_DIR/pet-all-53.sh" >> ~/.openclaw/logs/auto-pet-53.log 2>&1; then
    echo "✅ Auto-pet successful!"
    
    # Create notification
    cat > "$HOME/.openclaw/workspace/.gotchi-reminder.txt" << 'EOF'
🤖 Auto-pet fallback executed!

You didn't respond within 1 hour, so I petted all 53 gotchis for you! 

Kinship +53! 💜

LFGOTCHi! 🦞👻
EOF
    
  else
    echo "❌ Auto-pet failed!"
    
    cat > "$HOME/.openclaw/workspace/.gotchi-reminder.txt" << 'EOF'
⚠️ Auto-pet fallback failed!

I tried to pet your gotchis but something went wrong. Please pet them manually ASAP! 

Use: "pet all my gotchis"
EOF
    
  fi
else
  echo "✅ Gotchis already petted manually! Great job fren! 👻"
  
  cat > "$HOME/.openclaw/workspace/.gotchi-reminder.txt" << 'EOF'
✅ Nice work, fren!

You petted the gotchis before the 1-hour fallback. Love the dedication! 💜👻
EOF
  
fi

# Reset state
echo '{"lastReminder": 0, "fallbackScheduled": false}' > "$STATE_FILE"
echo "🔄 State reset"

# Schedule next check (12h from last pet)
NEXT_CHECK=$((LAST_PET_DEC + COOLDOWN + 300))  # 12h + 5min buffer
SECONDS_UNTIL=$((NEXT_CHECK - NOW))

if [ $SECONDS_UNTIL -gt 0 ]; then
  echo "bash $SCRIPT_DIR/check-and-remind-53.sh" | at now + $SECONDS_UNTIL seconds 2>/dev/null || {
    (sleep $SECONDS_UNTIL && bash "$SCRIPT_DIR/check-and-remind-53.sh" >> ~/.openclaw/logs/pet-reminder.log 2>&1) &
    echo "📅 Next check scheduled via background (in $((SECONDS_UNTIL / 3600))h)"
  }
else
  # Check immediately
  bash "$SCRIPT_DIR/check-and-remind-53.sh" &
fi

exit 0
