#!/usr/bin/env bash
# Submit the final result for a task.
#
# Usage: bash report-result.sh <task_id> <status> [extracted_data_json] [final_url]
#   status: "completed" or "failed"
#   extracted_data_json: JSON object string (default: "{}")
#   final_url: the final URL after task execution (optional)

source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
rmb_check_deps
rmb_load_state || true
rmb_ensure_auth

if [ $# -lt 2 ]; then
  rmb_log ERROR "Usage: report-result.sh <task_id> <status> [extracted_data_json] [final_url]"
  exit 1
fi

TASK_ID="$1"
STATUS="$2"
EXTRACTED_DATA="${3:-"{}"}"
FINAL_URL="${4:-}"

# Validate status
if [ "$STATUS" != "completed" ] && [ "$STATUS" != "failed" ]; then
  rmb_log ERROR "Status must be 'completed' or 'failed', got: $STATUS"
  exit 1
fi

# Build request body
body="$(jq -n \
  --arg status "$STATUS" \
  --argjson data "$EXTRACTED_DATA" \
  --arg url "$FINAL_URL" \
  '{status: $status, extracted_data: $data} | if $url != "" then . + {final_url: $url} else . end')"

rmb_log INFO "Submitting result for task $TASK_ID: $STATUS"
rmb_http POST "/tasks/$TASK_ID/result" "$body"

if [ "$HTTP_STATUS" = "200" ]; then
  actual_cost="$(echo "$HTTP_BODY" | jq -r '.actual_cost // 0')"
  steps_executed="$(echo "$HTTP_BODY" | jq -r '.steps_executed // 0')"
  duration_ms="$(echo "$HTTP_BODY" | jq -r '.duration_ms // 0')"

  rmb_log INFO "Task $TASK_ID $STATUS. Steps: $steps_executed, Cost: $actual_cost credits, Duration: ${duration_ms}ms"

  # Update session stats
  if [ "$STATUS" = "completed" ]; then
    rmb_update_stats "tasks_completed" 1
    rmb_update_stats "total_earnings" "$actual_cost"
  else
    rmb_update_stats "tasks_failed" 1
  fi
  rmb_update_stats "total_steps" "$steps_executed"
  rmb_set_stat "last_task_at" "$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  # Signal poll-loop to resume by deleting current task file
  task_file="$STATE_DIR/current-task.json"
  if [ -f "$task_file" ]; then
    rm -f "$task_file"
    rmb_log INFO "Task file cleared — polling will resume"
  fi

  exit 0
else
  rmb_log ERROR "Result submission failed (HTTP $HTTP_STATUS): $HTTP_BODY"
  exit 1
fi
