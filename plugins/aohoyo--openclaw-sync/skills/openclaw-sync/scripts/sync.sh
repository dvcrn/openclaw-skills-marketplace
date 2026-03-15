#!/bin/bash

# OpenClaw 轻量同步脚本
# 基于 rclone，定时备份 workspace 到云端

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 工作目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE_DIR="/home/wwlhlf/.openclaw/workspace"
CONFIG_DIR="$SKILL_DIR/config"
LOGS_DIR="$SKILL_DIR/logs"

# 配置文件
SYNC_CONFIG="$CONFIG_DIR/sync-config.json"
SYNC_LIST="$CONFIG_DIR/sync-list.txt"
LOG_FILE="$LOGS_DIR/sync.log"
LAST_SYNC_FILE="$SKILL_DIR/.last-sync"

# 默认配置
DEFAULT_REMOTE=""
DEFAULT_BUCKET=""
DEFAULT_PREFIX="openclaw-backup"
DEFAULT_INTERVAL="5"

# 确保日志目录存在
mkdir -p "$LOGS_DIR"

# 记录日志
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# 加载配置
load_config() {
    if [ -f "$SYNC_CONFIG" ]; then
        REMOTE=$(python3 -c "import json; print(json.load(open('$SYNC_CONFIG')).get('remote', '$DEFAULT_REMOTE'))" 2>/dev/null || echo "$DEFAULT_REMOTE")
        BUCKET=$(python3 -c "import json; print(json.load(open('$SYNC_CONFIG')).get('bucket', '$DEFAULT_BUCKET'))" 2>/dev/null || echo "$DEFAULT_BUCKET")
        PREFIX=$(python3 -c "import json; print(json.load(open('$SYNC_CONFIG')).get('prefix', '$DEFAULT_PREFIX'))" 2>/dev/null || echo "$DEFAULT_PREFIX")
        SYNC_DELETE=$(python3 -c "import json; print(json.load(open('$SYNC_CONFIG')).get('syncDelete', 'false'))" 2>/dev/null || echo "false")
    else
        echo -e "${RED}错误: 配置文件不存在 $SYNC_CONFIG${NC}"
        echo "请先复制 config/sync-config.json.example 并编辑"
        exit 1
    fi

    # 检查必要配置
    if [ -z "$REMOTE" ] || [ -z "$BUCKET" ]; then
        echo -e "${RED}错误: 配置不完整，请设置 remote 和 bucket${NC}"
        exit 1
    fi
}

# 检查 rclone
check_rclone() {
    if ! command -v rclone &> /dev/null; then
        echo -e "${RED}错误: rclone 未安装${NC}"
        echo "安装方法:"
        echo "  curl https://rclone.org/install.sh | sudo bash"
        echo "  或: sudo apt-get install rclone"
        exit 1
    fi

    # 检查 remote 是否配置
    if ! rclone listremotes | grep -q "^${REMOTE}:$"; then
        echo -e "${RED}错误: rclone remote '$REMOTE' 未配置${NC}"
        echo "请先运行: rclone config"
        exit 1
    fi
}

# 检查是否有文件变化
has_changes() {
    if [ ! -f "$LAST_SYNC_FILE" ]; then
        return 0  # 首次同步
    fi

    # 检查是否有新文件或修改的文件
    if find "$WORKSPACE_DIR" -type f -newer "$LAST_SYNC_FILE" 2>/dev/null | grep -q .; then
        return 0  # 有变化
    fi

    return 1  # 无变化
}

# 执行同步
perform_sync() {
    local dry_run="${1:-}"
    local remote_path="$REMOTE:$BUCKET/$PREFIX"

    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] 开始同步...${NC}"
    log "INFO" "开始同步到 $remote_path"

    local rclone_args=""
    if [ "$SYNC_DELETE" != "true" ]; then
        rclone_args="$rclone_args --immutable"
    fi

    if [ "$dry_run" = "--dry-run" ]; then
        rclone_args="$rclone_args --dry-run"
        echo -e "${YELLOW}[模拟运行模式]${NC}"
    fi

    # 执行 rclone 同步
    if rclone sync "$WORKSPACE_DIR" "$remote_path" \
        --include-from "$SYNC_LIST" \
        --log-file "$LOG_FILE" \
        --log-level INFO \
        --stats-one-line \
        --stats 5s \
        $rclone_args; then

        touch "$LAST_SYNC_FILE"
        echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅ 同步完成${NC}"
        log "SUCCESS" "同步完成"
    else
        echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ 同步失败${NC}"
        log "ERROR" "同步失败"
        exit 1
    fi
}

# 主函数
main() {
    case "${1:-}" in
        --dry-run)
            load_config
            check_rclone
            perform_sync --dry-run
            ;;
        --force)
            load_config
            check_rclone
            perform_sync
            ;;
        *)
            load_config
            check_rclone

            if has_changes; then
                perform_sync
            else
                echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] 无变化，跳过同步${NC}"
                log "INFO" "无变化，跳过同步"
            fi
            ;;
    esac
}

main "$@"
