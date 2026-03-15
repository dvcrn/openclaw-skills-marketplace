#!/bin/bash
# Pet gotchis safely - only includes verified working IDs
# Uses Bankr CLI for secure transaction signing

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SKILL_DIR/config.json"
CONTRACT=$(jq -r '.contract' "$CONFIG_FILE")

# Verified working gotchis from our tests
BANKR_GOTCHIS=(9638 10052 23688 14455 24869)
HW_WORKING=(22931 23329 20601 4673 23899 549 1249 2595 6041)

echo "👻 Pet Me Master - Safe Batch Mode"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Verified gotchis:"
echo "  • Bankr wallet: ${#BANKR_GOTCHIS[@]} gotchis"
echo "  • Hardware wallet: ${#HW_WORKING[@]} gotchis (verified working via operator)"
echo "  • Total: $((${#BANKR_GOTCHIS[@]} + ${#HW_WORKING[@]})) gotchis"
echo ""

# Combine verified gotchis
ALL_GOTCHIS=("${BANKR_GOTCHIS[@]}" "${HW_WORKING[@]}")

# Convert to comma-separated list
GOTCHI_LIST=$(IFS=,; echo "${ALL_GOTCHIS[*]}")

# Build calldata  
CALLDATA=$(cast calldata "interact(uint256[])" "[$GOTCHI_LIST]")

echo "🦞 Petting ${#ALL_GOTCHIS[@]} verified gotchis..."
echo "📋 IDs: ${ALL_GOTCHIS[@]}"
echo ""

# Submit via Bankr CLI
bankr submit tx \
  --to "$CONTRACT" \
  --chain-id 8453 \
  --value 0 \
  --data "$CALLDATA" \
  --description "Pet ${#ALL_GOTCHIS[@]} verified gotchis"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Batch petting complete!"
echo ""
echo "📊 Summary:"
echo "  • Petted: ${#ALL_GOTCHIS[@]} gotchis"
echo "  • Bankr wallet: ${#BANKR_GOTCHIS[@]}"
echo "  • Hardware wallet (OG squad): ${#HW_WORKING[@]}"
echo "  • Next pet: 12 hours from now"
echo ""
echo "💜 Kinship +${#ALL_GOTCHIS[@]}! LFGOTCHi! 🦞"
