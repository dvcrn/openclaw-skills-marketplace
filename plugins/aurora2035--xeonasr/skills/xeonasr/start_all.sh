#!/bin/bash
# start_all.sh - 使用 setsid 双 fork，完全脱离终端

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

echo "========================================"
echo "  启动 Xeon ASR 服务（setsid 后台模式）"
echo "========================================"

# 安装 Node 依赖
[ ! -d "node_modules" ] && npm install

# ========== 启动 5001 (Flask) ==========
log_step "启动 Flask ASR (5001)..."
if ! lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    ./start_asr_service.sh
    sleep 2
fi
log_info "Flask 运行中 (PID: $(cat asr.pid 2>/dev/null || echo 'unknown'))"

# ========== 启动 9001 (Node) ==========
log_step "清理旧进程..."
pkill -f "node.*server.js" 2>/dev/null || true
sleep 2

log_step "启动 Node Skill (9001) 后台模式..."

# 关键：setsid + 重定向 stdin，完全脱离终端控制
(setsid node server.js >> skill.log 2>&1 </dev/null &)

sleep 3

# 获取 PID（通过端口反查，因为 setsid 后 $! 不准确）
PID_9001=$(lsof -Pi :9001 -sTCP:LISTEN -t 2>/dev/null | head -1 || echo "")

if [ -n "$PID_9001" ] && kill -0 "$PID_9001" 2>/dev/null; then
    echo $PID_9001 > skill.pid
    log_info "Node 启动成功 (PID: $PID_9001)"
else
    log_warn "未找到 9001 监听进程，检查日志..."
    tail -n 10 skill.log
    exit 1
fi

echo ""
echo "========================================"
echo "  ✓ 所有服务已后台启动"
echo "========================================"
echo ""
echo "验证命令（执行这些再关闭终端）:"
echo "  curl http://127.0.0.1:5001/health"
echo "  curl http://127.0.0.1:9001/health"
echo ""
echo "日志:"
echo "  tail -f asr.log"
echo "  tail -f skill.log"
echo ""
echo "停止命令: ./stop.sh"

# ========== 重启 OpenClaw Gateway ==========
echo ""
log_step "检查 OpenClaw Gateway..."

if command -v openclaw &> /dev/null; then
    # 检查服务是否健康再重启
    sleep 2
    if curl -s http://127.0.0.1:5001/health >/dev/null 2>&1 && \
       curl -s http://127.0.0.1:9001/health >/dev/null 2>&1; then
        log_info "ASR 服务健康，准备重启 Gateway..."
        openclaw gateway restart
        log_info "✓ Gateway 已重启，STT 配置已生效"
    else
        log_warn "ASR 服务未通过健康检查，跳过 Gateway 重启"
        log_warn "请手动检查服务状态后再重启: openclaw gateway restart"
    fi
else
    log_warn "未找到 openclaw 命令，跳过 Gateway 重启"
    log_warn "请手动重启: openclaw gateway restart"
fi

echo ""
echo "========================================"
echo "  部署完成！"
echo "========================================"
echo ""
echo "现在可以安全关闭 Terminal。"