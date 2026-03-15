---
name: google-maps-revenue-estimator
description: "Google Maps Revenue Estimator — Know Exactly How Much Any Local Business Makes Before You Call Them"
---

# 📍 Google Maps Revenue Estimator — Know Exactly How Much Any Local Business Makes Before You Call Them

---

## 📋 ClawHub Info

**Slug:** `google-maps-revenue-estimator`

**Display Name:** `Google Maps Revenue Estimator — Know Exactly How Much Any Local Business Makes Before You Call Them`

**Changelog:** `v1.0.0 — Scrapes Google Maps for any business category and location, estimates monthly revenue per business using review velocity, ratings, foot traffic signals and industry benchmarks, scores each business by size and growth potential, and generates revenue-led outreach + a local market opportunity video via InVideo AI. Powered by Apify + InVideo AI + Claude AI.`

**Tags:** `google-maps` `local-business` `revenue-estimation` `b2b-sales` `apify` `invideo` `lead-generation` `sales-intelligence` `agency` `cold-outreach` `smb` `foot-traffic`

---

**Category:** Sales Intelligence / Local Lead Generation  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

> Input any business category + city. Get **estimated monthly revenue for every business on the map** — ranked from biggest spender to smallest. Know who has budget before you call. Pitch the right businesses. Close more deals. Faster.

---

## 💥 Why This Will Explode on ClawHub

The Google Maps B2B Goldmine is already one of the top-viewed skills on ClawHub with **449 views**. This skill takes it to a completely different level.

A list of businesses is useful. **Knowing which ones make $80,000/month vs $8,000/month before you pick up the phone** is a superpower.

Every agency, freelancer, SaaS rep, and service business wastes hours pitching businesses that have zero budget. This skill tells you exactly who has money — and how much — before you spend a single minute on outreach.

**Target audience:** Web design agencies, SEO agencies, marketing consultants, payment processors, POS vendors, accountants, insurance brokers, software reps — anyone who sells B2B to local businesses.

