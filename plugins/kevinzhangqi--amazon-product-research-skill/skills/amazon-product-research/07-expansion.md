# Expansion

> Stage 7: Help sellers expand beyond a current product or category.
>
> Core question: What should I launch next?

---

## APIs used in this file

- `categories` — discover adjacent categories and subcategories
- `markets/search` — evaluate whether adjacent markets are attractive
- `products/search` — shortlist adjacent or follow-on products
- `products/competitor-lookup` — understand who already owns nearby spaces

---

## Main use cases

| # | Use case | Typical question |
|---|----------|------------------|
| 7.1 | Adjacent product discovery | "What else can I sell around this product?" |
| 7.2 | New-category evaluation | "What should I test next?" |
| 7.3 | Trend expansion | "Where should I expand if this niche works?" |
| 7.4 | Product retirement decision | "Should I shift away from this product?" |

---

## Workflow

- Step 1/3: Identify adjacent categories or related product spaces with `categories`
- Step 2/3: Evaluate those markets using `markets/search`
- Step 3/3: Pull product candidates using `products/search` and rank them by fit and difficulty

### What to look for

- adjacent categories with healthier concentration
- categories with stronger new-product rates
- related products sharing similar buyers or use cases
- easier price bands or lower review barriers
- gaps where current competitors are weak

---

## Suggested output structure

```markdown
# Expansion Opportunities

## Recommended next directions
- adjacent category options
- follow-on products
- trend-driven opportunities

## Comparison
| Direction | Market size | Concentration | Review barrier | Price band | Priority |
|-----------|-------------|---------------|----------------|------------|----------|

## Recommendation
[What to test first and why]
```

---

## Decision guidance

Use this file when the user asks:

- "What can I expand into next?"
- "What related products should I add?"
- "What new category should I test?"
- "Should I keep pushing this product or move elsewhere?"
