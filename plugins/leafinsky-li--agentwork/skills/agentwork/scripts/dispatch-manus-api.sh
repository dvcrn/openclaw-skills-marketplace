#!/bin/bash
# dispatch-manus-api.sh — Execute prompt via Manus API and emit AgentWork process_evidence.
# Usage:
#   dispatch-manus-api.sh "<prompt>" --nonce <nonce> --execution-payload-hash <hash>
#     [--api-key <api_key>] [--timeout <seconds>] [--base-url <url>] [--model <model>] [--resume-task-id <task_id>]
set -euo pipefail

usage() {
  cat <<'USAGE' >&2
Usage:
  dispatch-manus-api.sh "<prompt>" --nonce <nonce> --execution-payload-hash <hash> \
    [--api-key <api_key>] [--timeout <seconds>] [--base-url <url>] [--model <model>] [--resume-task-id <task_id>]
USAGE
  exit 2
}

sha256_hex() {
  if command -v sha256sum >/dev/null 2>&1; then
    printf '%s' "$1" | sha256sum | awk '{print tolower($1)}'
  else
    printf '%s' "$1" | shasum -a 256 | awk '{print tolower($1)}'
  fi
}

PROMPT="${1:-}"
if [ -z "$PROMPT" ]; then
  usage
fi
shift

API_KEY="${MANUS_API_KEY:-}"
TIMEOUT=1800
BASE_URL="${MANUS_API_BASE_URL:-https://api.manus.ai}"
MODEL="${MANUS_MODEL:-}"
NONCE=""
EXECUTION_PAYLOAD_HASH=""
RESUME_TASK_ID=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --api-key)
      [ "$#" -ge 2 ] || usage
      API_KEY="$2"
      shift 2
      ;;
    --timeout)
      [ "$#" -ge 2 ] || usage
      TIMEOUT="$2"
      shift 2
      ;;
    --base-url)
      [ "$#" -ge 2 ] || usage
      BASE_URL="$2"
      shift 2
      ;;
    --model)
      [ "$#" -ge 2 ] || usage
      MODEL="$2"
      shift 2
      ;;
    --nonce)
      [ "$#" -ge 2 ] || usage
      NONCE="$2"
      shift 2
      ;;
    --execution-payload-hash)
      [ "$#" -ge 2 ] || usage
      EXECUTION_PAYLOAD_HASH="$2"
      shift 2
      ;;
    --resume-task-id)
      [ "$#" -ge 2 ] || usage
      RESUME_TASK_ID="$2"
      shift 2
      ;;
    *)
      usage
      ;;
  esac
done

[ -n "$API_KEY" ] || {
  jq -n '{status:"error", error:"MANUS_API_KEY not set and --api-key not provided"}'
  exit 1
}
[ -n "$NONCE" ] || usage
[ -n "$EXECUTION_PAYLOAD_HASH" ] || usage

STARTED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
START_EPOCH=$(date +%s)
task_id=""
resumed_from_task_id=""
if [ -n "$RESUME_TASK_ID" ]; then
  task_id="$RESUME_TASK_ID"
  resumed_from_task_id="$RESUME_TASK_ID"
else
  prompt_with_nonce="${PROMPT}\n\n[audit_ref:${NONCE}]"
  create_payload="$(jq -n \
    --arg prompt "$prompt_with_nonce" \
    --arg model "$MODEL" \
    'if $model == "" then {prompt:$prompt, createShareableLink:true} else {prompt:$prompt, model:$model, createShareableLink:true} end')"

  create_resp="$(curl -sS -f -X POST "${BASE_URL%/}/v1/tasks" \
    -H "API_KEY: ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d "$create_payload" || true)"

  task_id="$(printf '%s' "$create_resp" | jq -r '.task_id // .id // empty' 2>/dev/null || true)"
  if [ -z "$task_id" ]; then
    jq -n --arg raw "$create_resp" '{status:"error", error_code:"DISPATCH_CREATE_FAILED", error:"failed to create manus task", raw_response:$raw}'
    exit 1
  fi
fi

elapsed=0
poll_interval=10
final_resp=""
while [ "$elapsed" -lt "$TIMEOUT" ]; do
  status_resp="$(curl -sS -f "${BASE_URL%/}/v1/tasks/${task_id}" \
    -H "API_KEY: ${API_KEY}" || true)"
  task_status="$(printf '%s' "$status_resp" | jq -r '.status // empty' 2>/dev/null || true)"

  case "$task_status" in
    completed|done)
      final_resp="$status_resp"
      break
      ;;
    error|failed)
      final_resp="$status_resp"
      break
      ;;
  esac

  if [ "$elapsed" -ge 120 ]; then
    poll_interval=30
  fi
  sleep "$poll_interval"
  elapsed=$((elapsed + poll_interval))
done

COMPLETED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
END_EPOCH=$(date +%s)
EXECUTION_DURATION_SECONDS=$((END_EPOCH - START_EPOCH))
if [ -z "$final_resp" ]; then
  jq -n --arg task_id "$task_id" '{status:"error", error_code:"DISPATCH_TIMEOUT", error:"task timed out", run_id:$task_id, task_id:$task_id}'
  exit 1
