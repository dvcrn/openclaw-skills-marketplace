#!/bin/bash

# QQ 音乐播放器启动脚本（安全版本 - 仅本地访问）
# 移除了 SSH 隧道和后台进程，适合上传到 ClawHub

set -e

SKILL_DIR="/projects/.openclaw/skills/qq-music-radio"
PLAYER_DIR="$SKILL_DIR/player"
LOG_FILE="/tmp/qq-music-radio.log"

echo "🎵 QQ 音乐播放器启动脚本（安全版本）"
echo "=========================="
echo ""

# 检查并安装依赖
echo "📦 检查依赖..."
if [ ! -d "$PLAYER_DIR/node_modules" ] || [ -z "$(ls -A $PLAYER_DIR/node_modules)" ]; then
    echo "   ⚠️ 依赖未安装，正在安装..."
    cd "$PLAYER_DIR"
    npm install --silent > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "   ✅ 依赖安装成功"
    else
        echo "   ❌ 依赖安装失败"
        exit 1
    fi
else
    echo "   ✅ 依赖已存在"
fi

echo ""

# 检查服务器状态
echo "🔍 检查服务器状态..."
if pgrep -f "node.*server-qqmusic.js" > /dev/null; then
    echo "   ✅ 服务器已在运行"
    SERVER_PID=$(pgrep -f "node.*server-qqmusic.js" | head -1)
    echo "   PID: $SERVER_PID"
else
    echo "   ⚠️ 服务器未运行，正在启动..."
    cd "$PLAYER_DIR"
    # 使用前台模式或简单后台
    node server-qqmusic.js > "$LOG_FILE" 2>&1 &
    SERVER_PID=$!
    echo "   ✅ 服务器已启动，PID: $SERVER_PID"
    
    # 等待服务器启动
    echo "   ⏳ 等待服务器启动..."
    for i in {1..10}; do
        sleep 1
        if curl -s http://localhost:3000/health > /dev/null 2>&1; then
            echo "   ✅ 服务器健康检查通过"
            break
        fi
        if [ $i -eq 10 ]; then
            echo "   ❌ 服务器启动超时"
            exit 1
        fi
    done
fi

echo ""
echo "=========================="
echo "✅ QQ 音乐播放器已启动（本地模式）"
echo ""
echo "📊 状态信息："
echo "   本地地址: http://localhost:3000"
echo "   服务器 PID: $SERVER_PID"
echo ""
echo "🌐 访问方式："
echo "   浏览器打开: http://localhost:3000"
echo ""
echo "📝 管理命令："
echo "   停止播放器: $SKILL_DIR/stop.sh"
echo "   查看日志: tail -f $LOG_FILE"
echo ""
echo "💡 提示："
echo "   - 此版本仅支持本地访问"
echo "   - 如需公网访问，请手动配置反向代理"
echo ""
