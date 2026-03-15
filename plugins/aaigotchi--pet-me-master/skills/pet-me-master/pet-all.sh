#!/bin/bash
# Pet all gotchis owned by Bankr wallet + hardware wallet (via pet operator)
# Uses Bankr CLI for secure transaction signing

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SKILL_DIR/config.json"
CONTRACT=$(jq -r '.contract' "$CONFIG_FILE")
RPC_URL=$(jq -r '.rpcUrl' "$CONFIG_FILE")
CHAIN_ID=$(jq -r '.chain // "base"' "$CONFIG_FILE")

# Extract all gotchi IDs from config
BANKR_GOTCHIS=($(jq -r '.wallets[] | select(.name | contains("Bankr")) | .gotchiIds[]' "$CONFIG_FILE"))
HW_GOTCHIS=($(jq -r '.wallets[] | select(.name | contains("Hardware")) | .gotchiIds[]' "$CONFIG_FILE"))

echo "👻 Pet Me Master - Batch Petting"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Checking gotchis..."
echo "  • Bankr wallet: ${#BANKR_GOTCHIS[@]} gotchis"
echo "  • Hardware wallet: ${#HW_GOTCHIS[@]} gotchis (via pet operator)"
echo "  • Total: $((${#BANKR_GOTCHIS[@]} + ${#HW_GOTCHIS[@]})) gotchis"
echo ""

# Combine all gotchis
ALL_GOTCHIS=("${BANKR_GOTCHIS[@]}" "${HW_GOTCHIS[@]}")

# Convert to comma-separated list for calldata
GOTCHI_LIST=$(IFS=,; echo "${ALL_GOTCHIS[*]}")

# Build calldata
CALLDATA=$(cast calldata "interact(uint256[])" "[$GOTCHI_LIST]")

echo "🦞 Submitting batch petting transaction..."
echo ""

# Map chain name to chain ID for bankr CLI
case "$CHAIN_ID" in
  "base") CHAIN_ID_NUM=8453 ;;
  "ethereum") CHAIN_ID_NUM=1 ;;
  "polygon") CHAIN_ID_NUM=137 ;;
  *) CHAIN_ID_NUM=8453 ;; # default to Base
esac

# Submit via Bankr CLI
bankr submit tx \
  --to "$CONTRACT" \
  --chain-id "$CHAIN_ID_NUM" \
  --value 0 \
  --data "$CALLDATA" \
  --description "Pet all ${#ALL_GOTCHIS[@]} gotchis - AAI daily ritual"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Petting complete!"
echo ""
echo "📊 Summary:"
echo "  • Petted: ${#ALL_GOTCHIS[@]} gotchis"
echo "  • Bankr wallet: ${#BANKR_GOTCHIS[@]}"
echo "  • Hardware wallet: ${#HW_GOTCHIS[@]} (via operator)"
echo "  • Next pet: 12 hours from now"
echo ""
echo "💜 Kinship +${#ALL_GOTCHIS[@]}! LFGOTCHi! 🦞"
