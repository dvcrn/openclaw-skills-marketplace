---
name: ai-etsy-shopify-store-spy
description: "AI Etsy & Shopify Store Spy — Reverse-Engineer Any Winning Store & Launch Your Own in Days"
---

# 🛍️ AI Etsy & Shopify Store Spy — Reverse-Engineer Any Winning Store & Launch Your Own in Days

---

## 📋 ClawHub Info

**Slug:** `ai-etsy-shopify-store-spy`

**Display Name:** `AI Etsy & Shopify Store Spy — Reverse-Engineer Any Winning Store & Launch Your Own in Days`

**Changelog:** `v1.0.0 — Scrapes Etsy & Shopify stores to reveal best-selling products, estimated monthly revenue, pricing strategy, SEO keywords, traffic sources and customer reviews, then generates a complete copycat-proof launch strategy, optimized product listings, and a store launch video via InVideo AI. Powered by Apify + InVideo AI + Claude AI.`

**Tags:** `etsy` `shopify` `ecommerce` `product-research` `apify` `invideo` `store-spy` `best-sellers` `dropshipping` `print-on-demand` `revenue-estimation` `product-launch`

---

**Category:** E-commerce Intelligence / Product Research  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

> Input any Etsy or Shopify niche. Get a **complete store intelligence report** — top-selling products exposed, monthly revenue estimated, pricing strategy decoded, SEO keywords extracted, customer complaints mapped, and a full launch strategy generated. Stop guessing what sells. Know before you list.

---

## 💥 Why This Skill Will Go Straight to the Top of ClawHub

The Amazon & Etsy Product Research Engine already has **290 views and 2 real stars** — the highest-rated skill on the platform. This skill goes deeper, wider, and more actionable.

While everyone else is guessing what products to sell, this skill gives you **the exact blueprint of stores already making $20,000–$200,000/month** — their best sellers, their pricing, their keywords, their gaps — and builds you a launch strategy on top of it.

**Target audience:** Etsy sellers, Shopify store owners, print-on-demand entrepreneurs, dropshippers, e-commerce beginners, side hustlers, digital product creators. One of the largest online entrepreneur audiences on earth.

