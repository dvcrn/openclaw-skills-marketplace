#!/bin/bash
# Listen for immediate wake signals through the relay when available, then
# fall back to the legacy long-poll wake endpoint if relay setup is missing.

set -euo pipefail

SC_API_URL="${SC_API_URL:?SC_API_URL not set}"
SC_API_KEY="${SC_API_KEY:?SC_API_KEY not set}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
POLL_SCRIPT="$SCRIPT_DIR/poll-tasks.sh"
RELAY_CLIENT="$SCRIPT_DIR/wake-relay-client.py"
DISPATCH_PLAN_SCRIPT="$SCRIPT_DIR/wake-dispatch-plan.py"

LISTENER_RUNTIME_SEC="${SC_WAKE_LISTENER_RUNTIME_SEC:-840}" # 14 min, below 15m cron cadence
POLL_TIMEOUT_SEC="${SC_WAKE_POLL_TIMEOUT_SEC:-60}"
CURL_CONNECT_TIMEOUT="${SC_WAKE_CONNECT_TIMEOUT_SEC:-5}"
CURL_MAX_TIME="${SC_WAKE_MAX_TIME_SEC:-70}"
ERROR_RETRY_DELAY_SEC="${SC_WAKE_ERROR_RETRY_DELAY_SEC:-5}"
RELAY_CONNECT_TIMEOUT_SEC="${SC_WAKE_RELAY_CONNECT_TIMEOUT_SEC:-10}"
RELAY_HEARTBEAT_SEC="${SC_WAKE_HEARTBEAT_SEC:-30}"
WAKE_TRANSPORT="${SC_WAKE_TRANSPORT:-auto}" # auto | relay | poll
INSTANCE_LABEL="${SC_WAKE_INSTANCE_LABEL:-}"
EXIT_AFTER_WAKE="${SC_WAKE_EXIT_AFTER_EVENT:-1}"
WAKE_HANDOFF_EXIT_CODE=10
NO_ACTIONABLE_WORK_EXIT_CODE=11
NO_PENDING_DIRECT_DISPATCH_EXIT_CODE=12
EXPECTED_DIRECT_DISPATCH_FALLBACK_EXIT_CODE=13
DISPATCH_AGENT="${SC_WAKE_DISPATCH_AGENT:-main}"
WAKE_DISPATCH_MODE="${SC_WAKE_DISPATCH_MODE:-acp}" # acp | chat
ACP_AGENT="${SC_WAKE_ACP_AGENT:-codex}"
ACP_MODE="${SC_WAKE_ACP_MODE:-run}"
ACP_CWD="${SC_WAKE_ACP_CWD:-/tmp}"
LOCAL_GATEWAY_URL="${SC_WAKE_LOCAL_GATEWAY_URL:-${OPENCLAW_GATEWAY_URL:-}}"
LOCAL_GATEWAY_TOKEN="${SC_WAKE_LOCAL_GATEWAY_TOKEN:-${OPENCLAW_GATEWAY_TOKEN:-}}"
LOCAL_GATEWAY_TOKEN_FILE="${SC_WAKE_LOCAL_GATEWAY_TOKEN_FILE:-${HOME}/.openclaw/gateway.token}"
ACP_ENDPOINT_CACHE_TTL_SEC="${SC_WAKE_ACP_ENDPOINT_CACHE_TTL_SEC:-3600}"
ACP_ENDPOINT_CACHE_FILE="${SC_WAKE_ACP_ENDPOINT_CACHE_FILE:-${TMPDIR:-/tmp}/squad-control-wake-acp-endpoint.status}"
LAST_POLL_RESULT_JSON=""

LOCK_DIR="${TMPDIR:-/tmp}/squad-control-wake-listener.lock"
LOCK_TTL_SEC="${SC_WAKE_LISTENER_LOCK_TTL_SEC:-900}"

