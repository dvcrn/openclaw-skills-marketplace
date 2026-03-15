#!/usr/bin/env bash
# Setup inference-optimizer: make scripts executable; optionally wire commands into workspace.
# Default: preview only. Use --apply to modify AGENTS.md and TOOLS.md.
# Run after install. Targets ~/clawd and ~/.openclaw/workspace-whatsapp.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
WORKSPACE_MAIN="${WORKSPACE_MAIN:-$HOME/clawd}"
WORKSPACE_WHATSAPP="${WORKSPACE_WHATSAPP:-$HOME/.openclaw/workspace-whatsapp}"

chmod +x "$SKILL_DIR/scripts/openclaw-audit.sh"
chmod +x "$SKILL_DIR/scripts/purge-stale-sessions.sh"
chmod +x "$SKILL_DIR/scripts/preflight.sh"
chmod +x "$SKILL_DIR/scripts/verify.sh"
echo "[OK] Scripts executable"

APPLY=false
[[ "${1:-}" = "--apply" ]] && APPLY=true

AUDIT_PATH="$SKILL_DIR/scripts/openclaw-audit.sh"
PURGE_PATH="$SKILL_DIR/scripts/purge-stale-sessions.sh"
PREFLIGHT_PATH="$SKILL_DIR/scripts/preflight.sh"

SNIPPET_AGENTS="

## Chat commands (exact match, run immediately)

| Command | Action |
| \`/preflight\` | Exec \`bash $PREFLIGHT_PATH\`; creates backup archives, runs audit, runs setup preview, returns logs/next steps. |
| \`/audit\` | Exec \`bash $AUDIT_PATH\`; include script output only. Do not run file-changing actions. |
| \`/optimize\` | Exec \`bash $AUDIT_PATH\`; include script output, then propose optimization actions. Require explicit approval before purge/rewrite/deploy. |"

SNIPPET_TOOLS="

## inference-optimizer

| App | Use | Example |
| \`/preflight\` | Install checks and backup flow | exec \`bash $PREFLIGHT_PATH\`; optional apply: \`bash $PREFLIGHT_PATH --apply-setup\` after approval. |
| \`/audit\` | Analyze only | exec \`bash $AUDIT_PATH\`; include output only. |
| \`/optimize\` | Analyze + action flow | exec \`bash $AUDIT_PATH\`; then propose actions; run actions only after approval. |
| purge sessions | Approved action after audit/optimize | exec \`bash $PURGE_PATH\` (archives by default). |"

if [[ "$APPLY" = false ]]; then
  echo ""
  echo "Preview (no changes made). Run with --apply to modify workspace files."
  echo ""
  echo "Would add to AGENTS.md:"
  echo "$SNIPPET_AGENTS"
  echo ""
  echo "Would add to TOOLS.md:"
  echo "$SNIPPET_TOOLS"
  echo ""
  echo "Workspaces: $WORKSPACE_MAIN, $WORKSPACE_WHATSAPP"
  echo "Usage: bash $0 --apply"
  exit 0
fi

for ws in "$WORKSPACE_MAIN" "$WORKSPACE_WHATSAPP"; do
  [[ -d "$ws" ]] || continue
  if [[ -f "$ws/AGENTS.md" ]]; then
    if ! grep -q "/preflight" "$ws/AGENTS.md" 2>/dev/null; then
      echo "$SNIPPET_AGENTS" >> "$ws/AGENTS.md"
      echo "[OK] Added inference-optimizer commands to $ws/AGENTS.md"
    else
      echo "[SKIP] $ws/AGENTS.md already has /preflight"
    fi
  else
    echo "[WARN] $ws/AGENTS.md not found"
  fi
  if [[ -f "$ws/TOOLS.md" ]]; then
    if ! grep -q "/preflight" "$ws/TOOLS.md" 2>/dev/null; then
      echo "$SNIPPET_TOOLS" >> "$ws/TOOLS.md"
      echo "[OK] Added inference-optimizer commands to $ws/TOOLS.md"
    else
      echo "[SKIP] $ws/TOOLS.md already has /preflight"
    fi
  else
    echo "[WARN] $ws/TOOLS.md not found"
  fi
done

echo ""
echo "Done. Prefer manual purge: bash $PURGE_PATH (archives by default)."
echo "Verify: bash $SKILL_DIR/scripts/verify.sh"
