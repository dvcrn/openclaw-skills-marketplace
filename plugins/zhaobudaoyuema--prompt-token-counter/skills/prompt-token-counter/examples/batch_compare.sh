#!/usr/bin/env bash
# Compare token counts across multiple models for the same text
# Run from project root: bash examples/batch_compare.sh [text] [model1] [model2] ...

set -e
cd "$(dirname "$0")/.."

TEXT="${1:-Compare tokenization across different models.}"
shift || true
MODELS=("${@:-gpt-4 claude-3-opus gemini-pro}")

echo "Text: \"$TEXT\""
echo "Models: ${MODELS[*]}"
echo "---"

for model in "${MODELS[@]}"; do
  result=$(python -m scripts.cli -m "$model" "$TEXT" 2>/dev/null | head -1)
  echo "$model: $result"
done
