#!/bin/bash
# stop.sh - 停止所有 ASR 服务

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

echo "========================================"
echo "  停止 Xeon ASR 服务"
echo "========================================"

# 停止 5001 (Flask)
if [ -f "asr.pid" ]; then
    PID=$(cat asr.pid)
    if kill -0 "$PID" 2>/dev/null; then
        log_info "停止 Flask (PID: $PID)..."
        kill "$PID" 2>/dev/null || kill -9 "$PID" 2>/dev/null || true
    fi
    rm -f asr.pid
fi

# 停止 9001 (Node) - 通过端口精确查找
PID_9001=$(lsof -Pi :9001 -sTCP:LISTEN -t 2>/dev/null | head -1 || true)
if [ -n "$PID_9001" ]; then
    log_info "停止 Node (PID: $PID_9001)..."
    kill "$PID_9001" 2>/dev/null || kill -9 "$PID_9001" 2>/dev/null || true
fi

# 清理残留
pkill -f "node.*server.js" 2>/dev/null || true

sleep 1
log_info "✓ 服务已停止"