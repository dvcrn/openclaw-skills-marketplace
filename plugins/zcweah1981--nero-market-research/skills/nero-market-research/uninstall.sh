#!/bin/bash

# Nero Market Research - 卸载脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 确认卸载
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              Nero Market Research - 卸载脚本               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

read -p "确定要卸载 Nero Market Research 吗？(y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消卸载"
    exit 0
fi

INSTALL_DIR="$HOME/.nero-market-research"

# 停止服务
print_info "停止系统..."
nero stop 2>/dev/null || true

# 禁用 systemd 服务
if command -v systemctl &> /dev/null; then
    print_info "禁用 systemd 服务..."
    systemctl --user stop nero-cycle.service 2>/dev/null || true
    systemctl --user disable nero-cycle.service 2>/dev/null || true
    rm -f ~/.config/systemd/user/nero-cycle.service
    systemctl --user daemon-reload
fi

# 删除全局命令
if [ -L "/usr/local/bin/nero" ]; then
    print_info "删除全局命令..."
    sudo rm -f /usr/local/bin/nero
fi

# 询问是否删除数据
read -p "是否删除所有数据（配置、日志、缓存）？(y/N) " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "删除所有数据..."
    rm -rf "$INSTALL_DIR"
    print_success "所有数据已删除"
else
    print_warning "保留数据目录: $INSTALL_DIR"
fi

# 完成
echo ""
print_success "✅ 卸载完成！"
echo ""
echo "感谢使用 Nero Market Research！"
echo ""
