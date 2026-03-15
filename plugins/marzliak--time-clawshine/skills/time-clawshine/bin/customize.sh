#!/bin/bash
# =============================================================================
# bin/customize.sh — Time Clawshine AI-assisted path customization
#
# Analyzes your actual OpenClaw workspace and uses your agent to suggest:
#   - Extra paths worth backing up (whitelist)
#   - Additional exclusion patterns (blacklist)
#
# Always shows suggestions and asks for confirmation before changing anything.
# Updates config.yaml only after explicit user approval.
#
# Usage: sudo bin/customize.sh
# =============================================================================

set -uo pipefail

TC_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$TC_ROOT/lib.sh"

tc_check_deps
tc_load_config

# Must run as root
[[ $EUID -eq 0 ]] || { echo "ERROR: Run as root (sudo bin/customize.sh)"; exit 1; }

# Requires yq (already checked) and openclaw CLI
if ! command -v openclaw &>/dev/null; then
    echo ""
    echo "ERROR: openclaw CLI not found."
    echo "customize.sh uses your agent to analyze your workspace."
    echo "If you want to add paths manually, edit config.yaml directly:"
    echo "  backup.extra_paths  — additional paths to include"
    echo "  backup.extra_excludes — additional patterns to exclude"
    exit 1
fi

