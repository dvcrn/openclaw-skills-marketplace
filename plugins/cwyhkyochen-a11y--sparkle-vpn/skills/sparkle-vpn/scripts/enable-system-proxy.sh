#!/bin/bash
# Set system proxy to use Sparkle VPN

PROXY_HOST="127.0.0.1"
PROXY_PORT="7890"

echo "🔧 正在设置系统代理..."

# Check if running in a desktop environment
if command -v gsettings &> /dev/null; then
    # GNOME/GTK based desktop
    gsettings set org.gnome.system.proxy mode 'manual' 2>/dev/null || true
    gsettings set org.gnome.system.proxy.http host "$PROXY_HOST" 2>/dev/null || true
    gsettings set org.gnome.system.proxy.http port "$PROXY_PORT" 2>/dev/null || true
    gsettings set org.gnome.system.proxy.https host "$PROXY_HOST" 2>/dev/null || true
    gsettings set org.gnome.system.proxy.https port "$PROXY_PORT" 2>/dev/null || true
    gsettings set org.gnome.system.proxy.ftp host "$PROXY_HOST" 2>/dev/null || true
    gsettings set org.gnome.system.proxy.ftp port "$PROXY_PORT" 2>/dev/null || true
    gsettings set org.gnome.system.proxy.socks host "$PROXY_HOST" 2>/dev/null || true
    gsettings set org.gnome.system.proxy.socks port "$PROXY_PORT" 2>/dev/null || true
    echo "✅ GNOME 系统代理已设置: $PROXY_HOST:$PROXY_PORT"
fi

# Set environment variables for current session (optional)
export http_proxy="http://$PROXY_HOST:$PROXY_PORT"
export https_proxy="http://$PROXY_HOST:$PROXY_PORT"
export HTTP_PROXY="http://$PROXY_HOST:$PROXY_PORT"
export HTTPS_PROXY="http://$PROXY_HOST:$PROXY_PORT"

# Create/update proxy environment file for persistence
mkdir -p ~/.config/sparkle
cat > ~/.config/sparkle/proxy.env << EOF
# Sparkle VPN Proxy Settings
export http_proxy=http://$PROXY_HOST:$PROXY_PORT
export https_proxy=http://$PROXY_HOST:$PROXY_PORT
export HTTP_PROXY=http://$PROXY_HOST:$PROXY_PORT
export HTTPS_PROXY=http://$PROXY_HOST:$PROXY_PORT
export no_proxy=localhost,127.0.0.1,::1
EOF

echo ""
echo "📝 环境变量已保存到: ~/.config/sparkle/proxy.env"
echo ""
echo "💡 如需在当前终端使用代理，运行:"
echo "   source ~/.config/sparkle/proxy.env"
echo ""

# Test connection
IP=$(curl -s --max-time 5 https://ipinfo.io/ip 2>/dev/null || echo "unknown")
echo "🌐 当前出口 IP: $IP"
