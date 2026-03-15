#!/usr/bin/env bash
# Estimate API cost for a prompt (text or file)
# Run from project root: bash examples/estimate_cost.sh [file_or_text] [model]

set -e
cd "$(dirname "$0")/.."

INPUT="${1:-Your prompt text here}"
MODEL="${2:-gpt-4}"

if [[ -f "$INPUT" ]]; then
  echo "Estimating cost for file: $INPUT"
  python -m scripts.cli -f "$INPUT" -m "$MODEL" -c
else
  echo "Estimating cost for text: \"$INPUT\""
  python -m scripts.cli -m "$MODEL" -c "$INPUT"
fi
