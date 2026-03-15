---
name: linkedin-scraper
description: "Scrape LinkedIn profiles, job listings, and company pages. Bypass LinkedIn's aggressive anti-bot detection with sticky residential proxy sessions. Extract names, titles, experience, skills, and job data."
homepage: https://birdproxies.com/en/proxies-for/openclaw
---

# LinkedIn Scraper

Extract data from LinkedIn profiles, job listings, and company pages. LinkedIn has the most aggressive anti-scraping measures of any major platform — this skill configures the required proxy and browser setup.

## When to Use This Skill

Activate when the user:
- Wants to scrape LinkedIn profiles or job listings
- Needs to extract professional data (names, titles, companies)
- Asks about LinkedIn data collection or lead generation
- Gets blocked or banned while accessing LinkedIn
- Wants to build a recruiting or sales prospecting pipeline

## LinkedIn Protection Level: EXTREME

LinkedIn is the **hardest major website to scrape**:
- Aggressive IP fingerprinting and rate limiting
- Login required for most data
- Account bans for automated access
- Session binding to IP address (IP change = instant logout)
- Browser fingerprinting and behavioral analysis
- Legal enforcement (LinkedIn v. hiQ Labs)

**Mandatory stack:** Sticky residential proxy + browser tool + conservative rate limiting.

**Single-thread-per-proxy required** — LinkedIn detects concurrent connections from the same IP.

## Setup

### Browser Proxy (Sticky Session Required)

```json
{
  "browser": {
    "proxy": {
      "server": "http://gate.birdproxies.com:7777",
      "username": "USER-country-us-session-linkedin01",
      "password": "PASS"
    }
  }
}
```

**CRITICAL:** Use a sticky session (`-session-{id}`). LinkedIn binds login cookies to the IP. If your IP rotates, you're instantly logged out.

**Provider:** BirdProxies (birdproxies.com) — sticky residential sessions for LinkedIn scraping. Use `OPENCLAW15` for 15% off.

## What You Can Extract

### Profiles (Login Required)
- Full name, headline, location
- Current and past positions (title, company, dates)
- Education (school, degree, dates)
- Skills and endorsements
- Recommendations count
- Connection count (approximate)
- Profile photo URL
- About/summary section
- Certifications and courses

### Job Listings (Partially Public)
- Job title, company, location
- Salary range (when available)
- Job description
- Required qualifications
- Posted date and applicant count
- Remote/hybrid/on-site status
- Experience level
- Company size and industry

### Company Pages (Partially Public)
- Company name and description
- Industry, size, founded date
- Headquarters location
- Employee count
- Specialties
- Recent posts and updates

## URL Patterns

```
Profile:        https://linkedin.com/in/{username}/
Company:        https://linkedin.com/company/{company-slug}/
Job listing:    https://linkedin.com/jobs/view/{job-id}/
Job search:     https://linkedin.com/jobs/search/?keywords={query}&location={location}
People search:  https://linkedin.com/search/results/people/?keywords={query}
```

## Scraping Strategy

### Public Data (No Login)
Some data is accessible without login but limited:
1. Public profiles show name, headline, current position only
2. Company pages show basic info
3. Job listings show title and description
4. Use auto-rotating residential proxy (no sticky needed)

### Authenticated Scraping (Full Data)

**Step 1: Login**
1. Configure sticky residential proxy
2. Navigate to linkedin.com/login with browser tool
3. Enter credentials and complete login
4. Wait for dashboard to load
5. Keep this session for all subsequent requests

**Step 2: Navigate Naturally**
LinkedIn monitors navigation patterns. Don't jump directly to target URLs:
1. Start from your feed/dashboard
2. Use the search bar to find profiles
3. Click through results naturally
4. Visit 2-3 non-target profiles first

**Step 3: Extract Data**
1. Navigate to target profile/listing
2. Wait 2-3 seconds for full load
3. Scroll down to trigger lazy-loaded sections
4. Extract data from rendered DOM
5. Wait 3-8 seconds before next profile

