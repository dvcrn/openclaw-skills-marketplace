---
name: china-shopping
description: "China Shopping"
---

# SKILL.md - China Shopping

## Overview

**China Shopping** is an OpenClaw skill that recommends the best Chinese shopping websites based on product categories. This v1.0.1 version provides straightforward recommendations for common product types like electronics, clothing, groceries, and more.

## Security Updates (v1.0.1)

- Fixed potential command injection vulnerabilities in shell scripts
- Added input validation and sanitization for product names
- Used `--arg` parameter in jq queries to safely pass variables
- Added length limits and dangerous character filtering

## Description

When users input a product name (e.g., "手机", "衣服"), the skill recommends the most suitable Chinese e-commerce platforms for purchasing that product, helping users find the best shopping destinations quickly.

## Trigger Phrases & Usage

### Trigger Phrases
- "china-shopping"
- "中国购物"
- "推荐购物网站"
- "买[产品]去哪"
- "哪里买[产品]"

### Command Usage
```bash
# Basic recommendation
china-shopping recommend "手机"

# Alternative syntax
china-shopping 推荐 "衣服"

# Show all categories
china-shopping categories

# Help
china-shopping help
```

### In Chat Context
- "帮我推荐买手机的网站"
- "买衣服应该去哪个网站？"
- "中国购物推荐：笔记本电脑"

## Installation & Dependencies

This skill requires no external dependencies. It's a pure CLI tool with a simple data file.

### Files
- `china-shopping` (executable script)
- `categories.json` (product-category mapping)
- `recommendations.json` (category-website recommendations)

### Permissions
- Read access to data files
- Write access to logs (optional)

## How It Works

1. **Input Parsing**: Takes a product name as input
2. **Category Mapping**: Maps product to predefined categories (electronics, clothing, groceries, etc.)
3. **Recommendation Lookup**: Returns recommended websites for that category
4. **Output Formatting**: Presents results in a user-friendly format

## Example Output

```
$ china-shopping recommend "手机"
📱 手机 (Electronics) 推荐购物网站：
1. 京东 (JD.com) - 正品保障，物流快
2. 天猫 (Tmall.com) - 品牌官方旗舰店
3. 苏宁易购 (Suning.com) - 家电数码专业
4. 小米商城 (Mi.com) - 小米生态链产品

💡 提示：购买电子产品建议选择官方旗舰店或自营平台，注意查看用户评价和售后服务。
```

## Configuration

No configuration required for basic usage.

## Advanced Features (Future)

- Price comparison across platforms
- User preference learning
- Seasonal/realtime recommendations
- Coupon/price alert integration

## Notes

- This is v1.0.0 simple version
- Recommendations are based on general market consensus
- Actual shopping experience may vary
- Always verify seller reputation before purchase

## Author & License

OpenClaw Skill - MIT License