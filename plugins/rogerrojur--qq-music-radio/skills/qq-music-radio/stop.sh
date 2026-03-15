#!/bin/bash

# QQ 音乐播放器停止脚本

echo "🛑 停止 QQ 音乐播放器..."
echo "=========================="
echo ""

# 停止服务器
if pgrep -f "node.*server-qqmusic.js" > /dev/null; then
    SERVER_PIDS=$(pgrep -f "node.*server-qqmusic.js")
    echo "停止服务器..."
    for PID in $SERVER_PIDS; do
        echo "  停止 PID: $PID"
        kill $PID 2>/dev/null || true
    done
    sleep 1
    echo "✅ 服务器已停止"
else
    echo "⚠️ 服务器未运行"
fi

echo ""

# 停止隧道
if pgrep -f "ssh.*serveo.net" > /dev/null; then
    TUNNEL_PIDS=$(pgrep -f "ssh.*serveo.net")
    echo "停止隧道..."
    for PID in $TUNNEL_PIDS; do
        echo "  停止 PID: $PID"
        kill $PID 2>/dev/null || true
    done
    sleep 1
    echo "✅ 隧道已停止"
else
    echo "⚠️ 隧道未运行"
fi

echo ""

# 清理临时文件
rm -f /tmp/qq-music-radio-url.txt

echo "=========================="
echo "✅ QQ 音乐播放器已停止"