build_dispatch_message() {
  local poll_result_json="${1-}"

  if [ -n "$poll_result_json" ]; then
    cat <<EOF
Use the squad-control skill to execute the enclosed wake dispatch payload immediately.

This wake-listener handles pending-task launches in executable code when possible. If pending.tasks are still present in the payload below, the direct launch path did not run or failed, so you must handle them now. Treat the JSON envelope below as the source of truth. Do not stop at "On it" or summarize intent.

Execution rules:
- This is an execution turn, not a planning turn. Before you reply with any natural-language text, you must complete at least one real side effect with tools.
- A plain-text acknowledgement like "On it", "I will handle it", or a summary without side effects is a failure.
- If pending.tasks contains actionable tasks, follow Pickup & Dispatch for each eligible task and actually call sessions_spawn for every task you dispatch.
- For pending tasks, the job is not done after pickup or a thread message. Dispatch is only complete after the worker session exists.
- If you cannot dispatch a pending task, call /api/tasks/fail for that task with the real blocker instead of narrating intent.
- If review.tasks contains tasks, follow Review Dispatch for each one.
- If stuck.tasks contains tasks, follow Stuck Task Recovery for each one.
- Only re-poll Squad Control if the payload is malformed or you need to verify that task state changed after an action.
- If the payload has no actionable work, exit quickly without extra chatter.

POLL_RESULT:
$poll_result_json
EOF
    return 0
  fi

  cat <<'EOF'
Use the squad-control skill to check for and execute pending tasks right now.

This is a wake-listener handoff. Poll Squad Control immediately and execute the normal pickup, review, and stuck-task recovery flow without waiting for the next cron interval.

Execution rules:
- This is not a conversational turn. Do not reply with "On it" or a summary before you execute real actions.
- If pending tasks exist, you must actually dispatch them; pickup alone is not enough.
- If dispatch fails, call /api/tasks/fail with the real blocker instead of describing what you would do.

If there is no actionable work, exit quickly without extra chatter.
EOF
}

dispatch_via_openclaw_agent() {
  local poll_result_json="${1-}"

  if ! command -v openclaw >/dev/null 2>&1; then
    echo "WARN: wake handoff received but openclaw CLI is not available" >&2
    return 1
  fi

  local message
  message="$(build_dispatch_message "$poll_result_json")"
  echo "WAKE_AGENT_DISPATCH: agent=${DISPATCH_AGENT}" >&2
  openclaw agent -m "$message" --agent "$DISPATCH_AGENT"
}

decode_base64_text() {
  python3 -c 'import base64, sys; print(base64.b64decode(sys.stdin.read().strip()).decode("utf-8"))'
}

build_acp_session_label() {
  local task_id="${1:?task id required}"
  printf 'squad-control-%s' "$task_id"
}

trim_line() {
  python3 -c 'import sys; print(sys.stdin.read().strip())'
}

read_openclaw_config_value() {
  local key="${1:?config key required}"

  if ! command -v openclaw >/dev/null 2>&1; then
    return 1
  fi

  openclaw config get "$key" 2>/dev/null | trim_line
}

resolve_local_gateway_url() {
  local configured_url port host

  if [ -n "$LOCAL_GATEWAY_URL" ]; then
    printf '%s' "$LOCAL_GATEWAY_URL"
    return 0
  fi

  configured_url="$(read_openclaw_config_value gateway.url || true)"
  if [ -n "$configured_url" ]; then
    printf '%s' "$configured_url"
    return 0
  fi

  configured_url="$(read_openclaw_config_value gateway.localUrl || true)"
  if [ -n "$configured_url" ]; then
    printf '%s' "$configured_url"
    return 0
  fi

  port="$(read_openclaw_config_value gateway.port || true)"
  if [ -z "$port" ]; then
    return 1
  fi

  host="$(read_openclaw_config_value gateway.host || true)"
  if [ -z "$host" ]; then
    host="127.0.0.1"
  fi

  printf 'http://%s:%s' "$host" "$port"
}

resolve_local_gateway_token() {
  if [ -n "$LOCAL_GATEWAY_TOKEN" ]; then
    printf '%s' "$LOCAL_GATEWAY_TOKEN"
    return 0
  fi

  if [ -f "$LOCAL_GATEWAY_TOKEN_FILE" ]; then
    trim_line < "$LOCAL_GATEWAY_TOKEN_FILE"
    return 0
  fi

  return 1
}

clear_acp_endpoint_cache() {
  rm -f "$ACP_ENDPOINT_CACHE_FILE" 2>/dev/null || true
}

