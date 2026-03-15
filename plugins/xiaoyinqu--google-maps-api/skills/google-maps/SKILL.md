---
name: google-maps
description: "Access Google Maps data without setup. Search places, geocode addresses, get directions. No Google Cloud account needed."
homepage: https://skillboss.co
---

# Google Maps API

**Location data without Google Cloud setup.**

## Capabilities

| Feature | Description |
|---------|-------------|
| **Places Search** | Find businesses, POIs |
| **Geocoding** | Address to coordinates |
| **Reverse Geocoding** | Coordinates to address |
| **Place Details** | Reviews, hours, photos |

## Usage Examples

### Search Places
```bash
curl https://api.heybossai.com/v1/run \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -d '{
    "model": "googlemap",
    "input": {
      "query": "coffee shops near Times Square NYC",
      "limit": 10
    }
  }'
```

### Geocode Address
```bash
curl https://api.heybossai.com/v1/run \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -d '{
    "model": "googlemap",
    "input": {
      "address": "1600 Amphitheatre Parkway, Mountain View, CA"
    }
  }'
```

## Data Returned

- Name, address, phone
- Coordinates (lat/lng)
- Rating, review count
- Business hours
- Website, Google Maps URL
- Place photos

## Use Cases

- Store locator
- Address validation
- Lead enrichment
- Local SEO research
- Delivery routing

## Why SkillBoss?

- **No Google Cloud account** needed
- **No API key management**
- **No billing setup**
- **Pay per request** - no minimums

## Pricing

$0.005 per request

Get started: https://skillboss.co/pricing?utm_source=clawhub&utm_medium=skill&utm_campaign=google-maps-api
