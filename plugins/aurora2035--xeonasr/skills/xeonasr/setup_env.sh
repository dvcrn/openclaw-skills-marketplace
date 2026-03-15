#!/bin/bash
# setup_env.sh - 环境准备脚本

set -euo pipefail

unset PYENV_ROOT 2>/dev/null || true
export PATH=$(echo "$PATH" | tr ':' '\n' | grep -v "pyenv\|\.pyenv" | tr '\n' ':' | sed 's/:$//')

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

MODEL_PATH=""
FORCE=0
SKIP_DEPS=0

usage() {
    cat << EOF
用法: $0 [--model-path PATH] [--force] [--skip-deps]
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --model-path) MODEL_PATH="$2"; shift 2 ;;
        --force) FORCE=1; shift ;;
        --skip-deps) SKIP_DEPS=1; shift ;;
        -h|--help) usage ;;
        *) log_error "未知参数: $1"; exit 1 ;;
    esac
done

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SKILL_DIR"

echo "========================================"
echo "  Xeon ASR Skill 环境准备"
echo "========================================"

detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ -f /etc/redhat-release ]; then
        echo "centos"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
log_info "检测到操作系统: $OS"

check_sudo() {
    if [ "$EUID" -eq 0 ]; then SUDO=""; elif command -v sudo &> /dev/null; then SUDO="sudo"; else SUDO=""; fi
}

install_system_deps() {
    [ "$SKIP_DEPS" -eq 1 ] && return 0
    check_sudo
    case $OS in
        ubuntu|debian)
            log_step "安装依赖 (Debian/Ubuntu)..."
            $SUDO apt-get update -qq >/dev/null 2>&1 || true
            $SUDO apt-get install -y wget curl git lsof net-tools unzip bzip2 ca-certificates >/dev/null 2>&1 || $SUDO apt-get install -y wget curl git lsof net-tools unzip bzip2 ca-certificates
            ;;
        centos|rhel|fedora|rocky|almalinux|ol|alibabacloud|alios)
            log_step "安装依赖 (RHEL/CentOS/AlibabaCloud)..."
            if command -v dnf &> /dev/null; then PKG_MGR="dnf"; else PKG_MGR="yum"; fi
            $SUDO $PKG_MGR install -y -q epel-release >/dev/null 2>&1 || true
            if [[ "$OS" == "alibabacloud" ]] || [[ "$OS" == "alios" ]]; then
                $SUDO $PKG_MGR install -y -q openssl11 openssl11-devel >/dev/null 2>&1 || true
            fi
            $SUDO $PKG_MGR install -y wget curl git lsof net-tools unzip bzip2 ca-certificates which >/dev/null 2>&1 || $SUDO $PKG_MGR install -y wget curl git lsof net-tools unzip bzip2 ca-certificates which
            ;;
    esac
}

setup_miniconda() {
    log_step "安装 Miniconda Python 3.10..."
    local CONDA_DIR="$HOME/miniconda3"
    local CONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-py310_23.11.0-2-Linux-x86_64.sh"
    
    if [ "$FORCE" -eq 1 ] && [ -d "$CONDA_DIR" ]; then
        log_info "强制模式：删除旧 Miniconda"
        rm -rf "$CONDA_DIR"
    fi
    
    if [ ! -d "$CONDA_DIR" ]; then
        log_info "下载 Miniconda..."
        if command -v wget &> /dev/null; then
            wget --timeout=120 -q --show-progress "$CONDA_URL" -O /tmp/miniconda.sh 2>/dev/null || curl -fSL --connect-timeout 120 --progress-bar "$CONDA_URL" -o /tmp/miniconda.sh
        else
            curl -fSL --connect-timeout 120 --progress-bar "$CONDA_URL" -o /tmp/miniconda.sh
        fi
        log_info "安装 Miniconda..."
        bash /tmp/miniconda.sh -b -p "$CONDA_DIR" >/dev/null 2>&1
        rm -f /tmp/miniconda.sh
    fi
    
    if [ ! -f "$CONDA_DIR/bin/python" ]; then
        log_error "Miniconda 安装失败"
        exit 1
    fi
    
    PYTHON_CMD="$CONDA_DIR/bin/python"
    log_info "Python 就绪: $($PYTHON_CMD --version 2>&1)"
}

