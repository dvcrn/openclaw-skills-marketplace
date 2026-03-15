#!/bin/bash
# 缓存管理器
# 创建时间：2026-03-12 18:22
# 创建者：小米粒
# 功能：缓存管理，提升性能

# ============================================
# 版权声明
# ============================================
# MIT License
# Copyright (c) 2026 米粒儿 (miliger)
# GitHub: https://github.com/zhaog100/openclaw-skills
# ClawHub: https://clawhub.com
# 
# 免费使用、修改和重新分发时需注明出处

# ============================================
# 配置
# ============================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SMART_MODEL_DIR="$(dirname "$SCRIPT_DIR")"
CACHE_DIR="/tmp/smart_model_cache"
LOG_DIR="/tmp/smart_model_cache"
LOG_FILE="$LOG_DIR/cache_manager_$(date +%Y%m%d).log"

# 缓存配置
CACHE_TTL=3600  # 缓存有效期（秒）
MAX_CACHE_SIZE=100  # 最大缓存数量

# 创建目录
mkdir -p "$CACHE_DIR" "$LOG_DIR"

# ============================================
# 文件类型缓存
# ============================================

# 缓存文件类型检测结果
# 参数：$1 - 文件路径
#       $2 - 文件类型
#       $3 - 推荐模型
cache_file_type() {
    local file_path="$1"
    local file_type="$2"
    local recommended_model="$3"
    
    # 生成缓存key（使用文件路径的hash）
    local cache_key=$(echo "$file_path" | md5sum | cut -d' ' -f1)
    local cache_file="$CACHE_DIR/file_type_${cache_key}.json"
    
    # 写入缓存
    cat > "$cache_file" << EOF
{
    "file_path": "$file_path",
    "file_type": "$file_type",
    "recommended_model": "$recommended_model",
    "timestamp": $(date +%s),
    "ttl": $CACHE_TTL
}
EOF
    
    echo "[$(date -Iseconds)] 缓存文件类型：$file_path → $file_type" >> "$LOG_FILE"
}

# 从缓存获取文件类型
# 参数：$1 - 文件路径
# 返回：缓存结果（JSON格式）或空
get_cached_file_type() {
    local file_path="$1"
    local cache_key=$(echo "$file_path" | md5sum | cut -d' ' -f1)
    local cache_file="$CACHE_DIR/file_type_${cache_key}.json"
    
    if [ ! -f "$cache_file" ]; then
        return 1
    fi
    
    # 检查缓存是否过期
    local timestamp=$(grep -oP '"timestamp": \K[0-9]+' "$cache_file")
    local current=$(date +%s)
    local age=$((current - timestamp))
    
    if [ "$age" -gt "$CACHE_TTL" ]; then
        rm -f "$cache_file"
        echo "[$(date -Iseconds)] 缓存过期：$file_path" >> "$LOG_FILE"
        return 1
    fi
    
    # 返回缓存内容
    cat "$cache_file"
    return 0
}

# ============================================
# 复杂度缓存
# ============================================

# 缓存复杂度分析结果
# 参数：$1 - 消息内容
#       $2 - 复杂度得分
#       $3 - 推荐模型
cache_complexity() {
    local message="$1"
    local complexity_score="$2"
    local recommended_model="$3"
    
    # 生成缓存key（使用消息内容的hash）
    local cache_key=$(echo "$message" | md5sum | cut -d' ' -f1)
    local cache_file="$CACHE_DIR/complexity_${cache_key}.json"
    
    # 写入缓存
    cat > "$cache_file" << EOF
{
    "message_hash": "$cache_key",
    "complexity_score": $complexity_score,
    "recommended_model": "$recommended_model",
    "timestamp": $(date +%s),
    "ttl": $CACHE_TTL
}
EOF
    
    echo "[$(date -Iseconds)] 缓存复杂度：$cache_key → $complexity_score" >> "$LOG_FILE"
}

# 从缓存获取复杂度
# 参数：$1 - 消息内容
# 返回：缓存结果（JSON格式）或空
get_cached_complexity() {
    local message="$1"
    local cache_key=$(echo "$message" | md5sum | cut -d' ' -f1)
    local cache_file="$CACHE_DIR/complexity_${cache_key}.json"
    
    if [ ! -f "$cache_file" ]; then
        return 1
    fi
    
    # 检查缓存是否过期
    local timestamp=$(grep -oP '"timestamp": \K[0-9]+' "$cache_file")
    local current=$(date +%s)
    local age=$((current - timestamp))
    
    if [ "$age" -gt "$CACHE_TTL" ]; then
        rm -f "$cache_file"
        echo "[$(date -Iseconds)] 缓存过期：$cache_key" >> "$LOG_FILE"
        return 1
    fi
    
    # 返回缓存内容
    cat "$cache_file"
    return 0
}

