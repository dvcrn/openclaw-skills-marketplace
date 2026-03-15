#!/usr/bin/env bash
# Disconnect this node from the Rent My Browser marketplace.
# Stops the poll loop, handles in-progress tasks, and prints session summary.
#
# Usage: bash disconnect.sh

source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
rmb_check_deps
rmb_load_state || true

rmb_log INFO "Disconnecting from marketplace..."

# ── Remove cron job ─────────────────────────────────────────────────────────
openclaw cron remove --name "rmb-task-poll" 2>/dev/null \
  && rmb_log INFO "Cron job 'rmb-task-poll' removed" \
  || true

# ── Stop poll-loop if running ───────────────────────────────────────────────
PID_FILE="$STATE_DIR/poll-loop.pid"
if [ -f "$PID_FILE" ]; then
  pid="$(cat "$PID_FILE")"
  if kill -0 "$pid" 2>/dev/null; then
    rmb_log INFO "Stopping poll-loop (PID $pid)..."
    kill -TERM "$pid" 2>/dev/null || true

    # Wait up to 10 seconds for graceful exit
    for i in $(seq 1 10); do
      if ! kill -0 "$pid" 2>/dev/null; then
        break
      fi
      sleep 1
    done

    # Force kill if still running
    if kill -0 "$pid" 2>/dev/null; then
      rmb_log WARN "Poll-loop did not exit gracefully, forcing..."
      kill -9 "$pid" 2>/dev/null || true
    fi

    rmb_log INFO "Poll-loop stopped"
  fi
  rm -f "$PID_FILE"
fi

# ── Handle in-progress task ─────────────────────────────────────────────────
TASK_FILE="$STATE_DIR/current-task.json"
if [ -f "$TASK_FILE" ]; then
  task_id="$(jq -r '.task_id' "$TASK_FILE" 2>/dev/null || echo "")"
  if [ -n "$task_id" ] && [ "$task_id" != "null" ] && [ -n "${RMB_API_KEY:-}" ]; then
    rmb_log WARN "Task $task_id was in progress — reporting as failed"
    rmb_ensure_auth
    bash "$SCRIPT_DIR/report-result.sh" "$task_id" "failed" '{"reason":"node_disconnected"}' "" || true
  fi
  rm -f "$TASK_FILE"
fi

# ── Print session summary ───────────────────────────────────────────────────
STATS_FILE="$STATE_DIR/session-stats.json"
if [ -f "$STATS_FILE" ]; then
  echo ""
  rmb_log INFO "=== Session Summary ==="
  tasks_completed="$(jq -r '.tasks_completed // 0' "$STATS_FILE")"
  tasks_failed="$(jq -r '.tasks_failed // 0' "$STATS_FILE")"
  total_steps="$(jq -r '.total_steps // 0' "$STATS_FILE")"
  total_earnings="$(jq -r '.total_earnings // 0' "$STATS_FILE")"
  session_started="$(jq -r '.session_started // "unknown"' "$STATS_FILE")"

  rmb_log INFO "  Started:    $session_started"
  rmb_log INFO "  Completed:  $tasks_completed tasks"
  rmb_log INFO "  Failed:     $tasks_failed tasks"
  rmb_log INFO "  Steps:      $total_steps total"
  rmb_log INFO "  Earnings:   $total_earnings credits (\$$(echo "scale=2; $total_earnings / 100" | bc 2>/dev/null || echo "?.??"))"
  rmb_log INFO "========================"
  echo ""

  # Clean up session stats (fresh next session)
  rm -f "$STATS_FILE"
fi

# Clean up transient state (keep credentials for reconnection)
rm -f "$STATE_DIR/capabilities.json"

rmb_log INFO "Disconnected from marketplace."
