#!/usr/bin/env bash
# script to initialize a new Tick-Driven Project
set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <ProjectName>"
    exit 1
fi

PROJECT_NAME=$1
TARGET_DIR=$(pwd)/projects/$PROJECT_NAME

echo "🚀 Initializing Agent Memento Framework for: $PROJECT_NAME"

# Create project scaffolding
mkdir -p "$TARGET_DIR"/{docs,src,tests}

# Generate MASTER_PLAN.md template
cat << 'PLAN' > "$TARGET_DIR/docs/MASTER_PLAN.md"
# Project Master Plan: $PROJECT_NAME

> Write exactly ONE grand objective here. Ensure tickets are extremely granular. Never rewrite files entirely.

## Phase 1: Foundation
- [ ] Task 1.1: Setup initial file structure and basic package files.
- [ ] Task 1.2: Establish unit test baseline (e.g. \`npm test\` or \`pytest\`).

## Phase 2: Core Architecture
- [ ] Task 2.1: ...

*Remember: A Tick Agent reads this top-to-bottom. It will only execute the FIRST un-checked [ ] task it finds.*
PLAN

# Generate TICK_STATUS
cat << 'STATUS' > "$TARGET_DIR/TICK_STATUS.md"
# Tick Status Log
Agent will dump blocker logs and checkpoint validations here if it fails to flip a `[ ]` to `[x]`.
STATUS

# Generate the Engine Script
ENGINE_SCRIPT="$(pwd)/scripts/${PROJECT_NAME}_tick.sh"
cat << ENGINE > "$ENGINE_SCRIPT"
#!/usr/bin/env bash
set -euo pipefail

# Auto-Generated Tick Engine for $PROJECT_NAME
WORKSPACE_DIR="\$(cd "\$(dirname "\$0")/.." && pwd)"
TARGET_DIR="\$WORKSPACE_DIR/projects/$PROJECT_NAME"
PLAN_FILE="\$TARGET_DIR/docs/MASTER_PLAN.md"
TICK_LOG="\$WORKSPACE_DIR/logs/${PROJECT_NAME}_tick.log"

echo "[\$(date -u +%Y-%m-%dT%H:%M:%SZ)] Waking up tick worker for $PROJECT_NAME..." >> "\$TICK_LOG"

openclaw agent --agent main -m "
You are the autonomous Tick Worker for $PROJECT_NAME.
1. Read \$PLAN_FILE.
2. Scan sequentially from top to bottom and find the VERY FIRST task marked with '[ ]'.
3. Focus 100% of your effort on solving this single issue.
4. **CRITICAL**: Do NOT rewrite entire files. Use precise tools (sed, jq, surgical python AST edits) to avoid Context Overflow/OOM.
5. **VERIFY**: You MUST run a test (e.g., node script, curl, puppeteer) and prove functionality. Never flip '[ ]' to '[x]' without hard console evidence.
6. If blocked indefinitely, log the issue to \$TARGET_DIR/TICK_STATUS.md and wait for human intervention. Do not silently ghost.
" >> "\$TICK_LOG" 2>&1
ENGINE

chmod +x "$ENGINE_SCRIPT"

echo "✅ Project '$PROJECT_NAME' scaffolded successfully at $TARGET_DIR."
echo "✅ Engineering plan injected: $TARGET_DIR/docs/MASTER_PLAN.md"
echo "✅ Tick Engine erected at: $ENGINE_SCRIPT"
echo "💡 To begin autonomous execution, run or hook cron to: $ENGINE_SCRIPT"
