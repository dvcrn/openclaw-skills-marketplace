---
name: local-business-money-radar
description: "Local Business Money Radar — Detect Underperforming Businesses & Prioritize Your Best Opportunities"
---

# 📍 Local Business Money Radar — Detect Underperforming Businesses & Prioritize Your Best Opportunities

---

## 📋 ClawHub Info

**Slug:** `local-business-money-radar`

**Display Name:** `Local Business Money Radar — Detect Underperforming Businesses & Prioritize Your Best Opportunities`

**Changelog:** `v1.0.0 — Scrapes every local business in any location, runs a full health diagnostic per business (website, SEO, reviews, social), calculates monthly revenue at risk, ranks all leads by opportunity score, generates gap-specific outreach with revenue impact numbers, and produces a local market overview video via InVideo AI. Powered by Apify + InVideo AI + Claude AI.`

**Tags:** `local-business` `lead-generation` `google-maps` `seo` `reputation` `apify` `invideo` `agency` `web-design` `digital-marketing` `small-business` `opportunity-scoring`

---

**Category:** Local Lead Generation / Business Intelligence  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

> Input any location + service category. Get every local business ranked by **revenue opportunity score** — not just a list of leads, but a prioritized radar showing which businesses are underperforming, bleeding customers, missing revenue, and desperate for your service RIGHT NOW. Stop chasing cold leads. Start with the hottest opportunities in any market.

---

## 💥 Why This Is The Ultimate Local Lead Gen Skill

Google Maps scrapers give you a list. **This skill gives you a ranked intelligence report.** The difference is everything.

A list of 500 restaurants is useless. A ranked radar that shows you the 12 restaurants losing customers, with broken websites, zero social presence, and ratings that dropped 0.8 points this month — that's a goldmine.

**Every local agency, freelancer, SaaS company targeting SMBs, and service business needs this.** Web designers, SEO agencies, social media managers, POS vendors, payment processors — anyone who sells to local businesses.

