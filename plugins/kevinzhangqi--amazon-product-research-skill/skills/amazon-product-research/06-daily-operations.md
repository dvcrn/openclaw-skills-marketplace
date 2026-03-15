# Daily Operations

> Stage 6: Help sellers monitor market movement, competitor changes, and notable signals over time.
>
> Core question: What changed recently, and what deserves attention?

---

## APIs used in this file

- `products/search` — monitor product movement, rank changes, and filter-based watchlists
- `products/competitor-lookup` — monitor specific competitive sets
- `markets/search` — track market structure and category-level changes

---

## Typical use cases

| # | Use case | Typical question |
|---|----------|------------------|
| 6.1 | Market monitoring | "What changed in this category recently?" |
| 6.2 | Competitor watchlist | "What are my competitors doing?" |
| 6.3 | Top-product movement | "Which products are rising or weakening?" |
| 6.4 | Risk signals | "Is there anything I should pay attention to?" |

---

## Recommended workflow

- Step 1/3: Pull category-level metrics with `markets/search`
- Step 2/3: Pull top products or a filtered watchlist with `products/search`
- Step 3/3: Highlight changes in rank, new-product activity, pricing, sales momentum, and concentration

### What to monitor

- category concentration
- new SKU rate
- top product rank movement
- sales growth signals
- review growth spikes
- new entrants with low review counts
- competitor pricing changes
- seller-count changes indicating buy-box or competition pressure

---

## Suggested output structure

```markdown
# Market Watch Update

## Category-level changes
- concentration
- new product rate
- pricing movement

## Product-level changes
- rising products
- weakening products
- new entrants to watch

## Risks and opportunities
- possible saturation
- rising challengers
- price compression
- brand consolidation

## Suggested action
[What to monitor next or validate in detail]
```

---

## Decision guidance

Use this file when the user asks:

- "What changed in this category?"
- "What should I keep watching?"
- "Any new competitor worth paying attention to?"
- "What are the market signals right now?"