# ============================================
# 模型切换缓存
# ============================================

# 缓存模型切换结果
# 参数：$1 - 会话ID
#       $2 - 消息内容
#       $3 - 推荐模型
cache_model_switch() {
    local session_id="$1"
    local message="$2"
    local recommended_model="$3"
    
    # 生成缓存key（会话ID + 消息hash）
    local cache_key="${session_id}_$(echo "$message" | md5sum | cut -d' ' -f1)"
    local cache_file="$CACHE_DIR/model_switch_${cache_key}.json"
    
    # 写入缓存
    cat > "$cache_file" << EOF
{
    "session_id": "$session_id",
    "message_hash": "$(echo "$message" | md5sum | cut -d' ' -f1)",
    "recommended_model": "$recommended_model",
    "timestamp": $(date +%s),
    "ttl": $CACHE_TTL
}
EOF
    
    echo "[$(date -Iseconds)] 缓存模型切换：$session_id → $recommended_model" >> "$LOG_FILE"
}

# 从缓存获取模型切换
# 参数：$1 - 会话ID
#       $2 - 消息内容
# 返回：缓存结果（JSON格式）或空
get_cached_model_switch() {
    local session_id="$1"
    local message="$2"
    local cache_key="${session_id}_$(echo "$message" | md5sum | cut -d' ' -f1)"
    local cache_file="$CACHE_DIR/model_switch_${cache_key}.json"
    
    if [ ! -f "$cache_file" ]; then
        return 1
    fi
    
    # 检查缓存是否过期
    local timestamp=$(grep -oP '"timestamp": \K[0-9]+' "$cache_file")
    local current=$(date +%s)
    local age=$((current - timestamp))
    
    if [ "$age" -gt "$CACHE_TTL" ]; then
        rm -f "$cache_file"
        echo "[$(date -Iseconds)] 缓存过期：$cache_key" >> "$LOG_FILE"
        return 1
    fi
    
    # 返回缓存内容
    cat "$cache_file"
    return 0
}

# ============================================
# 缓存管理
# ============================================

