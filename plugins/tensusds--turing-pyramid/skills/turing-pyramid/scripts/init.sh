#!/bin/bash
# Turing Pyramid — Initialization Script
# Run once on skill installation

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_FILE="$SKILL_DIR/assets/needs-state.json"
TEMPLATE_FILE="$SKILL_DIR/assets/needs-state.template.json"

echo "🔺 Turing Pyramid — Initialization"
echo "=================================="

# Check if already initialized
if [[ -f "$STATE_FILE" ]]; then
    echo "⚠️  State file already exists: $STATE_FILE"
    read -p "   Reinitialize? This will reset all needs. (y/N): " confirm
    if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo "   Aborted."
        exit 0
    fi
fi

# Get current timestamp
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Create state file from template with current timestamps
jq --arg now "$NOW" '
  ._meta.initialized = $now |
  ._meta.last_cycle = $now |
  .needs |= with_entries(.value.last_satisfied = $now)
' "$TEMPLATE_FILE" > "$STATE_FILE"

echo "✅ State file created: $STATE_FILE"
echo "   All needs initialized to satisfaction=3 (full)"
echo ""
echo "📋 Next steps:"
echo "   1. Review assets/needs-config.json"
echo "   2. Run bootstrap (processes ALL needs once):"
echo "      ./scripts/run-cycle.sh --bootstrap"
echo "   3. Add to HEARTBEAT.md:"
echo "      source $SKILL_DIR/scripts/run-cycle.sh"
echo ""
echo "🤝 Discuss with your agent:"
echo "   - Are the decay rates right for you?"
echo "   - Is the importance hierarchy correct?"
echo "   - What actions actually satisfy each need?"
