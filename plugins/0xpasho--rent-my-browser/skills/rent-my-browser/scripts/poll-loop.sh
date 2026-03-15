#!/usr/bin/env bash
# Polling loop for the Rent My Browser skill.
# Sends heartbeats, polls for task offers, and claims them.
#
# Modes:
#   bash poll-loop.sh --once [--timeout N]  (foreground, polls for up to N seconds, prints task JSON if claimed)
#   bash poll-loop.sh &                     (background, writes tasks to state/current-task.json)
#
# Exit codes for --once mode:
#   0 = task claimed (JSON printed to stdout)
#   1 = error
#   2 = timeout (no task within the time limit)
#
# Stop background mode: kill $(cat state/poll-loop.pid) or run disconnect.sh

source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
rmb_check_deps
rmb_load_state || true
rmb_ensure_auth

ONCE_MODE=false
ONCE_TIMEOUT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --once) ONCE_MODE=true; shift ;;
    --timeout) ONCE_TIMEOUT="$2"; shift 2 ;;
    *) shift ;;
  esac
done

HEARTBEAT_INTERVAL=25
POLL_INTERVAL=5
TASK_WAIT_INTERVAL=3

# ── State ───────────────────────────────────────────────────────────────────
last_heartbeat=0
running=true
once_start="$(date +%s)"
TASK_FILE="$STATE_DIR/current-task.json"
PID_FILE="$STATE_DIR/poll-loop.pid"
CAPS_FILE="$STATE_DIR/capabilities.json"

# ── Graceful shutdown ───────────────────────────────────────────────────────
cleanup() {
  running=false
  rm -f "$PID_FILE"
  rmb_log INFO "Poll-loop shutting down"
  exit 0
}
trap cleanup SIGTERM SIGINT

# ── Check for existing instance (background mode only) ──────────────────────
if ! $ONCE_MODE; then
  if [ -f "$PID_FILE" ]; then
    existing_pid="$(cat "$PID_FILE")"
    if kill -0 "$existing_pid" 2>/dev/null; then
      rmb_log ERROR "Poll-loop already running (PID $existing_pid). Stop it first or run disconnect.sh."
      exit 1
    fi
    rm -f "$PID_FILE"
  fi
fi

# ── Write PID ───────────────────────────────────────────────────────────────
echo "$$" > "$PID_FILE"
rmb_log INFO "Poll-loop started (PID $$, once=$ONCE_MODE, timeout=$ONCE_TIMEOUT)"

# ── Load or detect capabilities ─────────────────────────────────────────────
if [ -f "$CAPS_FILE" ]; then
  capabilities="$(cat "$CAPS_FILE")"
else
  capabilities="$(bash "$SCRIPT_DIR/detect-capabilities.sh")" || {
    rmb_log ERROR "Failed to detect capabilities"
    rm -f "$PID_FILE"
    exit 1
  }
  echo "$capabilities" > "$CAPS_FILE"
fi

# ── Initialize session stats ────────────────────────────────────────────────
STATS_FILE="$STATE_DIR/session-stats.json"
if [ ! -f "$STATS_FILE" ]; then
  echo '{"session_started":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'","tasks_completed":0,"tasks_failed":0,"total_steps":0,"total_earnings":0,"last_task_at":null}' > "$STATS_FILE"
fi

