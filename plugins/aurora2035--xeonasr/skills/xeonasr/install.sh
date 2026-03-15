#!/bin/bash

# Xeon ASR Skill 环境准备脚本（setup_env.sh）
# 支持 Ubuntu/Debian/CentOS/RHEL/AlibabaCloud/Rocky/AlmaLinux
# 默认使用 Miniconda（预编译 Python 3.10，无需编译）

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# 参数解析
MODEL_PATH=""
FORCE=0
SKIP_DEPS=0

usage() {
    cat << EOF
Xeon ASR Skill 环境准备脚本

用法: $0 [选项]

选项:
  --model-path PATH    指定 Qwen3-ASR 模型绝对路径（强烈建议）
  --force              强制重新生成虚拟环境
  --skip-deps          跳过系统依赖安装
  -h, --help           显示此帮助

示例:
  $0 --model-path /root/models/Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO
  $0 --force --model-path /opt/models/asr
EOF
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --model-path) MODEL_PATH="$2"; shift 2 ;;
        --force) FORCE=1; shift ;;
        --skip-deps) SKIP_DEPS=1; shift ;;
        -h|--help) usage ;;
        *) log_error "未知参数: $1"; usage ;;
    esac
done

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SKILL_DIR"

echo "========================================"
echo "  Xeon ASR Skill 环境准备"
echo "========================================"
echo ""

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
    if [ "$EUID" -eq 0 ]; then
        SUDO=""
    elif command -v sudo &> /dev/null; then
        SUDO="sudo"
    else
        log_warn "没有 sudo 权限，且不是 root 用户"
        SUDO=""
    fi
}

install_system_deps() {
    if [ "$SKIP_DEPS" -eq 1 ]; then
        log_info "跳过系统依赖安装"
        return 0
    fi

    check_sudo

    case $OS in
        ubuntu|debian)
            install_deps_debian
            ;;
        centos|rhel|fedora|rocky|almalinux|ol|alibabacloud|alios)
            install_deps_redhat
            ;;
        *)
            log_warn "未知系统 $OS，继续尝试 Miniconda 安装"
            ;;
    esac
}

install_deps_debian() {
    log_step "安装系统依赖 (Debian/Ubuntu)..."
    $SUDO apt-get update -qq
    $SUDO apt-get install -y -qq wget curl git lsof net-tools unzip bzip2 ca-certificates || \
    $SUDO apt-get install -y wget curl git lsof net-tools unzip bzip2 ca-certificates
}

install_deps_redhat() {
    log_step "安装系统依赖 (RHEL/CentOS/AlibabaCloud)..."
    
    if command -v dnf &> /dev/null; then
        PKG_MGR="dnf"
        $SUDO dnf install -y -q epel-release 2>/dev/null || true
    else
        PKG_MGR="yum"
        $SUDO yum install -y -q epel-release 2>/dev/null || true
    fi
    
    # Alibaba Cloud 3 特殊处理
    if [[ "$OS" == "alibabacloud" ]] || [[ "$OS" == "alios" ]]; then
        log_info "检测到 Alibaba Cloud，安装额外依赖..."
        $SUDO $PKG_MGR install -y -q openssl11 openssl11-devel 2>/dev/null || true
    fi
    
    $SUDO $PKG_MGR install -y -q wget curl git lsof net-tools unzip bzip2 ca-certificates \
        which || \
    $SUDO $PKG_MGR install -y wget curl git lsof net-tools unzip bzip2 ca-certificates \
        which
}

# 使用 Miniconda 安装 Python 3.10（无需编译，100%成功）
setup_miniconda() {
    log_step "使用 Miniconda 部署 Python 3.10..."
    
    local CONDA_DIR="$HOME/miniconda3"
    local CONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-py310_23.11.0-2-Linux-x86_64.sh"
    
    if [ -d "$CONDA_DIR" ] && [ "$FORCE" -eq 0 ]; then
        log_info "Miniconda 已存在，跳过安装"
    else
        if [ "$FORCE" -eq 1 ] && [ -d "$CONDA_DIR" ]; then
            log_info "强制模式：删除旧 Miniconda"
            rm -rf "$CONDA_DIR"
        fi
        
        log_info "下载 Miniconda..."
        if ! wget --timeout=120 -q "$CONDA_URL" -O /tmp/miniconda.sh; then
            log_error "下载 Miniconda 失败，尝试使用 curl..."
            if ! curl -fsSL --connect-timeout 120 "$CONDA_URL" -o /tmp/miniconda.sh; then
                log_error "下载 Miniconda 失败，请检查网络"
                exit 1
            fi
        fi
        
        log_info "安装 Miniconda（约 30 秒）..."
        bash /tmp/miniconda.sh -b -p "$CONDA_DIR" >/dev/null 2>&1 || {
            log_error "Miniconda 安装失败"
            rm -f /tmp/miniconda.sh
            exit 1
        }
        rm -f /tmp/miniconda.sh
        log_info "Miniconda 安装完成"
    fi
    
    # 设置路径
    export PATH="$CONDA_DIR/bin:$PATH"
    
    # 初始化 conda（用于当前 shell）
    if [ -f "$CONDA_DIR/etc/profile.d/conda.sh" ]; then
        source "$CONDA_DIR/etc/profile.d/conda.sh" 2>/dev/null || true
    fi
    
    # 验证
    if [ ! -f "$CONDA_DIR/bin/python" ]; then
        log_error "Miniconda 安装验证失败"
        exit 1
    fi
    
    local PY_VERSION=$("$CONDA_DIR/bin/python" --version 2>&1)
    log_info "Python 就绪: $PY_VERSION"
    
    PYTHON_CMD="$CONDA_DIR/bin/python"
}