setup_venv() {
    if [ "$FORCE" -eq 1 ] && [ -d "venv" ]; then
        log_info "强制模式：删除旧虚拟环境"
        rm -rf venv
    fi
    
    if [ ! -d "venv" ]; then
        log_step "创建虚拟环境..."
        "$PYTHON_CMD" -m venv venv || { log_error "创建虚拟环境失败"; exit 1; }
    fi
    
    source venv/bin/activate
    pip install -q --upgrade pip
}

install_python_packages() {
    log_step "安装 xdp-audio-service..."
    pip install -q --upgrade xdp-audio-service || pip install -q --upgrade --no-cache-dir xdp-audio-service
    log_info "xdp-audio-service 安装完成"
}

generate_config() {
    if [ -f "audio_config.json" ] && [ "$FORCE" -ne 1 ]; then
        log_info "audio_config.json 已存在，跳过生成"
        return 0
    fi
    
    log_step "生成 audio_config.json..."
    if [ -f "venv/bin/xdp-asr-init-config" ]; then
        ./venv/bin/xdp-asr-init-config --output ./audio_config.json || create_default_config
    else
        create_default_config
    fi
}

create_default_config() {
    cat > audio_config.json << 'EOF'
{
  "qwen3_asr_ov": {
    "model": "/path/to/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO",
    "device": "CPU",
    "sample_rate": 16000,
    "language": "zh",
    "max_tokens": 256
  },
  "server": {
    "host": "127.0.0.1",
    "port": 5001
  }
}
EOF
    log_info "已生成 audio_config.json"
}

