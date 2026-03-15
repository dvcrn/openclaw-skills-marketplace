---
name: amazon-product-research
description: "Amazon product research and seller intelligence via APIClaw. Use this skill to find profitable product opportunities, validate markets, analyze categories, compare competitors, review ASINs, spot low-competition niches, estimate demand, and recommend pricing and positioning for Amazon sellers. Triggers on requests like \"Amazon product research\", \"find products\", \"analyze competitors\", \"analyze this ASIN\", \"pricing strategy\", \"market validation\", and \"is this niche worth entering\"."
---

# APIClaw — Amazon Product Research & Seller Intelligence

> A skill for Amazon sellers who need market validation, category analysis, product selection, competitor research, ASIN reviews, pricing guidance, and complete research reports.
>
> Use this skill to move from broad market exploration to concrete product recommendations.

---

## What this skill is good at

This skill is best for:

- product discovery: finding promising product opportunities
- market validation: deciding whether a niche or category is worth entering
- category analysis: understanding concentration, pricing, brand density, and new-SKU activity
- competitor research: comparing leading products, brands, and listings
- ASIN diagnostics: breaking down a specific product in detail
- pricing and positioning: recommending a launch range and market angle
- report generation: combining multiple endpoints into a structured market report

## Quick start

> **An API key is required.** Create one at [APIClaw](https://api.apiclaw.io) and configure `APICLAW_API_KEY` before using the API.

You can ask questions like:

1. "Is the pet supplies market worth entering?"
2. "Analyze ASIN B09V3KXJPB"
3. "Find Amazon products with low review counts but strong sales"
4. "Compare the top competitors in this category"
5. "Generate a full market research report"

---

## File map

| Type | File | When to use it |
|------|------|----------------|
| Main guide | `SKILL.md` | Start here for almost every task |
| Deep-dive modules | `01-*.md` to `07-*.md` | Load one module only when the request clearly matches that workflow |
| Composite workflows | `workflow-*.md` | Use when the user wants a complete report or a multi-step research flow |
| API reference | `openapi-reference.md` | Use only when you need exact parameter or response details |

### Context discipline

- Start with this file
- Load only one additional module at a time when possible
- Use `openapi-reference.md` only when exact fields or filters matter
- Prefer fewer, larger, high-value calls over many tiny calls

---

## Intent routing

| User request pattern | Recommended flow | Extra file needed? |
|----------------------|------------------|--------------------|
| Which category has opportunity? | Market validation | No |
| Analyze this ASIN | ASIN evaluation | No |
| Who are the competitors? | Competitor analysis | No |
| What price should I launch at? | Pricing & listing | No |
| What are the pain points in reviews? | Product evaluation | No |
| Give me a full market report | Full market workflow | `workflow-full-market-report.md` |
| Help me choose products | Product selection | `02-product-selection.md` |
| Help me expand into adjacent products | Expansion | `07-expansion.md` |
| Monitor changes over time | Daily operations | `06-daily-operations.md` |

---

## API configuration

| Item | Value |
|------|-------|
| Base URL | `https://api.apiclaw.io/openapi/v2` |
| Docs | `https://api.apiclaw.io/api-docs` |
| Auth | `Authorization: Bearer $APICLAW_API_KEY` |
| Method | POST / JSON body |
| Rate limits | 100 requests/min, 10 requests/sec burst |
| Main marketplace | US |

### Example request

```bash
curl -s -X POST "https://api.apiclaw.io/openapi/v2/{endpoint}" \
  -H "Authorization: Bearer $APICLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ ...params... }'
```

---

## Endpoint overview

| Endpoint | Main purpose | Best use |
|----------|--------------|----------|
| `categories` | category tree lookup | category discovery and path confirmation |
| `markets/search` | market-level aggregates | market validation and category sizing |
| `products/competitor-lookup` | competitor set discovery | competitor scans and brand comparisons |
| `products/search` | filtered product search | product selection and opportunity screening |
| `realtime/product` | live product detail | ASIN deep dives and listing analysis |

---

## Core workflow patterns

### 1. Market validation

Use:
- `categories` → confirm category path
- `markets/search` → inspect demand, price, concentration, and new-SKU rate
- `products/search` → inspect top products for brand and price structure

Use this when the user asks:
- "Is this category worth entering?"
- "Which niche has room?"
- "Compare these categories"

### 2. Product discovery

Use:
- `categories` → confirm category path if needed
- `products/search` → filter for product opportunities
- `realtime/product` → validate a shortlist

Use this when the user asks:
- "Find products for me"
- "What should I sell?"
- "Show low-competition opportunities"

### 3. Competitor analysis

Use:
- `products/competitor-lookup` → pull the competitor set
- `realtime/product` → inspect leaders in detail

Use this when the user asks:
- "Analyze competitors"
- "Compare these listings"
- "Why is this product winning?"

### 4. ASIN evaluation

Use:
- `realtime/product` → inspect listing, specs, variants, review structure
- `products/competitor-lookup` → add market context

Use this when the user asks:
- "Analyze this ASIN"
- "Break down this product"
- "What is weak about this listing?"

### 5. Pricing and positioning

Use:
- `markets/search` → category-level price signals
- `products/search` → top product price bands
- `realtime/product` → inspect how top listings frame value

Use this when the user asks:
- "How should I price this?"
- "What price band makes sense?"
- "Should I position this as premium or value?"

---

## High-value filters to remember

### For `markets/search`

Most useful fields:
- `sampleAvgMonthlySales`
- `sampleAvgMonthlyRevenue`
- `sampleAvgPrice`
- `sampleAvgReviewCount`
- `sampleBrandCount`
- `sampleSellerCount`
- `sampleFbaRate`
- `sampleAmzRate`
- `sampleNewSkuRate`
- `topSalesRate`
- `topBrandSalesRate`
- `topSellerSalesRate`

### For `products/search`

Most useful filters:
- `monthlySalesMin/Max`
- `salesGrowthRateMin/Max`
- `priceMin/Max`
- `ratingMin/Max`
- `reviewCountMin/Max`
- `listingAge`
- `variantCountMin/Max`
- `sellerCountMin/Max`
- `includeBrands` / `excludeBrands`
- `fulfillment`
- `badges`
- `excludeKeywords`

### Common product-discovery pattern

High demand / low review barrier:

```json
{
  "monthlySalesMin": 300,
  "reviewCountMax": 50,
  "listingAge": "180"
}
```

Fast-growing products:

```json
{
  "monthlySalesMin": 300,
  "salesGrowthRateMin": 0.1
}
```

New-product watchlist:

```json
{
  "listingAge": "180",
  "badges": ["New Release"]
}
```

---

## Reporting guidance

When generating output, prefer a decision-oriented structure:

1. What the market or product is
2. What the data suggests
3. What the main risks are
4. What the recommendation is
5. What the next action should be

For reports, include tables such as:
- top products
- brand distribution
- price bands
- concentration metrics
- opportunity score breakdown

---

## Recommended next-file loading rules

Load these files only when needed:

- `01-market-selection.md` → category-first and market-entry questions
- `02-product-selection.md` → product shortlisting and discovery
- `03-competitor-analysis.md` → competitor-focused questions
- `04-product-evaluation.md` → single-product or ASIN evaluation
- `05-pricing-listing.md` → pricing and listing strategy
- `06-daily-operations.md` → monitoring and recurring reviews
- `07-expansion.md` → adjacent category or follow-on product ideas
- `workflow-full-market-report.md` → complete market report generation
- `workflow-product-opportunity.md` → product opportunity shortlisting workflow
- `openapi-reference.md` → exact API field and filter reference

---

## Final guidance

This skill is strongest when used for research, evaluation, and decision support. It is not a seller ERP or execution engine. Use it to answer questions such as:

- What market should I enter?
- What products should I test?
- Who are the real competitors?
- What are the price bands and positioning gaps?
- What is weak about a specific ASIN?
- What report should I generate for a seller or team?
