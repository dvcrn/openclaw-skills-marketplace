#!/bin/bash
# Sparkle VPN Stop Script

SET_PROXY_MODE="$1"

echo "🛑 正在停止 Sparkle VPN..."

# Disable system proxy first
bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/disable-system-proxy.sh

echo ""

# Kill mihomo processes
pkill -f "mihomo.*19c48c94cbb" 2>/dev/null || true
pkill -x mihomo 2>/dev/null || true

# Also kill Sparkle GUI if running
pkill -x sparkle 2>/dev/null || true

sleep 1

# Verify stopped
if pgrep -x mihomo > /dev/null || pgrep -x sparkle > /dev/null; then
    echo "⚠️ 强制终止残留进程..."
    pkill -9 -x mihomo 2>/dev/null || true
    pkill -9 -x sparkle 2>/dev/null || true
fi

echo "✅ VPN 已停止"
echo ""

# Show current IP (should be original)
IP=$(curl -s --max-time 5 https://ipinfo.io/ip 2>/dev/null || echo "unknown")
echo "🌐 当前出口 IP: $IP"
