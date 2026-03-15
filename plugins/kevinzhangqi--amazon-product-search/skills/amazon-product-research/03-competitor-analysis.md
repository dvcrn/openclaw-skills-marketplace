# Competitor Analysis

> Stage 3: Help sellers understand the strongest competing products, brands, and listings.
>
> Core question: Who are the real competitors, and how are they winning?

---

## APIs used in this file

- `products/competitor-lookup` — find direct competitors by keyword, brand, ASIN, or category
- `products/search` — expand the market set and compare ranked products
- `realtime/product` — inspect listing copy, features, variants, ratings, and review patterns

---

## Main use cases

| # | Use case | Typical question |
|---|----------|------------------|
| 3.1 | Direct competitor lookup | "Who are the top competitors for this keyword?" |
| 3.2 | Brand comparison | "How does this brand compare to the leaders?" |
| 3.3 | ASIN-centered competitor scan | "What products compete with this ASIN?" |
| 3.4 | Listing and feature comparison | "What are top listings emphasizing?" |
| 3.5 | Review and pain-point comparison | "Where are competitors weak?" |

---

## Standard workflow

- Step 1/3: Pull a competitor set with `products/competitor-lookup`
- Step 2/3: Sort and cluster by price, sales, rating, reviews, and brand
- Step 3/3: Use `realtime/product` on a few leading ASINs to analyze listing strategy and review themes

```bash
POST /openapi/v2/products/competitor-lookup
{
  "keyword": "wireless earbuds",
  "sortBy": "monthlySales",
  "sortOrder": "desc",
  "pageSize": 20
}

POST /openapi/v2/realtime/product
{ "asin": "B09XXXXX", "marketplace": "US" }
```

---

## Recommended output structure

```markdown
# Competitor Analysis Report

## Top competitors

| # | ASIN | Brand | Price | Monthly sales | Rating | Reviews | Seller count |
|---|------|-------|-------|---------------|--------|---------|--------------|

## Competitive tiers
- Premium tier
- Mid-market tier
- Value tier

## What top listings emphasize
- Title patterns
- Feature patterns
- Packaging / use-case patterns

## Review-driven gaps
- Repeated customer complaints
- Missing features
- Quality issues
- Positioning gaps

## Strategic takeaway
[How to differentiate rather than copy]
```

---

## Analysis angles that matter most

### 1. Price architecture

Look for:
- dominant price clusters
- whether the market is polarized or concentrated
- whether premium players justify higher pricing with brand or feature density

### 2. Sales concentration

Look for:
- whether 1–3 products dominate demand
- whether newer brands are already breaking in
- whether smaller players still have room

### 3. Review barrier

Look for:
- how many reviews top performers have
- whether the market is locked by review count
- whether there are rising products with modest review counts

### 4. Listing strategy

Use `realtime/product` to inspect:
- title construction
- bullet-point positioning
- image / feature priorities
- variation strategy
- category and subcategory rank context

### 5. Review weaknesses

Use `topReviews` and `ratingBreakdown` to identify:
- recurring complaints
- missing features
- value-perception issues
- shipping or packaging problems
- quality consistency problems

---

## Decision guidance

Use this file when the user asks:

- "Analyze competitors"
- "Compare these products"
- "Why is this product winning?"
- "What are competitors doing differently?"
- "Where is the white space?"