**What gets automated:**
- 🗺️ Scrape **every business** in any category + city via Google Maps
- 💰 Estimate **monthly revenue** per business using review velocity + ratings + signals
- 📊 Rank businesses by **estimated revenue** — target big spenders first
- 📈 Detect **growth signals** — businesses scaling vs businesses declining
- ✍️ Generate **revenue-led outreach** — "your business makes ~$X/month, here's how we grow it"
- 🎬 Produce **local market opportunity video** via [InVideo AI](https://invideo.sjv.io/TBB)

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| [Apify](https://www.apify.com?fpr=dx06p) — Google Maps Scraper | All businesses in category — reviews, rating, hours, website |
| [Apify](https://www.apify.com?fpr=dx06p) — Google Search Scraper | SEO presence, ad spend signals, brand mentions |
| [Apify](https://www.apify.com?fpr=dx06p) — Website Content Crawler | Pricing pages, team size, service range — revenue signals |
| [Apify](https://www.apify.com?fpr=dx06p) — Instagram Scraper | Social following, post frequency, promoted content signals |
| [Apify](https://www.apify.com?fpr=dx06p) — Facebook Scraper | Ad library — is the business running paid ads? Budget signal. |
| [InVideo AI](https://invideo.sjv.io/TBB) | Produce local market revenue opportunity video |
| Claude AI | Revenue modeling, growth scoring, outreach personalization |

---

## ⚙️ Revenue Estimation Model

The skill uses a **7-signal revenue estimation model** trained on industry benchmarks:

```
SIGNAL 1 — Review Velocity
  └─ Reviews per month = proxy for customer volume
  └─ e.g. Restaurant: 20 reviews/month × avg ticket $35 × 30 = ~$21,000/month

SIGNAL 2 — Rating Quality
  └─ 4.5★+ with high volume = premium pricing power
  └─ 3.8★ with low volume = budget segment

SIGNAL 3 — Google Maps Category & Hours
  └─ Category benchmarks: restaurant vs law firm vs gym — different revenue profiles
  └─ Hours open × estimated hourly throughput = volume proxy

SIGNAL 4 — Website Presence & Quality
  └─ Premium website + booking system = established business with real revenue
  └─ No website or basic template = micro-business

SIGNAL 5 — Social Media Activity
  └─ Active Instagram with 2K+ followers + regular posts = marketing budget exists
  └─ Running Facebook ads = confirmed marketing spend

SIGNAL 6 — Team Size Signals
  └─ "Meet the team" page with 10+ staff = $500K+ annual revenue likely
  └─ Solo operator signals = micro-business tier

SIGNAL 7 — Location & Premises
  └─ Central location in premium area = higher revenue tier
  └─ Multiple locations = confirmed scale

COMBINED → Revenue tier estimate with confidence score
```

---

## ⚙️ Full Workflow

```
INPUT: Business category + city + your service offer
        ↓
STEP 1 — Full Map Scrape
  └─ Every business in category within radius
  └─ Extract: name, address, phone, website, rating, review count, hours
        ↓
STEP 2 — Revenue Signal Collection
  └─ Review velocity (reviews per month)
  └─ Website quality score
  └─ Social media presence + ad signals
  └─ Team size indicators
        ↓
STEP 3 — Revenue Estimation
  └─ Apply 7-signal model per business
  └─ Output: estimated monthly revenue range
  └─ Confidence score per estimate
        ↓
STEP 4 — Growth Signal Detection
  └─ Review count growing month-over-month? (expanding)
  └─ Recently started running ads? (investing in growth)
  └─ New location opened? (scaling)
  └─ Rating improving? (fixing problems = reinvesting)
        ↓
STEP 5 — Prospect Scoring
  └─ Revenue tier: Whale ($100K+/mo) / Solid ($20-100K) / Small ($5-20K) / Skip (<$5K)
  └─ Growth signal: Scaling / Stable / Declining
  └─ Budget likelihood: High / Medium / Low
        ↓
STEP 6 — Claude AI Writes Revenue-Led Outreach
  └─ Opens with their estimated revenue figure
  └─ Shows % improvement your service delivers
  └─ Positions ROI in their own revenue terms
        ↓
STEP 7 — InVideo AI Produces Market Video
  └─ "The revenue landscape of [category] in [city]"
  └─ Key stats: average revenue, who's growing, who's not
  └─ Perfect opener for cold email or LinkedIn outreach
        ↓
OUTPUT: Ranked business list by revenue + outreach per business + market video
```

---

## 📥 Inputs

```json
{
  "targeting": {
    "category": "dental practices",
    "city": "Chicago, Illinois",
    "radius_km": 20,
    "exclude_chains": true,
    "min_reviews": 15
  },
  "your_service": {
    "type": "digital marketing agency",
    "offer": "Google Ads + SEO package for dental practices",
    "result": "Average client adds 40 new patients per month",
    "price": "$1,500/month"
  },
  "targeting_filters": {
    "revenue_tiers": ["Whale", "Solid"],
    "growth_signals": ["Scaling", "Stable"],
    "skip_if": ["running google ads already", "chain/franchise"]
  },
  "max_results": 80,
  "production": {
    "invideo_api_key": "YOUR_INVIDEO_API_KEY"
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "market_overview": {
    "city": "Chicago, IL",
    "category": "Dental Practices",
    "businesses_scanned": 312,
    "revenue_distribution": {
      "whales_100k_plus": 18,
      "solid_20k_100k": 94,
      "small_5k_20k": 143,
      "skip_under_5k": 57
    },
    "total_estimated_monthly_revenue_in_market": "$42.8M",
    "avg_monthly_revenue_per_practice": "$137,200",
    "top_growth_signal": "34 practices started running Google Ads in last 90 days — market is getting competitive"
  },
  "top_prospects": [
    {
      "rank": 1,
      "revenue_tier": "🐋 WHALE",
      "prospect_score": 94,
      "business": {
        "name": "Lakefront Dental Group",
        "address": "840 N Michigan Ave, Chicago IL",
        "phone": "(312) 440-8820",
        "website": "lakefrontdental.com",
        "google_rating": 4.8,
        "review_count": 847,
        "reviews_last_30d": 23
      },
      "revenue_estimate": {
        "monthly_revenue_range": "$180,000 – $240,000/month",
        "confidence": "High (82%)",
        "model_signals": {
          "review_velocity": "23 reviews/month × avg dental ticket $780 = high volume practice",
          "website_quality": "Premium custom site with online booking — significant tech investment",
          "team_size": "11 dentists listed on team page",
          "location": "Prime Michigan Ave location — premium rent = premium revenue",
          "ads_detected": "Not currently running Google Ads — opportunity"
        }
      },
      "growth_signals": [
        "Review count up 34% in last 6 months",
        "Added 2 new dentists to team page recently",
        "Recently launched Invisalign service — expanding service range"
      ],
      "budget_likelihood": "Very High — $200K/month practice can easily justify $1,500/month marketing",
      "decision_maker": {
        "likely_title": "Practice Owner / Office Manager",
        "best_approach": "Call during 9–10am Tuesday–Thursday",
        "phone": "(312) 440-8820"
      },
      "outreach": {
        "email_subject": "Lakefront Dental — 40 new patients/month from Google Ads (you're not running any yet)",
        "email_body": "Hi Lakefront Dental team,\n\nI ran a quick analysis of dental practices on Michigan Ave and noticed something: Lakefront Dental is one of the highest-rated practices in Chicago (4.8★ from 847 reviews) but you're not running any Google Ads.\n\nYour competitors 3 blocks away are spending $2,000–$4,000/month on ads to capture patients who search 'dentist Chicago' — and those patients never find you organically.\n\nWe work exclusively with dental practices. Our average client adds 40 new patients per month from Google Ads. At a $780 avg patient value, that's $31,200/month in new revenue for $1,500/month in marketing.\n\nWould a 15-minute call this week make sense?\n\n[Your name] | [Agency]",
        "cold_call_opener": "Hi, I'm calling for the practice owner — I noticed Lakefront Dental has 847 Google reviews and a 4.8 rating, but you're not running any Google Ads. I work with dental practices specifically and I wanted to share what that's likely costing you in missed patients each month."
      }
    },
    {
      "rank": 2,
      "revenue_tier": "🐋 WHALE",
      "prospect_score": 89,
      "business": {
        "name": "Chicago Smile Design",
        "estimated_monthly_revenue": "$140,000 – $190,000/month",
        "key_signal": "Running Facebook ads but no Google Ads — channel gap opportunity"
      },
      "outreach": {
        "email_subject": "You're running Facebook ads but missing 3x the patients on Google",
        "email_body": "Hi Chicago Smile Design — I can see you're already investing in Facebook ads (smart). But Google Search captures patients at the exact moment they're searching for a dentist — 3x higher intent than social. You're currently invisible there. We fix that. 40 new patients/month average. Worth a call?"
      }
    }
  ],
  "market_video": {
    "script": "312 dental practices in Chicago. The average practice makes $137,000 a month. 18 of them make over $180,000. And only 34 of those 312 are running Google Ads right now. That means 278 high-revenue dental practices in this city are invisible to patients searching online. I analyzed every single one. Here are the 18 with the biggest budget and the biggest gap.",
    "duration": "60s",
    "status": "produced"
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class B2B sales intelligence analyst specializing in local business revenue modeling.

SCRAPED BUSINESS DATA: {{google_maps_website_social_data}}
AD SIGNAL DATA: {{facebook_google_ads_detection}}
INDUSTRY BENCHMARKS: {{category_revenue_benchmarks}}

YOUR SERVICE:
- Type: {{service_type}}
- Offer: {{offer}}
- Result: {{result}}
- Price: ${{price}}/month

TARGET:
- Category: {{category}}
- City: {{city}}

FOR EACH BUSINESS:
1. Revenue estimate using 7-signal model:
   - Review velocity × category avg ticket
   - Website quality tier
   - Team size signals
   - Location premium
   - Ad spend detection
   - Social following
   - Hours + category benchmark
   Output: monthly revenue range + confidence %

2. Revenue tier:
   - 🐋 Whale: $100K+/month
   - ✅ Solid: $20K–$100K/month
   - 🟡 Small: $5K–$20K/month
   - ⬇️ Skip: under $5K/month

3. Growth signals (specific, not generic):
   - Mention exact signals detected

4. Budget likelihood for YOUR price point:
   - Calculate as % of estimated revenue
   - Under 2% of revenue = easy yes
   - 2–5% = normal sales cycle
   - Over 5% = harder sell

5. Revenue-led outreach:
   - Email: open with their revenue estimate OR the gap it creates
   - Cold call opener: reference a specific signal
   - Subject line must include a number

6. 60-second market overview video script:
   - Lead with the total market revenue figure
   - Reveal the opportunity gap
   - End with the prospect count

GOLDEN RULE: Outreach must reference THEIR specific revenue signal.
"You have 847 reviews" beats "I noticed you have good reviews."

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Scan | Apify Cost | InVideo Cost | Total | Value Delivered |
|---|---|---|---|---|
| 100 businesses | ~$0.50 | ~$3 | ~$3.50 | Ranked revenue map |
| 500 businesses | ~$2 | ~$3 | ~$5 | Full city revenue intel |
| 5 cities (agency) | ~$10 | ~$15 | ~$25 | Full month pipeline |
| Weekly monitoring | ~$2/week | ~$3 | ~$11/month | Always-fresh leads |

> 💡 **Start free on [Apify](https://www.apify.com?fpr=dx06p) — $5 credits included**
> 🎬 **Produce your market videos with [InVideo AI](https://invideo.sjv.io/TBB)**

---

## 🔗 Revenue Opportunities

| User | How They Use It | Revenue |
|---|---|---|
| **Marketing Agency** | Pitch only businesses with $100K+/month revenue | 3x close rate |
| **SaaS Sales Rep** | Target whales first — skip micro-businesses | 5x revenue per deal |
| **Freelancer** | Know client budget before quoting | Never underprice again |
| **Payment Processor** | Find high-volume merchants worth onboarding | Higher transaction value |
| **Business Broker** | Estimate acquisition targets before approaching | Data-backed offers |

---

## 📊 Why This Beats Regular Maps Scrapers

| Feature | Basic Maps Scraper | Hunter.io | **Google Maps Revenue Estimator** |
|---|---|---|---|
| Contact extraction | ✅ | ✅ | ✅ |
| Revenue estimation | ❌ | ❌ | ✅ |
| Budget likelihood score | ❌ | ❌ | ✅ |
| Growth signal detection | ❌ | ❌ | ✅ |
| Revenue-led outreach | ❌ | ❌ | ✅ |
| Market overview video | ❌ | ❌ | ✅ |
| Cost | $49/mo | $49/mo | ~$5/run |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your [Apify](https://www.apify.com?fpr=dx06p) API Token**  
Go to: **Settings → Integrations → API Token**

**Step 2 — Get your [InVideo AI](https://invideo.sjv.io/TBB) account**  
Go to: **Settings → API → Copy your key**

**Step 3 — Input your category + city & run**  
Business type + location + your offer. Full revenue map in minutes.

---

## ⚡ Pro Tips

- **Whales first, always** — one $100K/month business is worth 20 micro-businesses
- **"You're not running Google Ads"** is the single best cold call opener for local businesses
- **Review velocity = best revenue proxy** — 20 reviews/month means 20+ real transactions/month
- **The market video closes on credibility** — "I analyzed every [category] in [city]" positions you as the expert
- **Budget likelihood under 2% of revenue = easiest close** — at that level it's a rounding error to them

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI*
