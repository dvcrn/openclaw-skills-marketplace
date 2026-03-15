#!/bin/bash
# dispatch-claude-code.sh — Execute prompt via Claude Code and emit AgentWork process_evidence.
# Usage:
#   dispatch-claude-code.sh "<prompt>" --nonce <nonce> --execution-payload-hash <hash> [--model <model>] [--max-budget <usd>]
set -euo pipefail

usage() {
  cat <<'USAGE' >&2
Usage:
  dispatch-claude-code.sh "<prompt>" --nonce <nonce> --execution-payload-hash <hash> [--model <model>] [--max-budget <usd>]
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

MODEL="sonnet"
MAX_BUDGET="1.00"
CLAUDE_PERMISSION_MODE="${CLAUDE_PERMISSION_MODE:-}"
NONCE=""
EXECUTION_PAYLOAD_HASH=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --model)
      [ "$#" -ge 2 ] || usage
      MODEL="$2"
      shift 2
      ;;
    --max-budget)
      [ "$#" -ge 2 ] || usage
      MAX_BUDGET="$2"
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
    *)
      usage
      ;;
  esac
done

[ -n "$NONCE" ] || usage
[ -n "$EXECUTION_PAYLOAD_HASH" ] || usage

if ! command -v claude >/dev/null 2>&1; then
  jq -n '{status:"error", error:"claude CLI not found in PATH"}'
  exit 1
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT
stdout_file="$tmp_dir/claude.stdout.jsonl"
stderr_file="$tmp_dir/claude.stderr.log"

STARTED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
claude_cmd=(
  claude -p "$PROMPT"
  --output-format stream-json \
  --model "$MODEL" \
  --max-budget-usd "$MAX_BUDGET" \
  --no-session-persistence
)
if [ -n "$CLAUDE_PERMISSION_MODE" ]; then
  claude_cmd+=(--permission-mode "$CLAUDE_PERMISSION_MODE")
fi
if "${claude_cmd[@]}" >"$stdout_file" 2>"$stderr_file"; then
  EXIT_CODE=0
else
  EXIT_CODE=$?
fi
COMPLETED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

RAW_TRACE="$(cat "$stdout_file" 2>/dev/null || true)"
STDERR_TEXT="$(cat "$stderr_file" 2>/dev/null || true)"
RAW_TRACE_HASH="$(sha256_hex "$RAW_TRACE")"

SESSION_ID="$(jq -r '
  select(type=="object")
  | (.session_id // .result.session_id // empty)
' "$stdout_file" 2>/dev/null | head -n 1)"
if [ -z "$SESSION_ID" ]; then
  SESSION_ID="unknown-session"
fi

OUTPUT_TEXT="$(jq -r '
  select(type=="object")
  | (.result // .message // .text // empty)
  | strings
' "$stdout_file" 2>/dev/null | tail -n 1)"
if [ -z "$OUTPUT_TEXT" ]; then
  OUTPUT_TEXT=""
fi

TOTAL_COST_USD="$(jq -sr '
  [ .[] | select(type=="object") | (.total_cost_usd // empty) ] | last // 0
' "$stdout_file" 2>/dev/null || echo 0)"
NUM_TURNS="$(jq -sr '
  [ .[] | select(type=="object") | (.num_turns // empty) ] | last // 0
' "$stdout_file" 2>/dev/null || echo 0)"
DURATION_MS="$(jq -sr '
  [ .[] | select(type=="object") | (.duration_ms // empty) ] | last // 0
' "$stdout_file" 2>/dev/null || echo 0)"
DURATION_API_MS="$(jq -sr '
  [ .[] | select(type=="object") | (.duration_api_ms // empty) ] | last // 0
' "$stdout_file" 2>/dev/null || echo 0)"
IS_ERROR="$(jq -sr '
  [ .[] | select(type=="object") | (.is_error // empty) ] | last // false
' "$stdout_file" 2>/dev/null || echo false)"
SUBTYPE="$(jq -sr '
  [ .[] | select(type=="object") | (.subtype // empty) ] | last // "unknown"
' "$stdout_file" 2>/dev/null || echo "unknown")"

if [ "$EXIT_CODE" -eq 0 ] && [ "$IS_ERROR" != "true" ]; then
  STATUS="success"
else
  STATUS="error"
fi

jq -n \
  --arg status "$STATUS" \
  --arg output "$OUTPUT_TEXT" \
  --arg run_id "$SESSION_ID" \
  --arg started_at "$STARTED_AT" \
  --arg completed_at "$COMPLETED_AT" \
  --arg nonce "$NONCE" \
  --arg eph "$EXECUTION_PAYLOAD_HASH" \
  --arg raw_trace "$RAW_TRACE" \
  --arg raw_trace_hash "$RAW_TRACE_HASH" \
  --arg stderr_text "$STDERR_TEXT" \
  --arg subtype "$SUBTYPE" \
  --argjson total_cost_usd "$TOTAL_COST_USD" \
  --argjson num_turns "$NUM_TURNS" \
  --argjson duration_ms "$DURATION_MS" \
  --argjson duration_api_ms "$DURATION_API_MS" \
  --argjson is_error "$IS_ERROR" \
  --argjson exit_code "$EXIT_CODE" \
  '{
    status: $status,
    output: $output,
    run_id: $run_id,
    started_at: $started_at,
    completed_at: $completed_at,
    exit_code: $exit_code,
    stderr: $stderr_text,
    process_evidence: {
      schema_version: "1.0",
      provider: "anthropic",
      tool: "claude_code",
      run_id: $run_id,
      nonce_echo: $nonce,
      execution_payload_hash: $eph,
      raw_trace: $raw_trace,
      raw_trace_format: "jsonl",
      raw_trace_hash: $raw_trace_hash,
      provider_evidence: {
        total_cost_usd: $total_cost_usd,
        num_turns: $num_turns,
        duration_ms: $duration_ms,
        duration_api_ms: $duration_api_ms,
        subtype: $subtype,
        is_error: $is_error
      }
    }
  }'
