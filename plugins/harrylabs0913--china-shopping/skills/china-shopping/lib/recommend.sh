#!/bin/bash

# Recommendation engine for china-shopping

# Main recommendation function
recommend() {
    local product="$1"
    
    # Validate product
    product=$(validate_product "$product")
    if [ $? -ne 0 ]; then
        echo "$product" >&2
        exit 1
    fi
    
    log_info "查找产品推荐: $product"
    
    # Check dependencies
    check_dependencies
    
    # Get category for product
    local category=$(get_category "$product")
    log_debug "产品类别: $category"
    
    # Load recommendations for category
    if [ "$category" = "general" ]; then
        recommend_general "$product"
    else
        recommend_by_category "$product" "$category"
    fi
}

# Recommend based on specific category
recommend_by_category() {
    local product="$1"
    local category="$2"
    local category_file="$DATA_DIR/categories.json"
    
    if [ ! -f "$category_file" ]; then
        echo "错误：找不到分类数据文件" >&2
        exit 1
    fi
    
    # Get category information using --arg for safe variable passing
    local category_name=$(jq -r --arg cat "$category" '.categories[$cat].name' "$category_file" 2>/dev/null)
    local category_desc=$(jq -r --arg cat "$category" '.categories[$cat].description' "$category_file" 2>/dev/null)
    
    if [ "$category_name" = "null" ] || [ -z "$category_name" ]; then
        log_debug "未找到类别信息: $category，使用通用推荐"
        recommend_general "$product"
        return
    fi
    
    # Get websites for this category using --arg for safe variable passing
    local websites_json=$(jq --arg cat "$category" '.categories[$cat].websites' "$category_file" 2>/dev/null)
    local website_count=$(echo "$websites_json" | jq 'length' 2>/dev/null)
    
    if [ "$website_count" -eq 0 ] || [ "$website_count" = "null" ]; then
        log_debug "类别 $category 没有网站推荐，使用通用推荐"
        recommend_general "$product"
        return
    fi
    
    # Limit to requested count
    local display_count=$((website_count < RECOMMENDATION_COUNT ? website_count : RECOMMENDATION_COUNT))
    
    # Output header
    echo "🛍️  $product ($category_name) 推荐购物网站："
    echo ""
    
    # Output each website
    for ((i=0; i<display_count; i++)); do
        local website_data=$(echo "$websites_json" | jq ".[$i]" 2>/dev/null)
        if [ "$website_data" != "null" ] && [ -n "$website_data" ]; then
            format_website "$website_data" "$((i+1))"
        fi
    done
    
    echo ""
    
    # Output shopping tips
    local tips=$(get_shopping_tips "$category")
    if [ -n "$tips" ]; then
        echo "💡 购物提示："
        echo "$tips" | while IFS= read -r tip; do
            if [ -n "$tip" ]; then
                echo "  • $tip"
            fi
        done
    fi
    
    # Footer
    echo ""
    echo "📊 共找到 $display_count 个推荐网站（基于 $category_desc）"
}

# General fallback recommendations
recommend_general() {
    local product="$1"
    local general_file="$DATA_DIR/general_fallback.json"
    
    if [ ! -f "$general_file" ]; then
        # Use hardcoded fallback if file doesn't exist
        recommend_hardcoded "$product"
        return
    fi
    
    local websites_json=$(jq ".websites" "$general_file" 2>/dev/null)
    local website_count=$(echo "$websites_json" | jq 'length' 2>/dev/null)
    
    if [ "$website_count" -eq 0 ] || [ "$website_count" = "null" ]; then
        recommend_hardcoded "$product"
        return
    fi
    
    local display_count=$((website_count < RECOMMENDATION_COUNT ? website_count : RECOMMENDATION_COUNT))
    
    echo "🛍️  $product 推荐购物网站："
    echo ""
    echo "💡 提示：未找到该产品的具体分类，以下是通用购物平台推荐："
    echo ""
    
    for ((i=0; i<display_count; i++)); do
        local website_data=$(echo "$websites_json" | jq ".[$i]" 2>/dev/null)
        if [ "$website_data" != "null" ] && [ -n "$website_data" ]; then
            format_website "$website_data" "$((i+1))"
        fi
    done
    
    echo ""
    echo "🔍 建议：使用更具体的产品名称或查看支持的产品类别："
    echo "       china-shopping categories"
}

# Hardcoded fallback recommendations
recommend_hardcoded() {
    local product="$1"
    
    echo "🛍️  $product 推荐购物网站："
    echo ""
    echo "💡 提示：以下是通用的中国购物平台推荐："
    echo ""
    
    cat << EOF
1. 京东 (https://www.jd.com) - 正品保障，物流速度快
2. 天猫 (https://www.tmall.com) - 品牌官方旗舰店
3. 淘宝 (https://www.taobao.com) - 商品种类最全
4. 苏宁易购 (https://www.suning.com) - 家电数码专业平台

🔍 建议：使用更具体的产品名称获取更精准的推荐
       china-shopping categories
EOF
}

# List all products in a category (for debugging)
list_products_in_category() {
    local category="$1"
    local mapping_file="$DATA_DIR/product_mapping.json"
    
    if [ ! -f "$mapping_file" ]; then
        echo "错误：找不到映射文件" >&2
        return 1
    fi
    
    echo "类别 '$category' 中的产品："
    # Use --arg for safe variable passing
    jq -r --arg cat "$category" 'to_entries[] | select(.value == $cat) | .key' "$mapping_file" 2>/dev/null | sort
}