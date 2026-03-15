# Bootstrap — Initialize Test Structure for New Projects

Set up a 5-layer test framework for a project from scratch.

## Procedure

1. **Discover project structure**:
   ```bash
   find <project_root> -name "*.sh" -o -name "*.py" | head -30
   ls <project_root>/scripts/ 2>/dev/null
   ```

2. **Create test directory and file**:
   ```bash
   mkdir -p <project_root>/tests
   ```

3. **Generate test file skeleton**:

```bash
#!/bin/bash
# [Project Name] Test Suite
# Generated: YYYY-MM-DD

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SCRIPTS="${PROJECT_DIR}/scripts"
RESULTS=""
PASS=0
FAIL=0
SKIP=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

log_pass() { PASS=$((PASS+1)); RESULTS="${RESULTS}\n${GREEN}✅ PASS${NC}: $1"; }
log_fail() { FAIL=$((FAIL+1)); RESULTS="${RESULTS}\n${RED}❌ FAIL${NC}: $1 — $2"; }
log_skip() { SKIP=$((SKIP+1)); RESULTS="${RESULTS}\n${YELLOW}⏭️ SKIP${NC}: $1 — $2"; }

# macOS-compatible timeout
_timeout() {
  local secs="$1"; shift
  if command -v timeout >/dev/null 2>&1; then timeout "$secs" "$@"
  elif command -v gtimeout >/dev/null 2>&1; then gtimeout "$secs" "$@"
  else perl -e 'alarm shift @ARGV; exec @ARGV' "$secs" "$@"
  fi
}

echo "================================================"
echo "  [Project Name] Test Suite"
echo "  $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================"

# ============================================
# L1: Unit Tests
# ============================================
# [Generate one test per script file found]

# ============================================
# L2: Integration Tests  
# ============================================
# [Generate after L1 based on data flow between scripts]

# ============================================
# Summary
# ============================================
echo ""
echo -e "$RESULTS"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
printf "  ${GREEN}PASS: %d${NC}  ${RED}FAIL: %d${NC}  ${YELLOW}SKIP: %d${NC}  TOTAL: %d\n" \
  "$PASS" "$FAIL" "$SKIP" "$((PASS+FAIL+SKIP))"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

4. **Auto-generate L1 tests** for each script:
   - Parse `case` statements to find subcommands
   - Generate one test per subcommand (basic invocation + output check)
   - For scripts without subcommands, generate one invocation test

5. **Create L5-SPEC.md** (empty template):
   ```markdown
   # L5 User Scenario Specification
   
   ## Ambiguity Scan
   (Run gaps analysis to populate)
   
   ## Clarification Decisions
   (Record decisions here)
   
   ## Coverage Matrix
   (Updated after each gaps analysis)
   ```

6. **Run the generated tests** to verify framework works:
   ```bash
   bash <project_root>/tests/run-tests.sh
   ```
