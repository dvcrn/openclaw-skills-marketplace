#!/bin/bash
# wx-article-fetcher 命令封装脚本
# 安全控制：权限 + 数据隔离

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="wx-article-fetcher"
ALLOWED_AGENT="蒜蓉"
ADMIN_AGENT="baseagent"

# 权限检查
check_permission() {
    local current_agent="${OPENCLAW_AGENT_NAME:-unknown}"
    
    # 允许 agent 管理者 (baseagent) 和授权 agent (蒜蓉) 使用
    if [[ "$current_agent" != "$ALLOWED_AGENT" && "$current_agent" != "$ADMIN_AGENT" ]]; then
        echo "❌ 权限拒绝：$SKILL_NAME 仅限 $ALLOWED_AGENT 使用"
        echo "   当前 agent: $current_agent"
        echo "   管理员：$ADMIN_AGENT"
        echo "   如需使用请联系张亮确认"
        exit 1
    fi
    
    echo "✅ 权限验证通过：$current_agent"
}

# 数据隔离检查 - 确保 agent 只能访问自己的工作空间
check_workspace_isolation() {
    local current_agent="${OPENCLAW_AGENT_NAME:-unknown}"
    local workspace="${OPENCLAW_WORKSPACE:-unknown}"
    
    # baseagent 可以访问所有数据
    if [[ "$current_agent" == "$ADMIN_AGENT" ]]; then
        echo "🔓 管理员模式：可访问全局数据"
        return 0
    fi
    
    # 其他 agent 只能访问自己的工作空间
    echo "🔒 隔离模式：工作空间 = $workspace"
    
    # 验证工作空间路径包含 agent 名称（防止路径穿越）
    if [[ ! "$workspace" *"$current_agent"* ]]; then
        echo "⚠️ 警告：工作空间路径不包含 agent 名称，可能存在安全风险"
    fi
}

# 检查签名
check_sign() {
    if [[ -z "$WX_QUERY_SIGN" ]]; then
        local sign_file="$HOME/.wx_biz_query/config.enc"
        if [[ ! -f "$sign_file" ]]; then
            echo "⚠️ 未找到签名配置，请先设置："
            echo "   export WX_QUERY_SIGN=\"your_sign_here\""
            echo "   或运行脚本交互式输入签名"
        fi
    fi
}

# 主命令
case "$1" in
    "wx-biz-query")
        check_permission
        check_workspace_isolation
        check_sign
        if [[ -z "$2" ]]; then
            echo "用法：wx-biz-query <公众号名称>"
            echo "示例：wx-biz-query 理财魔方"
            exit 1
        fi
        python3 "$SCRIPT_DIR/scripts/wx_biz_query.py" "$2"
        ;;
    
    "wx-articles-fetch")
        check_permission
        check_workspace_isolation
        check_sign
        if [[ -z "$2" ]]; then
            echo "用法：wx-articles-fetch <biz> [开始时间] [结束时间] [最大页数]"
            echo "示例：wx-articles-fetch MzU5MDkxMTI4Nw== 2025-01-01 2025-12-31"
            exit 1
        fi
        python3 "$SCRIPT_DIR/scripts/wx_article_fetcher.py" "$2" "$3" "$4" "$5"
        ;;
    
    "wx-biz-list")
        check_permission
        python3 "$SCRIPT_DIR/scripts/wx_biz_query.py" --list
        ;;
    
    "wx-biz-clear")
        check_permission
        python3 "$SCRIPT_DIR/scripts/wx_biz_query.py" --clear
        ;;
    
    "wx-biz-export")
        check_permission
        python3 "$SCRIPT_DIR/scripts/wx_biz_query.py" --export "$2"
        ;;
    
    *)
        echo "📱 $SKILL_NAME - 微信公众号文章抓取工具"
        echo ""
        echo "用法:"
        echo "  wx-biz-query <公众号名称>     - 查询公众号 biz"
        echo "  wx-articles-fetch <biz> [...] - 抓取公众号文章"
        echo "  wx-biz-list                   - 查看缓存的公众号"
        echo "  wx-biz-clear                  - 清空缓存"
        echo "  wx-biz-export [文件]          - 导出缓存"
        echo ""
        echo "示例:"
        echo "  wx-biz-query 理财魔方"
        echo "  wx-articles-fetch MzU5MDkxMTI4Nw== 2025-01-01 2025-12-31"
        ;;
esac
