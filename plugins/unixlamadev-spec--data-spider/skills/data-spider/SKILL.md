---
name: data-spider
description: "Extract structured data and insights from any webpage"
---

# Data Spider

Scrape and extract structured data from any webpage. Identifies facts, figures, names, dates, prices, and other concrete information. Returns organized data points with summary.

## When to Use

- Extracting product information from pages
- Gathering statistics and figures from articles
- Building datasets from web sources
- Research and competitive analysis

## Usage Flow

1. Provide a webpage URL
2. Specify what data to extract
3. AIProx routes to the data-spider agent
4. Returns data array, summary, and source URL

## Security Manifest

| Permission | Scope | Reason |
|------------|-------|--------|
| Network | aiprox.dev | API calls to orchestration endpoint |
| Env Read | AIPROX_SPEND_TOKEN | Authentication for paid API |

## Make Request

```bash
curl -X POST https://aiprox.dev/api/orchestrate \
  -H "Content-Type: application/json" \
  -H "X-Spend-Token: $AIPROX_SPEND_TOKEN" \
  -d '{
    "task": "extract all pricing and feature information",
    "url": "https://example.com/pricing"
  }'
```

### Response

```json
{
  "data": [
    "Free tier: $0/month, 1000 API calls",
    "Pro tier: $29/month, 50,000 API calls",
    "Enterprise tier: custom pricing, unlimited calls",
    "All plans include: SSL, 99.9% uptime SLA",
    "Annual billing saves 20%"
  ],
  "summary": "SaaS pricing page with three tiers targeting individuals, teams, and enterprises. Usage-based pricing model with API call limits.",
  "source": "https://example.com/pricing"
}
```

## Trust Statement

Data Spider fetches and analyzes webpage contents via URL. Content is processed transiently and not stored. Analysis is performed by Claude via LightningProx. Respects robots.txt and rate limits. Your spend token is used for payment only.
