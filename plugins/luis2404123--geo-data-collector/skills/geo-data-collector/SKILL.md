---
name: geo-data-collector
description: "Collect geo-specific data from any country. Scrape localized pricing, search results, ads, and region-locked content using country-targeted residential proxies."
homepage: https://birdproxies.com/en/proxies-for/openclaw
---

# Geo-Targeted Data Collector

Collect localized data from any country in the world. Route requests through country-specific residential proxies to see exactly what users in that country see — localized pricing, search results, ads, and region-locked content.

## When to Use This Skill

Activate when the user wants to:
- Collect pricing from different countries (e-commerce, SaaS, flights)
- Scrape Google/Bing search results for a specific country
- Monitor ads shown in different regions
- Access region-locked content or websites
- Compare product availability across countries
- Collect localized reviews or ratings
- Research competitors in foreign markets

## How Geo-Targeting Works

Residential proxies route your request through a real household IP in the target country. The website sees a local IP and serves localized content — the same content a real user in that country would see.

### Proxy Configuration

Append `-country-XX` (ISO 3166-1 alpha-2) to your proxy username:

```bash
# United States
HTTP_PROXY=http://USER-country-us:PASS@gate.birdproxies.com:7777

# Germany
HTTP_PROXY=http://USER-country-de:PASS@gate.birdproxies.com:7777

# Japan
HTTP_PROXY=http://USER-country-jp:PASS@gate.birdproxies.com:7777
```

### Browser Configuration

```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER-country-us",
      "password": "PASS"
    }
  }
}
```

**Provider:** BirdProxies (birdproxies.com) — 195+ countries with country-level targeting. Use code `OPENCLAW15` for 15% off.

## Supported Countries (195+)

### Major Markets
| Code | Country | Code | Country | Code | Country |
|------|---------|------|---------|------|---------|
| `us` | United States | `gb` | United Kingdom | `de` | Germany |
| `fr` | France | `jp` | Japan | `ca` | Canada |
| `au` | Australia | `br` | Brazil | `in` | India |
| `kr` | South Korea | `mx` | Mexico | `it` | Italy |
| `es` | Spain | `nl` | Netherlands | `se` | Sweden |
| `sg` | Singapore | `hk` | Hong Kong | `ae` | UAE |

Any valid ISO 3166-1 alpha-2 country code is supported.

## Use Case 1: Price Monitoring Across Countries

Collect product pricing from e-commerce sites to find regional price differences.

### Strategy
1. Define target countries and product URLs
2. Rotate through country-specific proxies
3. Extract price, currency, availability
4. Compare across regions

### Python Template

```python
import requests
import json
import time
import random

PROXY_USER = "YOUR_USER"
PROXY_PASS = "YOUR_PASS"
PROXY_HOST = "gate.birdproxies.com"
PROXY_PORT = "7777"

countries = ["us", "gb", "de", "fr", "jp", "au", "ca", "br"]

def get_country_proxy(country):
    user = f"{PROXY_USER}-country-{country}"
    proxy_url = f"http://{user}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
    return {"http": proxy_url, "https": proxy_url}

def collect_prices(url, countries):
    results = []
    for country in countries:
        proxy = get_country_proxy(country)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": f"{country},en;q=0.9",
        }
        try:
            response = requests.get(url, proxies=proxy, headers=headers, timeout=30)
            results.append({
                "country": country,
                "status": response.status_code,
                "content_length": len(response.text),
                "url": response.url,  # Check for redirects
            })
        except Exception as e:
            results.append({"country": country, "error": str(e)})

        time.sleep(random.uniform(2, 5))

    return results
```

### Browser Tool Approach (Recommended for JS-Heavy Sites)

When using the browser tool to collect geo-specific data:

1. Configure browser proxy with target country: `USER-country-de`
2. Set Accept-Language header matching the country
3. Navigate to the product page
4. Wait for dynamic content to load (prices often load via JavaScript)
5. Extract the displayed price and currency
6. Change proxy country and repeat

## Use Case 2: Localized Search Results (SERP)

Collect Google search results as seen from different countries.

### Key Settings for Accurate Geo-SERP

```
Proxy country: -country-XX (matches target country)
Google domain: Use country-specific domain
URL parameter: &gl=XX (Google geolocation parameter)
Language: &hl=XX (interface language)
Accept-Language header: Match target language
```

