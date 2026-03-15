# Product Selection

> Stage 2: Help sellers identify concrete products worth entering within a category.
>
> Core question: What exactly should I sell in this category?

---

## Quick mode index

### Beginner-friendly modes

| # | Mode | Filter logic | Recommended |
|---|------|--------------|-------------|
| 4 | High demand, low barrier | `monthlySalesMin: 300, reviewCountMax: 50, listingAge: "180"` | ★★★★★ |
| 13 | Beginner shortlist | `monthlySalesMin: 300, priceMin: 15, priceMax: 60, fulfillment: ["FBA"]` | ★★★★ |
| 9 | Low-price products | `priceMax: 10` | ★★★ |

### Growth / differentiation modes

| # | Mode | Filter logic | Recommended |
|---|------|--------------|-------------|
| 1 | Fast movers | `monthlySalesMin: 300, salesGrowthRateMin: 0.1` | ★★★★ |
| 6 | Underserved products | `monthlySalesMin: 300, ratingMax: 3.7, listingAge: "180"` | ★★★★ |
| 2 | Emerging products | `monthlySalesMax: 600, salesGrowthRateMin: 0.1, listingAge: "180"` | ★★★ |
| 3 | Single-variant potential | `salesGrowthRateMin: 0.2, variantCountMax: 1` | ★★★ |
| 7 | New-release watchlist | `monthlySalesMax: 500, badges: ["New Release"]` | ★★★ |

### Distribution / catalog modes

| # | Mode | Filter logic | Recommended |
|---|------|--------------|-------------|
| 10 | Broad catalog scan | `bsrGrowthRateMin: 0.99, reviewCountMax: 10, listingAge: "90"` | ★★★ |
| 11 | Selective catalog scan | `bsrGrowthRateMin: 0.99, listingAge: "90"` | ★★★ |
| 5 | Long-tail low-price | `bsrMin: 10000, bsrMax: 50000, priceMax: 30, sellerCountMax: 1` | ★★ |
| 12 | Speculative crowd market | `monthlySalesMin: 600, sellerCountMin: 3` | ★★ |

### Other useful modes

| # | Mode | Filter logic |
|---|------|--------------|
| 8 | Low inventory pressure | `monthlySalesMin: 300, fulfillment: ["FBM"]` |
| 14 | Top BSR products | `bsrMax: 1000` with a defined `categoryPath` |

---

## APIs used in this file

- `products/search` — core interface for product selection
- `categories` — confirm category paths
- `realtime/product` — validate shortlisted ASINs in detail

---

## Intent routing

| User request | Mode | # |
|-------------|------|---|
| "Find fast-growing products" | Fast movers | 1 |
| "Show me products with potential" | Emerging products | 2 |
| "Find low-review, high-sales products" | High demand, low barrier | 4 |
| "Find products with poor reviews but real demand" | Underserved products | 6 |
| "Show me new-product opportunities" | New-release watchlist | 7 |
| "I am a beginner" / "small budget" | Beginner shortlist | 13 |
| "Show the top products in this category" | Top BSR products | 14 |
| "Help me choose" | Composite recommendation | 2.10 |

---

## Standard workflow

- Step 1/3: Confirm category with `categories`
- Step 2/3: Run `products/search` using the right mode
- Step 3/3: Analyze the result set and recommend the top ideas

```bash
POST /openapi/v2/categories
{ "categoryKeyword": "pet toys" }

POST /openapi/v2/products/search
{
  "keyword": "pet toys",
  "monthlySalesMin": 300,
  "reviewCountMax": 50,
  "listingAge": "180",
  "sortBy": "monthlySales",
  "sortOrder": "desc",
  "pageSize": 20
}

POST /openapi/v2/realtime/product
{ "asin": "B09XXXXX", "marketplace": "US" }
```

### Output template

```markdown
# Product Selection Report — [Category] / [Mode]

## Filters used
[List the exact search filters]

## Top 5 products

| # | ASIN | Product | Price | Monthly sales | BSR | Rating | Reviews | Why it stands out |
|---|------|---------|-------|---------------|-----|--------|---------|-------------------|

## Market read
- Price distribution
- Brand structure
- Competition level
- Opportunity pattern

## Recommendation
[What to test, what to avoid, and what to validate next]
```

---

## Composite recommendation flow (2.10)

> Use this when the user says: "Help me choose", "What should I sell?", or "Give me the best options".

### Workflow

- Step 1/4: Confirm category with `categories`
- Step 2/4: Pull market conditions with `markets/search`
- Step 3/4: Run 2–3 product-selection modes with `products/search`
- Step 4/4: Score and rank products using the user's goal, budget, and experience level

### Inputs to clarify first

| Input | Options | Why it matters |
|------|---------|----------------|
| Goal | Fast growth / differentiation / market share / margin-first | Changes the weighting model |
| Budget | Low (<$5K) / mid ($5K–$20K) / high (>$20K) | Impacts price range and complexity |
| Experience | Beginner / experienced / advanced | Changes acceptable risk |

### Scoring suggestions

- Demand potential
- Review barrier
- Price/margin fit
- Competition density
- Operational complexity
- Differentiation room

---

## Decision guidance

Use this file when the user is asking product-first questions such as:

- "Find products for me"
- "What can I sell in this niche?"
- "Show low-competition opportunities"
- "Give me a shortlist"
