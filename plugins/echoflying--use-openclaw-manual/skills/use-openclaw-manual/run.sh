#!/bin/bash
# use-openclaw-manual 技能 - 入口脚本
# 用法：clawhub skill run use-openclaw-manual --init|--search|--sync|--check|--help

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/scripts/sync-docs.sh"
SEARCH_SCRIPT="$SCRIPT_DIR/scripts/search-docs.sh"

show_help() {
  echo "📚 use-openclaw-manual - 基于文档的 OpenClaw 配置技能"
  echo ""
  echo "用法：clawhub skill run use-openclaw-manual [选项]"
  echo ""
  echo "选项:"
  echo "  --init          首次初始化（完整同步文档）"
  echo "  --sync          增量同步文档（仅更新变更文件）"
  echo "  --check         检查文档更新（不同步）"
  echo "  --search <词>   搜索文档（可指定类型和数量）"
  echo "  --list <目录>   列出目录内容"
  echo "  --read <文档>   阅读文档内容"
  echo "  --stats         显示文档统计"
  echo "  --help          显示帮助"
  echo ""
  echo "环境变量:"
  echo "  OPENCLAW_MANUAL_PATH   - 文档目录路径"
  echo "  LAST_COMMIT_FILE       - Baseline 文件路径"
  echo "  DOC_UPDATE_LOG         - 日志文件路径"
  echo "  DOC_NOTIFY_CHANNEL     - 通知渠道（默认：webchat）"
  echo ""
  echo "示例:"
  echo "  clawhub skill run use-openclaw-manual --init"
  echo "  clawhub skill run use-openclaw-manual --search binding"
  echo "  DOC_NOTIFY_CHANNEL=discord clawhub skill run use-openclaw-manual --sync"
  echo "  clawhub skill run use-openclaw-manual --stats"
  echo ""
}

# 检查是否提供了参数
if [ $# -eq 0 ]; then
  show_help
  exit 0
fi

case "$1" in
  --init)
    echo "🚀 初始化 use-openclaw-manual 技能..."
    echo ""
    "$SYNC_SCRIPT" --init
    ;;
  
  --sync)
    echo "🔄 同步文档更新..."
    echo ""
    "$SYNC_SCRIPT" --sync
    ;;
  
  --check)
    echo "🔍 检查文档更新..."
    echo ""
    "$SYNC_SCRIPT" --check
    ;;
  
  --search|-s)
    shift
    "$SEARCH_SCRIPT" --search "$@"
    ;;
  
  --list|-l)
    shift
    "$SEARCH_SCRIPT" --list "$@"
    ;;
  
  --read|-r)
    shift
    "$SEARCH_SCRIPT" --read "$@"
    ;;
  
  --stats)
    "$SEARCH_SCRIPT" --stats
    ;;
  
  --help|-h)
    show_help
    ;;
  
  *)
    echo "错误：未知选项 '$1'"
    echo ""
    show_help
    exit 1
    ;;
esac
