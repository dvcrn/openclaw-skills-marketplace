# Technical Implementation

## Architecture Overview

```
┌─────────────────┐
│   User Input    │
│  ("买手机")      │
└────────┬────────┘
         │
┌────────▼────────┐
│   Command Parser│
│   - Parse args  │
│   - Validate    │
└────────┬────────┘
         │
┌────────▼────────┐
│  Product Matcher│
│  - Map to category│
└────────┬────────┘
         │
┌────────▼────────┐
│ Recommendation  │
│ Engine          │
│ - Load data     │
│ - Get websites  │
└────────┬────────┘
         │
┌────────▼────────┐
│  Formatter      │
│  - Format output│
│  - Add tips     │
└────────┬────────┘
         │
┌────────▼────────┐
│   Output        │
│   (CLI/Chat)    │
└─────────────────┘
```

## Implementation Choices

### Language: Bash/Shell Script
**Pros for v1.0.0:**
- Simple, no dependencies
- Easy integration with OpenClaw
- Fast execution
- Easy to modify and maintain

**Cons:**
- Limited data structures
- Basic string manipulation only

**Alternative**: Python or Node.js for more complex future versions.

### Data Storage: JSON Files
- `categories.json`: Category definitions and website recommendations
- `product_mapping.json`: Product-to-category mapping
- `websites.json`: Website metadata and descriptions

## File Structure

```
~/.openclaw/workspace/skills/china-shopping/
├── SKILL.md
├── china-shopping          # Main executable script
├── data/
│   ├── categories.json
│   ├── product_mapping.json
│   └── websites.json
├── lib/
│   ├── recommend.sh       # Recommendation logic
│   ├── match.sh          # Product matching
│   └── format.sh         # Output formatting
├── logs/                  # Optional log directory
└── tests/                 # Test scripts
```

## Main Script Implementation

### `china-shopping` (executable)

```bash
#!/bin/bash

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$SCRIPT_DIR/data"

# Source library functions
source "$SCRIPT_DIR/lib/recommend.sh"
source "$SCRIPT_DIR/lib/match.sh"
source "$SCRIPT_DIR/lib/format.sh"

# Parse command line arguments
parse_args() {
    # ... argument parsing logic
}

main() {
    parse_args "$@"
    
    case $COMMAND in
        recommend|推荐)
            product="$2"
            if [ -z "$product" ]; then
                echo "错误：请提供产品名称"
                exit 1
            fi
            recommend "$product"
            ;;
        categories)
            list_categories
            ;;
        help|--help|-h)
            show_help
            ;;
        version|--version|-v)
            echo "china-shopping v$VERSION"
            ;;
        *)
            echo "未知命令: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
```

## Data Files Structure

### `data/categories.json`
```json
{
  "electronics": {
    "name": "电子产品",
    "description": "手机、电脑、数码产品等",
    "websites": [
      {
        "id": "jd",
        "name": "京东",
        "url": "https://www.jd.com",
        "reason": "正品保障，物流速度快，售后服务好",
        "rank": 1,
        "tags": ["正品", "物流快", "售后好"]
      },
      {
        "id": "tmall", 
        "name": "天猫",
        "url": "https://www.tmall.com",
        "reason": "品牌官方旗舰店，品质有保障",
        "rank": 2,
        "tags": ["官方", "品牌", "品质"]
      }
    ],
    "shopping_tips": [
      "购买电子产品建议选择官方旗舰店或自营平台",
      "注意查看商品评价和售后服务政策",
      "比价时注意配置和套餐差异"
    ]
  }
}
```

### `data/product_mapping.json`
```json
{
  "手机": "electronics",
  "智能手机": "electronics",
  "iphone": "electronics",
  "华为手机": "electronics",
  "笔记本电脑": "electronics",
  "电脑": "electronics",
  "平板电脑": "electronics",
  "耳机": "electronics",
  
  "衣服": "clothing",
  "服装": "clothing",
  "上衣": "clothing",
  "裤子": "clothing",
  "裙子": "clothing",
  "外套": "clothing",
  "鞋子": "clothing",
  "运动鞋": "clothing",
  
  "零食": "groceries",
  "食品": "groceries",
  "大米": "groceries",
  "食用油": "groceries"
}
```

## Key Functions

