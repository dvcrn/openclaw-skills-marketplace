---
name: firecrawl
description: "Scrape any website to clean markdown or extract structured data with AI. Powered by Firecrawl. No rate limits, no blocked IPs."
homepage: https://skillboss.co
---

# Firecrawl Web Scraping

**Scrape any website, extract any data.**

## Capabilities

| Action | Description |
|--------|-------------|
| **scrape** | Convert any URL to clean markdown |
| **extract** | AI-powered structured data extraction |
| **map** | Generate sitemap of a domain |

## Usage Examples

### Scrape a page to markdown
```bash
curl https://api.heybossai.com/v1/run \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -d '{
    "model": "firecrawl/scrape",
    "input": {
      "url": "https://example.com/pricing"
    }
  }'
```

### Extract structured data
```bash
curl https://api.heybossai.com/v1/run \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -d '{
    "model": "firecrawl/extract",
    "input": {
      "url": "https://example.com/product",
      "schema": {
        "name": "string",
        "price": "number",
        "features": "array"
      }
    }
  }'
```

## Why SkillBoss?

- **No Firecrawl account** needed
- **No rate limits** - scrape at scale
- **No blocked IPs** - we handle proxies
- **Pay per use** - no monthly commitment

## Pricing

| Action | Cost |
|--------|------|
| scrape | $0.001/page |
| extract | $0.005/page |
| map | $0.01/domain |

Get started: https://skillboss.co/console?utm_source=clawhub&utm_medium=skill&utm_campaign=firecrawl-scraping
