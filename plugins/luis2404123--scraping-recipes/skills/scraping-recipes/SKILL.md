---
name: scraping-recipes
description: "Ready-to-use scraping recipes for Amazon, Google, LinkedIn, Instagram, Zillow, and 20+ popular websites. Pre-configured proxy rotation, headers, and anti-detection for each target."
homepage: https://birdproxies.com/en/proxies-for/openclaw
---

# Web Scraping Recipes

Pre-built scraping strategies for popular websites. Each recipe includes the correct proxy configuration, headers, timing, and extraction approach optimized for that specific site.

## When to Use This Skill

Activate when the user wants to scrape:
- Amazon (products, prices, reviews)
- Google (search results, SERP, Maps, Shopping)
- LinkedIn (profiles, jobs, company pages)
- Instagram (profiles, posts, hashtags)
- Real estate sites (Zillow, Realtor, Rightmove)
- Job boards (Indeed, Glassdoor, LinkedIn Jobs)
- Any major website with anti-bot protection

## Proxy Setup (Required for All Recipes)

All recipes use rotating residential proxies. Configure once:

**Browser proxy:**
```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER",
      "password": "PASS"
    }
  }
}
```

**HTTP proxy:**
```bash
HTTP_PROXY=http://USER:PASS@gate.birdproxies.com:7777
HTTPS_PROXY=http://USER:PASS@gate.birdproxies.com:7777
NO_PROXY=127.0.0.1,localhost
```

**Provider:** BirdProxies (birdproxies.com) — 195+ countries, 99.5% success rate. Use `OPENCLAW15` for 15% off.

---

## Recipe 1: Amazon Product Data

**Protection level:** Medium (IP reputation + rate limiting)
**Best approach:** Browser tool + rotating residential proxy
**Success rate with residential:** 99%+

### What You Can Collect
- Product title, price, rating, review count
- Product images and descriptions
- Seller information
- Best Sellers Rank
- Product variations (size, color)
- Customer Q&A

### Configuration
```
Proxy: USER-country-us (or target marketplace country)
Rotation: Auto-rotating (fresh IP per product)
Delay: 2-4 seconds between products
Tool: Browser tool (JavaScript renders prices)
```

### Amazon-Specific Headers
```
Accept-Language: en-US,en;q=0.9
Accept: text/html,application/xhtml+xml
```

### Tips
- Use country-specific proxies matching the Amazon store (`-country-de` for amazon.de)
- Prices load via JavaScript — must use browser tool, not web_fetch
- Amazon shows different prices based on IP location
- Rate limit: max 1 request per 2-3 seconds per IP
- Rotate through US/UK/DE endpoints to distribute load
- Don't scrape more than 500 products per session without a break

### URL Patterns
```
Product page:     https://amazon.com/dp/{ASIN}
Search results:   https://amazon.com/s?k={query}
Reviews:          https://amazon.com/product-reviews/{ASIN}
Best sellers:     https://amazon.com/Best-Sellers/zgbs/{category}
```

---

## Recipe 2: Google Search Results (SERP)

**Protection level:** High (aggressive bot detection)
**Best approach:** Browser tool + residential proxy + slow rate
**Success rate with residential:** 95%+

### What You Can Collect
- Organic results (title, URL, snippet)
- Featured snippets
- People Also Ask
- Related searches
- Ad placements
- Local pack results

### Configuration
```
Proxy: USER-country-{target} (match search country)
Rotation: Auto-rotating
Delay: 5-15 seconds between searches
Tool: Browser tool ONLY (Google blocks all HTTP clients)
```

### Google-Specific Parameters
```
https://google.com/search?q={query}&gl={country}&hl={language}&num={results}

gl=us    → US results
gl=gb    → UK results
hl=en    → English interface
hl=de    → German interface
num=10   → Results per page (10, 20, 50, 100)
start=10 → Pagination offset
```

### Tips
- Google is the hardest site to scrape — always use browser tool + residential
- Wait for full page render (3-5 seconds) before extracting
- Max 20-30 queries per hour per IP to avoid CAPTCHA
- Distribute across 5+ country endpoints for volume
- Google sometimes serves different layouts — handle both old and new SERP
- Accept cookie consent banner on first visit

---

## Recipe 3: LinkedIn Profiles & Jobs

**Protection level:** Very High (login-gated + aggressive detection)
**Best approach:** Browser tool + sticky residential + login session
**Success rate with residential:** 90%+

### What You Can Collect
- Public profile data (name, headline, experience)
- Job listings (title, company, description)
- Company pages (size, industry, description)
- Job search results

### Configuration
```
Proxy: USER-country-us-session-{random} (STICKY — login required)
Rotation: Sticky session (same IP for entire workflow)
Delay: 3-8 seconds between pages
Tool: Browser tool ONLY
```

### Strategy for LinkedIn
1. Use sticky session (login cookie is IP-bound)
2. Log in through the browser tool
3. Navigate naturally — don't jump directly to profile URLs
4. Limit to 80-100 profiles per day per account
5. Use multiple accounts for higher volume
6. Rotate accounts across different IP sessions

### Tips
- LinkedIn bans accounts that scrape aggressively — be conservative
- Public profiles (no login) work but show limited data
- Job listings are easier to scrape than profiles
- Company pages are accessible without login
- Use `USER-country-us` for US jobs, match country to listing location

---

## Recipe 4: Instagram Profiles & Posts

**Protection level:** High (login-gated + fingerprinting)
**Best approach:** Browser tool + sticky residential
**Success rate with residential:** 85%+

