#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# GPU CLI ClawHub Skill Runner
# - Whitelists `gpu` commands
# - Denies shell injections (pipes, chaining, redirection, subshells)
# - Preflight: gpu --version, gpu doctor --json
# - Optional caps: price/time (dry-run by default)
# - Exit-code remediation (daemon restart), cleanup on timeout/cancel
#
# Inputs (from ClawHub manifest settings or env overrides):
#   SKILL_DRY_RUN            (bool) default true
#   SKILL_REQUIRE_CONFIRM    (bool) default true
#   SKILL_MAX_PRICE_PER_HOUR (float) default 0.50, 0 disables
#   SKILL_MAX_RUNTIME_MIN    (int)   default 30,   0 disables
#   SKILL_DEFAULT_GPU_TYPE   (str)   default "RTX 4090"
#   SKILL_PROVIDER           (str)   default "runpod"
#   SKILL_CONFIRM            ("yes" to bypass confirm gate)
#   SKILL_INPUT              (optional freeform text)
#
# Invocation:
#   runner.sh <gpu ...>                 # e.g., runner.sh gpu status --json
#   SKILL_INPUT="gpu run python train.py" runner.sh    # parses input
###############################################################################

echo_info()  { printf "[gpu-skill] %s\n" "$*" >&2; }
echo_warn()  { printf "[gpu-skill][warn] %s\n" "$*" >&2; }
echo_error() { printf "[gpu-skill][error] %s\n" "$*" >&2; }

# Load settings with defaults (ClawHub should map manifest settings to envs)
SKILL_DRY_RUN=${SKILL_DRY_RUN:-true}
SKILL_REQUIRE_CONFIRM=${SKILL_REQUIRE_CONFIRM:-true}
SKILL_MAX_PRICE_PER_HOUR=${SKILL_MAX_PRICE_PER_HOUR:-0.50}
SKILL_MAX_RUNTIME_MIN=${SKILL_MAX_RUNTIME_MIN:-30}
SKILL_DEFAULT_GPU_TYPE=${SKILL_DEFAULT_GPU_TYPE:-"RTX 4090"}
SKILL_PROVIDER=${SKILL_PROVIDER:-"runpod"}
SKILL_CONFIRM=${SKILL_CONFIRM:-""}

