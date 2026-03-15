# Market Selection

> Stage 1: Help sellers identify promising markets, categories, and subcategories.
>
> Core question: Which category should I evaluate first?

---

## Scenarios

| # | Scenario | Typical question |
|---|----------|------------------|
| 1.1 | Top-level category scan | "Which major categories have opportunity?" |
| 1.2 | Subcategory filtering | "Which subcategory under Pet Supplies is worth entering?" |
| 1.3 | Market validation | "Is this category worth entering?" |

---

## APIs used in this file

- `categories` — confirm category paths and discover child categories
- `markets/search` — market-level aggregate metrics such as concentration, new-product rate, and brand count
- `products/search` — top product distribution to supplement brand and price analysis

See `SKILL.md` for the quick parameter guide and `openapi-reference.md` for full field definitions.

---

## Scenario 1.1: Top-level category scan

### Workflow

- Step 1/4: Load root categories with `categories`
- Step 2/4: Run `markets/search` on each candidate category
- Step 3/4: Filter categories using market quality thresholds
- Step 4/4: Rank categories and provide recommendations

```bash
POST /openapi/v2/categories
{}

POST /openapi/v2/markets/search
{ "categoryPath": ["Pet Supplies"], "topN": "10" }
```

### Suggested screening rules

- Monthly market value (`sampleAvgMonthlyRevenue × sampleSkuCount`) > $5M
- Product concentration (`topSalesRate`) < 60%
- New SKU rate (`sampleNewSkuRate`) > 5%

### Output template

```markdown
# US Category Opportunity Scan

## Top categories

| Rank | Category | Monthly market value | Top-10 concentration | New SKU rate | Brand count | Recommendation |
|------|----------|----------------------|----------------------|--------------|-------------|----------------|

## Summary
[Why these categories are attractive]

## Next step
Move into subcategory filtering (1.2) or market validation (1.3)
```

### Fallbacks

| Issue | Fallback |
|------|----------|
| `markets/search` timeout | Run categories one by one and reduce scope |
| Empty result | Use `categoryKeyword` to refine the category lookup |

---

## Scenario 1.2: Subcategory filtering

### Workflow

- Step 1/3: Fetch child categories using `categories` with `parentCategoryPath`
- Step 2/3: Run `markets/search` on each subcategory
- Step 3/3: Rank the options and recommend the top subcategories

```bash
POST /openapi/v2/categories
{ "parentCategoryPath": ["Pet Supplies"] }

POST /openapi/v2/markets/search
{ "categoryPath": ["Pet Supplies", "Dogs"], "topN": "10" }
```

### Output template

```markdown
# Subcategory Opportunity Review

## Comparison table

| Subcategory | Monthly market value | Concentration | New SKU rate | Brand count | Recommendation |
|-------------|----------------------|---------------|--------------|-------------|----------------|

## Top 3 recommendations
[Explain why each subcategory stands out]
```

---

## Scenario 1.3: Market validation

> This is the most important market-selection flow.

### Workflow

- Step 1/3: Confirm the category with `categories`
- Step 2/3: Pull market-level metrics with `markets/search`
- Step 3/3: Pull top products with `products/search` to inspect price and brand structure

```bash
POST /openapi/v2/categories
{ "categoryKeyword": "treadmill" }

POST /openapi/v2/markets/search
{ "categoryPath": ["Sports & Outdoors", "Exercise & Fitness", "Treadmills"], "topN": "10" }

POST /openapi/v2/products/search
{ "keyword": "treadmill", "sortBy": "monthlySales", "sortOrder": "desc", "pageSize": 50 }
```

### Evaluation framework

| Dimension | Good | Neutral | Risk |
|----------|------|---------|------|
| Monthly market value | > $10M | $5M–$10M | < $5M |
| Top-10 product concentration | < 40% | 40%–60% | > 60% |
| New SKU rate | > 15% | 5%–15% | < 5% |
| FBA rate | > 50% | 30%–50% | < 30% |
| Brand count | > 50 | 20–50 | < 20 |

### Output template

```markdown
# Market Validation Report

## Category
[Confirmed category path]

## Market score
[Recommended / Proceed with caution / Not recommended]

## Why
- Market size
- Concentration
- Brand saturation
- New product opportunity
- Pricing structure

## Suggested next step
Run product selection or competitor analysis
```

---

## Decision guidance

Use this file when the user is asking category-first questions such as:

- "Which category has room?"
- "Which niche should I enter?"
- "Is this market worth entering?"
- "Compare these subcategories"
