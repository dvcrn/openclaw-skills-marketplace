#!/bin/bash

# QQ 音乐播放器启动脚本（安全版本）
# 支持本地访问和可选的公网隧道

set -e

# Skill 目录
SKILL_DIR="/projects/.openclaw/skills/qq-music-radio"
PLAYER_DIR="$SKILL_DIR/player"

# 先保存命令行传入的环境变量
CLI_ENABLE_TUNNEL="${ENABLE_TUNNEL:-}"
CLI_TUNNEL_SERVICE="${TUNNEL_SERVICE:-}"
CLI_LOG_FILE="${LOG_FILE:-}"
CLI_SERVEO_LOG="${SERVEO_LOG:-}"
CLI_SHOW_SECURITY_WARNING="${SHOW_SECURITY_WARNING:-}"

# 读取配置文件（如果存在）
if [ -f "$SKILL_DIR/.env" ]; then
    source "$SKILL_DIR/.env"
fi

# 命令行参数优先级最高
ENABLE_TUNNEL="${CLI_ENABLE_TUNNEL:-${ENABLE_TUNNEL:-false}}"  # 默认禁用公网隧道
TUNNEL_SERVICE="${CLI_TUNNEL_SERVICE:-${TUNNEL_SERVICE:-serveo.net}}"
LOG_FILE="${CLI_LOG_FILE:-${LOG_FILE:-/tmp/qq-music-radio.log}}"
SERVEO_LOG="${CLI_SERVEO_LOG:-${SERVEO_LOG:-/tmp/serveo.log}}"
SHOW_SECURITY_WARNING="${CLI_SHOW_SECURITY_WARNING:-${SHOW_SECURITY_WARNING:-true}}"

echo "🎵 QQ 音乐播放器启动脚本"
echo "=========================="
echo ""

# 安全提示
if [ "$ENABLE_TUNNEL" = "true" ] && [ "$SHOW_SECURITY_WARNING" = "true" ]; then
    echo "⚠️  安全提示："
    echo "   本脚本将创建公网隧道，使播放器可从互联网访问"
    echo "   隧道服务: $TUNNEL_SERVICE"
    echo "   如不需要公网访问，请设置: ENABLE_TUNNEL=false"
    echo "   或修改配置文件: $SKILL_DIR/.env"
    echo ""
fi

# 0. 检查并安装依赖
echo "0️⃣ 检查依赖..."
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

# 1. 检查服务器是否运行
echo "1️⃣ 检查服务器状态..."
if pgrep -f "node.*server-qqmusic.js" > /dev/null; then
    echo "   ✅ 服务器已在运行"
    SERVER_PID=$(pgrep -f "node.*server-qqmusic.js" | head -1)
    echo "   PID: $SERVER_PID"
else
    echo "   ⚠️ 服务器未运行，正在启动..."
    cd "$PLAYER_DIR"
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

# 2. 检查公网隧道（可选）
if [ "$ENABLE_TUNNEL" = "true" ]; then
    echo "2️⃣ 检查公网隧道..."
    if pgrep -f "ssh.*$TUNNEL_SERVICE" > /dev/null; then
        echo "   ✅ 隧道已存在"
        TUNNEL_PID=$(pgrep -f "ssh.*$TUNNEL_SERVICE" | head -1)
        echo "   PID: $TUNNEL_PID"
        
        # 尝试从日志中提取 URL
        if [ -f "$SERVEO_LOG" ]; then
            PUBLIC_URL=$(grep -oP 'https://[a-zA-Z0-9-]+\.serveousercontent\.com' "$SERVEO_LOG" | tail -1)
            if [ -n "$PUBLIC_URL" ]; then
                echo "   ✅ 公网地址: $PUBLIC_URL"
            fi
        fi
        
    else
        echo "   ⚠️ 隧道未运行，正在创建..."
        # 清空旧日志
        > "$SERVEO_LOG"
        
        # 创建隧道（使用更安全的选项）
        ssh -o StrictHostKeyChecking=no \
            -o ServerAliveInterval=60 \
            -o ExitOnForwardFailure=yes \
            -R 80:localhost:3000 \
            "$TUNNEL_SERVICE" > "$SERVEO_LOG" 2>&1 &
        TUNNEL_PID=$!
        echo "   ✅ 隧道已创建，PID: $TUNNEL_PID"
        
        # 等待隧道建立并提取 URL
        echo "   ⏳ 等待隧道建立..."
        for i in {1..15}; do
            sleep 1
            PUBLIC_URL=$(grep -oP 'https://[a-zA-Z0-9-]+\.serveousercontent\.com' "$SERVEO_LOG" | tail -1)
            if [ -n "$PUBLIC_URL" ]; then
                echo "   ✅ 公网地址: $PUBLIC_URL"
                break
            fi
            if [ $i -eq 15 ]; then
                echo "   ⚠️ 无法自动获取公网地址"
                echo "   请手动查看日志: tail -f $SERVEO_LOG"
            fi
        done
    fi
else
    echo "2️⃣ 公网隧道已禁用"
    echo "   如需启用，请运行: ENABLE_TUNNEL=true $0"
fi

echo ""
echo "=========================="
echo "✅ QQ 音乐播放器已就绪！"
echo ""
echo "📊 状态信息："
echo "   Skill 目录: $SKILL_DIR"
echo "   播放器目录: $PLAYER_DIR"
echo "   服务器 PID: ${SERVER_PID:-未知}"
if [ "$ENABLE_TUNNEL" = "true" ]; then
    echo "   隧道 PID: ${TUNNEL_PID:-未知}"
fi
echo "   本地地址: http://localhost:3000"
if [ -n "$PUBLIC_URL" ]; then
    echo "   公网地址: $PUBLIC_URL"
fi
echo ""
echo "🌐 访问方式："
echo "   本地: http://localhost:3000"
if [ "$ENABLE_TUNNEL" = "true" ]; then
    if [ -n "$PUBLIC_URL" ]; then
        echo "   公网: $PUBLIC_URL"
    else
        echo "   公网: 查看 $SERVEO_LOG"
    fi
else
    echo "   公网: 已禁用（设置 ENABLE_TUNNEL=true 启用）"
fi
echo ""
echo "📝 管理命令："
echo "   停止播放器: $SKILL_DIR/stop.sh"
echo "   查看日志: tail -f $LOG_FILE"
if [ "$ENABLE_TUNNEL" = "true" ]; then
    echo "   查看隧道日志: tail -f $SERVEO_LOG"
fi
echo ""
echo "🔒 安全说明："
echo "   - 本地服务器运行在 localhost:3000"
echo "   - 仅调用 QQ 音乐公开 API"
if [ "$ENABLE_TUNNEL" = "true" ]; then
    echo "   - 公网隧道使用 $TUNNEL_SERVICE"
    echo "   - 隧道仅转发 HTTP 流量到本地端口"
fi
echo ""

# 输出 URL 到文件，方便其他脚本读取
if [ -n "$PUBLIC_URL" ]; then
    echo "$PUBLIC_URL" > /tmp/qq-music-radio-url.txt
else
    echo "http://localhost:3000" > /tmp/qq-music-radio-url.txt
fi
