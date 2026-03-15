#!/bin/bash
# =============================================================================
# lib.sh — shared functions for Time Clawshine
# Sourced by all bin/ scripts via: source "$TC_ROOT/lib.sh"
# =============================================================================

# --- Resolve config path -----------------------------------------------------
# lib.sh lives at project root — no ".." needed
TC_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${TC_CONFIG:-$TC_ROOT/config.yaml}"

[[ -f "$CONFIG_FILE" ]] || { echo "[time-clawshine] ERROR: config.yaml not found at $CONFIG_FILE"; exit 1; }

# --- YAML parser (requires yq v4) -------------------------------------------
_cfg() {
    # Usage: _cfg '.repository.path'
    yq e "$1" "$CONFIG_FILE"
}

_cfg_list() {
    # Usage: _cfg_list '.backup.paths[]'  → one item per line
    yq e "$1" "$CONFIG_FILE"
}

# --- Load config into variables ----------------------------------------------
tc_load_config() {
    REPO=$(_cfg '.repository.path')
    PASS_FILE=$(_cfg '.repository.password_file')
    KEEP_LAST=$(_cfg '.retention.keep_last')
    LOG_FILE=$(_cfg '.logging.file')
    VERBOSE=$(_cfg '.logging.verbose')
    CRON_EXPR=$(_cfg '.schedule.cron')

    TG_ENABLED=$(_cfg '.notifications.telegram.enabled')
    TG_TOKEN=$(_cfg '.notifications.telegram.bot_token')
    TG_CHAT_ID=$(_cfg '.notifications.telegram.chat_id')

    # Validate critical config values
    _require_cfg() {
        local name="$1" val="$2"
        if [[ -z "$val" || "$val" == "null" ]]; then
            echo "[time-clawshine] ERROR: config.yaml missing required field: $name"
            exit 1
        fi
    }
    _require_cfg 'repository.path'          "$REPO"
    _require_cfg 'repository.password_file' "$PASS_FILE"
    _require_cfg 'retention.keep_last'      "$KEEP_LAST"
    _require_cfg 'logging.file'             "$LOG_FILE"

    # Build backup paths array (standard + extra)
    mapfile -t _BASE_PATHS  < <(_cfg_list '.backup.paths[]')
    mapfile -t _EXTRA_PATHS < <(_cfg_list '.backup.extra_paths[]' 2>/dev/null || true)
    BACKUP_PATHS=("${_BASE_PATHS[@]}")
    for p in "${_EXTRA_PATHS[@]}"; do
        [[ -n "$p" && "$p" != "null" ]] && BACKUP_PATHS+=("$p")
    done

    # Build exclude flags array (standard + extra)
    mapfile -t _BASE_EX  < <(_cfg_list '.backup.exclude[]')
    mapfile -t _EXTRA_EX < <(_cfg_list '.backup.extra_excludes[]' 2>/dev/null || true)
    EXCLUDES=()
    for ex in "${_BASE_EX[@]}" "${_EXTRA_EX[@]}"; do
        [[ -n "$ex" && "$ex" != "null" ]] && EXCLUDES+=("--exclude=$ex")
    done
}

# --- Logging -----------------------------------------------------------------
timestamp() { date '+%Y-%m-%d %H:%M:%S'; }

log() {
    local level="${1:-INFO}"
    local msg="${2:-}"
    echo "[$(timestamp)] [$level] $msg" | tee -a "$LOG_FILE"
}

log_info()  { log "INFO " "$1"; }
log_warn()  { log "WARN " "$1"; }
log_error() { log "ERROR" "$1"; }

# --- Telegram ----------------------------------------------------------------
tg_send() {
    local msg="$1"
    [[ "$TG_ENABLED" != "true" ]]     && return 0
    [[ -z "$TG_TOKEN" ]]              && return 0
    [[ "$TG_TOKEN" == "null" ]]       && return 0
    [[ -z "$TG_CHAT_ID" ]]            && return 0
    [[ "$TG_CHAT_ID" == "null" ]]     && return 0

    curl -s -X POST \
        "https://api.telegram.org/bot${TG_TOKEN}/sendMessage" \
        -H "Content-Type: application/json" \
        -d "$(jq -n \
            --arg chat_id "$TG_CHAT_ID" \
            --arg text "$msg" \
            '{chat_id: $chat_id, text: $text, parse_mode: "Markdown"}')" \
        > /dev/null 2>&1 || true
}

tg_failure() {
    local error_msg="$1"
    local hostname; hostname=$(hostname)
    # Truncate error output to avoid leaking sensitive paths/data via Telegram
    local safe_msg
    safe_msg=$(head -c 800 <<< "$error_msg")
    [[ ${#error_msg} -gt 800 ]] && safe_msg+=$'\n[...truncated]'
    tg_send "🔴 *Time Clawshine — Backup FALHOU*
🖥 \`$hostname\`
🕐 $(timestamp)

\`\`\`
$safe_msg
\`\`\`"
}

# --- Restic wrapper ----------------------------------------------------------
restic_cmd() {
    RESTIC_PASSWORD_FILE="$PASS_FILE" restic -r "$REPO" "$@"
}

# --- Validation --------------------------------------------------------------
tc_validate_paths() {
    local missing=()
    for path in "${BACKUP_PATHS[@]}"; do
        [[ -e "$path" ]] || missing+=("$path")
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        log_error "Paths not found: ${missing[*]}"
        tg_failure "Paths not found:\n${missing[*]}"
        return 1
    fi
    return 0
}

tc_check_deps() {
    local missing=()
    for cmd in restic yq curl jq; do
        command -v "$cmd" &>/dev/null || missing+=("$cmd")
    done
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "[time-clawshine] ERROR: Missing dependencies: ${missing[*]}"
        echo "Run: sudo bin/setup.sh"
        exit 1
    fi
}
