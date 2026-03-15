#!/usr/bin/env bash
# Cognition — Install script
# Creates the full cognitive memory directory structure and template files.
# Usage: bash scripts/install.sh [workspace_path]
# Default: ~/.openclaw/workspace

set -euo pipefail

WORKSPACE="${1:-$HOME/.openclaw/workspace}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
TEMPLATES="$SKILL_DIR/templates"

echo "🧠 Cognition — Installing cognitive memory architecture"
echo "   Workspace: $WORKSPACE"
echo ""

# Create directories
dirs=(
  "memory/procedures"
  "memory/consolidation"
  "memory/summaries"
  "memory/meta"
  "memory/bank"
)

for dir in "${dirs[@]}"; do
  if [[ ! -d "$WORKSPACE/$dir" ]]; then
    mkdir -p "$WORKSPACE/$dir"
    echo "  ✅ Created $dir/"
  else
    echo "  ⏭️  $dir/ already exists"
  fi
done

# Copy templates (only if not already present)
copy_template() {
  local src="$1"
  local dest="$2"
  if [[ ! -f "$dest" ]]; then
    cp "$src" "$dest"
    echo "  ✅ Created $(basename "$dest")"
  else
    echo "  ⏭️  $(basename "$dest") already exists (skipped)"
  fi
}

copy_template "$TEMPLATES/FUTURE_INTENTS.md" "$WORKSPACE/memory/FUTURE_INTENTS.md"
copy_template "$TEMPLATES/KNOWLEDGE_MAP.md" "$WORKSPACE/memory/KNOWLEDGE_MAP.md"
copy_template "$TEMPLATES/cross-references.md" "$WORKSPACE/memory/bank/cross-references.md"
copy_template "$TEMPLATES/procedures-index.yaml" "$WORKSPACE/memory/procedures/index.yaml"
copy_template "$TEMPLATES/gap_tracker.json" "$WORKSPACE/memory/meta/gap_tracker.json"
copy_template "$TEMPLATES/retrieval_log.json" "$WORKSPACE/memory/meta/retrieval_log.json"

echo ""
echo "🧠 Cognition installed!"
echo ""
echo "Next steps:"
echo "  1. Read the SKILL.md for the 4-phase adoption guide"
echo "  2. Add the Memory Protocol to your AGENTS.md (see references/protocols.md)"
echo "  3. Set up the nightly consolidation cron (see references/consolidation-prompt.md)"
echo "  4. Customize KNOWLEDGE_MAP.md for your domains"
echo ""