# 清理过期缓存
cleanup_expired_cache() {
    local current=$(date +%s)
    local cleaned=0
    
    for cache_file in "$CACHE_DIR"/*.json; do
        if [ ! -f "$cache_file" ]; then
            continue
        fi
        
        local timestamp=$(grep -oP '"timestamp": \K[0-9]+' "$cache_file" 2>/dev/null || echo "0")
        local ttl=$(grep -oP '"ttl": \K[0-9]+' "$cache_file" 2>/dev/null || echo "$CACHE_TTL")
        local age=$((current - timestamp))
        
        if [ "$age" -gt "$ttl" ]; then
            rm -f "$cache_file"
            cleaned=$((cleaned + 1))
        fi
    done
    
    echo "[$(date -Iseconds)] 清理过期缓存：$cleaned 个" >> "$LOG_FILE"
    echo "{\"cleaned\": $cleaned}"
}

# 清理所有缓存
clear_all_cache() {
    local count=$(find "$CACHE_DIR" -name "*.json" | wc -l)
    rm -rf "$CACHE_DIR"/*.json
    
    echo "[$(date -Iseconds)] 清理所有缓存：$count 个" >> "$LOG_FILE"
    echo "{\"cleared\": $count}"
}

# 获取缓存统计
get_cache_stats() {
    local total=$(find "$CACHE_DIR" -name "*.json" | wc -l)
    local file_type=$(find "$CACHE_DIR" -name "file_type_*.json" | wc -l)
    local complexity=$(find "$CACHE_DIR" -name "complexity_*.json" | wc -l)
    local model_switch=$(find "$CACHE_DIR" -name "model_switch_*.json" | wc -l)
    
    # 计算缓存大小
    local size=$(du -sh "$CACHE_DIR" 2>/dev/null | cut -f1)
    
    cat << EOF
{
    "total": $total,
    "by_type": {
        "file_type": $file_type,
        "complexity": $complexity,
        "model_switch": $model_switch
    },
    "size": "$size",
    "ttl": $CACHE_TTL,
    "max_cache_size": $MAX_CACHE_SIZE,
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# 优化缓存（清理超过最大数量的缓存）
optimize_cache() {
    local total=$(find "$CACHE_DIR" -name "*.json" | wc -l)
    
    if [ "$total" -le "$MAX_CACHE_SIZE" ]; then
        echo "{\"status\": \"no need to optimize\", \"total\": $total}"
        return 0
    fi
    
    # 按时间排序，删除最旧的缓存
    local to_delete=$((total - MAX_CACHE_SIZE))
    
    find "$CACHE_DIR" -name "*.json" -printf '%T@ %p\n' | \
        sort -n | \
        head -n "$to_delete" | \
        cut -d' ' -f2- | \
        xargs rm -f
    
    echo "[$(date -Iseconds)] 优化缓存：删除 $to_delete 个最旧缓存" >> "$LOG_FILE"
    echo "{\"optimized\": $to_delete, \"remaining\": $MAX_CACHE_SIZE}"
}

# ============================================
# 性能监控
# ============================================

# 记录性能指标
record_performance() {
    local operation="$1"
    local duration="$2"
    local cache_hit="$3"
    
    local perf_file="$LOG_DIR/performance.log"
    
    echo "$(date +%s)|$operation|$duration|$cache_hit" >> "$perf_file"
}

# 获取性能统计
get_performance_stats() {
    local perf_file="$LOG_DIR/performance.log"
    
    if [ ! -f "$perf_file" ]; then
        echo '{"error": "no performance data"}'
        return 1
    fi
    
    local total_ops=$(wc -l < "$perf_file")
    local cache_hits=$(grep "|hit$" "$perf_file" | wc -l)
    local cache_misses=$(grep "|miss$" "$perf_file" | wc -l)
    local hit_rate=0
    
    if [ "$total_ops" -gt 0 ]; then
        hit_rate=$((cache_hits * 100 / total_ops))
    fi
    
    # 计算平均响应时间
    local avg_duration=$(awk -F'| '{sum+=$3} END {print int(sum/NR)}' "$perf_file")
    
    cat << EOF
{
    "total_operations": $total_ops,
    "cache_hits": $cache_hits,
    "cache_misses": $cache_misses,
    "hit_rate": $hit_rate,
    "avg_duration_ms": $avg_duration,
    "timestamp": "$(date -Iseconds)"
}
EOF
}

# ============================================
# 批量操作优化
# ============================================

# 批量缓存文件类型
# 参数：$@ - 文件路径列表
batch_cache_file_types() {
    local files=("$@")
    local results="["
    local first=true
    
    for file in "${files[@]}"; do
        if [ "$first" = true ]; then
            first=false
        else
            results+=","
        fi
        
        # 检查缓存
        local cached=$(get_cached_file_type "$file")
        if [ $? -eq 0 ]; then
            results+="$cached"
        else
            # 未缓存，需要检测
            if [ -f "$SMART_MODEL_DIR/smart-model-v2.sh" ]; then
                source "$SMART_MODEL_DIR/smart-model-v2.sh"
                local file_type=$(detect_file_type "$file")
                local model=$(get_recommended_model "$file_type")
                
                # 缓存结果
                cache_file_type "$file" "$file_type" "$model"
                
                results+="{\"file\": \"$file\", \"type\": \"$file_type\", \"model\": \"$model\", \"cached\": false}"
            else
                results+="{\"file\": \"$file\", \"error\": \"smart model not found\"}"
            fi
        fi
    done
    
    results+="]"
    echo "$results"
}

# ============================================
# 主入口
# ============================================

case "${1:-}" in
    --cleanup)
        cleanup_expired_cache
        ;;
    --clear)
        clear_all_cache
        ;;
    --stats)
        get_cache_stats
        ;;
    --optimize)
        optimize_cache
        ;;
    --perf)
        get_performance_stats
        ;;
    --batch-file)
        shift
        batch_cache_file_types "$@"
        ;;
    --test)
        echo "=== 缓存管理器测试 ==="
        echo ""
        
        echo "测试1：缓存文件类型"
        cache_file_type "/test/file.py" "code" "coding"
        get_cached_file_type "/test/file.py"
        echo ""
        
        echo "测试2：缓存复杂度"
        cache_complexity "帮我写一个Python函数" "45" "main"
        get_cached_complexity "帮我写一个Python函数"
        echo ""
        
        echo "测试3：缓存统计"
        get_cache_stats
        echo ""
        
        echo "测试4：优化缓存"
        optimize_cache
        echo ""
        
        echo "测试5：性能统计"
        get_performance_stats
        echo ""
        
        echo "测试6：清理过期缓存"
        cleanup_expired_cache
        echo ""
        
        echo "=== 测试完成 ==="
        ;;
    *)
        echo "用法："
        echo "  $0 --cleanup                  - 清理过期缓存"
        echo "  $0 --clear                    - 清理所有缓存"
        echo "  $0 --stats                    - 缓存统计"
        echo "  $0 --optimize                 - 优化缓存"
        echo "  $0 --perf                     - 性能统计"
        echo "  $0 --batch-file 文件1 文件2... - 批量缓存文件类型"
        echo "  $0 --test                     - 运行测试"
        ;;
esac
