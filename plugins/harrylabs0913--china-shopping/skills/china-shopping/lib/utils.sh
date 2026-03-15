#!/bin/bash

# Utility functions for china-shopping

# Logging functions
log_info() {
    if [ "$DEBUG" = true ]; then
        echo "[INFO] $1" >&2
    fi
}

log_error() {
    echo "[ERROR] $1" >&2
}

log_debug() {
    if [ "$DEBUG" = true ]; then
        echo "[DEBUG] $1" >&2
    fi
}

# Check if jq is installed
check_dependencies() {
    if ! command -v jq &> /dev/null; then
        log_error "jq 未安装，请先安装 jq："
        echo "  macOS: brew install jq" >&2
        echo "  Ubuntu/Debian: sudo apt-get install jq" >&2
        echo "  CentOS/RHEL: sudo yum install jq" >&2
        exit 1
    fi
}

# Load JSON data safely
load_json() {
    local file="$1"
    local query="$2"
    
    if [ ! -f "$file" ]; then
        log_error "文件不存在: $file"
        return 1
    fi
    
    # Use jq to query JSON
    if [ -z "$query" ]; then
        jq '.' "$file" 2>/dev/null
    else
        jq "$query" "$file" 2>/dev/null
    fi
}

# Get category for a product
get_category() {
    local product="$1"
    local mapping_file="$DATA_DIR/product_mapping.json"
    
    if [ ! -f "$mapping_file" ]; then
        log_error "映射文件不存在: $mapping_file"
        echo "general"
        return 1
    fi
    
    # Sanitize product name for jq query - escape special characters
    local safe_product=$(echo "$product" | sed 's/\\/\\\\/g; s/"/\\"/g')
    
    # Try exact match first using --arg for safe variable passing
    local category=$(jq -r --arg prod "$product" '.[$prod]' "$mapping_file" 2>/dev/null)
    
    if [ "$category" = "null" ] || [ -z "$category" ]; then
        log_debug "未找到精确匹配: $product"
        
        # Try to find partial match using --arg for safe variable passing
        category=$(jq -r --arg prod "$product" 'to_entries[] | select(.key | contains($prod)) | .value' "$mapping_file" 2>/dev/null | head -1)
        
        if [ -z "$category" ]; then
            log_debug "未找到部分匹配: $product"
            echo "general"
            return 0
        fi
    fi
    
    echo "$category"
    return 0
}

# Format website recommendation
format_website() {
    local website_data="$1"
    local index="$2"
    
    local name=$(echo "$website_data" | jq -r '.name')
    local reason=$(echo "$website_data" | jq -r '.reason')
    local url=$(echo "$website_data" | jq -r '.url // ""')
    
    if [ -n "$url" ] && [ "$url" != "null" ]; then
        echo "$index. $name ($url) - $reason"
    else
        echo "$index. $name - $reason"
    fi
}

# Get shopping tips for category
get_shopping_tips() {
    local category="$1"
    local category_file="$DATA_DIR/categories.json"
    
    if [ ! -f "$category_file" ]; then
        return 1
    fi
    
    # Use --arg for safe variable passing
    jq -r --arg cat "$category" '.categories[$cat].shopping_tips[]' "$category_file" 2>/dev/null
}

# Validate product name (basic validation)
validate_product() {
    local product="$1"
    
    # Remove extra whitespace
    product=$(echo "$product" | xargs)
    
    # Check if product is empty
    if [ -z "$product" ]; then
        echo "错误：产品名称不能为空"
        return 1
    fi
    
    # Check length (reasonable product name length)
    if [ ${#product} -gt 50 ]; then
        echo "错误：产品名称过长"
        return 1
    fi
    
    # Check for potentially dangerous characters (basic)
    if [[ "$product" =~ [\<\>\|\&\;] ]]; then
        echo "错误：产品名称包含无效字符"
        return 1
    fi
    
    echo "$product"
    return 0
}