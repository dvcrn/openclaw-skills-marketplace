# Pricing & Listing

> Stage 5: Help sellers define pricing, positioning, and listing strategy.
>
> Core question: What price point makes sense, and how should the listing be framed?

---

## APIs used in this file

- `markets/search` — category-level average pricing and market positioning data
- `products/search` — price-band distribution across top products
- `realtime/product` — listing content, features, and specification references from strong competitors

---

## Use cases

| # | Use case | Typical question |
|---|----------|------------------|
| 5.1 | Price-band analysis | "What is the right price range for this category?" |
| 5.2 | Profit and fee awareness | "Does this price range still leave room after fees?" |
| 5.3 | Listing reference study | "How are top listings structured?" |
| 5.4 | Positioning recommendation | "Should I launch as value, mid-market, or premium?" |

---

## Workflow

- Step 1/3: Pull category pricing signals with `markets/search`
- Step 2/3: Pull top products with `products/search` to understand actual price clusters
- Step 3/3: Pull a few strong competitor listings with `realtime/product` to study copy, features, and positioning

```bash
POST /openapi/v2/markets/search
{ "categoryPath": ["Electronics", "Headphones"], "topN": "10" }

POST /openapi/v2/products/search
{
  "keyword": "headphones",
  "sortBy": "monthlySales",
  "sortOrder": "desc",
  "pageSize": 50
}

POST /openapi/v2/realtime/product
{ "asin": "B09XXXXX", "marketplace": "US" }
```

---

## What to evaluate

### Pricing
- market average price
- top-seller price bands
- premium vs value clusters
- whether the category rewards low pricing or clear feature premiums

### Positioning
- value play
- mainstream / mid-market
- premium feature-led positioning
- beginner-friendly / giftable / niche-specific positioning

### Listing strategy
- title pattern
- feature and benefit hierarchy
- use-case language
- whether top players emphasize specs, outcomes, or lifestyle framing

---

## Suggested output structure

```markdown
# Pricing & Listing Strategy

## Market pricing overview
- category average price
- top-selling price bands
- recommended launch range

## Recommended positioning
- value / mid-market / premium
- target user
- key promise

## Listing guidance
- title direction
- bullet-point structure
- main selling points to emphasize
- points to avoid or downplay

## Pricing recommendation
[Recommended launch price and why]
```

---

## Decision guidance

Use this file when the user asks:

- "How should I price this?"
- "What price band should I target?"
- "How are top listings written?"
- "Should I position this as premium or value?"