echo "╔══════════════════════════════════════════════════════╗"
echo "║       Time Clawshine — Customize Backup Paths        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "This command will:"
echo "  1. Scan your OpenClaw workspace"
echo "  2. Ask your agent to suggest extra paths and exclusions"
echo "  3. Show you the suggestions"
echo "  4. Ask for your confirmation before changing anything"
echo ""
read -rp "Continue? [y/N]: " CONFIRM
[[ "$CONFIRM" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }

# --- Detect workspace path ---------------------------------------------------
WORKSPACE_PATH=$(openclaw config get agents.defaults.workspace 2>/dev/null \
    || echo "/root/.openclaw/workspace")

echo ""
echo "==> Detected workspace: $WORKSPACE_PATH"

if [[ ! -d "$WORKSPACE_PATH" ]]; then
    echo "ERROR: Workspace directory not found at $WORKSPACE_PATH"
    echo "Set the correct path in openclaw.json (agents.defaults.workspace)"
    exit 1
fi

# --- Build workspace tree (safe depth, no secrets) ---------------------------
echo "==> Scanning workspace..."
WORKSPACE_TREE=$(find "$WORKSPACE_PATH" \
    -maxdepth 3 \
    -not -path "*/.git/*" \
    -not -name "*.env" \
    -not -name "secrets.*" \
    -not -name "*.pass" \
    2>/dev/null | sort | head -200)

# --- Build current paths and excludes as readable lists ----------------------
CURRENT_PATHS=$(printf '%s\n' "${BACKUP_PATHS[@]}")
CURRENT_EXCLUDES=$(printf '%s\n' "${EXCLUDES[@]}" | sed 's/--exclude=//')

# --- Helper: fill prompt template --------------------------------------------
fill_prompt() {
    local template_file="$1"
    local template
    template=$(<"$template_file")
    template="${template//\{\{WORKSPACE_PATH\}\}/$WORKSPACE_PATH}"
    template="${template//\{\{CURRENT_PATHS\}\}/$CURRENT_PATHS}"
    template="${template//\{\{CURRENT_EXCLUDES\}\}/$CURRENT_EXCLUDES}"
    template="${template//\{\{WORKSPACE_TREE\}\}/$WORKSPACE_TREE}"
    printf '%s' "$template"
}

# --- Run whitelist prompt -----------------------------------------------------
echo ""
echo "==> Asking your agent for whitelist suggestions..."
WHITELIST_PROMPT=$(fill_prompt "$TC_ROOT/prompts/whitelist.txt")
WHITELIST_RAW=$(echo "$WHITELIST_PROMPT" | openclaw agent ask --no-memory - 2>/dev/null || echo "ERROR")

if [[ "$WHITELIST_RAW" == "ERROR" ]]; then
    echo "WARN: Could not reach agent for whitelist. Skipping."
    WHITELIST_SUGGESTIONS=()
else
    mapfile -t WHITELIST_SUGGESTIONS < <(echo "$WHITELIST_RAW" \
        | grep -v "^NONE$" \
        | grep -v "^#" \
        | grep -v "^$" \
        | grep "^/" \
        | sort -u)
fi

# --- Run blacklist prompt -----------------------------------------------------
echo "==> Asking your agent for blacklist suggestions..."
BLACKLIST_PROMPT=$(fill_prompt "$TC_ROOT/prompts/blacklist.txt")
BLACKLIST_RAW=$(echo "$BLACKLIST_PROMPT" | openclaw agent ask --no-memory - 2>/dev/null || echo "ERROR")

if [[ "$BLACKLIST_RAW" == "ERROR" ]]; then
    echo "WARN: Could not reach agent for blacklist. Skipping."
    BLACKLIST_SUGGESTIONS=()
else
    mapfile -t BLACKLIST_SUGGESTIONS < <(echo "$BLACKLIST_RAW" \
        | grep -v "^NONE$" \
        | grep -v "^#" \
        | grep -v "^$" \
        | sort -u)
fi

# --- Show suggestions --------------------------------------------------------
echo ""
echo "┌─────────────────────────────────────────────────────────┐"
echo "│              Agent Suggestions                          │"
echo "├─────────────────────────────────────────────────────────┤"

if [[ ${#WHITELIST_SUGGESTIONS[@]} -eq 0 ]]; then
    echo "│  Extra paths (whitelist): none suggested                │"
else
    echo "│  Extra paths to ADD to backup:                          │"
    for path in "${WHITELIST_SUGGESTIONS[@]}"; do
        printf "│    + %-51s │\n" "$path"
    done
fi

echo "│                                                         │"

if [[ ${#BLACKLIST_SUGGESTIONS[@]} -eq 0 ]]; then
    echo "│  Exclusions (blacklist): none suggested                 │"
else
    echo "│  Patterns to EXCLUDE from backup:                       │"
    for pat in "${BLACKLIST_SUGGESTIONS[@]}"; do
        printf "│    - %-51s │\n" "$pat"
    done
fi

echo "└─────────────────────────────────────────────────────────┘"

# --- Bail early if nothing to do ---------------------------------------------
if [[ ${#WHITELIST_SUGGESTIONS[@]} -eq 0 && ${#BLACKLIST_SUGGESTIONS[@]} -eq 0 ]]; then
    echo ""
    echo "No suggestions from the agent. Your current config.yaml is already optimal."
    echo "You can always edit backup.extra_paths and backup.extra_excludes manually."
    exit 0
fi

# --- Confirmation gate -------------------------------------------------------
echo ""
echo "⚠️  Review the suggestions above carefully before accepting."
echo "   Your current config.yaml will be updated."
echo "   A backup of the original will be saved as config.yaml.bak"
echo ""
read -rp "Apply these suggestions to config.yaml? [y/N]: " APPLY
[[ "$APPLY" =~ ^[Yy]$ ]] || { echo "Aborted. config.yaml unchanged."; exit 0; }

# --- Apply to config.yaml ----------------------------------------------------
echo ""
echo "==> Saving config.yaml.bak..."
cp "$CONFIG_FILE" "${CONFIG_FILE}.bak"

echo "==> Updating config.yaml..."

# Sanitize function — only allow safe characters (whitelist approach)
_sanitize_entry() {
    local entry="$1"
    if [[ ! "$entry" =~ ^[a-zA-Z0-9/_.*@:~-]+$ ]]; then
        echo "    ⚠ Skipped unsafe entry (invalid chars): $entry" >&2
        return 1
    fi
    return 0
}

# Add whitelist entries to extra_paths
for path in "${WHITELIST_SUGGESTIONS[@]}"; do
    _sanitize_entry "$path" || continue
    # Skip if already in standard paths or extra_paths
    if ! grep -qF "$path" "$CONFIG_FILE"; then
        yq e -i ".backup.extra_paths += [\"$path\"]" "$CONFIG_FILE"
        echo "    + Added path: $path"
    else
        echo "    ~ Already present: $path"
    fi
done

# Add blacklist entries to extra_excludes
for pat in "${BLACKLIST_SUGGESTIONS[@]}"; do
    _sanitize_entry "$pat" || continue
    if ! grep -qF "$pat" "$CONFIG_FILE"; then
        yq e -i ".backup.extra_excludes += [\"$pat\"]" "$CONFIG_FILE"
        echo "    - Added exclude: $pat"
    else
        echo "    ~ Already present: $pat"
    fi
done

# --- Re-register cron with updated config ------------------------------------
echo ""
echo "==> Re-running setup to apply updated config..."
bash "$TC_ROOT/bin/setup.sh" --skip-backup

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║              Customization complete ✓                ║"
echo "╠══════════════════════════════════════════════════════╣"
echo "║  config.yaml updated                                 ║"
echo "║  Original saved as config.yaml.bak                  ║"
echo "║  Run 'sudo bin/backup.sh' to test the new config     ║"
echo "╚══════════════════════════════════════════════════════╝"
