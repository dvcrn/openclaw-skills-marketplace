# Product Opportunity Workflow

> Composite workflow for turning a broad product idea into a shortlist of viable opportunities.
>
> Best for sellers who start with a niche or category and want concrete product candidates.

---

## Input

| Parameter | Required | Description |
|-----------|----------|-------------|
| Category or keyword | Yes | Product area, niche, or keyword to explore |
| Goal | No | Growth / low competition / margin / beginner-friendly |
| Budget | No | Low / medium / high |

---

## Execution chain

- Step 1/4: Confirm the category with `categories`
- Step 2/4: Validate the category with `markets/search`
- Step 3/4: Pull product candidates with `products/search`
- Step 4/4: Inspect shortlisted ASINs with `realtime/product`

```yaml
Step 1: category confirmation
  tool: categories
  input: { categoryKeyword: "user keyword" }

Step 2: market validation
  tool: markets/search
  input: { categoryPath: [from step 1], topN: "10" }

Step 3: candidate discovery
  tool: products/search
  input: { keyword: "user keyword", sortBy: "monthlySales", sortOrder: "desc", pageSize: 20 }

Step 4: shortlist validation
  tool: realtime/product
  input: { asin: "shortlisted ASIN", marketplace: "US" }
```

---

## Recommended output structure

```markdown
# Product Opportunity Report

## Market fit
- Is the niche attractive?
- Is concentration manageable?
- Are there signs of room for entry?

## Candidate shortlist
| # | ASIN | Product | Price | Monthly sales | Rating | Reviews | Why it stands out |
|---|------|---------|-------|---------------|--------|---------|-------------------|

## Opportunity patterns
- high demand / low review barrier
- rising products
- underserved products
- price-band gaps

## Recommendation
- best first product to test
- products to avoid
- what to validate next
```

---

## Decision guidance

Use this workflow when the user asks for:

- product opportunities in a niche
- a shortlist of product ideas
- a product validation workflow
- the best products to test in a category
