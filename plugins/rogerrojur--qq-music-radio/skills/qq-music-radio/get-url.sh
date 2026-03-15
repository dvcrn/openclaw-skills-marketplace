#!/bin/bash

# 获取 QQ 音乐播放器的公网访问地址

SERVEO_LOG="/tmp/serveo.log"
URL_FILE="/tmp/qq-music-radio-url.txt"

# 1. 尝试从缓存文件读取
if [ -f "$URL_FILE" ]; then
    URL=$(cat "$URL_FILE")
    if [ -n "$URL" ]; then
        echo "$URL"
        exit 0
    fi
fi

# 2. 从 serveo 日志中提取
if [ -f "$SERVEO_LOG" ]; then
    URL=$(grep -oP 'https://[a-zA-Z0-9-]+\.serveousercontent\.com' "$SERVEO_LOG" | tail -1)
    if [ -n "$URL" ]; then
        echo "$URL"
        echo "$URL" > "$URL_FILE"  # 缓存
        exit 0
    fi
fi

# 3. 都没有，返回本地地址
echo "http://localhost:3000"
