# Full Market Report

> Composite workflow for generating a complete market analysis report in one pass.
>
> Best for category validation, market-entry decisions, and strategic opportunity reviews.

---

## Input

| Parameter | Required | Description |
|-----------|----------|-------------|
| Category keyword | Yes | A category name, market phrase, or niche keyword |

---

## Execution chain

- Step 1/4: Confirm the category with `categories`
- Step 2/4: Pull market-level metrics with `markets/search`
- Step 3/4: Pull top products with `products/search`
- Step 4/4: Pull one or more leading ASINs with `realtime/product`

```yaml
Step 1: Category confirmation
  tool: categories
  input: { categoryKeyword: "user category keyword" }
  output: confirmed category path

Step 2: Market overview
  tool: markets/search
  input: { categoryPath: [from step 1], topN: "10" }
  output: market metrics such as sales, price, concentration, new-SKU rate, and brand count

Step 3: Top product review
  tool: products/search
  input: { keyword: "category keyword", sortBy: "monthlySales", sortOrder: "desc", pageSize: 50 }
  output: top 50 products for brand, price, and listing-structure analysis

Step 4: Detail review
  tool: realtime/product
  input: { asin: "top ASIN", marketplace: "US" }
  output: listing strategy, review insights, specs, and variant structure
```

---

## Recommended output template

```markdown
# Full Market Analysis Report

## 1. Market overview
| Metric | Value | Read |
|--------|-------|------|

## 2. Competitive structure
| Metric | Value | Read |
|--------|-------|------|

## 3. Market vitality
| Metric | Value | Read |
|--------|-------|------|

## 4. Brand distribution
| Brand | Product count | Monthly sales | Share |
|-------|---------------|---------------|-------|

## 5. Price distribution
| Price band | Product count | Share | Avg monthly sales |
|------------|---------------|-------|-------------------|

## 6. Top products
| # | ASIN | Title | Brand | Price | Monthly sales | BSR | Rating | Reviews |
|---|------|-------|-------|-------|---------------|-----|--------|---------|

## 7. Leading-product breakdown
- Listing strategy
- Feature emphasis
- Review insights
- Product specifications

## 8. Overall assessment
- Opportunity score
- Recommendation
- Risks
- Suggested next step
```

---

## Suggested scoring logic

| Dimension | Strong | Medium | Weak |
|----------|--------|--------|------|
| Monthly market value | > $10M | $5M–$10M | < $5M |
| Product concentration | < 40% | 40%–60% | > 60% |
| New SKU rate | > 15% | 5%–15% | < 5% |
| FBA rate | > 50% | 30%–50% | < 30% |
| Brand count | > 50 | 20–50 | < 20 |

---

## Decision guidance

Use this workflow when the user asks for:

- a full market report
- category validation
- a niche opportunity report
- a strategic market-entry summary