fi

RAW_TRACE="$final_resp"
RAW_TRACE_HASH="$(sha256_hex "$RAW_TRACE")"
TASK_STATUS="$(printf '%s' "$final_resp" | jq -r '.status // "unknown"' 2>/dev/null || echo "unknown")"
OUTPUT_TEXT="$(printf '%s' "$final_resp" | jq -r '.output // .result // .message // ""' 2>/dev/null || echo "")"
CREDIT_USAGE="$(printf '%s' "$final_resp" | jq -r '.credit_usage // .credits_used // 0' 2>/dev/null || echo 0)"
TASK_URL="$(printf '%s' "$final_resp" | jq -r '.metadata.task_url // .task_url // ""' 2>/dev/null || echo "")"
SHARE_URL="$(printf '%s' "$final_resp" | jq -r '.share_url // .metadata.share_url // ""' 2>/dev/null || echo "")"
MODEL_USED="$(printf '%s' "$final_resp" | jq -r '.model // .metadata.model // ""' 2>/dev/null || echo "")"
INSTRUCTIONS="$(printf '%s' "$final_resp" | jq -r '.instructions // .prompt // ""' 2>/dev/null || echo "")"
CREATED_TS="$(printf '%s' "$final_resp" | jq -r '.created_at // 0' 2>/dev/null || echo 0)"
UPDATED_TS="$(printf '%s' "$final_resp" | jq -r '.updated_at // 0' 2>/dev/null || echo 0)"

if [ "$TASK_STATUS" = "completed" ] || [ "$TASK_STATUS" = "done" ]; then
  STATUS="success"
else
  STATUS="error"
fi

if [ "$STATUS" = "success" ] && [ -z "$SHARE_URL" ]; then
  enable_resp="$(curl -sS -f -X PUT "${BASE_URL%/}/v1/tasks/${task_id}" \
    -H "API_KEY: ${API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{"enableShared":true}' 2>/dev/null || true)"
  if [ -n "$enable_resp" ]; then
    SHARE_URL="$(printf '%s' "$enable_resp" | jq -r '.share_url // .metadata.share_url // ""' 2>/dev/null || echo "")"
  fi
fi

if [ "$STATUS" = "success" ] && [ -z "$SHARE_URL" ]; then
  jq -n --arg task_id "$task_id" '{status:"error", error_code:"MISSING_SHARE_URL", error:"task completed but share_url is empty; buyer cannot view results without Manus login", run_id:$task_id, task_id:$task_id}'
  exit 1
fi

jq -n \
  --arg status "$STATUS" \
  --arg error_code "$( [ "$STATUS" = "success" ] && echo '' || echo 'DISPATCH_TASK_FAILED' )" \
  --arg output "$OUTPUT_TEXT" \
  --arg run_id "$task_id" \
  --arg task_id "$task_id" \
  --arg resumed_from_task_id "$resumed_from_task_id" \
  --arg started_at "$STARTED_AT" \
  --arg completed_at "$COMPLETED_AT" \
  --arg nonce "$NONCE" \
  --arg eph "$EXECUTION_PAYLOAD_HASH" \
  --arg raw_trace "$RAW_TRACE" \
  --arg raw_trace_hash "$RAW_TRACE_HASH" \
  --arg task_status "$TASK_STATUS" \
  --arg task_url "$TASK_URL" \
  --arg model_used "$MODEL_USED" \
  --arg instructions "$INSTRUCTIONS" \
  --argjson credit_usage "$CREDIT_USAGE" \
  --argjson created_ts "$CREATED_TS" \
  --argjson updated_ts "$UPDATED_TS" \
  --argjson execution_duration_seconds "$EXECUTION_DURATION_SECONDS" \
  --arg share_url "$SHARE_URL" \
  '{
    status: $status,
    error_code: (if $error_code == "" then null else $error_code end),
    output: $output,
    share_url: $share_url,
    run_id: $run_id,
    task_id: $task_id,
    resumed_from_task_id: (if $resumed_from_task_id == "" then null else $resumed_from_task_id end),
    started_at: $started_at,
    completed_at: $completed_at,
    process_evidence: {
      schema_version: "1.0",
      provider: "manus",
      tool: "manus_api",
      run_id: $run_id,
      nonce_echo: $nonce,
      execution_payload_hash: $eph,
      raw_trace: $raw_trace,
      raw_trace_format: "json",
      raw_trace_hash: $raw_trace_hash,
      provider_evidence: {
        api_credit_usage: $credit_usage,
        task_url: $task_url,
        share_url: $share_url,
        resumed_from_task_id: (if $resumed_from_task_id == "" then null else $resumed_from_task_id end),
        model: $model_used,
        instructions: $instructions,
        api_created_at: $created_ts,
        api_updated_at: $updated_ts,
        execution_duration_seconds: $execution_duration_seconds,
        task_status: $task_status
      }
    }
  }'
