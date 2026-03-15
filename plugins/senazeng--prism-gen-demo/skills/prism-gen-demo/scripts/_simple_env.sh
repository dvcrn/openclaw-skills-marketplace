#!/bin/bash
# PRISM_GEN_DEMO 简化环境设置
# 避免重复的环境检查

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_CACHE_FILE="$PROJECT_DIR/.env_checked"

# 检查环境（带缓存）
check_environment() {
    # 如果缓存存在且小于5分钟，跳过检查
    if [[ -f "$ENV_CACHE_FILE" ]]; then
        local cache_age=$(($(date +%s) - $(stat -c %Y "$ENV_CACHE_FILE" 2>/dev/null || echo 0)))
        if [[ $cache_age -lt 300 ]]; then
            return 0
        fi
    fi
    
    # 运行环境检查
    if python3 "$SCRIPT_DIR/_check_env_simple.py" 2>/dev/null; then
        touch "$ENV_CACHE_FILE"
        return 0
    else
        # 环境不完整，但允许继续运行（用户可能只使用基础功能）
        touch "$ENV_CACHE_FILE"
        return 0
    fi
}

# 清除缓存
clear_env_cache() {
    rm -f "$ENV_CACHE_FILE"
    echo "环境缓存已清除"
}

# 导出函数
export -f check_environment
export -f clear_env_cache

# 如果直接调用，检查环境
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ "${1:-}" == "--clear" ]]; then
        clear_env_cache
    else
        check_environment
    fi
fi