setup_venv() {
    if [ "$FORCE" -eq 1 ] && [ -d "venv" ]; then
        log_info "强制模式：删除旧虚拟环境"
        rm -rf venv
    fi
    
    if [ ! -d "venv" ]; then
        log_step "创建 Python 虚拟环境..."
        "$PYTHON_CMD" -m venv venv || {
            log_error "创建虚拟环境失败"
            exit 1
        }
    fi
    
    source venv/bin/activate
    pip install -q --upgrade pip
    log_info "虚拟环境就绪"
}

install_python_packages() {
    log_step "安装 xdp-audio-service..."
    pip install -q xdp-audio-service || {
        log_error "安装 xdp-audio-service 失败"
        log_info "尝试不使用缓存重新安装..."
        pip install --no-cache-dir xdp-audio-service || {
            exit 1
        }
    }
    log_info "xdp-audio-service 安装完成"
}

generate_config() {
    if [ -f "audio_config.json" ] && [ "$FORCE" -ne 1 ]; then
        log_info "配置文件已存在，跳过生成（使用 --force 覆盖）"
        return 0
    fi
    
    log_step "生成 ASR 配置文件..."
    
    if command -v xdp-asr-init-config &> /dev/null; then
        xdp-asr-init-config --output ./audio_config.json || create_default_config
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
    log_info "已生成默认配置文件"
}

update_model_path() {
    if [ -z "$MODEL_PATH" ]; then
        log_warn "未指定 --model-path，请稍后手动修改 audio_config.json"
        return 0
    fi
    
    if [ ! -d "$MODEL_PATH" ]; then
        log_warn "模型目录不存在: $MODEL_PATH，请检查路径"
        return 0
    fi
    
    log_step "配置模型路径: $MODEL_PATH"
    
    python3 << PYEOF
import json
import sys

try:
    with open('./audio_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if 'qwen3_asr_ov' not in config:
        config['qwen3_asr_ov'] = {}
    
    config['qwen3_asr_ov']['model'] = '$MODEL_PATH'
    
    with open('./audio_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✓ 模型路径已更新")
except Exception as e:
    print(f"✗ 更新失败: {e}")
    sys.exit(1)
PYEOF
}

setup_openclaw() {
    local OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
    
    if [ ! -f "$OPENCLAW_CONFIG" ]; then
        log_warn "未找到 OpenClaw 配置，跳过"
        return 0
    fi
    
    log_step "配置 OpenClaw..."
    
    if ! python3 -c "
import json
with open('$OPENCLAW_CONFIG', 'r') as f:
    c = json.load(f)
exit(0 if 'channels' in c and 'qqbot' in c['channels'] else 1)
" 2>/dev/null; then
        log_warn "OpenClaw 未配置 qqbot，跳过 STT 配置"
        return 0
    fi
    
    cp "$OPENCLAW_CONFIG" "$OPENCLAW_CONFIG.bak.$(date +%Y%m%d%H%M%S)" 2>/dev/null || true
    
    python3 << PYEOF
import json
import sys

try:
    with open('$OPENCLAW_CONFIG', 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    if 'channels' not in config:
        config['channels'] = {}
    if 'qqbot' not in config['channels']:
        config['channels']['qqbot'] = {}
    
    config['channels']['qqbot']['stt'] = {
        "enabled": True,
        "provider": "custom",
        "baseUrl": "http://127.0.0.1:5001",
        "model": "Qwen3-ASR-0.6B-INT8_ASYM-OpenVINO",
        "apiKey": "not-needed"
    }
    
    with open('$OPENCLAW_CONFIG', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("✓ STT 配置已更新")
    print("  请启动服务后运行: openclaw gateway restart")
except Exception as e:
    print(f"✗ 配置失败: {e}")
PYEOF
}

ensure_scripts_executable() {
    if [ -f "$SKILL_DIR/start_asr.sh" ]; then
        chmod +x "$SKILL_DIR/start_asr.sh"
        log_info "start_asr.sh 已设为可执行"
    fi
    
    if [ -f "$SKILL_DIR/stop_asr.sh" ]; then
        chmod +x "$SKILL_DIR/stop_asr.sh"
        log_info "stop_asr.sh 已设为可执行"
    fi
}

show_completion() {
    echo ""
    echo "========================================"
    echo "  环境准备完成！"
    echo "========================================"
    echo ""
    
    if [ -z "$MODEL_PATH" ]; then
        echo -e "${YELLOW}⚠ 尚未配置模型路径${NC}"
        echo "请编辑配置文件："
        echo "  $SKILL_DIR/audio_config.json"
        echo "或重新运行："
        echo "  ./setup_env.sh --model-path /path/to/model"
        echo ""
    else
        echo -e "${GREEN}✓ 模型路径已配置${NC}"
    fi
    
    echo -e "${BLUE}【服务管理命令】${NC}"
    echo "  启动 Flask ASR:  ./start_asr.sh"
    echo "  停止 Flask ASR:  ./stop_asr.sh"
    echo "  查看状态:        ./stop_asr.sh status"
    echo ""
    echo "  日志文件:        tail -f $SKILL_DIR/asr.log"
    echo ""
    
    if command -v openclaw &> /dev/null; then
        echo -e "${BLUE}【OpenClaw 集成】${NC}"
        echo "  启动 Skill:      npm start"
        echo "  重启 Gateway:    openclaw gateway restart"
        echo ""
    fi
}

main() {
    install_system_deps
    setup_miniconda  # 直接使用 Miniconda，不再尝试 pyenv 或系统 Python
    setup_venv
    install_python_packages
    generate_config
    update_model_path
    setup_openclaw
    ensure_scripts_executable
    show_completion
}

main