cache_acp_endpoint_unavailable() {
  local gateway_url="${1:?gateway url required}"
  local status_code="${2:?status code required}"
  local expires_at

  expires_at=$(( $(date +%s) + ACP_ENDPOINT_CACHE_TTL_SEC ))
  cat > "$ACP_ENDPOINT_CACHE_FILE" <<EOF
url=${gateway_url%/}/api/sessions/spawn
status=${status_code}
expiresAt=${expires_at}
EOF

  echo "WAKE_DIRECT_ACP_UNAVAILABLE_CACHED: status=${status_code} until=${expires_at} url=${gateway_url%/}/api/sessions/spawn" >&2
}

acp_endpoint_unavailable_cached() {
  local gateway_url="${1:?gateway url required}"
  local target_url cached_url cached_status cached_expiry now

  if [ ! -f "$ACP_ENDPOINT_CACHE_FILE" ]; then
    return 1
  fi

  target_url="${gateway_url%/}/api/sessions/spawn"
  cached_url="$(grep '^url=' "$ACP_ENDPOINT_CACHE_FILE" 2>/dev/null | head -n1 | cut -d= -f2-)"
  cached_status="$(grep '^status=' "$ACP_ENDPOINT_CACHE_FILE" 2>/dev/null | head -n1 | cut -d= -f2-)"
  cached_expiry="$(grep '^expiresAt=' "$ACP_ENDPOINT_CACHE_FILE" 2>/dev/null | head -n1 | cut -d= -f2-)"
  now="$(date +%s)"

  if [ -z "$cached_url" ] || [ -z "$cached_expiry" ]; then
    clear_acp_endpoint_cache
    return 1
  fi

  if [ "$cached_url" != "$target_url" ]; then
    return 1
  fi

  if [ "$cached_expiry" -le "$now" ]; then
    clear_acp_endpoint_cache
    return 1
  fi

  echo "WAKE_DIRECT_ACP_UNAVAILABLE_SKIP: status=${cached_status:-unknown} until=${cached_expiry} url=${target_url}" >&2
  return 0
}

normalize_acp_mode() {
  case "${1:-run}" in
    oneshot) printf 'run' ;;
    persistent) printf 'session' ;;
    run|session) printf '%s' "$1" ;;
    *) printf 'run' ;;
  esac
}

build_acp_spawn_params() {
  local task_id="${1:?task id required}"
  local acp_agent="${2:?ACP agent required}"
  local message="${3:?message required}"
  local session_label="${4:?session label required}"
  local acp_mode normalized_mode

  normalized_mode="$(normalize_acp_mode "$ACP_MODE")"
  python3 - "$task_id" "$acp_agent" "$message" "$session_label" "$ACP_CWD" "$normalized_mode" <<'PY'
import json
import sys

_, task_id, agent_id, task, label, cwd, mode = sys.argv
payload = {
    "task": task,
    "runtime": "acp",
    "agentId": agent_id,
    "mode": mode,
    "thread": False,
    "cwd": cwd,
    "label": label,
}
print(json.dumps(payload))
PY
}

