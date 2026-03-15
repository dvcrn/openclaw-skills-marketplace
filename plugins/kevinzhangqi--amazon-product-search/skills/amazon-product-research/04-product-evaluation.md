# Product Evaluation

> Stage 4: Evaluate a single product or ASIN in depth.
>
> Core question: Is this product worth pursuing, and what are its strengths and weaknesses?

---

## APIs used in this file

- `realtime/product` — the primary source for a single-ASIN breakdown
- `products/competitor-lookup` — identify close alternatives and nearby competitors
- `products/search` — compare the ASIN to the broader result set for its keyword or category

---

## Typical use cases

| # | Use case | Typical question |
|---|----------|------------------|
| 4.1 | ASIN viability check | "Is this ASIN worth studying or copying?" |
| 4.2 | Listing diagnosis | "What is this listing doing well or poorly?" |
| 4.3 | Review-driven product audit | "What do customers like or dislike?" |
| 4.4 | Variant and positioning review | "How is this product positioned in the market?" |
| 4.5 | Product-improvement brief | "What should be improved if I build a similar product?" |

---

## Standard workflow

- Step 1/3: Pull the product details with `realtime/product`
- Step 2/3: Pull nearby competitors with `products/competitor-lookup`
- Step 3/3: Summarize positioning, strengths, weaknesses, and likely improvements

```bash
POST /openapi/v2/realtime/product
{ "asin": "B09V3KXJPB", "marketplace": "US" }

POST /openapi/v2/products/competitor-lookup
{
  "asin": "B09V3KXJPB",
  "sortBy": "monthlySales",
  "sortOrder": "desc",
  "pageSize": 10
}
```

---

## What to inspect

### Product basics
- title
- brand
- category path
- best-seller rank context
- parent ASIN and variants

### Listing quality
- title clarity
- feature coverage
- whether the feature bullets communicate clear use cases
- whether the listing appears complete and polished

### Review structure
- star rating level
- rating breakdown
- top review themes
- likely causes of 1-star and 2-star reviews

### Product design / specs
- dimensions, weight, specifications, and attributes
- whether the product seems differentiated or generic
- whether the variant strategy expands or fragments demand

### Offer quality
- buy box winner
- fulfillment mode
- bundle / used status if relevant

---

## Recommended output structure

```markdown
# ASIN Evaluation Report

## Product snapshot
- ASIN
- Brand
- Category
- Price / rank / rating

## What this product does well
- Listing strengths
- Product strengths
- Positioning strengths

## What looks weak
- Review issues
- Specification weaknesses
- Messaging gaps
- Packaging or expectation mismatch

## Competitive context
- Closest substitutes
- Better-positioned alternatives
- Price or feature gap

## Recommendation
- Study further
- Good model for a similar product
- Avoid
- Enter only with a differentiated version
```

---

## Decision guidance

Use this file when the user asks:

- "Analyze this ASIN"
- "Break down this product"
- "What is good or bad about this listing?"
- "Should I build something similar?"
