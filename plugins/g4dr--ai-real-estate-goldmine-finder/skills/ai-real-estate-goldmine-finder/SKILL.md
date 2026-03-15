---
name: ai-real-estate-goldmine-finder
description: "AI Real Estate Goldmine Finder — Spot Undervalued Properties & Hot Markets Before Everyone Else"
---

# 🏠 AI Real Estate Goldmine Finder — Spot Undervalued Properties & Hot Markets Before Everyone Else

---

## 📋 ClawHub Info

**Slug:** `ai-real-estate-goldmine-finder`

**Display Name:** `AI Real Estate Goldmine Finder — Spot Undervalued Properties & Hot Markets Before Everyone Else`

**Changelog:** `v1.0.0 — Scrapes Zillow, Rightmove & property portals for undervalued listings, detects distressed sellers and motivated owners, maps neighbourhood price trajectory, scores each property by investment potential, generates deal analysis reports and outreach to agents & owners, and produces an investment brief video via InVideo AI. Powered by Apify + InVideo AI + Claude AI.`

**Tags:** `real-estate` `property-investment` `zillow` `airbnb` `apify` `invideo` `deal-finder` `rental-yield` `flipping` `motivated-seller` `market-analysis` `roi`

---

**Category:** Real Estate / Investment Intelligence  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

> Input a city or postcode. Get a **complete property investment intelligence report** — undervalued listings identified, distressed sellers detected, rental yield calculated, neighbourhood growth scored, and a deal-by-deal analysis ready to act on. Find the deals professionals miss. Before they do.

---

## 💥 Why This Skill Is a Goldmine on ClawHub

Real estate is the **#1 wealth-building vehicle on earth**. Every property investor, buy-to-let landlord, house flipper, Airbnb host, and real estate agent is constantly hunting for the next deal.

The problem: the best deals disappear in hours. Finding them requires scanning hundreds of listings, running comps, calculating yields, and researching neighbourhoods — all manually.

This skill automates the entire deal-finding pipeline. For any market. In minutes.

**Target audience:** Property investors, buy-to-let landlords, house flippers, Airbnb hosts, real estate agents, developers, wealth managers. Every person trying to build wealth through property.

