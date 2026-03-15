#!/bin/bash
# =============================================================================
# bin/backup.sh — Time Clawshine backup engine
# Called by cron every hour — silent on success, Telegram on failure
# =============================================================================

set -euo pipefail

TC_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
source "$TC_ROOT/lib.sh"

tc_check_deps
tc_load_config

# Ensure log file exists and is writable
touch "$LOG_FILE" 2>/dev/null || { echo "ERROR: Cannot write to $LOG_FILE"; exit 1; }

# --- Concurrency lock — skip if another backup is already running -----------
exec 200>/var/lock/time-clawshine.lock
chmod 600 /var/lock/time-clawshine.lock 2>/dev/null || true
flock -n 200 || { log_warn "Another backup is already running — skipping"; exit 0; }

log_info "--- Time Clawshine started ---"

# --- Validate backup paths --------------------------------------------------
tc_validate_paths || exit 1

# --- Run backup -------------------------------------------------------------
RESTIC_ARGS=(backup "${BACKUP_PATHS[@]}" "${EXCLUDES[@]}")
[[ "$VERBOSE" == "true" ]] && RESTIC_ARGS+=(--verbose)

BACKUP_OUTPUT=$(restic_cmd "${RESTIC_ARGS[@]}" 2>&1)
BACKUP_EXIT=$?

if [[ $BACKUP_EXIT -ne 0 ]]; then
    log_error "restic backup failed (exit $BACKUP_EXIT)"
    log_error "$BACKUP_OUTPUT"
    tg_failure "restic backup failed (exit $BACKUP_EXIT):\n\n$BACKUP_OUTPUT"
    exit 1
fi

# Log summary lines only (not full verbose output unless configured)
if [[ "$VERBOSE" == "true" ]]; then
    while IFS= read -r line; do log_info "  $line"; done <<< "$BACKUP_OUTPUT"
else
    grep -E "(snapshot|Added to the repo|processed)" <<< "$BACKUP_OUTPUT" \
        | while IFS= read -r line; do log_info "  $line"; done || true
fi

log_info "Backup OK"

# --- Apply retention policy -------------------------------------------------
log_info "Applying retention policy (keep-last $KEEP_LAST)..."

FORGET_OUTPUT=$(restic_cmd forget --keep-last "$KEEP_LAST" --prune 2>&1)
FORGET_EXIT=$?

if [[ $FORGET_EXIT -ne 0 ]]; then
    log_error "restic forget/prune failed (exit $FORGET_EXIT)"
    log_error "$FORGET_OUTPUT"
    tg_failure "restic forget/prune failed (exit $FORGET_EXIT):\n\n$FORGET_OUTPUT"
    exit 1
fi

log_info "Retention OK"
log_info "--- Time Clawshine finished ---"
