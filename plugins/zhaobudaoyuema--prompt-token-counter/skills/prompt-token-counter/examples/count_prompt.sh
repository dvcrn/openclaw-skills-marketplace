#!/usr/bin/env bash
# Count tokens for a prompt using the CLI
# Run from project root: bash examples/count_prompt.sh [prompt] [model]

set -e
cd "$(dirname "$0")/.."

PROMPT="${1:-Hello, world!}"
MODEL="${2:-gpt-4}"

echo "Counting tokens for: \"$PROMPT\""
echo "Model: $MODEL"
echo "---"
python -m scripts.cli -m "$MODEL" "$PROMPT"