# ── Main loop ───────────────────────────────────────────────────────────────
while $running; do
  now="$(date +%s)"

  # ── Timeout check (--once mode) ──────────────────────────────────────────
  if $ONCE_MODE && [ "$ONCE_TIMEOUT" -gt 0 ]; then
    elapsed_total=$((now - once_start))
    if [ "$elapsed_total" -ge "$ONCE_TIMEOUT" ]; then
      rmb_log INFO "Timeout reached (${ONCE_TIMEOUT}s), no task claimed"
      rm -f "$PID_FILE"
      exit 2
    fi
  fi

  # ── Heartbeat if due ──────────────────────────────────────────────────────
  elapsed=$((now - last_heartbeat))
  if [ "$elapsed" -ge "$HEARTBEAT_INTERVAL" ]; then
    rmb_http POST "/nodes/$RMB_NODE_ID/heartbeat" "$capabilities" || true

    if [ "$HTTP_STATUS" = "200" ]; then
      last_heartbeat="$now"
    elif [ "$HTTP_STATUS" = "404" ] || [ "$HTTP_STATUS" = "401" ]; then
      rmb_log ERROR "Heartbeat returned $HTTP_STATUS — stopping poll-loop"
      cleanup
    else
      rmb_log WARN "Heartbeat failed (HTTP $HTTP_STATUS), will retry next cycle"
    fi
  fi

  # ── Skip polling if a task is being executed (background mode) ────────────
  if ! $ONCE_MODE && [ -f "$TASK_FILE" ]; then
    sleep "$TASK_WAIT_INTERVAL"
    continue
  fi

  # ── Poll for offers ───────────────────────────────────────────────────────
  rmb_http GET "/nodes/$RMB_NODE_ID/offers" || {
    rmb_log WARN "Offer poll failed, retrying next cycle"
    sleep "$POLL_INTERVAL"
    continue
  }

  if [ "$HTTP_STATUS" != "200" ]; then
    rmb_log WARN "Offer poll returned HTTP $HTTP_STATUS"
    sleep "$POLL_INTERVAL"
    continue
  fi

  # Check if there are any offers
  offer_count="$(echo "$HTTP_BODY" | jq '.offers | length' 2>/dev/null || echo 0)"

  if [ "$offer_count" -gt 0 ]; then
    # Take the first offer (server pre-sorts by relevance)
    offer_id="$(echo "$HTTP_BODY" | jq -r '.offers[0].offer_id')"
    task_id="$(echo "$HTTP_BODY" | jq -r '.offers[0].task_id')"
    goal_summary="$(echo "$HTTP_BODY" | jq -r '.offers[0].goal_summary')"
    payout="$(echo "$HTTP_BODY" | jq -r '.offers[0].payout_per_step')"
    est_steps="$(echo "$HTTP_BODY" | jq -r '.offers[0].estimated_steps')"

    rmb_log INFO "Offer received: $goal_summary (~$est_steps steps, $payout credits/step)"

    # ── Claim the offer ─────────────────────────────────────────────────────
    claim_body="$(jq -n --arg nid "$RMB_NODE_ID" '{"node_id": $nid}')"
    rmb_http POST "/offers/$offer_id/claim" "$claim_body" || {
      rmb_log WARN "Claim request failed, continuing"
      sleep "$POLL_INTERVAL"
      continue
    }

    if [ "$HTTP_STATUS" = "200" ]; then
      rmb_log INFO "Claimed task $task_id"

      # Write task payload for the agent (atomic write)
      local_task="$(echo "$HTTP_BODY" | jq --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '. + {"claimed_at": $ts}')"
      echo "$local_task" > "$TASK_FILE.tmp"

      # ── Validate task before agent sees it ─────────────────────────────
      rejection="$(node "$SCRIPT_DIR/validate-task.mjs" "$TASK_FILE.tmp" 2>/dev/null)"
      if [ $? -ne 0 ] && [ -n "$rejection" ]; then
        rmb_log WARN "Task $task_id rejected by validator: $rejection"
        # Report as failed safety rejection
        fail_body="$(jq -n --arg reason "$rejection" '{"status":"failed","extracted_data":{"reason":"safety_rejection","details":$reason}}')"
        rmb_http POST "/tasks/$task_id/result" "$fail_body" || true
        rm -f "$TASK_FILE.tmp"
        rmb_update_stats "tasks_failed" 1
        rmb_set_stat "last_task_at" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        sleep "$POLL_INTERVAL"
        continue
      fi
      rm -f "$TASK_FILE.tmp"

      # ── --once mode: print task to stdout and exit ─────────────────────
      if $ONCE_MODE; then
        echo "$local_task"
        rm -f "$PID_FILE"
        exit 0
      fi

      # ── Background mode: write file and wait for agent ─────────────────
      echo "$local_task" > "$TASK_FILE.tmp"
      mv "$TASK_FILE.tmp" "$TASK_FILE"

      rmb_log INFO "Task validated and written to $TASK_FILE — waiting for agent to execute..."

      # Wait for the agent to complete the task (deletes the file via report-result.sh)
      while $running && [ -f "$TASK_FILE" ]; do
        sleep "$TASK_WAIT_INTERVAL"

        # Keep sending heartbeats while waiting
        now="$(date +%s)"
        elapsed=$((now - last_heartbeat))
        if [ "$elapsed" -ge "$HEARTBEAT_INTERVAL" ]; then
          rmb_http POST "/nodes/$RMB_NODE_ID/heartbeat" "$capabilities" || true
          if [ "$HTTP_STATUS" = "200" ]; then
            last_heartbeat="$now"
          fi
        fi
      done

      rmb_log INFO "Task completed, resuming polling"

    elif [ "$HTTP_STATUS" = "409" ]; then
      rmb_log INFO "Offer $offer_id already claimed by another node"
    elif [ "$HTTP_STATUS" = "404" ]; then
      rmb_log INFO "Offer $offer_id expired or not found"
    else
      rmb_log WARN "Claim failed (HTTP $HTTP_STATUS): $HTTP_BODY"
    fi
  fi

  sleep "$POLL_INTERVAL"
done