dispatch_pending_task_via_acp() {
  local task_id="${1:?task id required}"
  local acp_agent="${2:?ACP agent required}"
  local message="${3:?message required}"
  local session_label params gateway_url gateway_token response_file stderr_file http_status curl_exit
  local -a curl_args

  session_label="$(build_acp_session_label "$task_id")"
  params="$(build_acp_spawn_params "$task_id" "$acp_agent" "$message" "$session_label")"
  gateway_url="$(resolve_local_gateway_url || true)"
  gateway_token="$(resolve_local_gateway_token || true)"

  if [ -z "$gateway_url" ]; then
    echo "WARN: no local OpenClaw gateway URL available for ACP wake dispatch" >&2
    return "$EXPECTED_DIRECT_DISPATCH_FALLBACK_EXIT_CODE"
  fi

  if acp_endpoint_unavailable_cached "$gateway_url"; then
    return "$EXPECTED_DIRECT_DISPATCH_FALLBACK_EXIT_CODE"
  fi

  curl_args=(
    -sSL
    --connect-timeout "$CURL_CONNECT_TIMEOUT"
    --max-time "$CURL_MAX_TIME"
    -X POST "${gateway_url%/}/api/sessions/spawn"
    -H "Content-Type: application/json"
  )
  if [ -n "$gateway_token" ]; then
    curl_args+=(
      -H "Authorization: Bearer ${gateway_token}"
      -H "x-api-key: ${gateway_token}"
    )
  fi
  echo "WAKE_DIRECT_ACP_DISPATCH: task=${task_id} agent=${acp_agent} label=${session_label}" >&2
  echo "WAKE_DIRECT_ACP_HTTP_SPAWN: task=${task_id} agent=${acp_agent} label=${session_label} url=${gateway_url%/}/api/sessions/spawn" >&2
  response_file="$(mktemp)"
  stderr_file="$(mktemp)"
  http_status="$(curl "${curl_args[@]}" --data "$params" -o "$response_file" -w "%{http_code}" 2>"$stderr_file")"
  curl_exit=$?

  if [ -s "$stderr_file" ]; then
    cat "$stderr_file" >&2
  fi

  if [ "$curl_exit" -ne 0 ]; then
    if [ -s "$response_file" ]; then
      cat "$response_file" >&2
    fi
    rm -f "$response_file" "$stderr_file"
    return 1
  fi

  if [ -s "$response_file" ]; then
    cat "$response_file" >&2
  fi

  case "$http_status" in
    2??)
      clear_acp_endpoint_cache
      ;;
    404|405|410|501)
      cache_acp_endpoint_unavailable "$gateway_url" "$http_status"
      rm -f "$response_file" "$stderr_file"
      return "$EXPECTED_DIRECT_DISPATCH_FALLBACK_EXIT_CODE"
      ;;
    *)
      echo "WARN: local ACP spawn returned HTTP ${http_status}" >&2
      rm -f "$response_file" "$stderr_file"
      return 1
      ;;
  esac

  rm -f "$response_file" "$stderr_file"
}

dispatch_pending_tasks_directly() {
  local poll_result_json="${1:?poll result json required}"
  local task_id acp_agent_b64 message_b64 acp_agent message
  local -a launch_rows=()

  if [ "$WAKE_DISPATCH_MODE" = "chat" ]; then
    echo "WAKE_DIRECT_DISPATCH_SKIPPED: mode=chat" >&2
    return "$EXPECTED_DIRECT_DISPATCH_FALLBACK_EXIT_CODE"
  fi

  if [ ! -f "$DISPATCH_PLAN_SCRIPT" ] || ! command -v python3 >/dev/null 2>&1; then
    return 1
  fi

  if ! command -v openclaw >/dev/null 2>&1; then
    echo "WARN: direct wake dispatch requested but openclaw CLI is not available" >&2
    return 1
  fi

  mapfile -t launch_rows < <(printf '%s' "$poll_result_json" | python3 "$DISPATCH_PLAN_SCRIPT" pending-launches)
  if [ "${#launch_rows[@]}" -eq 0 ]; then
    return "$NO_PENDING_DIRECT_DISPATCH_EXIT_CODE"
  fi

  for row in "${launch_rows[@]}"; do
    IFS=$'\t' read -r task_id acp_agent_b64 message_b64 <<< "$row"
    [ -n "$task_id" ] || continue
    [ -n "$acp_agent_b64" ] || continue
    [ -n "$message_b64" ] || continue

    acp_agent="$(printf '%s' "$acp_agent_b64" | decode_base64_text)"
    message="$(printf '%s' "$message_b64" | decode_base64_text)"

    if dispatch_pending_task_via_acp "$task_id" "$acp_agent" "$message"; then
      :
    else
      return $?
    fi
  done

  return 0
}

handle_wake_dispatch_payload() {
  local poll_result_json="${1:?poll result json required}"
  local direct_dispatch_exit residual_payload=""

  if dispatch_pending_tasks_directly "$poll_result_json"; then
    return 0
  fi

  direct_dispatch_exit=$?
  if [ "$direct_dispatch_exit" -eq "$NO_PENDING_DIRECT_DISPATCH_EXIT_CODE" ]; then
    if [ -f "$DISPATCH_PLAN_SCRIPT" ] && command -v python3 >/dev/null 2>&1; then
      residual_payload="$(printf '%s' "$poll_result_json" | python3 "$DISPATCH_PLAN_SCRIPT" residual-payload)"
    fi

    if [ -n "$residual_payload" ]; then
      dispatch_via_openclaw_agent "$residual_payload" || echo "WARN: wake-triggered OpenClaw dispatch failed" >&2
      return 0
    fi
  elif [ "$direct_dispatch_exit" -eq "$EXPECTED_DIRECT_DISPATCH_FALLBACK_EXIT_CODE" ]; then
    echo "WAKE_DIRECT_DISPATCH_FALLBACK: using dispatcher agent" >&2
  else
    echo "WARN: direct wake dispatch failed; falling back to dispatcher agent" >&2
  fi

  dispatch_via_openclaw_agent "$poll_result_json" || echo "WARN: wake-triggered OpenClaw dispatch failed" >&2
  return 0
}

