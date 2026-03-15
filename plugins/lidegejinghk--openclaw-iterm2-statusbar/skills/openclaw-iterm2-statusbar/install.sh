#!/usr/bin/env bash
# OpenClaw iTerm2 Status Bar Installer
# Usage (local):  bash install.sh
# Usage (remote): curl -fsSL https://raw.githubusercontent.com/lidegejingHk/openclaw-iterm2-statusbar/main/install.sh | bash

set -e

SCRIPT_NAME="openclaw_status.py"
AUTOLAUNCH_DIR="$HOME/Library/Application Support/iTerm2/Scripts/AutoLaunch"
REMOTE_URL="https://raw.githubusercontent.com/lidegejingHk/openclaw-iterm2-statusbar/main/${SCRIPT_NAME}"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[✓]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✗]${NC} $*"; exit 1; }

echo "OpenClaw iTerm2 Status Bar Installer"
echo "======================================"

# 检查 macOS
[[ "$(uname)" == "Darwin" ]] || error "仅支持 macOS"

# 检查 iTerm2
if ! osascript -e 'id of app "iTerm2"' &>/dev/null 2>&1; then
  error "未检测到 iTerm2，请先安装: https://iterm2.com"
fi
info "检测到 iTerm2"

# 创建目录
mkdir -p "$AUTOLAUNCH_DIR"

# 获取脚本：优先本地，否则远程下载
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-/dev/null}")" 2>/dev/null && pwd || echo "")"
if [[ -n "$SCRIPT_DIR" && -f "$SCRIPT_DIR/$SCRIPT_NAME" ]]; then
  cp "$SCRIPT_DIR/$SCRIPT_NAME" "$AUTOLAUNCH_DIR/$SCRIPT_NAME"
  info "已安装（本地）→ $AUTOLAUNCH_DIR/$SCRIPT_NAME"
else
  warn "从远程下载..."
  curl -fsSL "$REMOTE_URL" -o "$AUTOLAUNCH_DIR/$SCRIPT_NAME" \
    || error "下载失败，请检查网络或手动下载"
  info "已安装（远程）→ $AUTOLAUNCH_DIR/$SCRIPT_NAME"
fi

chmod +x "$AUTOLAUNCH_DIR/$SCRIPT_NAME"

echo ""
echo -e "${GREEN}✅ 安装完成！${NC}"
echo ""
echo "后续步骤："
echo "  1. 重启 iTerm2（或 Scripts → Refresh）"
echo "  2. Preferences → Profiles → Session → Status Bar → Configure"
echo "  3. 拖入 'OpenClaw' 组件"
echo ""
warn "需要 OpenClaw Gateway 在本地运行（端口 18789）"
