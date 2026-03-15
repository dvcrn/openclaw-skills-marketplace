#!/bin/bash
# Sparkle VPN Start Script - Using Mihomo Core directly
# Usage: start-vpn.sh [--with-proxy]

set -e

WITH_PROXY=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --with-proxy)
            WITH_PROXY=true
            shift
            ;;
    esac
done

echo "🚀 正在启动 Sparkle VPN (Mihomo core)..."

# Check if already running
if pgrep -f "mihomo.*19c48c94cbb" > /dev/null; then
    echo "⚠️ VPN 已经在运行"
    if [ "$WITH_PROXY" = true ]; then
        echo ""
        bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/enable-system-proxy.sh
    fi
    exit 0
fi

# Kill any existing mihomo processes
pkill mihomo 2>/dev/null || true
sleep 1

# Start mihomo core directly with the DirectACCESS profile
nohup /opt/sparkle/resources/sidecar/mihomo \
    -f ~/.config/sparkle/profiles/19c48c94cbb.yaml \
    -d ~/.config/sparkle/ \
    > /tmp/mihomo.log 2>&1 &

sleep 2

# Verify it's running
if pgrep -f "mihomo.*19c48c94cbb" > /dev/null; then
    echo "✅ VPN 启动成功，代理端口: 7890"
    
    # Test connection
    export https_proxy=http://127.0.0.1:7890
    IP=$(curl -s --max-time 5 https://ipinfo.io/ip 2>/dev/null || echo "unknown")
    echo "🌐 代理 IP: $IP"
    
    # Enable system proxy if requested
    if [ "$WITH_PROXY" = true ]; then
        echo ""
        bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/enable-system-proxy.sh
    else
        echo ""
        echo "💡 系统代理未自动开启"
        echo "   如需开启系统代理，运行:"
        echo "   sparkle_vpn_start --with-proxy"
        echo "   或单独运行: sparkle_vpn_enable_proxy"
    fi
else
    echo "❌ 错误: VPN 启动失败"
    exit 1
fi
