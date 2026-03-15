#!/bin/bash

# OpenClaw语音技能套装 - 统一安装脚本
# 作者：米粒儿
# 版本：1.0.0
# 日期：2026-03-03

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        OpenClaw 语音技能套装 - 安装向导                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# 检测操作系统
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
echo -e "${BLUE}检测到操作系统: $OS${NC}"
echo ""

# 1. 安装系统依赖
echo -e "${YELLOW}[1/4] 安装系统依赖...${NC}"
if [[ "$OS" == "linux" ]]; then
    sudo apt update
    sudo apt install -y ffmpeg portaudio19-dev espeak python3-pip
elif [[ "$OS" == "macos" ]]; then
    brew install ffmpeg portaudio espeak
else
    echo -e "${RED}不支持的操作系统: $OS${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 系统依赖安装完成${NC}"
echo ""

# 2. 安装Python依赖
echo -e "${YELLOW}[2/4] 安装Python依赖...${NC}"
pip3 install --upgrade pip

# 核心依赖（所有技能共用）
pip3 install openai-whisper pyttsx3 pyaudio webrtcvad

# 可选：Porcupine唤醒词引擎（需要Access Key）
read -p "是否安装Porcupine唤醒词引擎？(需要免费Access Key) [y/N]: " install_porcupine
if [[ "$install_porcupine" =~ ^[Yy]$ ]]; then
    pip3 install pvporcupine
    echo -e "${BLUE}请访问 https://console.picovoice.ai/ 获取免费Access Key${NC}"
fi

echo -e "${GREEN}✓ Python依赖安装完成${NC}"
echo ""

# 3. 下载Whisper模型
echo -e "${YELLOW}[3/4] 下载Whisper Medium模型（769MB）...${NC}"
python3 -c "import whisper; whisper.load_model('medium')"
echo -e "${GREEN}✓ Whisper模型下载完成${NC}"
echo ""

# 4. 验证安装
echo -e "${YELLOW}[4/4] 验证安装...${NC}"
echo ""

# 检查ffmpeg
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓ ffmpeg 已安装${NC}"
else
    echo -e "${RED}✗ ffmpeg 未安装${NC}"
fi

# 检查Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓ Python 已安装: $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ Python 未安装${NC}"
fi

# 检查关键Python包
python3 -c "import whisper; print('✓ Whisper 已安装')" 2>/dev/null || echo -e "${RED}✗ Whisper 未安装${NC}"
python3 -c "import pyttsx3; print('✓ pyttsx3 已安装')" 2>/dev/null || echo -e "${RED}✗ pyttsx3 未安装${NC}"
python3 -c "import pyaudio; print('✓ PyAudio 已安装')" 2>/dev/null || echo -e "${RED}✗ PyAudio 未安装${NC}"
python3 -c "import webrtcvad; print('✓ WebRTC VAD 已安装')" 2>/dev/null || echo -e "${RED}✗ WebRTC VAD 未安装${NC}"
python3 -c "import pvporcupine; print('✓ Porcupine 已安装')" 2>/dev/null || echo -e "${YELLOW}○ Porcupine 未安装（可选）${NC}"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  安装完成！                                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "已安装技能："
echo "  1. voice-chat  - 语音对话（6种方言 + Medium模型）"
echo "  2. voice-wake  - 语音唤醒（5种唤醒词）"
echo "  3. talk-mode   - 持续对话模式（VAD检测）"
echo ""
echo "快速开始："
echo "  # 测试语音识别"
echo "  python3 ~/.openclaw/skills/voice-chat/scripts/test_recognition.py"
echo ""
echo "  # 测试语音唤醒"
echo "  python3 ~/.openclaw/skills/voice-wake/scripts/wake_test.py"
echo ""
echo "  # 启动持续对话"
echo "  python3 ~/.openclaw/skills/talk-mode/scripts/start_talk.py"
echo ""
echo "详细文档："
echo "  ~/.openclaw/skills/voice-chat/SKILL.md"
echo "  ~/.openclaw/skills/voice-wake/SKILL.md"
echo "  ~/.openclaw/skills/talk-mode/SKILL.md"
echo ""
