# Command Design

## CLI Command Structure

```
china-shopping [command] [arguments] [options]
```

## Commands

### 1. `recommend` (推荐)
**Description**: Get shopping website recommendations for a product

**Syntax**: 
```bash
china-shopping recommend <product-name>
china-shopping 推荐 <产品名称>
```

**Examples**:
```bash
# Chinese product names
china-shopping recommend "手机"
china-shopping recommend "笔记本电脑"
china-shopping recommend "运动鞋"

# English product names (optional future support)
china-shopping recommend "smartphone"
```

**Output**:
- Product category identification
- Recommended websites with brief descriptions
- Shopping tips for that product category

### 2. `categories`
**Description**: List all supported product categories

**Syntax**:
```bash
china-shopping categories
```

**Output**:
- Category list with example products
- Count of categories supported

### 3. `help`
**Description**: Show help information

**Syntax**:
```bash
china-shopping help
china-shopping --help
china-shopping -h
```

### 4. `version`
**Description**: Show skill version

**Syntax**:
```bash
china-shopping version
china-shopping --version
china-shopping -v
```

## Command-Line Options

### Global Options
- `--lang [zh/en]`: Language preference (default: zh)
- `--format [text/json]`: Output format (default: text)
- `--verbose`: Show detailed information

### Recommendation Options
- `--count N`: Number of recommendations to show (default: 4)
- `--explain`: Explain why these websites are recommended

## Interactive Mode (Future)

```bash
# Start interactive Q&A mode
china-shopping interactive
```

## Integration with OpenClaw

### As a Standalone Skill
The skill can be called directly from the command line or via OpenClaw's skill routing.

### In Chat Context
When triggered by chat phrases, OpenClaw will invoke:
```bash
china-shopping recommend "{product}"
```

### Example Integration
```bash
# In OpenClaw skill handler
product=$(extract_product_from_message "$message")
result=$(china-shopping recommend "$product" --format text)
send_response "$result"
```

## Error Handling

- Invalid product: "抱歉，暂时没有找到适合'xxx'的购物推荐。"
- Network issues: "无法获取推荐数据，请稍后重试。"
- No input: "请输入产品名称，例如：china-shopping recommend '手机'"

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `3`: Product not found
- `4`: Data file missing