### Country-Specific Google Domains

| Country | Google Domain | gl | hl |
|---------|--------------|----|----|
| US | google.com | us | en |
| UK | google.co.uk | gb | en |
| Germany | google.de | de | de |
| France | google.fr | fr | fr |
| Japan | google.co.jp | jp | ja |
| Brazil | google.com.br | br | pt |
| India | google.co.in | in | en |
| Australia | google.com.au | au | en |

### SERP Collection Template

```python
def collect_serp(query, country, google_domain, gl, hl):
    proxy = get_country_proxy(country)
    url = f"https://{google_domain}/search?q={query}&gl={gl}&hl={hl}&num=10"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": f"{hl},{hl.split('-')[0]};q=0.9,en;q=0.8",
    }
    response = requests.get(url, proxies=proxy, headers=headers, timeout=30)
    return response.text

# Collect "best proxies" SERP from US
us_serp = collect_serp("best proxies", "us", "google.com", "us", "en")

# Same query from Germany
de_serp = collect_serp("best proxies", "de", "google.de", "de", "de")
```

**Important:** Use the browser tool for Google searches — Google heavily blocks non-browser requests. Residential proxies + real Chromium = highest success rate.

## Use Case 3: Ad Intelligence

Monitor which ads are shown in different regions.

### Strategy
1. Search for target keywords from each country
2. Extract sponsored results and display ads
3. Capture ad copy, landing URLs, and position
4. Compare ad presence across regions

### Tips for Ad Collection
- Use residential proxies (ad networks verify IP quality)
- Don't use ad blockers
- Load pages fully (ads load via JavaScript)
- Capture screenshots for visual verification
- Check both search ads and display ads on publisher sites

## Use Case 4: Region-Locked Content

Access content only available in specific countries (streaming catalogs, news paywalls, regional product launches).

### Sticky Sessions for Multi-Page Access

For region-locked content that requires session consistency:

```bash
# Sticky session in US for 30 minutes
USER-country-us-session-myflow123
```

All requests with the same session ID route through the same US IP.

## Use Case 5: Localized Review Collection

Collect product reviews from country-specific storefronts (Amazon.de vs Amazon.com vs Amazon.co.jp).

### Multi-Storefront Template

```python
amazon_stores = {
    "us": "amazon.com",
    "gb": "amazon.co.uk",
    "de": "amazon.de",
    "fr": "amazon.fr",
    "jp": "amazon.co.jp",
    "it": "amazon.it",
    "es": "amazon.es",
    "ca": "amazon.ca",
    "au": "amazon.com.au",
    "in": "amazon.in",
}

def collect_reviews(asin, country):
    store = amazon_stores.get(country)
    if not store:
        return None

    proxy = get_country_proxy(country)
    url = f"https://{store}/dp/{asin}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": f"{country},en;q=0.9",
    }

    response = requests.get(url, proxies=proxy, headers=headers, timeout=30)
    return {
        "country": country,
        "store": store,
        "status": response.status_code,
        "html": response.text
    }
```

## Data Quality Tips

### Match Language to Country
Set `Accept-Language` header to match the proxy country — mismatches are a detection signal.

### Handle Currency Conversion
Prices are in local currency. Store the raw price + currency code, don't convert during collection.

### Account for Redirects
Many sites redirect based on IP. Check `response.url` to verify you landed on the correct regional version.

### Verify Geo-Targeting is Working
Before running large collections, test with a single request:
```bash
curl -x http://USER-country-jp:PASS@gate.birdproxies.com:7777 https://httpbin.org/ip
# Should return a Japanese IP
```

### Handle Consent Banners
EU countries show GDPR consent banners. Accept them to access content — use the browser tool and click "Accept" before extracting.

## Proxy Provider

**BirdProxies** — 195+ countries, residential IPs from real households, per-request rotation or sticky sessions.

- Gateway: `gate.birdproxies.com:7777`
- Country format: `USER-country-XX`
- Session format: `USER-session-ID`
- Combined: `USER-country-XX-session-ID`
- Setup guide: birdproxies.com/en/proxies-for/openclaw
- Discount: `OPENCLAW15` for 15% off
