#!/bin/bash
# Schedule the next reminder check at exactly 12h 5m after last pet

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONTRACT="0xA99c4B08201F2913Db8D28e71d020c4298F29dBF"
RPC_URL="https://mainnet.base.org"
FIRST_GOTCHI=9638

# Get last pet time from blockchain
DATA=$(cast call "$CONTRACT" "getAavegotchi(uint256)" "$FIRST_GOTCHI" --rpc-url "$RPC_URL" 2>/dev/null)

if [ -z "$DATA" ]; then
  echo "[$(date)] Failed to query blockchain"
  exit 1
fi

LAST_PET_HEX=${DATA:2498:64}
LAST_PET=$(( 16#$LAST_PET_HEX ))
REMINDER_TIME=$(( $LAST_PET + 43500 ))  # 12h 5m (43500 seconds)
NOW=$(date +%s)
SECONDS_UNTIL=$(( $REMINDER_TIME - $NOW ))

# If reminder time already passed, send immediately
if [ $SECONDS_UNTIL -le 0 ]; then
  echo "[$(date)] Reminder time passed - sending now"
  bash "$SKILL_DIR/scripts/send-reminder.sh"
  exit 0
fi

# Schedule using 'at' command
REMINDER_DATE=$(date -d "@$REMINDER_TIME" '+%H:%M %Y-%m-%d')

echo "bash $SKILL_DIR/scripts/send-reminder.sh" | at "$REMINDER_DATE" 2>/dev/null && {
  echo "[$(date)] ✅ Next reminder scheduled for $REMINDER_DATE (in $((SECONDS_UNTIL / 3600))h $((SECONDS_UNTIL % 3600 / 60))m)"
  exit 0
}

# Fallback: background sleep if 'at' not available
(sleep $SECONDS_UNTIL && bash "$SKILL_DIR/scripts/send-reminder.sh") &
echo "[$(date)] ✅ Next reminder scheduled via background process (in $((SECONDS_UNTIL / 3600))h $((SECONDS_UNTIL % 3600 / 60))m)"