**What gets automated:**
- 🔍 Spy on **any Etsy or Shopify store** — best sellers, pricing, review count, estimated revenue
- 💰 Estimate **monthly revenue** per product and per store
- 📉 Mine **1-star reviews** for product improvement angles
- 🔑 Extract **SEO keywords** they rank for — organic traffic source revealed
- 📊 Detect **pricing strategy** — where are they leaving money on the table?
- ✍️ Generate **optimized product listings** — title, tags, description, pricing
- 🎬 Produce **store launch video** via [InVideo AI](https://invideo.sjv.io/TBB) for ads & social

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| [Apify](https://www.apify.com?fpr=dx06p) — Etsy Scraper | Best-selling products, review count, pricing, sales estimates |
| [Apify](https://www.apify.com?fpr=dx06p) — Shopify Store Scraper | Product catalog, pricing, collections, traffic signals |
| [Apify](https://www.apify.com?fpr=dx06p) — Amazon Reviews Scraper | Cross-platform review mining for product improvement |
| [Apify](https://www.apify.com?fpr=dx06p) — Google Search Scraper | SEO keywords stores rank for — organic traffic decoded |
| [Apify](https://www.apify.com?fpr=dx06p) — Pinterest Scraper | Top pins in niche — what designs & concepts go viral |
| [Apify](https://www.apify.com?fpr=dx06p) — Google Trends Scraper | Demand trajectory — seasonal vs evergreen products |
| [InVideo AI](https://invideo.sjv.io/TBB) | Produce store launch video for ads & social media |
| Claude AI | Revenue modeling, gap analysis, listing optimization, launch strategy |

---

## ⚙️ Full Workflow

```
INPUT: Niche or competitor store URL + your platform + budget
        ↓
STEP 1 — Store Intelligence Scrape
  └─ Top 50 best-selling products per competitor store
  └─ Extract: title, price, review count, sales estimate, tags
  └─ Estimate monthly revenue per product + total store revenue
        ↓
STEP 2 — Best-Seller Pattern Recognition
  └─ What do the top 10 products have in common?
  └─ Price point sweet spot for this niche
  └─ Listing format: what title structures convert?
  └─ Photo style: lifestyle vs white background vs flat lay?
        ↓
STEP 3 — SEO Keyword Extraction
  └─ Keywords each top product ranks for on Etsy search
  └─ Google keywords driving organic traffic to Shopify stores
  └─ Long-tail keyword gaps — high volume, low competition
  └─ Pinterest keyword clusters for visual discovery
        ↓
STEP 4 — Review Mining (1 & 2 Star)
  └─ What do customers hate about top competitor products?
  └─ Recurring complaints = your product differentiation list
  └─ What do customers love? (replicate in your listing copy)
        ↓
STEP 5 — Pricing Gap Analysis
  └─ Price distribution in the niche
  └─ Identify underserved price points (premium gap, budget gap)
  └─ Bundle opportunities: what products are bought together?
        ↓
STEP 6 — Launch Strategy Generation
  └─ Top 5 products to launch first (highest demand, lowest competition)
  └─ Pricing strategy: entry price → raise after 10 reviews
  └─ SEO listing formula: title + 13 tags + description structure
  └─ Pinterest + TikTok organic traffic plan
        ↓
STEP 7 — Claude AI Writes Optimized Listings
  └─ Etsy: title + 13 tags + description (SEO + conversion optimized)
  └─ Shopify: product title + description + meta tags
  └─ Each listing built from real keyword + review data
        ↓
STEP 8 — InVideo AI Produces Store Launch Video
  └─ 30-second product showcase for TikTok & Reels
  └─ 60-second store story ad for Facebook & Instagram
  └─ Drives first traffic before organic kicks in
        ↓
OUTPUT: Store intelligence report + 5 product launch briefs + optimized listings + launch video
```

---

## 📥 Inputs

```json
{
  "research": {
    "niche": "personalized pet gifts",
    "platforms": ["Etsy"],
    "competitor_stores": [
      "https://www.etsy.com/shop/PawfectPersonalized",
      "https://www.etsy.com/shop/CustomPetPortraits"
    ],
    "your_platform": "Etsy",
    "fulfillment": "print-on-demand (Printify)"
  },
  "your_store": {
    "status": "not launched yet",
    "budget_for_launch": 500,
    "target_monthly_revenue": 3000
  },
  "criteria": {
    "max_competitor_reviews_for_product": 1500,
    "min_estimated_monthly_sales": 30,
    "avoid_seasonal_only": false
  },
  "production": {
    "invideo_api_key": "YOUR_INVIDEO_API_KEY",
    "video_style": "warm_lifestyle_pet"
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "market_intelligence": {
    "niche": "Personalized Pet Gifts",
    "platform": "Etsy",
    "stores_analyzed": 12,
    "products_scanned": 847,
    "niche_total_monthly_revenue_estimate": "$2.8M",
    "avg_top_store_monthly_revenue": "$34,200",
    "price_sweet_spot": "$18–$45",
    "best_selling_product_type": "Custom pet portrait prints (digital download)",
    "biggest_opportunity": "Custom pet memorial gifts — high demand, emotionally driven, premium pricing untapped"
  },
  "competitor_breakdown": [
    {
      "store": "PawfectPersonalized",
      "estimated_monthly_revenue": "$41,000",
      "total_sales_estimate": "28,400 lifetime",
      "top_products": [
        {
          "title": "Custom Dog Portrait Print — Watercolor Style",
          "price": "$12.99",
          "reviews": 2847,
          "estimated_monthly_sales": 340,
          "estimated_monthly_revenue": "$4,416",
          "listing_quality_score": 91
        },
        {
          "title": "Personalized Pet Name Sign — Custom Wood Look Print",
          "price": "$8.99",
          "reviews": 1204,
          "estimated_monthly_sales": 180,
          "estimated_monthly_revenue": "$1,618"
        }
      ],
      "their_weaknesses": [
        "No premium tier — everything under $15, leaving $35–$75 price point completely open",
        "Zero memorial/grief products despite high Etsy search volume",
        "Generic descriptions — no emotional storytelling in listings",
        "No video listings — Etsy boosts listings with video"
      ],
      "their_top_seo_keywords": [
        "custom dog portrait", "personalized pet gift", "pet memorial print",
        "custom cat portrait digital", "watercolor pet portrait printable"
      ]
    }
  ],
  "product_launch_plan": [
    {
      "rank": 1,
      "product": "Custom Pet Memorial Print — 'Forever In Our Hearts'",
      "why_this_wins": "Top competitors have ZERO memorial products. Etsy searches for 'pet loss gift' hit 22,000/month. Emotional products command 3x the price of regular pet gifts.",
      "target_price": "$34.99",
      "competitor_gap": "Nobody owns this at premium price on first page",
      "estimated_monthly_revenue_at_scale": "$3,500–$6,000",
      "differentiation": "Emotional copy + premium presentation + sympathy card included in digital download pack",
      "review_mining_insight": "Buyers of competitor products say 'wish there was something more personal for when my pet passed' — 67 mentions across competitor reviews",
      "optimized_etsy_listing": {
        "title": "Custom Pet Memorial Print Personalized | Pet Loss Gift | Dog Cat Rainbow Bridge | Digital Download | Pet Portrait Memorial | Sympathy Gift",
        "tags": ["pet memorial gift", "pet loss gift", "custom pet portrait", "rainbow bridge print", "dog memorial", "cat memorial", "pet sympathy gift", "personalized pet gift", "digital download print", "pet portrait digital", "loss of dog gift", "loss of cat gift", "pet bereavement"],
        "description": "When words aren't enough, this personalized memorial print says everything your heart can't.\n\nCustomized with your pet's name, dates, and the breed that made your home whole — this digital download is ready to print and frame within minutes of purchase.\n\n✨ WHAT'S INCLUDED:\n→ High-resolution 8x10 and 5x7 printable files\n→ Matching digital sympathy card\n→ Lifetime download access\n\nSimply send us your pet's name and dates in the 'note to seller' at checkout. We'll customize and deliver to your Etsy inbox within 2 hours.\n\nBecause they deserve to be remembered beautifully. 🐾",
        "pricing_strategy": "Launch at $24.99 with 20% off coupon for first 50 sales → raise to $34.99 once 25 reviews collected"
      }
    },
    {
      "rank": 2,
      "product": "Personalized Pet Portrait — Minimalist Line Art Style",
      "target_price": "$14.99",
      "why_this_wins": "Line art style trending 340% on Pinterest. No competitor in top 20 has this style. Easy to produce via Printify.",
      "estimated_monthly_revenue_at_scale": "$2,200–$3,800"
    },
    {
      "rank": 3,
      "product": "Custom Pet Name Neon Sign Print — Digital Download",
      "target_price": "$9.99",
      "why_this_wins": "Neon aesthetic trending on TikTok. High volume, low competition on Etsy. Perfect impulse buy price point.",
      "estimated_monthly_revenue_at_scale": "$1,500–$2,500"
    }
  ],
  "launch_strategy": {
    "week_1": "List all 5 products with full SEO optimization. Set 20% launch coupons. Share on Pinterest (3 pins per product) and TikTok (process video).",
    "week_2_4": "Request reviews from first buyers via Etsy messages. Add listing videos to all products — Etsy boosts video listings.",
    "month_2": "Run Etsy Ads at $3/day on top 2 products. Expand to 15 product variations based on what's selling.",
    "path_to_3k_monthly": "Product 1 at 90 sales/month ($3,149) + Products 2 & 3 supporting = $3,000+ by month 3"
  },
  "launch_video": {
    "tiktok_script": "POV: I just found the gap that's making Etsy sellers $40,000 a month. Personalized pet gifts. $2.8 million dollar niche. And there is not a single premium memorial product on the first page. So I'm launching one. Here's the exact listing I'm testing this week.",
    "ad_script": "Your pet gave you everything. This print gives them something back. Personalized with their name, their dates, and the love they left behind. Digital download — ready in 2 hours. Ships to your heart instantly.",
    "duration": "tiktok: 30s, ad: 45s",
    "status": "produced"
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class e-commerce product researcher and Etsy/Shopify launch strategist.

COMPETITOR STORE DATA: {{scraped_products_and_sales}}
REVIEW DATA: {{positive_and_negative_reviews}}
SEO DATA: {{keyword_rankings_and_search_volume}}
TREND DATA: {{pinterest_google_trends}}

RESEARCH BRIEF:
- Niche: {{niche}}
- Platform: {{platform}}
- Fulfillment: {{fulfillment}}
- Budget: ${{budget}}
- Revenue target: ${{target}}/month

GENERATE COMPLETE STORE SPY REPORT:

1. Market intelligence:
   - Niche total monthly revenue estimate
   - Average top store monthly revenue
   - Price sweet spot (most successful price range)
   - Biggest underserved opportunity (specific gap from data)

2. Per competitor store:
   - Revenue estimate (review velocity × avg price × conversion benchmark)
   - Top 5 products with revenue per product
   - Their weaknesses (specific, from review mining and listing analysis)
   - Their top SEO keywords

3. Top 5 product launch opportunities:
   - Why this product wins (data-backed, not opinion)
   - Competitor gap (exactly who is missing this)
   - Review mining insight (exact quote from competitor reviews)
   - Target price + pricing strategy
   - Revenue estimate at scale

4. Full optimized listing per product:
   - Etsy: title (140 chars, keyword-rich) + 13 tags + emotional description
   - Shopify: product title + description + meta title
   - Pricing ladder: launch price → review-gated price increase

5. Launch strategy:
   - Week 1, Weeks 2-4, Month 2
   - Path to revenue target with specific sales numbers

6. Two video scripts: 30s TikTok (process/reveal) + 45s ad (emotional)

LISTING COPY RULES:
- Etsy titles: front-load the highest-volume keyword
- Descriptions: emotion first, features second, logistics last
- Tags: mix high-volume (broad) + long-tail (specific) + adjacent (related needs)

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Research | Apify Cost | InVideo Cost | Total | Value Delivered |
|---|---|---|---|---|
| 1 niche full spy report | ~$0.80 | ~$3 | ~$3.80 | Blueprint to $3K/month |
| 5 niches compared | ~$4 | ~$15 | ~$19 | Pick the winner |
| Monthly store monitoring | ~$3/month | ~$3 | ~$6/month | Stay ahead of competitors |

> 💡 **Start free on [Apify](https://www.apify.com?fpr=dx06p) — $5 credits included**
> 🎬 **Produce your store launch videos with [InVideo AI](https://invideo.sjv.io/TBB)**

---

## 🔗 Revenue Opportunities

| User | How They Use It | Revenue |
|---|---|---|
| **Etsy Beginner** | Launch with a proven blueprint, not guesswork | $1K–$10K/month from month 3 |
| **Print-on-Demand Seller** | Find untapped designs before competitors | Scale to 6 figures |
| **Shopify Store Owner** | Spy on direct competitors, close the gaps | 2x existing revenue |
| **E-commerce Consultant** | Deliver store audit + launch plan as service | $500–$2,000 per report |
| **Side Hustler** | Pick the most validated product before spending a cent | Risk-free launch |

---

## 📊 Why This Beats Every Alternative

| Feature | EverBee ($19/mo) | Alura ($19/mo) | **AI Etsy & Shopify Store Spy** |
|---|---|---|---|
| Competitor revenue estimation | ✅ | ✅ | ✅ |
| 1-star review mining | ❌ | ❌ | ✅ |
| Full optimized listing written | ❌ | ❌ | ✅ |
| Pricing gap analysis | ❌ | ❌ | ✅ |
| Pinterest trend detection | ❌ | ❌ | ✅ |
| Store launch video produced | ❌ | ❌ | ✅ |
| 90-day launch strategy | ❌ | ❌ | ✅ |
| Monthly cost | $19 | $19 | ~$6 |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your [Apify](https://www.apify.com?fpr=dx06p) API Token**  
Go to: **Settings → Integrations → API Token**

**Step 2 — Get your [InVideo AI](https://invideo.sjv.io/TBB) account**  
Go to: **Settings → API → Copy your key**

**Step 3 — Input your niche or competitor URL & run**  
Niche + platform + budget. Full spy report in 10 minutes.

---

## ⚡ Pro Tips

- **Memorial & grief products command 3x the price** — highest margin, lowest competition, most loyal buyers
- **Reviews under 500 with strong sales = your entry point** — beatable without months of grinding
- **Add a listing video on day 1** — Etsy algorithmically boosts listings with video by default
- **TikTok process videos drive free Etsy traffic** — "watch me list this product" format converts like crazy
- **Price low to launch, raise after 25 reviews** — the algorithm rewards momentum, not margins

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI*