**What gets automated:**
- 📍 Scrape **every business** in any location + category
- 🩺 Run a **business health diagnostic** on each one
- 💰 Calculate **revenue opportunity score** — how much money are they leaving on the table?
- 📊 Detect **specific gaps** — no website, bad SEO, zero reviews, dead social, poor photos
- ⚡ Prioritize by **urgency score** — who needs help most RIGHT NOW
- ✍️ Generate **gap-specific outreach** — references their exact problem with a revenue number
- 🎬 Produce **local market overview video** via [InVideo AI](https://invideo.sjv.io/TBB)

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| [Apify](https://www.apify.com?fpr=dx06p) — Google Maps Scraper | All businesses in location — rating, reviews, details |
| [Apify](https://www.apify.com?fpr=dx06p) — Website Content Crawler | Website quality — speed, mobile, SEO basics |
| [Apify](https://www.apify.com?fpr=dx06p) — Google Search Scraper | SEO visibility — are they ranking for their keywords? |
| [Apify](https://www.apify.com?fpr=dx06p) — Instagram Scraper | Social media presence — active or dead? |
| [Apify](https://www.apify.com?fpr=dx06p) — Facebook Scraper | Facebook page — reviews, activity, engagement |
| [Apify](https://www.apify.com?fpr=dx06p) — Trustpilot / Yelp Scraper | Extended review data beyond Google |
| [InVideo AI](https://invideo.sjv.io/TBB) | Produce local market opportunity overview video |
| Claude AI | Opportunity scoring, gap analysis, outreach generation |

---

## ⚙️ Full Workflow

```
INPUT: Location + business category + your service offer
        ↓
STEP 1 — Full Location Scrape
  └─ Every business in category within radius
  └─ Extract: name, address, phone, website, rating, review count
  └─ Filter: exclude chains & franchises (optional)
        ↓
STEP 2 — Business Health Diagnostic (per business)
  └─ Website: exists? mobile-friendly? loads under 3s?
  └─ SEO: ranking for "[category] + [city]"?
  └─ Review score & trend: improving or declining?
  └─ Review response rate: do they respond to reviews?
  └─ Social: Instagram/Facebook — active or ghost?
  └─ Google listing: photos, posts, Q&A complete?
        ↓
STEP 3 — Revenue Opportunity Calculation
  └─ Estimate lost customers from low rating
  └─ Estimate lost traffic from no SEO presence
  └─ Estimate missed bookings from no online booking
  └─ Total: "This business may be losing ~$X/month"
        ↓
STEP 4 — Urgency Signal Detection
  └─ Rating dropped in last 90 days = crisis
  └─ New competitor opened nearby = threat
  └─ No response to recent negative reviews = ignored
  └─ Website last updated 2+ years ago = neglect signal
        ↓
STEP 5 — Opportunity Scoring (0–100)
  └─ Gap size (how broken are they?) — 40%
  └─ Business viability (worth helping?) — 30%
  └─ Urgency (how soon do they need help?) — 30%
        ↓
STEP 6 — Claude AI Generates Gap-Specific Outreach
  └─ Each email references THEIR specific gap
  └─ Includes revenue impact estimate ("you may be losing $2,400/month")
  └─ Clear CTA based on the gap detected
        ↓
STEP 7 — InVideo AI Produces Market Overview Video
  └─ "The state of [category] businesses in [city]"
  └─ Key stats: how many have broken websites, low ratings, etc.
  └─ CTA: "We help local [category] businesses fix this"
        ↓
OUTPUT: Radar report ranked by opportunity score + outreach per business + market video
```

---

## 📥 Inputs

```json
{
  "targeting": {
    "location": "Austin, Texas",
    "radius_km": 15,
    "category": "restaurants",
    "exclude_chains": true,
    "min_reviews": 10
  },
  "your_service": {
    "type": "digital marketing agency",
    "offer": "Social media management + Google review strategy",
    "usp": "Average client gets 40 new Google reviews in 60 days",
    "price_point": "$499/month"
  },
  "scoring": {
    "gap_weights": {
      "no_website": 25,
      "low_rating": 30,
      "declining_rating": 35,
      "no_social_presence": 20,
      "unanswered_reviews": 25
    }
  },
  "max_results": 100,
  "production": {
    "invideo_api_key": "YOUR_INVIDEO_API_KEY",
    "video_style": "local_market_report"
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "market_overview": {
    "location": "Austin, TX (15km radius)",
    "category": "Restaurants",
    "total_scanned": 312,
    "opportunity_breakdown": {
      "hot_opportunities": 28,
      "warm_opportunities": 67,
      "healthy_businesses": 217
    },
    "market_stats": {
      "no_website": "34% of businesses (106)",
      "rating_below_4": "28% (87 businesses)",
      "rating_declined_90d": "19% (59 businesses)",
      "zero_social_presence": "41% (128 businesses)",
      "unanswered_reviews": "62% (193 businesses)"
    },
    "total_revenue_opportunity_estimate": "$890K/month in lost revenue across hot opportunities"
  },
  "top_opportunities": [
    {
      "rank": 1,
      "opportunity_score": 94,
      "urgency": "🔴 CRITICAL",
      "business": {
        "name": "Casa Verde Mexican Kitchen",
        "address": "1847 South Congress Ave, Austin TX",
        "phone": "(512) 946-0234",
        "website": null,
        "google_rating": 3.6,
        "review_count": 247
      },
      "health_diagnostic": {
        "website": "❌ No website — losing every customer who searches them online",
        "seo": "❌ Invisible — not ranking for 'Mexican restaurant Austin South Congress'",
        "rating_trend": "📉 Was 4.1★ six months ago — dropped 0.5 points",
        "social": "❌ Instagram: last post 14 months ago (312 followers, dead)",
        "reviews": "⚠️ 23 unanswered reviews in last 6 months including 4 negative ones",
        "google_photos": "⚠️ Only 3 photos — most restaurants have 50+"
      },
      "revenue_impact_estimate": {
        "lost_from_low_rating": "~$3,200/month",
        "lost_from_no_website": "~$1,800/month",
        "lost_from_dead_social": "~$800/month",
        "total_estimated_loss": "~$5,800/month"
      },
      "decision_maker": {
        "likely_contact": "Owner/Manager",
        "best_approach": "Walk in Tuesday–Thursday 2–4pm (off-peak hours)",
        "phone": "(512) 946-0234"
      },
      "outreach": {
        "email_subject": "Casa Verde is losing ~$5,800/month online — here's why",
        "email_body": "Hi Casa Verde team,\n\nI ran a quick digital audit of your restaurant and wanted to share something you should know.\n\nYou have 247 Google reviews — clearly people love your food. But a few things are costing you customers every week:\n\n→ No website: every person who searches you after a recommendation hits a dead end\n→ Your rating dropped from 4.1 to 3.6 in 6 months — 23 reviews went unanswered\n→ Your Instagram has been inactive for 14 months\n\nBased on similar restaurants we've worked with in Austin, this is likely costing you $4,000–$6,000/month in missed revenue.\n\nWe specialize in helping local restaurants fix exactly this. Our average client gets 40 new Google reviews in 60 days.\n\nWorth a 15-minute chat?\n\n[Your name] | [Agency]",
        "in_person_opener": "Hi — I noticed Casa Verde doesn't have a website and your Google rating has dropped recently. We work with restaurants on exactly this — do you have 10 minutes? I have some specific ideas for you."
      }
    },
    {
      "rank": 2,
      "opportunity_score": 89,
      "urgency": "🔴 HOT",
      "business": {
        "name": "Barrel & Vine Wine Bar",
        "address": "623 West 6th Street, Austin TX",
        "google_rating": 3.9,
        "review_count": 118
      },
      "health_diagnostic": {
        "website": "✅ Has website — but loads in 8.4 seconds (industry average: 2.1s)",
        "seo": "❌ Ranking #14 for 'wine bar Austin' — effectively invisible",
        "rating_trend": "📉 -0.3 in 90 days",
        "social": "⚠️ Posts once per month — not enough for algorithm"
      },
      "revenue_impact_estimate": {
        "total_estimated_loss": "~$3,400/month"
      },
      "outreach": {
        "email_subject": "Barrel & Vine ranks #14 for 'wine bar Austin' — here's the fix",
        "email_body": "Hi Barrel & Vine team,\n\nWhen someone searches 'wine bar Austin' right now, you appear on page 2. That's page 1 money going to your competitors every day.\n\nYour site also loads in 8+ seconds on mobile — most people leave after 3. And your rating has dipped 0.3 points in the last 90 days.\n\nWe help Austin hospitality businesses fix exactly this. Average results: ranking page 1 in 90 days + 40 new Google reviews in 60 days.\n\nWould a quick call this week make sense?"
      }
    }
  ],
  "market_video": {
    "script": "312 restaurants in Austin. 34% have no website. 62% never respond to their Google reviews. 28% have ratings below 4 stars — losing customers every day because of it. We analyzed every independent restaurant within 15 miles. Here are the 28 losing the most revenue right now — and exactly how to fix it.",
    "duration": "60s",
    "status": "produced",
    "file": "outputs/austin_restaurant_market_radar.mp4"
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class local business analyst and digital marketing strategist.

SCRAPED BUSINESS DATA: {{google_maps_and_website_data}}
SOCIAL & REVIEW DATA: {{social_review_data}}
SEO VISIBILITY DATA: {{search_ranking_data}}

YOUR SERVICE:
- Type: {{service_type}}
- Offer: {{offer}}
- USP: {{usp}}
- Price: {{price}}

TARGET:
- Location: {{location}}
- Category: {{category}}

FOR EACH BUSINESS GENERATE:
1. Opportunity score (0–100):
   - Gap severity (40%): how broken are they?
   - Business viability (30%): real business worth helping?
   - Urgency signals (30%): rating drop, new competitor, neglected reviews

2. Health diagnostic per channel:
   - Website: exists? speed? mobile?
   - SEO: ranking for main keyword?
   - Reviews: score, trend, response rate
   - Social: last post date, engagement
   - Google listing: photos, Q&A

3. Revenue impact estimate:
   - Calculate lost customers from each gap
   - Estimate $ value per gap
   - Total monthly revenue at risk

4. Decision maker + best contact approach

5. Outreach (gap-specific — always reference a specific number):
   - Email: lead with the revenue impact number
   - In-person opener for walk-in approach
   - Subject line must include a specific stat

GOLDEN RULE: Every outreach must reference a SPECIFIC gap with a SPECIFIC number.
"You have no website" < "You have no website — losing ~$1,800/month in online discovery"

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Scan | Apify Cost | InVideo Cost | Total | Value Generated |
|---|---|---|---|---|
| 100 businesses | ~$0.70 | ~$3 | ~$3.70 | 28 hot leads |
| 500 businesses | ~$3 | ~$3 | ~$6 | 140 hot leads |
| 5 cities (agency) | ~$15 | ~$15 | ~$30 | Full month pipeline |
| Daily auto-run | ~$0.70/day | ~$3 | ~$24/month | Always-fresh leads |

> 💡 **Get started free on [Apify](https://www.apify.com?fpr=dx06p) — $5 credits included**
> 🎬 **Produce your local market videos with [InVideo AI](https://invideo.sjv.io/TBB)**

---

## 🔗 Revenue Opportunities

| User | How They Use It | Revenue |
|---|---|---|
| **Web Design Agency** | Find businesses with no website — easiest close | $1,500–$5,000 per site |
| **SEO Agency** | Find businesses invisible on Google | $500–$2,000/month retainer |
| **Social Media Manager** | Find businesses with dead social accounts | $500–$1,500/month per client |
| **Reputation Manager** | Find businesses with declining ratings | $300–$800/month per client |
| **Freelancer** | 10 warm leads per city run | Full client roster |

---

## 📊 Why This Beats Regular Google Maps Scrapers

| Feature | Basic Maps Scraper | **Local Business Money Radar** |
|---|---|---|
| Contact list output | ✅ | ✅ |
| Website health check | ❌ | ✅ |
| SEO visibility analysis | ❌ | ✅ |
| Rating trend detection | ❌ | ✅ |
| Revenue impact estimate | ❌ | ✅ |
| Opportunity scoring | ❌ | ✅ |
| Gap-specific outreach | ❌ | ✅ |
| Market overview video | ❌ | ✅ |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your [Apify](https://www.apify.com?fpr=dx06p) API Token**  
Go to: **Settings → Integrations → API Token**

**Step 2 — Get your [InVideo AI](https://invideo.sjv.io/TBB) account**  
Go to: **Settings → API → Copy your key**

**Step 3 — Set your location + category & run**  
City + business type + your service. Ranked radar ready in minutes.

---

## ⚡ Pro Tips

- **Lead with the revenue number** — "you may be losing $5,800/month" opens every door
- **Walk in during off-peak hours** — 2–4pm Tuesday to Thursday for restaurants
- **No website = easiest close** — the gap is obvious, the solution is obvious
- **Rating drop = urgency** — they know something is wrong, you show up with the answer
- **Use the market video as cold email opener** — "I made a quick video about [category] in [city]" gets clicked

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI*
