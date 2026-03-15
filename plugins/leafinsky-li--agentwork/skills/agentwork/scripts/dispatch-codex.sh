#!/bin/bash
# dispatch-codex.sh — Execute prompt via Codex CLI and emit AgentWork process_evidence.
# Usage:
#   dispatch-codex.sh "<prompt>" --nonce <nonce> --execution-payload-hash <hash> [--model <model>]
# Output:
#   JSON { status, output, run_id, started_at, completed_at, exit_code, process_evidence, stderr }
set -euo pipefail

usage() {
  cat <<'USAGE' >&2
Usage:
  dispatch-codex.sh "<prompt>" --nonce <nonce> --execution-payload-hash <hash> [--model <model>]
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
if [ -z "${PROMPT}" ]; then
  usage
fi
shift

MODEL="o4-mini"
NONCE=""
EXECUTION_PAYLOAD_HASH=""

while [ "$#" -gt 0 ]; do
  case "$1" in
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
    *)
      usage
      ;;
  esac
done

[ -n "$NONCE" ] || usage
[ -n "$EXECUTION_PAYLOAD_HASH" ] || usage

if ! command -v codex >/dev/null 2>&1; then
  jq -n '{status:"error", error:"codex CLI not found in PATH"}'
  exit 1
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT
stdout_file="$tmp_dir/codex.stdout.jsonl"
stderr_file="$tmp_dir/codex.stderr.log"

STARTED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
START_EPOCH=$(date +%s)
if codex exec "$PROMPT" \
  --json --color never \
  --sandbox read-only \
  --skip-git-repo-check \
  --model "$MODEL" \
  >"$stdout_file" 2>"$stderr_file"; then
  EXIT_CODE=0
else
  EXIT_CODE=$?
fi
COMPLETED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
END_EPOCH=$(date +%s)
EXECUTION_DURATION_SECONDS=$((END_EPOCH - START_EPOCH))

RAW_TRACE="$(cat "$stdout_file" 2>/dev/null || true)"
STDERR_TEXT="$(cat "$stderr_file" 2>/dev/null || true)"
RAW_TRACE_HASH="$(sha256_hex "$RAW_TRACE")"

RUN_ID="$(jq -r '
  select(type=="object" and .type=="thread.started")
  | (.thread_id // .thread.id // empty)
' "$stdout_file" 2>/dev/null | head -n 1)"
if [ -z "$RUN_ID" ]; then
  RUN_ID="$(jq -r '
    select(type=="object")
    | (.thread_id // empty)
  ' "$stdout_file" 2>/dev/null | head -n 1)"
fi
if [ -z "$RUN_ID" ]; then
  RUN_ID="unknown-thread"
fi

INPUT_TOKENS="$(jq -s '
  [ .[] | select(type=="object" and .type=="turn.completed")
    | (.usage.input_tokens // .usage.input // 0) ] | add // 0
' "$stdout_file" 2>/dev/null || echo 0)"
OUTPUT_TOKENS="$(jq -s '
  [ .[] | select(type=="object" and .type=="turn.completed")
    | (.usage.output_tokens // .usage.output // 0) ] | add // 0
' "$stdout_file" 2>/dev/null || echo 0)"
CACHED_INPUT_TOKENS="$(jq -s '
  [ .[] | select(type=="object" and .type=="turn.completed")
    | (.usage.cached_input_tokens // .usage.cached_input // 0) ] | add // 0
' "$stdout_file" 2>/dev/null || echo 0)"
ACTION_TYPES_JSON="$(jq -sc '
  [ .[] | select(type=="object" and .type=="item.completed")
    | (.item.type // .item_type // .action_type // empty)
  ] | map(select(. != "")) | unique
' "$stdout_file" 2>/dev/null || echo '[]')"
EVENT_COUNT="$(jq -s 'length' "$stdout_file" 2>/dev/null || echo 0)"

OUTPUT_TEXT="$(jq -r '
  select(type=="object")
  | (.result // .output // .message // .text // .content // empty)
  | strings
' "$stdout_file" 2>/dev/null | tail -n 1)"
if [ -z "$OUTPUT_TEXT" ]; then
  OUTPUT_TEXT=""
fi

if [ "$EXIT_CODE" -eq 0 ]; then
  STATUS="success"
else
  STATUS="error"
fi

jq -n \
  --arg status "$STATUS" \
  --arg output "$OUTPUT_TEXT" \
  --arg run_id "$RUN_ID" \
  --arg started_at "$STARTED_AT" \
  --arg completed_at "$COMPLETED_AT" \
  --arg nonce "$NONCE" \
  --arg eph "$EXECUTION_PAYLOAD_HASH" \
  --arg raw_trace "$RAW_TRACE" \
  --arg raw_trace_hash "$RAW_TRACE_HASH" \
  --arg stderr_text "$STDERR_TEXT" \
  --argjson input_tokens "$INPUT_TOKENS" \
  --argjson output_tokens "$OUTPUT_TOKENS" \
  --argjson cached_input_tokens "$CACHED_INPUT_TOKENS" \
  --argjson action_types "$ACTION_TYPES_JSON" \
  --argjson event_count "$EVENT_COUNT" \
  --argjson execution_duration_seconds "$EXECUTION_DURATION_SECONDS" \
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
      provider: "openai",
      tool: "codex",
      run_id: $run_id,
      nonce_echo: $nonce,
      execution_payload_hash: $eph,
      raw_trace: $raw_trace,
      raw_trace_format: "jsonl",
      raw_trace_hash: $raw_trace_hash,
      provider_evidence: {
        input_tokens: $input_tokens,
        output_tokens: $output_tokens,
        cached_input_tokens: $cached_input_tokens,
        action_types: $action_types,
        event_count: $event_count,
        execution_duration_seconds: $execution_duration_seconds
      }
    }
  }'
