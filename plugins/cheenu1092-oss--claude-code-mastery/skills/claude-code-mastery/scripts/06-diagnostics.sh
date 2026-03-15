#!/bin/bash
# 06-diagnostics.sh
# Health check and diagnostics for Claude Code setup

# Timeout function for commands that might hang
# Works on both macOS and Linux
run_with_timeout() {
    local timeout_secs=$1
    shift
    local cmd="$@"
    
    # Try gtimeout (macOS with coreutils), then timeout (Linux), then fallback
    if command -v gtimeout &>/dev/null; then
        gtimeout "$timeout_secs" $cmd 2>/dev/null
    elif command -v timeout &>/dev/null; then
        timeout "$timeout_secs" $cmd 2>/dev/null
    else
        # Fallback: run in background with kill
        $cmd &
        local pid=$!
        local count=0
        while kill -0 $pid 2>/dev/null && [ $count -lt $timeout_secs ]; do
            sleep 1
            count=$((count + 1))
        done
        if kill -0 $pid 2>/dev/null; then
            kill -9 $pid 2>/dev/null
            # Wait for killed process to prevent zombie - critical fix
            wait $pid 2>/dev/null
            return 124  # timeout exit code
        fi
        wait $pid 2>/dev/null
        return $?
    fi
}

echo "🔍 Claude Code Diagnostics"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Generated: $(date)"
echo ""

# System Info
echo "📦 SYSTEM"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "OS:        $(uname -s) $(uname -r)"
echo "Arch:      $(uname -m)"
echo "Shell:     $SHELL"
echo "User:      $USER"
echo "Home:      $HOME"
echo ""

# Claude Code
echo "📦 CLAUDE CODE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CLAUDE_BIN="$HOME/.local/bin/claude"

if [[ -f "$CLAUDE_BIN" ]]; then
    echo "Status:    ✅ Installed"
    echo "Version:   $($CLAUDE_BIN --version 2>/dev/null || echo 'unknown')"
    echo "Location:  $CLAUDE_BIN"
    
    # Check if in PATH
    if command -v claude &> /dev/null; then
        echo "PATH:      ✅ In PATH"
    else
        echo "PATH:      ⚠️  Not in PATH"
    fi
    
    # Auth status (with timeout to prevent hangs)
    AUTH_CHECK=$(run_with_timeout 5 $CLAUDE_BIN auth status 2>&1)
    AUTH_EXIT=$?
    if [ $AUTH_EXIT -eq 124 ]; then
        echo "Auth:      ⚠️  Check timed out (run 'claude auth status' manually)"
    elif [ $AUTH_EXIT -eq 0 ] && echo "$AUTH_CHECK" | grep -qi "authenticated\|logged in\|valid"; then
        echo "Auth:      ✅ Authenticated"
    else
        echo "Auth:      ❌ Not authenticated or unknown status"
    fi
else
    echo "Status:    ❌ Not installed"
fi
echo ""

# Config directories
echo "📦 CONFIGURATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "User config:    ~/.claude/"
if [[ -d "$HOME/.claude" ]]; then
    echo "  Status:       ✅ Exists"
    echo "  Settings:     $(test -f "$HOME/.claude/settings.json" && echo '✅' || echo '❌') settings.json"
    echo "  Agents:       $(ls -1 "$HOME/.claude/agents" 2>/dev/null | wc -l | tr -d ' ') subagents"
else
    echo "  Status:       ❌ Not found"
fi

echo ""
echo "Project config: .claude/"
if [[ -d ".claude" ]]; then
    echo "  Status:       ✅ Exists (in current dir)"
    echo "  Settings:     $(test -f ".claude/settings.json" && echo '✅' || echo '❌') settings.json"
    echo "  Agents:       $(ls -1 ".claude/agents" 2>/dev/null | wc -l | tr -d ' ') subagents"
else
    echo "  Status:       ℹ️  Not found in current directory"
fi

echo ""
echo "CLAUDE.md:      $(test -f "CLAUDE.md" && echo '✅ Found' || echo '❌ Not found in current dir')"
echo ""

