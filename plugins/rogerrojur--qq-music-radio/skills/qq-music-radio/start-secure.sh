#!/bin/bash

# QQ 音乐播放器启动脚本（安全版 - 无隧道）
# 仅本地访问，无任何公网暴露功能

set -e

# Skill 目录
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLAYER_DIR="$SKILL_DIR/player"

# 配置（仅本地）
PORT="${PORT:-3000}"
LOG_FILE="${LOG_FILE:-/tmp/qq-music-radio.log}"

echo "🎵 QQ 音乐播放器 - 安全版"
echo "=========================="
echo ""
echo "✅ 本版本特性："
echo "   - 仅本地访问（localhost:$PORT）"
echo "   - 无 SSH 隧道功能"
echo "   - 无公网暴露"
echo "   - 安全透明"
echo ""

# 0. 检查并安装依赖
echo "0️⃣ 检查依赖..."
if [ ! -d "$PLAYER_DIR/node_modules" ] || [ -z "$(ls -A $PLAYER_DIR/node_modules 2>/dev/null)" ]; then
    echo "   ⚠️ 依赖未安装，正在安装..."
    echo "   将从 npm registry 下载以下包："
    echo "      - express@^4.18.2"
    echo "      - axios@^1.6.0"
    echo "      - cors@^2.8.5"
    echo "      - dotenv@^16.3.1"
    echo ""
    
    cd "$PLAYER_DIR"
    npm install --silent
    
    if [ $? -eq 0 ]; then
        echo "   ✅ 依赖安装成功"
    else
        echo "   ❌ 依赖安装失败，请检查网络连接"
        exit 1
    fi
else
    echo "   ✅ 依赖已安装"
fi

echo ""

# 1. 检查端口占用
echo "1️⃣ 检查端口..."
if command -v lsof >/dev/null 2>&1; then
    if lsof -i :$PORT >/dev/null 2>&1; then
        echo "   ⚠️ 端口 $PORT 已被占用"
        echo "   请使用: PORT=8080 ./start.sh 指定其他端口"
        exit 1
    fi
elif command -v netstat >/dev/null 2>&1; then
    if netstat -tuln | grep ":$PORT " >/dev/null 2>&1; then
        echo "   ⚠️ 端口 $PORT 已被占用"
        exit 1
    fi
fi
echo "   ✅ 端口 $PORT 可用"

echo ""

# 2. 启动服务器
echo "2️⃣ 启动服务器..."
cd "$PLAYER_DIR"

# 启动 Node.js 服务器（后台运行）
PORT=$PORT node server-qqmusic.js > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# 保存 PID
echo $SERVER_PID > /tmp/qq-music-radio.pid

# 等待启动
echo "   等待服务器启动..."
sleep 3

# 健康检查
if command -v curl >/dev/null 2>&1; then
    for i in {1..10}; do
        if curl -s http://localhost:$PORT/health >/dev/null 2>&1; then
            echo "   ✅ 服务器启动成功 (PID: $SERVER_PID)"
            break
        fi
        sleep 1
    done
else
    echo "   ⚠️ 未安装 curl，无法进行健康检查"
    echo "   服务器已启动 (PID: $SERVER_PID)"
fi

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║  🎵 QQ 音乐播放器已启动                            ║"
echo "╠════════════════════════════════════════════════════╣"
echo "║  ⚠️  仅本地访问（安全模式）                       ║"
echo "║                                                    ║"
echo "║  📍 本地地址:                                      ║"
echo "║     http://localhost:$PORT                          ║"
echo "║     http://127.0.0.1:$PORT                          ║"
echo "║                                                    ║"
echo "║  🔒 安全特性:                                      ║"
echo "║     ✅ 无公网访问                                  ║"
echo "║     ✅ 无 SSH 隧道                                 ║"
echo "║     ✅ 仅监听 localhost                            ║"
echo "║                                                    ║"
echo "║  📊 状态:                                          ║"
echo "║     进程 PID: $SERVER_PID                               ║"
echo "║     日志文件: $LOG_FILE                             ║"
echo "║                                                    ║"
echo "║  🛑 停止服务:                                      ║"
echo "║     ./stop.sh                                      ║"
echo "║                                                    ║"
echo "║  📋 查看日志:                                      ║"
echo "║     tail -f $LOG_FILE                               ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "在浏览器访问: http://localhost:$PORT"
echo ""
