#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

pass() { printf "[PASS] %s\n" "$1"; }
fail() { printf "[FAIL] %s\n" "$1"; exit 1; }

# 1) Preflight dry-run of a safe command
SKILL_DRY_RUN=true SKILL_REQUIRE_CONFIRM=false ./runner.sh gpu status --json && pass "dry-run status"

# 2) Deny injection
if ./runner.sh gpu status --json \; rm -rf / ; then
  fail "injection not blocked"
else
  pass "injection blocked"
fi

# 3) Doctor runs
if OUT=$(./runner.sh gpu doctor --json 2>&1); then
  pass "doctor ran (dry-run by default)"
else
  echo "$OUT"
  fail "doctor failed"
fi

echo "All self-tests completed."