### 1. Product Matching (`lib/match.sh`)
```bash
#!/bin/bash

get_category() {
    local product="$1"
    local mapping_file="$DATA_DIR/product_mapping.json"
    
    # Simple exact match (future: fuzzy matching)
    local category=$(jq -r ".[\"$product\"]" "$mapping_file" 2>/dev/null)
    
    if [ "$category" = "null" ] || [ -z "$category" ]; then
        # Try partial matching
        category=$(find_partial_match "$product")
    fi
    
    echo "$category"
}

find_partial_match() {
    # Implement basic substring matching
    # Return "general" if no match found
    echo "general"
}
```

### 2. Recommendation Engine (`lib/recommend.sh`)
```bash
#!/bin/bash

recommend() {
    local product="$1"
    local category=$(get_category "$product")
    
    if [ -z "$category" ] || [ "$category" = "null" ]; then
        echo "抱歉，暂时没有找到适合'$product'的购物推荐。"
        echo "您可以尝试："
        echo "1. 使用更通用的产品名称"
        echo "2. 查看支持的产品类别：china-shopping categories"
        return 1
    fi
    
    load_recommendations "$category" "$product"
}

load_recommendations() {
    local category="$1"
    local product="$2"
    
    local category_data=$(jq ".categories[\"$category\"]" "$DATA_DIR/categories.json")
    
    # Extract and format recommendations
    # ... implementation details
}
```

### 3. Output Formatter (`lib/format.sh`)
```bash
#!/bin/bash

format_recommendations() {
    local category_name="$1"
    local product="$2"
    local websites="$3"
    
    echo "🛍️  $product ($category_name) 推荐购物网站："
    echo ""
    
    local count=1
    echo "$websites" | while IFS= read -r line; do
        # Parse website data and format
        echo "$count. $line"
        count=$((count + 1))
    done
    
    echo ""
    echo "💡 购物提示："
    # Output shopping tips
}
```

## Dependencies

### Required Tools
1. **jq**: JSON processing (lightweight, likely already installed)
   ```bash
   # Install on macOS
   brew install jq
   
   # Install on Ubuntu/Debian
   apt-get install jq
   ```

2. **Standard Unix tools**: grep, awk, sed, curl (for future enhancements)

### Optional Dependencies (Future)
1. **Python 3**: For advanced NLP matching
2. **sqlite3**: For larger product databases
3. **redis**: For caching recommendations

## Performance Considerations

1. **Data Loading**: JSON files are loaded on each invocation (small size, acceptable)
2. **Matching Speed**: Simple hash lookup (O(1) for exact matches)
3. **Memory Usage**: Minimal (few KB of JSON data)

## Testing Strategy

### Unit Tests
```bash
# Test product matching
test_match() {
    assert "$(get_category '手机')" = "electronics"
    assert "$(get_category '衣服')" = "clothing"
}

# Test recommendation output
test_recommend() {
    output=$(recommend "手机")
    assert_contains "$output" "京东"
    assert_contains "$output" "天猫"
}
```

### Integration Tests
```bash
# Test full command line
test_cli() {
    output=$(china-shopping recommend "手机")
    # Verify output format and content
}
```

## Deployment

### Installation Script
```bash
#!/bin/bash
# install.sh

# Copy script to OpenClaw skills directory
cp china-shopping ~/.openclaw/workspace/skills/china-shopping/

# Make executable
chmod +x ~/.openclaw/workspace/skills/china-shopping/china-shopping

# Create data directory
mkdir -p ~/.openclaw/workspace/skills/china-shopping/data

# Copy data files
cp data/*.json ~/.openclaw/workspace/skills/china-shopping/data/

echo "安装完成！"
```

### OpenClaw Integration
Add to OpenClaw skill registry:
```json
{
  "name": "china-shopping",
  "path": "~/.openclaw/workspace/skills/china-shopping",
  "description": "Chinese shopping website recommendations"
}
```

## Security Considerations

1. **No external API calls** in v1.0.0 (safe)
2. **Local data files only** (no privacy concerns)
3. **Input validation** to prevent injection attacks
4. **Read-only execution** (no file modification)

## Maintenance

1. **Data Updates**: Periodically update product mappings and website info
2. **Category Expansion**: Add new categories as needed
3. **Website Updates**: Update platform recommendations based on market changes

## Future Scalability

1. **Plugin Architecture**: Allow third-party recommendation modules
2. **API Server**: REST API for other applications to use
3. **Browser Extension**: Direct integration with shopping websites
4. **Mobile App**: Dedicated mobile interface