# Subagents
echo "📦 SUBAGENTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
AGENTS_DIR="$HOME/.claude/agents"
if [[ -d "$AGENTS_DIR" ]]; then
    echo "Location:  $AGENTS_DIR"
    echo "Count:     $(ls -1 "$AGENTS_DIR"/*.md 2>/dev/null | wc -l | tr -d ' ')"
    echo ""
    echo "Installed agents:"
    for f in "$AGENTS_DIR"/*.md; do
        if [[ -f "$f" ]]; then
            name=$(grep -m1 "^name:" "$f" | sed 's/name: *//' | tr -d '\r')
            model=$(grep -m1 "^model:" "$f" | sed 's/model: *//' | tr -d '\r')
            echo "  - $name ($model)"
        fi
    done
else
    echo "Status:    ❌ No agents directory"
fi
echo ""

# Claude-mem
echo "📦 CLAUDE-MEM (Optional)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PLUGIN_DIR="$HOME/.claude/plugins/marketplaces/thedotmack"

if [[ -d "$PLUGIN_DIR" ]]; then
    echo "Status:    ✅ Installed"
    echo "Location:  $PLUGIN_DIR"
    
    # Check worker
    cd "$PLUGIN_DIR" 2>/dev/null
    if command -v bun &>/dev/null; then
        WORKER_STATUS=$(bun plugin/scripts/worker-service.cjs status 2>&1 || echo "error")
        if echo "$WORKER_STATUS" | grep -q "running"; then
            echo "Worker:    ✅ Running"
            PID=$(echo "$WORKER_STATUS" | grep -o "PID: [0-9]*" | cut -d' ' -f2)
            PORT=$(echo "$WORKER_STATUS" | grep -o "Port: [0-9]*" | cut -d' ' -f2)
            echo "  PID:     $PID"
            echo "  Port:    $PORT"
            echo "  Web UI:  http://localhost:$PORT"
        else
            echo "Worker:    ❌ Not running"
        fi
    else
        echo "Worker:    ⚠️  Cannot check (bun not installed)"
    fi
    
    # Check database
    if [[ -f "$HOME/.claude-mem/claude-mem.db" ]]; then
        DB_SIZE=$(ls -lh "$HOME/.claude-mem/claude-mem.db" | awk '{print $5}')
        echo "Database:  ✅ $DB_SIZE"
    else
        echo "Database:  ❌ Not found"
    fi
else
    echo "Status:    ℹ️  Not installed (optional)"
fi
echo ""

# Dependencies
echo "📦 DEPENDENCIES"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Node.js:   $(node --version 2>/dev/null || echo '❌ Not installed')"
echo "Bun:       $(bun --version 2>/dev/null || echo '❌ Not installed')"
echo "Git:       $(git --version 2>/dev/null | cut -d' ' -f3 || echo '❌ Not installed')"
echo "curl:      $(curl --version 2>/dev/null | head -1 | cut -d' ' -f2 || echo '❌ Not installed')"
echo ""

# Recent sessions
echo "📦 RECENT ACTIVITY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PROJECTS_DIR="$HOME/.claude/projects"
if [[ -d "$PROJECTS_DIR" ]]; then
    echo "Projects directory: $PROJECTS_DIR"
    RECENT=$(ls -1t "$PROJECTS_DIR" 2>/dev/null | head -5)
    if [[ -n "$RECENT" ]]; then
        echo "Recent projects:"
        echo "$RECENT" | while read proj; do
            echo "  - $proj"
        done
    else
        echo "No recent projects"
    fi
else
    echo "No projects directory yet"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 HEALTH SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ISSUES=0

if [[ ! -f "$CLAUDE_BIN" ]]; then
    echo "❌ Claude Code not installed"
    ISSUES=$((ISSUES + 1))
fi

if ! command -v claude &>/dev/null && [[ -f "$CLAUDE_BIN" ]]; then
    echo "⚠️  Claude Code not in PATH"
fi

if [[ ! -d "$HOME/.claude/agents" ]] || [[ $(ls -1 "$HOME/.claude/agents"/*.md 2>/dev/null | wc -l) -eq 0 ]]; then
    echo "⚠️  No subagents installed"
fi

if [[ $ISSUES -eq 0 ]]; then
    echo "✅ All systems operational!"
else
    echo ""
    echo "Run setup scripts to fix issues."
fi
