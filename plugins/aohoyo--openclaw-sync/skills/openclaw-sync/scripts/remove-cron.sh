#!/bin/bash

# OpenClaw 同步 - 移除定时任务

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 创建临时 crontab
crontab -l 2>/dev/null > /tmp/current_crontab || true

# 移除 openclaw-sync 任务
grep -v "openclaw-sync" /tmp/current_crontab > /tmp/new_crontab || true

# 安装新 crontab
crontab /tmp/new_crontab
rm -f /tmp/current_crontab /tmp/new_crontab

echo -e "${GREEN}✅ 定时任务已移除${NC}"
echo ""
echo "查看确认: crontab -l"