cleanup_lock() {
  rm -rf "$LOCK_DIR" 2>/dev/null || true
}

acquire_lock() {
  local now lock_ts age
  now=$(date +%s)

  if mkdir "$LOCK_DIR" 2>/dev/null; then
    echo "$now" > "$LOCK_DIR/ts"
    trap cleanup_lock EXIT
    return 0
  fi

  lock_ts=$(cat "$LOCK_DIR/ts" 2>/dev/null || echo 0)
  age=$(( now - lock_ts ))
  if [ "$age" -gt "$LOCK_TTL_SEC" ]; then
    rm -rf "$LOCK_DIR" 2>/dev/null || true
    if mkdir "$LOCK_DIR" 2>/dev/null; then
      echo "$now" > "$LOCK_DIR/ts"
      trap cleanup_lock EXIT
      return 0
    fi
  fi

  echo "WAKE_LISTENER_ALREADY_RUNNING" >&2
  exit 0
}

fetch_wake() {
  curl -sSL \
    --connect-timeout "$CURL_CONNECT_TIMEOUT" \
    --max-time "$CURL_MAX_TIME" \
    --fail \
    "${SC_API_URL}/api/wake/poll?timeoutSec=${POLL_TIMEOUT_SEC}" \
    -H "x-api-key: ${SC_API_KEY}" 2>/dev/null
}

request_relay_session() {
  local payload='{}'
  if [ -n "$INSTANCE_LABEL" ]; then
    payload=$(python3 - "$INSTANCE_LABEL" <<'PY'
import json
import sys

print(json.dumps({"instanceLabel": sys.argv[1]}))
PY
)
  fi

  curl -sSL \
    --connect-timeout "$CURL_CONNECT_TIMEOUT" \
    --max-time "$CURL_MAX_TIME" \
    --fail \
    -X POST "${SC_API_URL}/api/wake/session" \
    -H "Content-Type: application/json" \
    -H "x-api-key: ${SC_API_KEY}" \
    --data "$payload" 2>/dev/null
}

extract_wake_json() {
  python3 -c 'import json,sys; data=json.load(sys.stdin); wake=data.get("wake"); print(json.dumps(wake) if wake else "")'
}

extract_session_fields() {
  python3 -c 'import json,sys; data=json.load(sys.stdin); print(data.get("relayUrl") or ""); print(data.get("token") or ""); print(data.get("listenerId") or "")'
}

extract_poll_result_json() {
  python3 -c 'import json, sys
raw = sys.stdin.read()
marker = "POLL_RESULT:"
index = raw.find(marker)
if index < 0:
    print("")
    raise SystemExit(0)
payload = raw[index + len(marker):].strip()
if not payload:
    print("")
    raise SystemExit(0)
try:
    parsed = json.loads(payload)
except Exception:
    print(payload)
else:
    print(json.dumps(parsed))
'
}

run_poll_and_capture_result() {
  local poll_output
  LAST_POLL_RESULT_JSON=""

  if ! poll_output="$("$POLL_SCRIPT")"; then
    return 1
  fi

  if [ -n "$poll_output" ]; then
    printf '%s\n' "$poll_output" >&2
  fi

  LAST_POLL_RESULT_JSON=$(printf '%s' "$poll_output" | extract_poll_result_json)
  if [ -z "$LAST_POLL_RESULT_JSON" ]; then
    echo "WAKE_LISTENER_NO_ACTIONABLE_WORK" >&2
    return "$NO_ACTIONABLE_WORK_EXIT_CODE"
  fi

  return 0
}