update_model_path() {
    if [ -z "$MODEL_PATH" ]; then
        log_warn "未指定 --model-path，请稍后手动修改 audio_config.json"
        return 0
    fi
    
    if [ ! -d "$MODEL_PATH" ]; then
        log_warn "模型目录不存在: $MODEL_PATH"
        return 0
    fi
    
    log_step "配置模型路径: $MODEL_PATH"
    ./venv/bin/python << PYEOF
import json
try:
    with open('./audio_config.json', 'r') as f:
        config = json.load(f)
    if 'qwen3_asr_ov' not in config:
        config['qwen3_asr_ov'] = {}
    config['qwen3_asr_ov']['model'] = '$MODEL_PATH'
    with open('./audio_config.json', 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("✓ 模型路径已更新")
except Exception as e:
    print(f"✗ 失败: {e}")
    exit(1)
PYEOF
}

# ========== 新增：复制 config.example.json ==========
copy_node_config() {
    if [ -f "config.json" ] && [ "$FORCE" -ne 1 ]; then
        log_info "config.json 已存在，跳过复制"
        return 0
    fi
    
    if [ ! -f "config.example.json" ]; then
        log_warn "未找到 config.example.json，跳过复制"
        return 0
    fi
    
    log_step "复制 config.example.json 为 config.json..."
    
    # 复制并去除可能的空格问题
    cp config.example.json config.json
    
    # 修复 URL 中的空格（如果有的话）
    sed -i 's|http://127.0.0.1:5001/transcribe |http://127.0.0.1:5001/transcribe|g' config.json 2>/dev/null || true
    
    log_info "config.json 已生成"
}

install_node_deps() {
    if [ ! -f "package.json" ]; then
        log_warn "未找到 package.json，跳过 Node 依赖安装"
        return 0
    fi
    
    if [ -d "node_modules" ] && [ "$FORCE" -ne 1 ]; then
        log_info "node_modules 已存在，跳过 npm install"
        return 0
    fi
    
    if ! command -v npm &> /dev/null; then
        log_warn "未找到 npm，请手动安装 Node.js 后运行 npm install"
        return 0
    fi
    
    log_step "安装 Node.js 依赖..."
    npm install || {
        log_warn "npm install 失败，请检查网络或手动运行"
        return 0
    }
    log_info "Node.js 依赖安装完成"
}

setup_openclaw() {
    local OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
    
    if [ ! -f "$OPENCLAW_CONFIG" ]; then
        log_warn "未找到 OpenClaw 配置，跳过"
        return 0
    fi
    
    log_step "配置 OpenClaw STT (指向 9001 端口)..."
    
    if ! ./venv/bin/python -c "
import json
with open('$OPENCLAW_CONFIG', 'r') as f:
    c = json.load(f)
exit(0 if 'channels' in c and 'qqbot' in c['channels'] else 1)
" 2>/dev/null; then
        log_warn "OpenClaw 未配置 qqbot，跳过"
        return 0
    fi
    
    cp "$OPENCLAW_CONFIG" "$OPENCLAW_CONFIG.bak.$(date +%Y%m%d%H%M%S)" 2>/dev/null || true
    
    ./venv/bin/python << PYEOF
import json
try:
    with open('$OPENCLAW_CONFIG', 'r') as f:
        config = json.load(f)
    if 'channels' not in config:
        config['channels'] = {}
    if 'qqbot' not in config['channels']:
        config['channels']['qqbot'] = {}
    
    config['channels']['qqbot']['stt'] = {
        "enabled": True,
        "provider": "custom",
        "baseUrl": "http://127.0.0.1:9001",
        "model": "Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO",
        "apiKey": "not-needed"
    }
    
    with open('$OPENCLAW_CONFIG', 'w') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print("✓ OpenClaw STT 配置已更新（指向 9001 端口）")
except Exception as e:
    print(f"✗ 配置失败: {e}")
PYEOF
}

ensure_scripts_executable() {
    [ -f "$SKILL_DIR/start_all.sh" ] && chmod +x "$SKILL_DIR/start_all.sh"
    [ -f "$SKILL_DIR/start_asr_service.sh" ] && chmod +x "$SKILL_DIR/start_asr_service.sh"
    [ -f "$SKILL_DIR/stop_asr.sh" ] && chmod +x "$SKILL_DIR/stop_asr.sh"
}

show_completion() {
    echo ""
    echo "========================================"
    echo "  环境准备完成！"
    echo "========================================"
    echo ""
    
    if [ -z "$MODEL_PATH" ]; then
        echo -e "${YELLOW}⚠ 尚未配置模型路径${NC}"
        echo "编辑: $SKILL_DIR/audio_config.json"
        echo ""
    else
        echo -e "${GREEN}✓ 模型路径已配置${NC}"
    fi
    
    echo -e "${BLUE}【配置文件】${NC}"
    echo "  Python配置: audio_config.json"
    echo "  Node配置:   config.json (从 example 复制)"
    echo ""
    
    echo -e "${BLUE}【服务架构】${NC}"
    echo "  5001: Flask ASR (Python) - 模型推理"
    echo "  9001: ASR Skill (Node.js) - QQ 语音网关"
    echo ""
    echo -e "${BLUE}【启动步骤】${NC}"
    echo "  1. ./start_asr_service.sh   (启动 5001)"
    echo "  2. npm start        (启动 9001)"
    echo "  3. ./start_all.sh        (同时启动 5001 9001)"
    echo "" 
    echo -e "${BLUE}【管理命令】${NC}"
    echo "  停止 Flask: ./stop_asr.sh"
    echo "  查看日志:   tail -f $SKILL_DIR/asr.log"
    echo ""
    
    if command -v openclaw &> /dev/null; then
        echo -e "${BLUE}【OpenClaw】${NC}"
        echo "  重启 Gateway: openclaw gateway restart"
        echo ""
    fi
}

main() {
    install_system_deps
    setup_miniconda
    setup_venv
    install_python_packages
    generate_config
    update_model_path
    copy_node_config        # ← 新增：复制 Node 配置
    install_node_deps       # ← 新增：安装 Node 依赖
    setup_openclaw
    ensure_scripts_executable
    show_completion
}

main