#!/bin/bash

# OpenClaw 同步 - 安装定时任务

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
SYNC_SCRIPT="$SCRIPT_DIR/sync.sh"
CONFIG_FILE="$SKILL_DIR/config/sync-config.json"

# 检查配置
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}错误: 配置文件不存在${NC}"
    echo "请先编辑 config/sync-config.json"
    exit 1
fi

# 读取同步间隔
INTERVAL=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('interval', '5'))" 2>/dev/null || echo "5")

# 验证 rclone
if ! command -v rclone &> /dev/null; then
    echo -e "${YELLOW}警告: rclone 未安装${NC}"
    echo "请先安装: curl https://rclone.org/install.sh | sudo bash"
    exit 1
fi

echo -e "${BLUE}安装 OpenClaw 定时同步任务...${NC}"
echo "同步间隔: 每 $INTERVAL 分钟"
echo ""

# 生成 cron 表达式
CRON_EXPR="*/$INTERVAL * * * *"

# 创建临时 crontab
crontab -l 2>/dev/null > /tmp/current_crontab || true

# 移除旧的 openclaw-sync 任务
grep -v "openclaw-sync" /tmp/current_crontab > /tmp/new_crontab || true

# 添加新任务
echo "$CRON_EXPR $SYNC_SCRIPT >> $SKILL_DIR/logs/cron.log 2>&1 # openclaw-sync" >> /tmp/new_crontab

# 安装新 crontab
crontab /tmp/new_crontab
rm -f /tmp/current_crontab /tmp/new_crontab

echo -e "${GREEN}✅ 定时任务已安装${NC}"
echo ""
echo "查看任务: crontab -l"
echo "查看日志: tail -f $SKILL_DIR/logs/sync.log"
echo "手动同步: bash $SYNC_SCRIPT"
echo ""
echo -e "${YELLOW}提示: 首次运行建议先手动测试${NC}"
echo "  bash $SYNC_SCRIPT --dry-run"
