#!/bin/bash

# OpenClaw 同步 - 查看状态

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$SKILL_DIR/config/sync-config.json"
LOG_FILE="$SKILL_DIR/logs/sync.log"
LAST_SYNC_FILE="$SKILL_DIR/.last-sync"

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   OpenClaw 同步状态                      ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# 检查 rclone
if command -v rclone &> /dev/null; then
    echo -e "${GREEN}✓${NC} rclone 已安装: $(rclone version | head -1)"
else
    echo -e "${YELLOW}✗${NC} rclone 未安装"
fi
echo ""

# 显示配置
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${BLUE}配置信息：${NC}"
    python3 -c "
import json
with open('$CONFIG_FILE') as f:
    config = json.load(f)
    for k, v in config.items():
        print(f'  {k}: {v}')
" 2>/dev/null || cat "$CONFIG_FILE"
else
    echo -e "${YELLOW}配置文件不存在${NC}"
fi
echo ""

# 检查定时任务
echo -e "${BLUE}定时任务：${NC}"
if crontab -l 2>/dev/null | grep -q "openclaw-sync"; then
    echo -e "${GREEN}✓${NC} 已启用"
    crontab -l | grep "openclaw-sync" | sed 's/^/  /'
else
    echo -e "${YELLOW}✗${NC} 未启用"
fi
echo ""

# 上次同步时间
if [ -f "$LAST_SYNC_FILE" ]; then
    echo -e "${BLUE}上次同步：${NC} $(stat -c '%y' "$LAST_SYNC_FILE" 2>/dev/null | cut -d'.' -f1)"
else
    echo -e "${YELLOW}尚未同步${NC}"
fi
echo ""

# 最近日志
if [ -f "$LOG_FILE" ]; then
    echo -e "${BLUE}最近日志：${NC}"
    tail -10 "$LOG_FILE" | sed 's/^/  /'
else
    echo -e "${YELLOW}暂无日志${NC}"
fi
