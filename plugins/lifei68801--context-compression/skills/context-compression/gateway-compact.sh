#!/bin/bash
# OpenClaw Gateway Compaction Helper
# NOTE: This script ONLY calls local Gateway API (localhost:18789)
# It does NOT make any external network requests

set -e

# 颜色定义
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# 默认值
OPENCLAW_DIR="${OPENCLAW_DIR:-$HOME/.openclaw}"
GATEWAY_PORT="${GATEWAY_PORT:-18789}"

# 打印帮助
print_help() {
    echo "OpenClaw 会话压缩工具"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -s, --session <id>  指定会话ID"
    echo "  -a, --aggressive    aggressive compaction"
    echo "  -d, --dry-run       仅模拟，不实际执行"
    echo "  -h, --help          显示帮助"
    echo ""
    echo "注意: 此脚本需要 OpenClaw Gateway 运行"
}

# 解析参数
SESSION_ID=""
AGGRESSIVE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--session)
            SESSION_ID="$2"
            shift 2
            ;;
        -a|--aggressive)
            AGGRESSIVE=true
            shift
            ;;
        -d|--dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            print_help
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            print_help
            exit 1
            ;;
    esac
done

# 检查 Gateway 是否运行
check_gateway() {
    if curl -s "http://localhost:$GATEWAY_PORT/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 获取 Gateway token
get_gateway_token() {
    local config_file="$OPENCLAW_DIR/openclaw.json"
    if [[ -f "$config_file" ]]; then
        grep -o '"token"[[:space:]]*:[[:space:]]*"[^"]*"' "$config_file" | grep -o '"[^"]*"$' | tr -d '"'
    fi
}

# 执行压缩
do_compact() {
    local session_id="$1"
    local token="$2"
    
    echo -e "${BLUE}正在压缩会话: ${session_id}${NC}"
    
    if $DRY_RUN; then
        echo -e "${YELLOW}[DRY RUN] 将执行压缩${NC}"
        return 0
    fi
    
    # 通过 API 触发压缩
    local response
    response=$(curl -s -X POST "http://localhost:$GATEWAY_PORT/api/session/compact" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d "{\"sessionKey\": \"$session_id\", \"aggressive\": $AGGRESSIVE}" \
        2>&1)
    
    if echo "$response" | grep -q "error"; then
        echo -e "${RED}❌ 压缩失败: $(echo "$response" | grep -o '"error"[^}]*' | head -1)${NC}"
        return 1
    else
        echo -e "${GREEN}✅ 压缩成功${NC}"
        return 0
    fi
}

# 生成摘要
generate_summary() {
    local session_id="$1"
    local sessions_dir="$OPENCLAW_DIR/agents/main/sessions"
    local session_file="$sessions_dir/${session_id}.jsonl"
    
    if [[ ! -f "$session_file" ]]; then
        echo -e "${YELLOW}⚠️ 会话文件不存在${NC}"
        return 1
    fi
    
    echo -e "${BLUE}生成会话摘要...${NC}"
    
    # 创建摘要目录
    local memory_dir="$OPENCLAW_DIR/workspace/memory/sessions/daily"
    mkdir -p "$memory_dir"
    
    local today=$(date +%Y-%m-%d)
    local summary_file="$memory_dir/session-${session_id}-${today}.md"
    
    if $DRY_RUN; then
        echo -e "${YELLOW}[DRY RUN] 将生成摘要: ${summary_file}${NC}"
        return 0
    fi
    
    # 生成摘要（简单版本，实际应由 AI 生成）
    cat > "$summary_file" << EOF
# 会话摘要 - ${today}

## 元信息
- Session: ${session_id}
- 生成时间: $(date '+%H:%M')
- 文件大小: $(du -h "$session_file" | cut -f1)

## 注意
此摘要由脚本自动生成，需要 AI 完善内容。

---
*完整会话: ${session_file}*
EOF
    
    echo -e "${GREEN}✅ 摘要已生成: ${summary_file}${NC}"
}

# 主逻辑
main() {
    echo -e "${BLUE}OpenClaw 会话压缩${NC}"
    echo ""
    
    # 检查 Gateway
    if ! check_gateway; then
        echo -e "${RED}❌ OpenClaw Gateway 未运行${NC}"
        echo "请先启动: openclaw gateway"
        exit 1
    fi
    
    # 获取 token
    local token=$(get_gateway_token)
    if [[ -z "$token" ]]; then
        echo -e "${YELLOW}⚠️ 未找到 Gateway token${NC}"
    fi
    
    # 检查会话
    if [[ -z "$SESSION_ID" ]]; then
        echo -e "${YELLOW}⚠️ 未指定会话ID${NC}"
        echo "使用 -s <session-id> 指定会话"
        exit 1
    fi
    
    # 显示模式
    if $AGGRESSIVE; then
        echo -e "${YELLOW}模式: 激进压缩${NC}"
    else
        echo -e "模式: 安全压缩"
    fi
    
    if $DRY_RUN; then
        echo -e "${YELLOW}模拟模式: 仅预览，不实际执行${NC}"
    fi
    
    echo ""
    
    # 执行压缩
    if [[ -n "$token" ]]; then
        do_compact "$SESSION_ID" "$token"
    else
        echo -e "${YELLOW}跳过压缩（无 token）${NC}"
    fi
    
    # 生成摘要
    if $AGGRESSIVE || $DRY_RUN; then
        generate_summary "$SESSION_ID"
    fi
    
    echo ""
    echo -e "${BLUE}完成${NC}"
}

main
