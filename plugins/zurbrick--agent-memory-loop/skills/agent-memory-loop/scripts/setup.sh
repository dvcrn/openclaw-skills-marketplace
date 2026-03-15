#!/usr/bin/env bash
# setup.sh — Initialize agent-memory-loop in a workspace
# Usage: ./setup.sh [workspace_path]

set -uo pipefail

WORKSPACE="${1:-.}"
LEARNINGS_DIR="${WORKSPACE}/.learnings"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASSETS_DIR="${SCRIPT_DIR}/../assets"

echo "🧠 Setting up agent-memory-loop in: ${WORKSPACE}"

mkdir -p "${LEARNINGS_DIR}"
mkdir -p "${LEARNINGS_DIR}/archive"

for file in errors.md learnings.md wishes.md; do
  if [[ -f "${LEARNINGS_DIR}/${file}" ]]; then
    echo "  ⏭️  ${file} already exists — skipping"
  elif [[ -f "${ASSETS_DIR}/${file}" ]]; then
    cp "${ASSETS_DIR}/${file}" "${LEARNINGS_DIR}/${file}"
    echo "  ✅ Created ${file}"
  else
    touch "${LEARNINGS_DIR}/${file}"
    echo "  ✅ Created ${file} (empty)"
  fi
done

echo ""
echo "Done. Files at: ${LEARNINGS_DIR}/"
echo ""
echo "Next: add this to your agent's instructions (AGENTS.md, CLAUDE.md, etc.):"
echo ""
echo '  ## Self-Improvement'
echo '  Before major tasks: `grep -i "keyword" .learnings/*.md` for relevant past issues.'
echo '  After errors or corrections: log to `.learnings/` using the agent-memory-loop format.'
