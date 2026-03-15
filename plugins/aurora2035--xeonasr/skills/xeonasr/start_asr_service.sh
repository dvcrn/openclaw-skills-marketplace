#!/bin/bash
# start_asr.sh - 启动 Flask ASR 服务（后台运行）

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[CHECK]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PID_FILE="$SCRIPT_DIR/asr.pid"
LOG_FILE="$SCRIPT_DIR/asr.log"
CONFIG_FILE="$SCRIPT_DIR/audio_config.json"
VENV_DIR="$SCRIPT_DIR/venv"
PORT=5001

check_venv() {
    log_step "检测 Python 虚拟环境..."
    if [ ! -d "$VENV_DIR" ]; then
        log_error "虚拟环境不存在，请先运行: bash setup_env.sh"
        exit 1
    fi
    
    PY_VERSION=$("$VENV_DIR/bin/python" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
    log_info "Python 版本: $PY_VERSION"
}

check_xdp() {
    log_step "检测 xdp-audio-service..."
    
    # 优先检测 xdp-asr-service（你环境中的实际命令）
    if [ -f "$VENV_DIR/bin/xdp-asr-service" ]; then
        START_CMD="$VENV_DIR/bin/xdp-asr-service --config $CONFIG_FILE"
        log_info "发现启动命令: xdp-asr-service"
        return 0
    fi
    
    # 备选：检测 xdp-asr-server
    if [ -f "$VENV_DIR/bin/xdp-asr-server" ]; then
        START_CMD="$VENV_DIR/bin/xdp-asr-server --config $CONFIG_FILE"
        log_info "发现启动命令: xdp-asr-server"
        return 0
    fi
    
    log_error "未找到 xdp-asr-service 或 xdp-asr-server 命令"
    log_error "请确认 xdp-audio-service 是否正确安装"
    exit 1
}

check_config() {
    log_step "检测配置文件..."
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "配置文件不存在: $CONFIG_FILE"
        exit 1
    fi
    
    MODEL_PATH=$("$VENV_DIR/bin/python" -c "
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
print(config.get('qwen3_asr_ov', {}).get('model', ''))
" 2>/dev/null || echo "")
    
    if [ -z "$MODEL_PATH" ] || [ "$MODEL_PATH" == "None" ] || [[ "$MODEL_PATH" == "/path/to/"* ]]; then
        log_error "模型路径未配置，请编辑: $CONFIG_FILE"
        exit 1
    fi
    
    if [ ! -d "$MODEL_PATH" ]; then
        log_error "模型目录不存在: $MODEL_PATH"
        exit 1
    fi
    
    log_info "模型路径: $MODEL_PATH"
}

check_port() {
    log_step "检测端口 $PORT..."
    if command -v lsof &> /dev/null && lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_error "端口 $PORT 已被占用"
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            log_warn "已有服务在运行 (PID: $(cat "$PID_FILE"))"
            echo "如需重启，请先运行: ./stop_asr.sh"
        fi
        exit 1
    fi
    log_info "端口可用"
}

check_environment() {
    echo "========================================"
    echo "  ASR 服务环境检测"
    echo "========================================"
    check_venv
    check_xdp
    check_config
    check_port
    echo ""
    log_info "✓ 环境检测全部通过"
    echo ""
}

start_service() {
    echo "========================================"
    echo "  启动 ASR 服务"
    echo "========================================"
    
    # 检查是否已有实例
    if [ -f "$PID_FILE" ]; then
        OLD_PID=$(cat "$PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            log_error "服务已在运行中 (PID: $OLD_PID)"
            echo "如需重启，请先运行: ./stop_asr.sh"
            exit 1
        fi
        rm -f "$PID_FILE"
    fi
    
    log_info "启动命令: $START_CMD"
    log_info "日志文件: $LOG_FILE"
    
    nohup $START_CMD > "$LOG_FILE" 2>&1 &
    
    NEW_PID=$!
    echo $NEW_PID > "$PID_FILE"
    
    log_info "服务进程已启动 (PID: $NEW_PID)"
    sleep 2
    
    if ! kill -0 "$NEW_PID" 2>/dev/null; then
        log_error "服务启动失败，进程已退出"
        log_error "查看日志: tail -n 20 $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
    
    log_step "进行健康检查..."
    sleep 2
    
    if curl -s http://127.0.0.1:$PORT/health >/dev/null 2>&1 || \
       curl -s http://127.0.0.1:$PORT >/dev/null 2>&1; then
        echo ""
        log_info "✓ 服务启动成功！"
        log_info "  监听地址: http://127.0.0.1:$PORT"
        log_info "  进程 PID: $NEW_PID"
        echo "  日志查看: tail -f $LOG_FILE"
        echo ""
        echo "停止服务: ./stop_asr.sh"
    else
        log_warn "服务已启动但健康检查未通过（可能服务正在初始化）"
        log_info "  进程 PID: $NEW_PID"
        log_info "  请稍后检查: curl http://127.0.0.1:$PORT/health"
    fi
}

main() {
    check_environment
    start_service
}

main