# Build the command string
CMD_STR=""
if [[ $# -gt 0 ]]; then
  CMD_STR="$*"
elif [[ -n "${SKILL_INPUT:-}" ]]; then
  # Normalize whitespace
  CMD_STR=$(echo "$SKILL_INPUT" | tr -s ' ')
else
  echo_error "No command provided. Example: 'gpu status --json' or set SKILL_INPUT."
  exit 2
fi

# Whitelist: must start with 'gpu '
if [[ ! "$CMD_STR" =~ ^gpu[[:space:]]+ ]]; then
  echo_error "Only 'gpu …' commands are permitted by this skill."
  exit 2
fi

# Debug: show parsed command (stderr)
echo_info "Parsed command: $CMD_STR"

# Deny injection characters: any of ; & | ` ( ) > <
if [[ "$CMD_STR" =~ [\;\&\|\`\(\)\>\<] ]]; then
  echo_error "Command contains disallowed shell operators. Please provide a single 'gpu …' command without chaining or redirection."
  exit 2
fi

# Extract subcommand
read -r _gpu SUBCMD _rest <<<"$CMD_STR"

# Subcommand allowlist
ALLOW_CMDS=(run status doctor logs attach stop inventory config auth daemon volume llm comfyui notebook)
is_allowed=false
for c in "${ALLOW_CMDS[@]}"; do
  if [[ "$SUBCMD" == "$c" ]]; then is_allowed=true; break; fi
done
if [[ "$is_allowed" != true ]]; then
  echo_error "Subcommand '$SUBCMD' not permitted by this skill."
  exit 2
fi
echo_info "Allowlist OK for subcommand: $SUBCMD"

# Append --json for known JSON-capable commands if not present
maybe_force_json() {
  local s="$1"
  case "$SUBCMD" in
    status|inventory|logs|config|daemon|volume|llm|comfyui)
      if [[ "$s" != *" --json"* && "$s" != *" --json "* ]]; then
        s+=" --json"
      fi
      ;;
  esac
  printf "%s" "$s"
}

CMD_STR=$(maybe_force_json "$CMD_STR")
echo_info "JSON flag normalized: $CMD_STR"

# Preflight checks
echo_info "Preflight: checking gpu --version"
if ! gpu --version >/dev/null 2>&1; then
  echo_error "'gpu' binary not found on PATH. Please install: curl -fsSL https://gpu-cli.sh/install.sh | sh"
  exit 2
fi

echo_info "Preflight: running gpu doctor --json"
if ! OUT=$(gpu doctor --json 2>&1); then
  echo_error "'gpu doctor' failed. Output:\n$OUT"
  exit 1
fi
echo_info "Preflight: doctor bytes $(printf "%s" "$OUT" | wc -c | tr -d ' ')"
if ! printf "%s" "$OUT" | tr -d '\n' | grep -q '"healthy"[[:space:]]*:[[:space:]]*true'; then
  echo_warn "Readiness check reported not healthy. Proceeding may fail."
fi

# Price check (best-effort; requires inventory JSON). Skip if disabled.
PRICE_NOTE=""
if [[ "${SKILL_MAX_PRICE_PER_HOUR}" != "0" ]]; then
  # Determine target GPU from command or default
  TARGET_GPU="$SKILL_DEFAULT_GPU_TYPE"
  if echo "$CMD_STR" | grep -q -- "--gpu-type"; then
    # Extract next token after --gpu-type (handles quotes crudely)
    TARGET_GPU=$(echo "$CMD_STR" | sed -E 's/.*--gpu-type[[:space:]]+"?([^" ]+)"?.*/\1/' )
    # Re-substitute spaces if user quoted; fallback if parse failed
    if [[ -z "$TARGET_GPU" ]]; then TARGET_GPU="$SKILL_DEFAULT_GPU_TYPE"; fi
  fi
  if INV=$(gpu inventory --json --available 2>/dev/null); then
    # Find cost_per_hour for TARGET_GPU (simple grep/sed; tolerate whitespace)
    INV_FLAT=$(printf "%s" "$INV" | tr -d '\n' | tr -d ' ')
    TGT_FLAT=$(printf "%s" "$TARGET_GPU" | tr -d ' ')
    LINE=$(printf "%s" "$INV_FLAT" | grep -oi "{[^}]*\"gpu_type\":\"$TGT_FLAT\"[^}]*}" | head -n1 || true)
    if [[ -n "$LINE" ]]; then
      PRICE=$(printf "%s" "$LINE" | sed -E 's/.*\"cost_per_hour\":([0-9.]+).*/\1/' || true)
      if [[ -n "$PRICE" ]]; then
        PRICE_NOTE="GPU $TARGET_GPU at \$${PRICE}/hr"
        # If PRICE > MAX, gate execution
        cmp=$(awk -v a="$PRICE" -v b="$SKILL_MAX_PRICE_PER_HOUR" 'BEGIN{if (a>b) print 1; else print 0}' || echo 0)
        if [[ "$cmp" == "1" ]]; then
          echo_warn "Estimated price ${PRICE_NOTE} exceeds cap \$${SKILL_MAX_PRICE_PER_HOUR}/hr."
          if [[ "$SKILL_REQUIRE_CONFIRM" == "true" && "$SKILL_CONFIRM" != "yes" ]]; then
            echo_info "Set SKILL_CONFIRM=yes to proceed despite cap, or lower GPU price."
            exit 0
          fi
        fi
      fi
    fi
  fi
fi

# Dry-run preview or confirmation gate
echo_info "Command preview: $CMD_STR"
if [[ -n "$PRICE_NOTE" ]]; then echo_info "Cost estimate: $PRICE_NOTE"; fi
if [[ "$SKILL_DRY_RUN" == "true" ]]; then
  echo_info "Dry-run enabled; not executing. Toggle SKILL_DRY_RUN=false to run."
  exit 0
fi
if [[ "$SKILL_REQUIRE_CONFIRM" == "true" && "$SKILL_CONFIRM" != "yes" ]]; then
  echo_info "Confirmation required. Set SKILL_CONFIRM=yes to proceed."
  exit 0
fi

# Runtime timeout (best-effort). Prefer coreutils 'timeout' if present.
run_with_timeout() {
  local minutes="$1"; shift
  if [[ "$minutes" -gt 0 ]] && command -v timeout >/dev/null 2>&1; then
    timeout "$((minutes*60))" bash -lc "$*"
    return $?
  fi
  bash -lc "$*"
}

# Execute with basic remediation: if daemon error (13), start daemon and retry once for 'run'
ATTEMPT=1
MAX_ATTEMPTS=2
EXIT=1
while [[ $ATTEMPT -le $MAX_ATTEMPTS ]]; do
  echo_info "Executing (attempt $ATTEMPT/$MAX_ATTEMPTS)…"
  if [[ "$SKILL_MAX_RUNTIME_MIN" =~ ^[0-9]+$ ]]; then
    set +e
    run_with_timeout "$SKILL_MAX_RUNTIME_MIN" "$CMD_STR"
    EXIT=$?
    set -e
  else
    set +e
    bash -lc "$CMD_STR"
    EXIT=$?
    set -e
  fi

  if [[ $EXIT -eq 0 ]]; then break; fi
  if [[ $EXIT -eq 13 && "$SUBCMD" == "run" && $ATTEMPT -lt $MAX_ATTEMPTS ]]; then
    echo_warn "Daemon connection error (13). Attempting 'gpu daemon start' then retry."
    gpu daemon start || true
    sleep 2
    ATTEMPT=$((ATTEMPT+1))
    continue
  fi
  break
done

# Cleanup on timeout/cancel
if [[ $EXIT -eq 124 || $EXIT -eq 130 ]]; then
  echo_warn "Command interrupted or timed out; attempting cleanup with 'gpu stop -y'"
  gpu stop -y || true
fi

case "$EXIT" in
  0) echo_info "Completed successfully." ;;
  10) echo_error "Auth required/failed (10). Remediation: run 'gpu auth login' from your environment." ;;
  11) echo_error "Quota exceeded (11). Consider 'gpu upgrade' or waiting for quota refresh." ;;
  12) echo_error "Resource not found (12). Verify IDs and context." ;;
  13) echo_error "Daemon connection error (13). Tried restart once; check 'gpu daemon status' and logs." ;;
  14) echo_error "Timeout (14). Increase caps or simplify the job." ;;
  15) echo_error "Cancelled (15)." ;;
  *) echo_error "Exited with code $EXIT." ;;
esac

exit "$EXIT"
