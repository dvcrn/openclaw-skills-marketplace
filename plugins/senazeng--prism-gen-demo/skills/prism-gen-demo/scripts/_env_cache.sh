#!/bin/bash
# PRISM_GEN_DEMO 环境缓存机制
# 避免重复的环境检查和安装

ENV_CACHE_FILE="/tmp/prism_demo_env_cache.txt"
ENV_CACHE_TIMEOUT=300  # 5分钟缓存

# 检查缓存是否有效
check_env_cache() {
    if [[ -f "$ENV_CACHE_FILE" ]]; then
        local cache_time=$(stat -c %Y "$ENV_CACHE_FILE" 2>/dev/null || stat -f %m "$ENV_CACHE_FILE")
        local current_time=$(date +%s)
        local age=$((current_time - cache_time))
        
        if [[ $age -lt $ENV_CACHE_TIMEOUT ]]; then
            return 0  # 缓存有效
        fi
    fi
    return 1  # 缓存无效或不存在
}

# 创建缓存
create_env_cache() {
    echo "ENV_CHECKED=true" > "$ENV_CACHE_FILE"
    echo "TIMESTAMP=$(date +%s)" >> "$ENV_CACHE_FILE"
    echo "PYTHON_PATH=$(which python3)" >> "$ENV_CACHE_FILE"
}

# 清除缓存
clear_env_cache() {
    rm -f "$ENV_CACHE_FILE"
}

# 快速环境检查（使用缓存）
quick_env_check() {
    if check_env_cache; then
        return 0
    fi
    
    # 运行完整环境检查
    source "$(dirname "$0")/env_setup.sh"
    activate_env
    
    # 创建缓存
    create_env_cache
}

# 导出函数
export -f check_env_cache
export -f create_env_cache
export -f clear_env_cache
export -f quick_env_check