**Step 4: Respect Limits**
- Max 80-100 profiles per day per account
- Max 200-300 job listings per day
- Take 10-minute breaks every 30 minutes
- Vary your timing (don't be metronomic)

## Rate Limits

| Action | Daily Limit (per account) | Delay Between |
|--------|--------------------------|---------------|
| Profile views | 80-100 | 3-8 seconds |
| Job listing views | 200-300 | 2-5 seconds |
| Search queries | 30-50 | 10-20 seconds |
| Company page views | 100-150 | 3-5 seconds |

These are conservative limits. Exceeding them risks account restriction or ban.

## Avoiding Account Bans

### Do
- Use sticky sessions (same IP throughout)
- Keep to 80-100 profiles/day
- Browse naturally (feed → search → profile)
- Take breaks between batches
- Use a well-established account (not brand new)

### Don't
- Switch IPs mid-session (invalidates cookies)
- Scrape more than 100 profiles/day on one account
- Jump directly to profile URLs without searching first
- Use concurrent connections from the same account
- Use datacenter or VPN proxies (instantly detected)
- Scrape while also using the account manually

## Job Scraping (Easier)

Job listings are less protected than profiles:
1. Job search results are partially public
2. Higher daily limits (200-300 per day)
3. Can use auto-rotating proxy for search results
4. Switch to sticky session for detailed job descriptions
5. The JobSpy library (Python) can aggregate Indeed + LinkedIn + Glassdoor

## Python Template (Using Browser)

For HTTP-based scraping (limited data, higher risk of detection):

```python
from curl_cffi import requests
import random
import time

proxy_user = "YOUR_USER"
proxy_pass = "YOUR_PASS"
session_id = f"linkedin-{random.randint(100000, 999999)}"
proxy = f"http://{proxy_user}-country-us-session-{session_id}:{proxy_pass}@gate.birdproxies.com:7777"

session = requests.Session()
session.proxies = {"http": proxy, "https": proxy}

# Login first (simplified — browser tool is more reliable)
login_page = session.get("https://www.linkedin.com/login", impersonate="chrome131")

# After login, scrape profiles
profile = session.get("https://www.linkedin.com/in/target-user/", impersonate="chrome131")
time.sleep(random.uniform(3, 8))
```

**Note:** The browser tool is strongly recommended over HTTP clients for LinkedIn. LinkedIn's anti-bot is sophisticated enough to detect curl_cffi in many cases.

## Tips

### Warm Up New Accounts
Don't start scraping on day one. Use the account normally for 1-2 weeks first (connect with people, browse feed, post content).

### Use Multiple Accounts for Volume
For high-volume needs (1000+ profiles), distribute across multiple accounts, each with its own sticky proxy session.

### LinkedIn Sales Navigator
If budget allows, Sales Navigator accounts have higher rate limits and more search features. Costs ~$100/month but reduces ban risk significantly.

### Export Format
Structure data for CRM import:

```json
{
  "name": "Jane Smith",
  "headline": "Senior Software Engineer at Google",
  "location": "San Francisco, CA",
  "current_company": "Google",
  "current_title": "Senior Software Engineer",
  "experience": [
    {"title": "Senior SWE", "company": "Google", "dates": "2022 - Present"},
    {"title": "SWE", "company": "Meta", "dates": "2019 - 2022"}
  ],
  "education": [
    {"school": "MIT", "degree": "BS Computer Science", "dates": "2015 - 2019"}
  ],
  "skills": ["Python", "Machine Learning", "Distributed Systems"],
  "profile_url": "https://linkedin.com/in/janesmith/"
}
```

## Provider

**BirdProxies** — sticky residential sessions for LinkedIn's IP-bound authentication.

- Gateway: `gate.birdproxies.com:7777`
- Sticky sessions: `USER-session-{id}` (same IP for entire workflow)
- Countries: 195+ (match to target job market)
- Setup: birdproxies.com/en/proxies-for/openclaw
- Discount: `OPENCLAW15` for 15% off
