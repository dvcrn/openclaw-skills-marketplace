#!/usr/bin/env bash
# Report a single execution step to the server.
#
# Usage: bash report-step.sh <task_id> <step_number> "<action>" [screenshot_base64]
# Output: Step confirmation. Prints BUDGET_EXHAUSTED if budget is used up.

source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
rmb_check_deps
rmb_load_state || true
rmb_ensure_auth

if [ $# -lt 3 ]; then
  rmb_log ERROR "Usage: report-step.sh <task_id> <step_number> <action> [screenshot_base64]"
  exit 1
fi

TASK_ID="$1"
STEP_NUM="$2"
ACTION="$3"
SCREENSHOT="${4:-}"

# Build request body
if [ -n "$SCREENSHOT" ]; then
  body="$(jq -n \
    --argjson step "$STEP_NUM" \
    --arg action "$ACTION" \
    --arg screenshot "$SCREENSHOT" \
    '{"step": $step, "action": $action, "screenshot": $screenshot}')"
else
  body="$(jq -n \
    --argjson step "$STEP_NUM" \
    --arg action "$ACTION" \
    '{"step": $step, "action": $action}')"
fi

rmb_http POST "/tasks/$TASK_ID/steps" "$body"

if [ "$HTTP_STATUS" = "200" ]; then
  budget_remaining="$(echo "$HTTP_BODY" | jq -r '.budget_remaining // "unknown"')"
  rmb_log INFO "Step $STEP_NUM reported. Budget remaining: $budget_remaining credits"

  if [ "$budget_remaining" != "unknown" ] && [ "$budget_remaining" -le 0 ] 2>/dev/null; then
    rmb_log WARN "BUDGET_EXHAUSTED — stop execution immediately"
    echo "BUDGET_EXHAUSTED"
  fi
  exit 0
elif [ "$HTTP_STATUS" = "400" ]; then
  # Budget cap or validation error
  error_msg="$(echo "$HTTP_BODY" | jq -r '.error // .message // "unknown error"')"
  if echo "$error_msg" | grep -qi "budget"; then
    rmb_log WARN "BUDGET_EXHAUSTED — $error_msg"
    echo "BUDGET_EXHAUSTED"
    exit 0
  fi
  rmb_log ERROR "Step report rejected (HTTP 400): $error_msg"
  exit 1
else
  rmb_log ERROR "Step report failed (HTTP $HTTP_STATUS): $HTTP_BODY"
  exit 1
fi