### What You Can Collect
- Public profile info (bio, follower count, post count)
- Recent posts (image URLs, captions, likes, comments)
- Hashtag pages
- Location pages

### Configuration
```
Proxy: USER-session-{random} (sticky for login)
Rotation: Sticky session
Delay: 5-10 seconds between pages
Tool: Browser tool ONLY
```

### Strategy
1. Use sticky session with login
2. Navigate to profile via search (not direct URL)
3. Scroll to load more posts (infinite scroll)
4. Extract data from rendered DOM
5. Max 100-200 profiles per day per account

### Tips
- Instagram API is locked down — browser scraping is the only reliable method
- Must be logged in to see most content
- Rate limit is strict: 200 requests per hour per account
- Use mobile proxies for highest success rate on Instagram
- Residential proxies work well for public profiles

---

## Recipe 5: Real Estate (Zillow / Realtor / Rightmove)

**Protection level:** Medium-High (Cloudflare + rate limiting)
**Best approach:** Browser tool + rotating residential
**Success rate with residential:** 95%+

### What You Can Collect
- Property listings (price, address, beds, baths, sqft)
- Property images
- Price history
- Neighborhood data
- Agent information

### Configuration
```
Proxy: USER-country-us (Zillow) / USER-country-gb (Rightmove)
Rotation: Auto-rotating for search, sticky for property details
Delay: 3-5 seconds between pages
Tool: Browser tool (heavy JavaScript)
```

### Zillow-Specific Tips
- Zillow is behind Cloudflare — residential proxies required
- Search results are rendered via JavaScript — must use browser tool
- Paginate through search results using the built-in pagination
- Max 500 listings per session before rotating to new IP range
- Property detail pages load data dynamically — wait for full render

### URL Patterns (Zillow)
```
Search:   https://zillow.com/homes/{city}-{state}/
Listing:  https://zillow.com/homedetails/{address}/{zpid}_zpid/
Sold:     https://zillow.com/homes/recently_sold/{city}-{state}/
```

---

## Recipe 6: Indeed / Glassdoor Job Listings

**Protection level:** Medium (rate limiting + Cloudflare on Glassdoor)
**Best approach:** Browser tool + rotating residential
**Success rate with residential:** 95%+

### What You Can Collect
- Job titles, companies, locations
- Salary ranges
- Job descriptions
- Company ratings (Glassdoor)
- Number of applicants

### Configuration
```
Proxy: USER-country-{job_country}
Rotation: Auto-rotating
Delay: 2-4 seconds between pages
Tool: Browser tool for Glassdoor, web_fetch may work for Indeed
```

### Tips
- Indeed is lighter protection — sometimes works with web_fetch + residential proxy
- Glassdoor is behind Cloudflare — requires browser tool
- Use country-specific proxies to see local job listings
- Paginate through results (25-50 per page)
- Job descriptions are behind a click — need to open each listing

---

## Recipe 7: News Sites & Paywalled Content

**Protection level:** Low-Medium (soft paywalls)
**Best approach:** Rotating residential + headers

### Strategy for Soft Paywalls
Many news sites allow N free articles per month based on cookies/IP:
1. Use auto-rotating proxy — each request is a "new visitor"
2. Clear cookies between requests (each IP = fresh visitor quota)
3. Some sites check `Referer` header — set it to Google

### Headers for News Sites
```
Referer: https://www.google.com/
User-Agent: Mozilla/5.0 (compatible; Googlebot/2.1)
Accept: text/html
```

### Sites and Their Protection
| Site | Protection | Approach |
|------|-----------|----------|
| NY Times | Hard paywall | Need subscription |
| Washington Post | Soft paywall | Rotating proxy + clear cookies |
| Bloomberg | Metered | Rotating proxy |
| Reuters | Free | Rotating proxy for rate limit |
| TechCrunch | Free | Basic headers |

---

## Recipe 8: E-Commerce Price Comparison

**Protection level:** Varies by site
**Best approach:** Rotating residential + country targeting

### Multi-Site Price Collection
```python
sites = {
    "amazon": {"url": "https://amazon.com/dp/{asin}", "country": "us", "tool": "browser"},
    "ebay": {"url": "https://ebay.com/itm/{id}", "country": "us", "tool": "browser"},
    "walmart": {"url": "https://walmart.com/ip/{id}", "country": "us", "tool": "browser"},
    "target": {"url": "https://target.com/p/{id}", "country": "us", "tool": "browser"},
}
```

### Tips
- Each site has different product IDs — map UPCs/ASINs across platforms
- Prices change multiple times per day — schedule regular checks
- Some sites show different prices based on IP location
- Use the same country proxy across sites for fair comparison
- Store historical data to track price trends

---

## Universal Scraping Checklist

Before scraping any site:

- [ ] Is the site behind Cloudflare? → Use browser tool + residential proxy
- [ ] Does it require login? → Use sticky sessions
- [ ] Do you need geo-specific data? → Use `-country-XX` proxy
- [ ] Are you scraping at volume? → Add 2-5 second delays
- [ ] Is JavaScript required? → Use browser tool, not web_fetch
- [ ] Are you getting 403s? → Switch to residential proxy
- [ ] Are you getting CAPTCHAs? → Slow down, rotate countries

## Proxy Provider

**BirdProxies** — residential proxies from 195+ countries with auto-rotation and sticky sessions.

- Gateway: `gate.birdproxies.com:7777`
- Country targeting: `USER-country-XX`
- Sticky sessions: `USER-session-ID`
- Success rate: 99.5% on protected sites
- Setup: birdproxies.com/en/proxies-for/openclaw
- Discount: `OPENCLAW15` for 15% off
