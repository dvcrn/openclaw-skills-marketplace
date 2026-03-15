#!/bin/bash
# dispatch-codex.sh - Dispatch a Codex task with automatic callback handling
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RUNNER="${SCRIPT_DIR}/runner.py"

# Show help
show_help() {
    cat <<EOF
Usage: dispatch-codex.sh [OPTIONS]

Dispatch a Codex task asynchronously with automatic callback on completion.

Required:
  -t, --task TEXT           Task prompt/payload
  -n, --name TEXT           Task name (for identification)

Optional:
  -w, --workspace PATH      Working directory (default: ~/projects)
  --agent-id NAME           Agent ID from openclaw config (default: codex)
  --model MODEL             Model override (e.g., openai-codex/gpt-5.2)
  --timeout SECONDS         Total task timeout (default: 3600)
  --operation-timeout SEC   Per-operation timeout (default: 300)
  --context-messages NUM    Context window size (default: 10)
  --priority [low|normal|high]  Task priority (default: normal)
  -c, --callback-channel NAME   Callback channel (telegram, webhook)
  -g, --callback-group ID       Callback target (e.g., Telegram group ID)
  --webhook-url URL         Webhook URL for callback
  --config PATH             Config file path
  --result-dir PATH         Result storage directory (default: /tmp/codex-results)
  --daemon-watch            Start watcher daemon after dispatch
  -h, --help                Show this help

Examples:
  dispatch-codex.sh -t "Fix CI" -n "ci-fix" -g "-100123" -c telegram
  dispatch-codex.sh -t "Refactor login" -n "login-refactor" -w ~/projects/auth

Callbacks:
  When task completes, notifications are sent via configured channels.

Monitor task:
  cat /tmp/codex-results/tasks/<task_id>/task-meta.json
  ls /tmp/codex-results/tasks/

EOF
}

# Defaults
TASK_NAME=""
PROMPT=""
WORKSPACE="${HOME}/projects"
AGENT_ID="codex"
MODEL=""
TIMEOUT=3600
OPERATION_TIMEOUT=300
CONTEXT_MESSAGES=10
PRIORITY="normal"
CALLBACK_CHANNELS=()
CALLBACK_GROUPS=()
WEBHOOK_URLS=()
CONFIG=""
DAEMON_WATCH=false
RESULT_DIR=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--task)
            PROMPT="$2"
            shift 2
            ;;
        -n|--name)
            TASK_NAME="$2"
            shift 2
            ;;
        -w|--workspace)
            WORKSPACE="$2"
            shift 2
            ;;
        --agent-id)
            AGENT_ID="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --operation-timeout)
            OPERATION_TIMEOUT="$2"
            shift 2
            ;;
        --context-messages)
            CONTEXT_MESSAGES="$2"
            shift 2
            ;;
        --priority)
            PRIORITY="$2"
            shift 2
            ;;
        -c|--callback-channel)
            CALLBACK_CHANNELS+=("$2")
            shift 2
            ;;
        -g|--callback-group)
            CALLBACK_GROUPS+=("$2")
            shift 2
            ;;
        --webhook-url)
            WEBHOOK_URLS+=("$2")
            shift 2
            ;;
        --config)
            CONFIG="$2"
            shift 2
            ;;
        --result-dir)
            RESULT_DIR="$2"
            shift 2
            ;;
        --daemon-watch)
            DAEMON_WATCH=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate required args
if [[ -z "$PROMPT" ]]; then
    echo "Error: --task is required"
    exit 1
fi
if [[ -z "$TASK_NAME" ]]; then
    echo "Error: --name is required"
    exit 1
fi

# Build runner command
RUNNER_CMD=(
    python3 "$RUNNER"
    -t "$PROMPT"
    -n "$TASK_NAME"
    -w "$WORKSPACE"
    --agent-id "$AGENT_ID"
    --timeout "$TIMEOUT"
    --operation-timeout "$OPERATION_TIMEOUT"
    --context-messages "$CONTEXT_MESSAGES"
    --priority "$PRIORITY"
)

# Optional args
if [[ -n "$MODEL" ]]; then
    RUNNER_CMD+=(--model "$MODEL")
fi
if [[ -n "$RESULT_DIR" ]]; then
    RUNNER_CMD+=(--result-dir "$RESULT_DIR")
fi
if [[ -n "$CONFIG" ]]; then
    RUNNER_CMD+=(--config "$CONFIG")
fi

# Execute runner and capture output
echo "🚀 Dispatching Codex task..."
if OUTPUT=$("${RUNNER_CMD[@]}" 2>&1); then
    echo "$OUTPUT"
    # Extract task_id from output
    TASK_ID=$(echo "$OUTPUT" | grep '^TASK_ID:' | cut -d: -f2 | tr -d ' ')
    if [[ -n "$TASK_ID" ]]; then
        echo "✅ Task dispatched successfully"
        echo "   Task ID: $TASK_ID"
        echo "   Monitor: codex-tasks status $TASK_ID"
        
        # Optionally start watcher daemon
        if [[ "$DAEMON_WATCH" == true ]]; then
            echo "Starting watcher daemon..."
            "${SCRIPT_DIR}/watcher.py" --daemon &
        fi
    else
        echo "⚠️ Task submitted but couldn't extract task_id"
    fi
else
    echo "❌ Failed to dispatch task"
    exit 1
fi
