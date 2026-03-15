---
name: high-intent-lead-sniper
description: "High-Intent Lead Sniper — Find Prospects Ready to Buy RIGHT NOW"
---

# 💰 High-Intent Lead Sniper — Find Prospects Who Are Ready to Buy RIGHT NOW

**Slug:** `high-intent-lead-sniper`  
**Category:** Sales Intelligence / Lead Generation  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

> Stop prospecting cold leads. This skill detects **companies showing real buying signals RIGHT NOW** — recent funding, hiring sprees, tech stack changes, competitor frustration posts, and LinkedIn trigger events — then generates hyper-personalized outreach timed to the exact moment they're ready to spend.

---

## 💥 Why This Is The Most Powerful Lead Gen Skill on ClawHub

The difference between a 2% reply rate and a 34% reply rate is **timing**. The exact same offer sent to the exact same person converts 17x better when it arrives at the moment they have budget, urgency, and pain.

Most lead gen tools find WHO to contact. This skill finds WHO to contact AND **exactly when** — by detecting the real-world signals that precede a buying decision.

**Every B2B sales team, agency, SaaS company, and consultant on earth needs this.** Intent data tools like Bombora and 6sense charge **$30,000–$100,000/year**. This skill delivers the same intelligence for under $2 per run.

**Buying signals detected automatically:**
- 💰 **Recent funding** — fresh cash = new budget cycles. Series A/B companies buy tools immediately after closing.
- 👥 **Hiring for specific roles** — hiring a VP Sales = scaling. Hiring SDRs = outbound investment.
- 🔧 **Tech stack changes** — switching CRM, adding new tools = active evaluation period.
- 😤 **Competitor frustration** — public complaints about your competitor = warm lead with proven need.
- 📣 **LinkedIn trigger posts** — "We just hit $1M ARR", "We're expanding to Europe", "Looking for X solution."
- 📰 **Press & news signals** — new product launches, executive hires = growth phase.

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| [Apify](https://www.apify.com?fpr=dx06p) — LinkedIn Jobs Scraper | Detect hiring signals — who's scaling right now |
| [Apify](https://www.apify.com?fpr=dx06p) — LinkedIn Post Scraper | Trigger posts — expansion, wins, frustrations |
| [Apify](https://www.apify.com?fpr=dx06p) — Crunchbase Scraper | Recent funding rounds — who just got money |
| [Apify](https://www.apify.com?fpr=dx06p) — Twitter/X Scraper | Public complaints about competitors |
| [Apify](https://www.apify.com?fpr=dx06p) — Google News Scraper | Press mentions — launches, awards, expansions |
| [Apify](https://www.apify.com?fpr=dx06p) — Wappalyzer | Tech stack detection — recent tool changes |
| [InVideo AI](https://invideo.sjv.io/TBB) | Produce personalized video outreach per lead |
| Claude AI | Signal scoring, intent analysis, outreach personalization |

---

## ⚙️ Full Workflow

```
INPUT: Your ICP (niche + company size + geography) + your offer
        ↓
STEP 1 — Funding Signal Detection
  └─ Companies that raised in last 90 days in your niche
  └─ Extract: amount, round, investors, use of funds
  └─ Score: Series A/B = highest intent for B2B tools
        ↓
STEP 2 — Hiring Signal Analysis
  └─ Job postings that signal YOUR specific buying trigger
  └─ e.g. "Hiring VP Sales" → need CRM / sales tools
  └─ e.g. "Hiring 5 SDRs" → need outbound tools + training
        ↓
STEP 3 — LinkedIn Trigger Post Detection
  └─ Expansion announcements ("launching in Germany")
  └─ Growth milestones ("just hit 1,000 customers")
  └─ Pain signals ("looking for recommendations on X")
        ↓
STEP 4 — Competitor Frustration Mining
  └─ Twitter/X: public complaints about your top 3 competitors
  └─ Reddit: threads asking for competitor alternatives
  └─ G2/Trustpilot: recent 1-2 star reviews of competitors
        ↓
STEP 5 — Tech Stack Change Detection
  └─ Companies that recently added/removed tools
  └─ New tool installs = active evaluation period
  └─ Removed tool = replacement opportunity
        ↓
STEP 6 — Intent Score Calculation (0–100)
  └─ Each signal weighted by recency + relevance + strength
  └─ 🔴 HOT (80+): Multiple signals in last 14 days
  └─ 🟡 WARM (50–79): 1-2 signals in last 30 days
  └─ 🟢 WATCH (30–49): Early signals, monitor weekly
        ↓
STEP 7 — Claude AI Generates Signal-Specific Outreach
  └─ Email references THE exact signal that triggered the alert
  └─ LinkedIn DM written around their specific trigger event
  └─ Video script personalized to their buying moment
        ↓
OUTPUT: Ranked lead list by intent score + signal breakdown + outreach per lead
```

---

## 📥 Inputs

```json
{
  "icp": {
    "description": "B2B SaaS companies, Series A–B, 20–200 employees",
    "industries": ["HR Tech", "Sales Tech", "MarTech"],
    "geographies": ["United States", "United Kingdom", "Germany"],
    "exclude": ["agencies", "consulting firms"]
  },
  "your_offer": {
    "product": "AI-powered sales analytics platform",
    "problem_solved": "Sales teams flying blind on pipeline — no real-time visibility",
    "key_result": "Average customer increases win rate by 28% in 90 days",
    "competitor_alternatives": ["Gong", "Chorus", "Clari"]
  },
  "buying_signals": {
    "funding_rounds": ["Series A", "Series B"],
    "hiring_triggers": ["VP of Sales", "Sales Operations", "Revenue Operations", "SDR"],
    "linkedin_keywords": ["scaling", "expanding", "pipeline", "revenue growth"],
    "competitor_frustration_targets": ["Gong", "Chorus"],
    "tech_stack_triggers": ["removed Salesforce", "added HubSpot", "added Outreach"]
  },
  "max_leads": 50,
  "lookback_days": 30,
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
  "scan_summary": {
    "date": "2026-03-03",
    "companies_scanned": 847,
    "hot_leads": 12,
    "warm_leads": 31,
    "watch_list": 44,
    "avg_intent_score_hot": 88
  },
  "leads": [
    {
      "rank": 1,
      "company": "RevFlow HQ",
      "website": "revflowhq.com",
      "industry": "Sales Tech",
      "size": "45 employees",
      "intent_score": 96,
      "intent_label": "🔴 HOT — Contact within 24 hours",
      "signals_detected": [
        {
          "type": "💰 Series A Funding",
          "detail": "Raised $8.2M Series A — announced 6 days ago",
          "source": "TechCrunch / Crunchbase",
          "insight": "New budget cycle just opened. CTOs get discretionary budgets post-funding."
        },
        {
          "type": "👥 Hiring Signal",
          "detail": "Posted 4 SDR roles + 1 VP of Sales in last 14 days",
          "source": "LinkedIn Jobs",
          "insight": "Scaling outbound team = active need for sales analytics."
        },
        {
          "type": "😤 Competitor Frustration",
          "detail": "CEO tweeted: 'Gong is great but costs a fortune at our stage — anyone using alternatives?'",
          "source": "Twitter/X — 3 days ago",
          "insight": "Actively evaluating Gong alternatives RIGHT NOW. This is a hand-raise."
        }
      ],
      "decision_maker": {
        "name": "Marcus Webb",
        "title": "CEO & Co-founder",
        "linkedin": "linkedin.com/in/marcus-webb-revflow",
        "email": "marcus@revflowhq.com",
        "twitter": "@marcuswebb_sf"
      },
      "outreach": {
        "email_subject": "Re: your tweet about Gong alternatives — worth 15 min?",
        "email_body": "Hi Marcus,\n\nSaw your tweet about Gong being expensive at your stage — we hear that a lot, especially post-Series A when every dollar counts.\n\nWe built exactly what you're describing: real-time sales analytics at a fraction of Gong's cost. Typical Series A team pays around $1,200/month total — not per seat.\n\nWith 4 SDRs coming on board, the timing makes sense — our customers see a 28% win rate improvement within 90 days.\n\nWorth a 15-minute call this week?\n\n[Your name]",
        "linkedin_dm": "Marcus — congrats on the Series A! Saw your tweet about Gong costs. We built a lighter-weight alternative for exactly your stage. 28% avg win rate lift. Worth a quick chat?",
        "best_channel": "Twitter DM first — he's active there and it references his public post naturally",
        "best_time": "Tuesday or Wednesday morning 8–10am PST"
      },
      "video_outreach": {
        "script": "Marcus, congrats on RevFlow's Series A. You mentioned on Twitter you're evaluating Gong alternatives. Here's exactly how we'd help your new sales team hit quota faster — in 60 seconds.",
        "status": "produced",
        "file": "outputs/video_revflow_marcus.mp4"
      }
    }
  ],
  "competitor_frustration_leads": {
    "total_found": 23,
    "highlights": [
      {
        "person": "@startupfounder_nyc",
        "post": "Gong is great but $1,500/seat/year is insane for a 15-person team. What are people using instead?",
        "posted": "2 days ago",
        "engagement": "47 likes, 31 replies",
        "intent": "🔴 HOT — actively seeking alternative RIGHT NOW"
      }
    ]
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class B2B sales intelligence analyst specializing in buying intent signals.

DETECTED SIGNALS DATA: {{all_signals_data}}

YOUR OFFER:
- Product: {{product}}
- Problem solved: {{problem_solved}}
- Key result: {{key_result}}
- Competitors you replace: {{competitors}}

ICP: {{icp_description}}

FOR EACH COMPANY GENERATE:
1. Intent score (0–100):
   - Funding signal: up to 35 pts (recency + round size)
   - Hiring signal: up to 30 pts (role relevance + volume)
   - LinkedIn trigger: up to 25 pts (recency + specificity)
   - Competitor frustration: up to 35 pts (public + active)
   - Tech stack change: up to 25 pts (recency + relevance)
   Cap at 100.

2. Intent label + urgency instruction

3. Signal breakdown — for each signal:
   - Specific detail, source + date
   - Why it indicates buying intent for YOUR offer

4. Decision maker + best contact channel

5. Outreach:
   - Email: subject references specific signal, max 120 words, clear CTA
   - LinkedIn DM: 60 words max
   - Video script: 60 seconds personalized to buying moment
   - Best channel + timing

GOLDEN RULE: Every outreach MUST reference a SPECIFIC signal.
Generic outreach = this skill has failed.

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Leads | Apify Cost | InVideo Cost | Total | Intent Tool Equivalent |
|---|---|---|---|---|
| 50 leads | ~$0.80 | ~$10 | ~$10.80 | Bombora: $30K/year |
| 200 leads | ~$2.80 | ~$30 | ~$32.80 | 6sense: $60K/year |
| 500 leads | ~$6.50 | ~$50 | ~$56.50 | G2 Buyer Intent: $20K/year |
| Daily auto-run | ~$0.80/day | ~$10 | ~$34/month | Savings: $29,966/month |

> 💡 **Get started free on [Apify](https://www.apify.com?fpr=dx06p) — $5 credits included**
> 🎬 **Produce personalized video outreach with [InVideo AI](https://invideo.sjv.io/TBB)**

---

## 🔗 Revenue Opportunities

| User | How They Use It | Revenue Impact |
|---|---|---|
| **B2B Sales Team** | Contact hot leads at perfect timing | 3–5x pipeline conversion |
| **SDR / BDR** | Replace 20h manual research | 10x more qualified meetings |
| **Marketing Agency** | Sell intent-based lead gen as premium service | $2,000–$10,000/month per client |
| **SaaS Founder** | Find early customers with exact buying signals | First 100 customers in 60 days |
| **VC / Investor** | Detect companies about to raise | Deal flow edge |

---

## 📊 Why This Destroys Every Competitor

| Feature | Bombora ($30K/yr) | LinkedIn Sales Nav ($1,200/yr) | **High-Intent Lead Sniper** |
|---|---|---|---|
| Funding signal detection | ❌ | ❌ | ✅ |
| Hiring intent analysis | ❌ | Partial | ✅ |
| Competitor frustration mining | ❌ | ❌ | ✅ |
| LinkedIn trigger post detection | ❌ | Manual | ✅ |
| Tech stack change alerts | ❌ | ❌ | ✅ |
| AI-personalized outreach | ❌ | ❌ | ✅ |
| Video outreach produced | ❌ | ❌ | ✅ |
| Annual cost | $30,000 | $1,200 | ~$408/year |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your [Apify](https://www.apify.com?fpr=dx06p) API Token**  
Go to: **Settings → Integrations → API Token**

**Step 2 — Get your [InVideo AI](https://invideo.sjv.io/TBB) account**  
Go to: **Settings → API → Copy your key**

**Step 3 — Define your ICP + buying signals & run**  
Niche + signals + your offer. Ranked hot leads in under 10 minutes.

---

## ⚡ Pro Tips

- **Contact HOT leads within 2 hours** — intent signals decay fast
- **Always reference THE specific signal** — "Saw your Series A" converts 8x better than generic openers
- **Competitor frustration = easiest close** — they already know they have a problem
- **Funding signal = open budget window** — new money spent in the first 60–90 days post-close
- **Video on hot leads** — 60-second personalized video gets 3x the reply rate of cold email alone

---

## 🏷️ Tags

`lead-generation` `intent-data` `b2b-sales` `buying-signals` `funding-detection` `hiring-signals` `apify` `invideo` `outreach` `sales-intelligence` `pipeline` `sdr`

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI*