**What gets automated:**
- 🔍 Scrape **every listing** in a target area — price, days on market, price reductions
- 📉 Detect **undervalued properties** — priced below comparable sales
- 🚨 Find **distressed sellers** — long days on market, multiple price drops, estate sales
- 💰 Calculate **rental yield & ROI** — buy-to-let and Airbnb projections
- 📈 Score **neighbourhood trajectory** — up-and-coming areas before prices spike
- ✍️ Generate **deal analysis report** per property with go/no-go recommendation
- 🎬 Produce **investment brief video** via [InVideo AI](https://invideo.sjv.io/TBB) for partners or lenders

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| [Apify](https://www.apify.com?fpr=dx06p) — Zillow Scraper | US property listings — price, history, comps |
| [Apify](https://www.apify.com?fpr=dx06p) — Rightmove Scraper | UK property listings — asking price vs sold price |
| [Apify](https://www.apify.com?fpr=dx06p) — Airbnb Scraper | Short-let revenue data — what properties earn nearby |
| [Apify](https://www.apify.com?fpr=dx06p) — Google Maps Scraper | Neighbourhood amenities, transport links, development signals |
| [Apify](https://www.apify.com?fpr=dx06p) — Google News Scraper | Regeneration plans, infrastructure investment, area news |
| [Apify](https://www.apify.com?fpr=dx06p) — Reddit Scraper | Local community signals — "moving to X" threads, area sentiment |
| [InVideo AI](https://invideo.sjv.io/TBB) | Produce investment brief video for lenders or partners |
| Claude AI | Deal scoring, yield calculation, neighbourhood analysis, report writing |

---

## ⚙️ Full Workflow

```
INPUT: Target city/postcode + investment strategy + budget
        ↓
STEP 1 — Full Market Scrape
  └─ All active listings in target area + price band
  └─ Extract: price, size, bedrooms, days on market, price history
  └─ Pull recent sold prices for comparable properties
        ↓
STEP 2 — Undervaluation Detection
  └─ Compare asking price vs avg price per sqft in same postcode
  └─ Flag properties priced 10%+ below comparable sales
  └─ Detect recent price reductions (2+ drops = motivated seller)
        ↓
STEP 3 — Distressed Seller Signals
  └─ Days on market: 60+ days = seller pressure
  └─ Multiple price reductions in short period
  └─ Keywords in listing: "chain-free", "must sell", "estate sale", "probate"
  └─ Empty property signals (utilities disconnected, no furniture photos)
        ↓
STEP 4 — Rental Yield & ROI Calculation
  └─ Scrape Airbnb: what similar properties earn short-let in this area
  └─ Estimate long-let rental from market comparables
  └─ Calculate gross yield, net yield (after costs), cash-on-cash return
  └─ Break-even timeline
        ↓
STEP 5 — Neighbourhood Trajectory Scoring
  └─ Google News: regeneration plans, new transport links, investment news
  └─ Google Maps: new cafés, gyms, co-working spaces opening = gentrification signal
  └─ Reddit: "moving to X" threads + local sentiment
  └─ Planning applications: new developments = rising demand signal
        ↓
STEP 6 — Deal Score Calculation (0–100)
  └─ Undervaluation margin (30%)
  └─ Rental yield strength (25%)
  └─ Distressed seller urgency (25%)
  └─ Neighbourhood growth trajectory (20%)
        ↓
STEP 7 — Claude AI Writes Full Deal Analysis
  └─ Go/No-Go recommendation with rationale
  └─ Suggested offer price (below asking)
  └─ Key risks + mitigation
  └─ Exit strategy options (flip / hold / short-let)
        ↓
STEP 8 — InVideo AI Produces Investment Brief Video
  └─ 60-second deal overview for lenders, JV partners or your own records
  └─ Key numbers: price, yield, ROI, comparable sales
  └─ Professional format — perfect for raising private finance
        ↓
OUTPUT: Ranked deal list + full analysis per property + investment brief video
```

---

## 📥 Inputs

```json
{
  "target_market": {
    "location": "Manchester, UK",
    "search_radius_km": 10,
    "postcodes_focus": ["M1", "M4", "M8", "M14"],
    "property_types": ["flat", "terraced house", "semi-detached"]
  },
  "investment_criteria": {
    "strategy": "buy-to-let",
    "budget_max": 200000,
    "min_gross_yield": 7.0,
    "min_bedrooms": 2,
    "exclude_new_builds": true,
    "target_tenant": "young professionals"
  },
  "deal_signals": {
    "min_days_on_market": 45,
    "min_price_reductions": 1,
    "distressed_keywords": ["chain free", "must sell", "reduced to sell", "probate", "estate sale"]
  },
  "production": {
    "invideo_api_key": "YOUR_INVIDEO_API_KEY",
    "video_style": "professional_investment_brief"
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "market_summary": {
    "location": "Manchester, UK",
    "total_listings_scanned": 1847,
    "hot_deals_found": 14,
    "distressed_sellers_detected": 9,
    "avg_gross_yield_area": "6.2%",
    "best_postcode_by_yield": "M8 — avg 8.4% gross yield",
    "neighbourhood_rising": ["M8 Moston — regeneration investment confirmed", "M14 Fallowfield — student demand surge"]
  },
  "top_deals": [
    {
      "rank": 1,
      "deal_score": 91,
      "label": "🔥 MOTIVATED SELLER — Offer below asking",
      "property": {
        "address": "47 Laburnum Street, Moston, Manchester M8 0LT",
        "type": "3-bed terraced house",
        "asking_price": "£129,000",
        "days_on_market": 84,
        "price_reductions": 2,
        "original_asking_price": "£145,000",
        "listing_notes": "chain-free, seller relocating, must sell"
      },
      "valuation_analysis": {
        "avg_price_per_sqft_postcode": "£148/sqft",
        "this_property_price_per_sqft": "£127/sqft",
        "undervaluation": "14% below comparable sales",
        "estimated_market_value": "£151,000",
        "instant_equity_on_purchase": "~£22,000"
      },
      "rental_analysis": {
        "estimated_monthly_rent_long_let": "£950/month",
        "gross_yield_at_asking": "8.84%",
        "gross_yield_at_suggested_offer": "9.8%",
        "airbnb_comparable_monthly": "£1,650/month (short-let potential)",
        "airbnb_gross_yield": "15.3%",
        "net_yield_estimate": "7.1% (after mortgage, insurance, management)"
      },
      "distressed_signals": [
        "84 days on market — significantly above 28-day area average",
        "Two price reductions totalling £16,000 (11% drop)",
        "Listing says 'must sell — seller relocating to Australia'",
        "Chain-free — fastest possible completion"
      ],
      "neighbourhood_score": 78,
      "neighbourhood_notes": "M8 Moston received £4.2M regeneration funding announced Jan 2026. New tram extension confirmed for 2027. 3 new coffee shops opened in 6 months = early gentrification signal.",
      "deal_analysis": {
        "verdict": "🟢 GO — Strong buy-to-let deal with motivated seller",
        "suggested_offer": "£115,000 (11% below current asking)",
        "offer_rationale": "84 days on market + relocation urgency = high acceptance probability at this level",
        "exit_strategies": [
          "Hold as buy-to-let: 9.8% gross yield at offer price",
          "Short-let via Airbnb: 15%+ gross yield",
          "Refurb & sell: estimated £20-25K uplift with cosmetic renovation"
        ],
        "key_risks": [
          "M8 is still emerging — liquidity risk if you need to sell quickly",
          "Verify structural condition before committing — terrace of this age may need roof work"
        ]
      }
    },
    {
      "rank": 2,
      "deal_score": 86,
      "label": "⚡ UNDERVALUED — Strong yield play",
      "property": {
        "address": "12 Wilmslow Road, Fallowfield, Manchester M14 6NJ",
        "type": "2-bed flat",
        "asking_price": "£148,000",
        "days_on_market": 52
      },
      "rental_analysis": {
        "estimated_monthly_rent": "£1,100/month (student/young professional demand)",
        "gross_yield": "8.92%",
        "airbnb_potential": "£1,900/month — Fallowfield festivals & Manchester events"
      },
      "deal_analysis": {
        "verdict": "🟢 GO — Consistent demand from students + young professionals",
        "suggested_offer": "£138,000"
      }
    }
  ],
  "rising_neighbourhoods": [
    {
      "area": "Moston M8",
      "current_avg_price": "£129,000",
      "5yr_growth_projection": "+28% based on regeneration signals",
      "why_rising": "£4.2M council investment + tram extension + early gentrification indicators"
    }
  ],
  "investment_brief_video": {
    "script": "Manchester M8. 3-bed terraced house. Asking £129,000 — we're offering £115,000. The seller has been on market 84 days and has dropped the price twice. They're relocating to Australia and need to move. Comparable sales put market value at £151,000 — that's £36,000 in instant equity at our offer price. Rental income: £950 per month, 9.8% gross yield. Regeneration funding of £4.2 million just confirmed for this postcode. This is the deal.",
    "duration": "60s",
    "status": "produced",
    "file": "outputs/manchester_m8_deal_brief.mp4"
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class real estate investment analyst and deal sourcer.

PROPERTY LISTINGS DATA: {{scraped_listings}}
SOLD PRICES DATA: {{comparable_sales}}
RENTAL DATA: {{rental_and_airbnb_comparables}}
NEIGHBOURHOOD DATA: {{news_maps_reddit_data}}

INVESTMENT CRITERIA:
- Strategy: {{strategy}}
- Budget: {{budget}}
- Min yield: {{min_yield}}%
- Location: {{location}}

FOR EACH PROPERTY GENERATE:
1. Deal score (0–100):
   - Undervaluation margin (30%): price vs comparable sqft value
   - Rental yield strength (25%): gross yield vs area benchmark
   - Distressed seller urgency (25%): days on market + price drops + keywords
   - Neighbourhood trajectory (20%): regeneration + demand signals

2. Label: 🔥 Motivated Seller / ⚡ Undervalued / ✅ Solid Yield / ⚠️ Monitor

3. Valuation analysis:
   - Price per sqft vs area average
   - % undervaluation vs comparable sales
   - Estimated instant equity at asking price

4. Rental analysis:
   - Long-let monthly estimate + gross yield
   - Airbnb monthly estimate + gross yield (if applicable)
   - Net yield after typical costs
   - Break-even timeline

5. Distressed signals list (specific, not generic)

6. Neighbourhood score + key growth catalysts

7. Deal analysis:
   - GO / PROCEED WITH CAUTION / NO
   - Suggested offer price with rationale
   - 3 exit strategies
   - Top 2 risks with mitigation

8. 60-second investment brief video script (for lenders/partners)

RULES:
- All yield calculations must show working — no black box numbers
- Suggested offer must be defensible with data
- Never recommend without flagging key risks

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Scan | Apify Cost | InVideo Cost | Total | Agent/Sourcer Price |
|---|---|---|---|---|
| 1 market (100 properties) | ~$0.80 | ~$3 | ~$3.80 | £500–£2,000 deal fee |
| 5 markets | ~$4 | ~$15 | ~$19 | £2,500–£10,000 |
| Weekly deal alerts | ~$0.80/week | ~$3 | ~$15/month | Always-fresh pipeline |

> 💡 **Start free on [Apify](https://www.apify.com?fpr=dx06p) — $5 credits included**
> 🎬 **Produce your investment briefs with [InVideo AI](https://invideo.sjv.io/TBB)**

---

## 🔗 Revenue Opportunities

| User | How They Use It | Revenue |
|---|---|---|
| **Property Investor** | Find undervalued deals before competition | Build £1M+ portfolio faster |
| **Deal Sourcer** | Sell sourced deals to investors at £2,000–£5,000 fee | £10K–£50K/month |
| **Estate Agent** | Identify motivated sellers for quick sale service | Premium listings |
| **Mortgage Broker** | Bring investment deals to HNW clients | More transactions |
| **Property Coach** | Deliver live deal analysis to students | Premium course content |

---

## 📊 Why This Beats Every Alternative

| Feature | Rightmove Premium | Manual Research | **AI Real Estate Goldmine Finder** |
|---|---|---|---|
| Undervaluation scoring | ❌ | Partial | ✅ |
| Distressed seller detection | ❌ | ❌ | ✅ |
| Rental yield calculation | ❌ | Manual | ✅ |
| Airbnb revenue estimation | ❌ | ❌ | ✅ |
| Neighbourhood trajectory | ❌ | ❌ | ✅ |
| Suggested offer price | ❌ | ❌ | ✅ |
| Investment brief video | ❌ | ❌ | ✅ |
| Cost | £19.99/month | Weeks of time | ~£3/run |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your [Apify](https://www.apify.com?fpr=dx06p) API Token**  
Go to: **Settings → Integrations → API Token**

**Step 2 — Get your [InVideo AI](https://invideo.sjv.io/TBB) account**  
Go to: **Settings → API → Copy your key**

**Step 3 — Input your target market & criteria & run**  
Location + strategy + budget. Full deal radar in minutes.

---

## ⚡ Pro Tips

- **Days on market is your best friend** — 60+ days = negotiating power, 90+ = serious motivation
- **Two price reductions = near-desperation** — they've already accepted less is coming
- **Run the Airbnb calculator on every deal** — short-let yields are often double long-let
- **Rising neighbourhood > already risen** — buy the area before the coffee shops, not after
- **The investment brief video closes JV partners** — lenders respond to visuals + numbers together

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI*
