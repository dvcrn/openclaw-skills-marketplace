#!/bin/bash
# Pet ALL 53 gotchis - verified working list from March 2, 2026
# Uses Bankr CLI for secure transaction signing

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONTRACT="0xA99c4B08201F2913Db8D28e71d020c4298F29dBF"

# Exact 53 gotchis from successful March 2 transaction (TX: 0x316aea...)
# 5 Bankr wallet + 48 Hardware wallet (via pet operator)
ALL_53=(9638 10052 23688 14455 24869 22931 23329 20601 4673 23899 23313 18013 6955 6956 8068 24823 8453 8543 17395 10018 22819 23918 19247 10051 10060 10388 11430 12031 23930 14028 14555 16309 24923 16659 22470 549 8254 10046 6953 6952 12214 24965 10043 23666 6041 24566 1249 23936 24067 24850 10028 16633 2595)

echo "👻 Pet Me Master - Full Squad Mode"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Petting ${#ALL_53[@]} gotchis..."
echo "  • Bankr wallet: 5 gotchis"
echo "  • Hardware wallet: 48 gotchis (via pet operator)"
echo ""

# Build calldata
GOTCHI_LIST=$(IFS=,; echo "${ALL_53[*]}")
CALLDATA=$(cast calldata "interact(uint256[])" "[$GOTCHI_LIST]")

echo "🦞 Submitting batch transaction..."

# Submit via Bankr CLI
bankr submit tx \
  --to "$CONTRACT" \
  --chain-id 8453 \
  --value 0 \
  --data "$CALLDATA" \
  --description "Pet all 53 gotchis - AAI daily ritual"

EXIT_CODE=$?

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ All gotchis petted!"
  echo ""
  echo "📊 Summary:"
  echo "  • Total petted: ${#ALL_53[@]} gotchis"
  echo "  • Includes 5 OG Haunt 1 gotchis (#549, #1249, #2595, #4673, #6041)"
  echo "  • Next reminder: 12h 5m from now"
  echo ""
  echo "💜 Kinship +${#ALL_53[@]}! LFGOTCHi! 🦞"
  
  # Schedule next reminder
  bash "$SKILL_DIR/scripts/after-pet-hook.sh" &
else
  echo "❌ Petting failed!"
  exit $EXIT_CODE
fi