run_poll_fallback_loop() {
  local poll_result_exit

  while [ "$(date +%s)" -lt "$listener_ends_at" ]; do
    response=$(fetch_wake) || {
      echo "WARN: wake poll failed; retrying in ${ERROR_RETRY_DELAY_SEC}s" >&2
      sleep "$ERROR_RETRY_DELAY_SEC"
      continue
    }

    wake_json=$(printf '%s' "$response" | extract_wake_json)
    if [ -z "$wake_json" ]; then
      continue
    fi

    echo "WAKE_EVENT: ${wake_json}" >&2
    if run_poll_and_capture_result; then
      :
    else
      poll_result_exit=$?
      if [ "$poll_result_exit" -eq "$NO_ACTIONABLE_WORK_EXIT_CODE" ]; then
        continue
      fi
      echo "WARN: wake-triggered poll failed; continuing listener loop" >&2
      continue
    fi

    if [ "$EXIT_AFTER_WAKE" = "1" ]; then
      echo "WAKE_LISTENER_HANDOFF" >&2
      return "$WAKE_HANDOFF_EXIT_CODE"
    fi
  done
}

acquire_lock

listener_started_at=$(date +%s)
listener_ends_at=$((listener_started_at + LISTENER_RUNTIME_SEC))

echo "WAKE_LISTENER_STARTED" >&2

while [ "$(date +%s)" -lt "$listener_ends_at" ]; do
  if [ "$WAKE_TRANSPORT" != "poll" ] && [ -x "$(command -v python3)" ] && [ -f "$RELAY_CLIENT" ]; then
    session_json=$(request_relay_session) || session_json=""
    if [ -n "$session_json" ]; then
      mapfile -t session_fields < <(printf '%s' "$session_json" | extract_session_fields)
      relay_url="${session_fields[0]:-}"
      relay_token="${session_fields[1]:-}"
      listener_id="${session_fields[2]:-}"

      if [ -n "$relay_url" ] && [ -n "$relay_token" ] && [ -n "$listener_id" ]; then
        if python3 "$RELAY_CLIENT" \
          --relay-url "$relay_url" \
          --token "$relay_token" \
          --listener-id "$listener_id" \
          --poll-script "$POLL_SCRIPT" \
          --deadline-epoch "$listener_ends_at" \
          --heartbeat-sec "$RELAY_HEARTBEAT_SEC" \
          --connect-timeout-sec "$RELAY_CONNECT_TIMEOUT_SEC" \
          --exit-after-wake "$EXIT_AFTER_WAKE"; then
          continue
        else
          relay_exit=$?
          if [ "$relay_exit" -eq "$WAKE_HANDOFF_EXIT_CODE" ]; then
            if run_poll_and_capture_result; then
              handle_wake_dispatch_payload "$LAST_POLL_RESULT_JSON"
              exit 0
            fi

            poll_result_exit=$?
            if [ "$poll_result_exit" -eq "$NO_ACTIONABLE_WORK_EXIT_CODE" ]; then
              continue
            fi

            echo "WARN: wake-triggered poll failed after relay handoff; retrying in ${ERROR_RETRY_DELAY_SEC}s" >&2
            sleep "$ERROR_RETRY_DELAY_SEC"
            continue
          fi

          echo "WARN: wake relay client exited; retrying in ${ERROR_RETRY_DELAY_SEC}s" >&2
          if [ "$WAKE_TRANSPORT" = "relay" ]; then
            sleep "$ERROR_RETRY_DELAY_SEC"
            continue
          fi
        fi
      fi
    fi

    if [ "$WAKE_TRANSPORT" = "relay" ]; then
      echo "WARN: wake relay session unavailable; retrying in ${ERROR_RETRY_DELAY_SEC}s" >&2
      sleep "$ERROR_RETRY_DELAY_SEC"
      continue
    fi
  fi

  if [ "$WAKE_TRANSPORT" = "poll" ] || [ "$WAKE_TRANSPORT" = "auto" ]; then
    if run_poll_fallback_loop; then
      break
    else
      poll_exit=$?
      if [ "$poll_exit" -eq "$WAKE_HANDOFF_EXIT_CODE" ]; then
        handle_wake_dispatch_payload "$LAST_POLL_RESULT_JSON"
        exit 0
      fi

      break
    fi
  else
    echo "WARN: unsupported wake transport '${WAKE_TRANSPORT}'; retrying in ${ERROR_RETRY_DELAY_SEC}s" >&2
    sleep "$ERROR_RETRY_DELAY_SEC"
  fi
done

echo "WAKE_LISTENER_EXIT" >&2
