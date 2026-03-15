---
name: outbound-campaign-autopilot
description: "Outbound Campaign Autopilot — From Niche to Full Campaign in 15 Minutes"
---

# 🎯 Outbound Campaign Autopilot — From Niche to Full Campaign in 15 Minutes

---

## 📋 ClawHub Info

**Slug:** `outbound-campaign-autopilot`

**Display Name:** `Outbound Campaign Autopilot — From Niche to Full Campaign in 15 Minutes`

**Changelog:** `v1.0.0 — Scrapes qualified leads, segments them by intent level, writes 15 personalized emails across 3 sequences, generates LinkedIn messages, creates 3 ad hooks, produces a video outreach asset via InVideo AI, and delivers a full campaign brief with objection handlers. Powered by Apify + InVideo AI + Claude AI.`

**Tags:** `outbound` `cold-email` `linkedin-outreach` `sales-automation` `lead-generation` `apify` `invideo` `email-sequence` `b2b-sales` `campaign` `sdr` `autopilot`

---

**Category:** Sales Automation / Outbound Marketing  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

> Input your niche, country, and offer. Get a **complete outbound campaign** — qualified leads scraped, personalized email sequences written, LinkedIn messages crafted, ad hooks generated, and a video cold outreach asset produced. Everything you need to launch a full outbound campaign in under 15 minutes. On autopilot.

---

## 💥 Why "Autopilot" Is The Magic Word That Sells This Skill

Building an outbound campaign from scratch takes 2–3 weeks: find leads, research them, write emails, build sequences, create LinkedIn messages, test ad angles. Most teams never finish before priorities shift.

This skill collapses that 3-week process into **one 15-minute run.** Input your niche. Get a campaign-ready package with everything already done.

**Every sales team, agency, freelancer, SaaS founder, and recruiter is your audience.** Outbound is the #1 revenue-generating activity in B2B — and this skill makes it effortless.

**What gets automated:**
- 🔍 Scrape **qualified leads** matching your exact ICP
- 🧠 Research each lead — company context, personal signals
- ✍️ Write **5-email sequences** personalized per lead segment
- 💼 Generate **LinkedIn connection + follow-up messages**
- 📣 Create **3 ad hooks** for paid retargeting of the same audience
- 🎬 Produce **video cold outreach asset** via [InVideo AI](https://invideo.sjv.io/TBB)
- 📊 Build **campaign brief** — messaging pillars, objection handlers, talk tracks

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| [Apify](https://www.apify.com?fpr=dx06p) — LinkedIn Company Scraper | Qualified companies matching ICP |
| [Apify](https://www.apify.com?fpr=dx06p) — LinkedIn Profile Scraper | Decision maker identification + personal context |
| [Apify](https://www.apify.com?fpr=dx06p) — Website Content Crawler | Company context for personalization |
| [Apify](https://www.apify.com?fpr=dx06p) — Google News Scraper | Recent news for hyper-personalized openers |
| [Apify](https://www.apify.com?fpr=dx06p) — LinkedIn Jobs Scraper | Hiring signals for timing intelligence |
| [Apify](https://www.apify.com?fpr=dx06p) — Email Finder | Verified contact emails per lead |
| [InVideo AI](https://invideo.sjv.io/TBB) | Produce 60s video cold outreach asset |
| Claude AI | Sequence writing, personalization, objection handling, ad copy |

---

## ⚙️ Full Workflow

```
INPUT: Niche + country + offer + ICP + campaign goal
        ↓
STEP 1 — Lead Scraping & Qualification
  └─ LinkedIn: companies matching ICP filters
  └─ Filter: size, industry, location, tech stack, growth signals
  └─ Extract: company name, website, headcount, recent news
        ↓
STEP 2 — Decision Maker Identification
  └─ Find decision maker per company (title match)
  └─ Extract: name, title, LinkedIn URL, email
  └─ Personal context: recent posts, career moves
        ↓
STEP 3 — Lead Segmentation (3 segments)
  └─ Segment A: Hot — hiring + funding + trigger signal
  └─ Segment B: Warm — ICP match, no immediate signal
  └─ Segment C: Long-term — ICP match, early stage
        ↓
STEP 4 — Claude AI Writes Full Campaign
  └─ 5-email sequence per segment (15 emails total)
  └─ Email 1: personalized cold opener
  └─ Email 2: value/insight (no ask)
  └─ Email 3: social proof + case study
  └─ Email 4: objection pre-empt
  └─ Email 5: breakup email
        ↓
STEP 5 — LinkedIn Sequence
  └─ Connection request note (300 chars)
  └─ Day 3 follow-up after connect
  └─ Day 7 value message
  └─ Day 14 CTA message
        ↓
STEP 6 — Ad Hooks for Retargeting
  └─ 3 hooks for Facebook/LinkedIn/Google ads
  └─ Hook A: pain-led
  └─ Hook B: result-led
  └─ Hook C: curiosity-led
        ↓
STEP 7 — InVideo AI Produces Video Asset
  └─ 60-second video for cold email / LinkedIn DM
  └─ Personalized intro + offer + social proof + CTA
  └─ Increases reply rate 3x vs text-only
        ↓
STEP 8 — Campaign Brief
  └─ Core messaging pillars (3)
  └─ Top 5 objections + responses
  └─ Talk track for discovery call
  └─ A/B subject line variations per email
        ↓
OUTPUT: 50 qualified leads + full 3-segment campaign + video asset + campaign brief
```

---

## 📥 Inputs

```json
{
  "campaign": {
    "niche": "E-commerce brands doing $1M–$10M revenue",
    "country": "United States",
    "offer": "AI-powered customer retention platform — reduces churn by 35% in 90 days",
    "icp": {
      "company_size": "10–100 employees",
      "industries": ["DTC", "fashion", "beauty", "home goods"],
      "tech_stack_signals": ["Shopify", "Klaviyo"],
      "decision_maker_titles": ["CMO", "Head of Retention", "VP Marketing", "Founder"]
    },
    "campaign_goal": "Book 20 discovery calls in 30 days",
    "from_name": "Alex Chen",
    "company": "RetainAI"
  },
  "limits": {
    "max_leads": 50,
    "segments": 3
  },
  "production": {
    "invideo_api_key": "YOUR_INVIDEO_API_KEY",
    "video_style": "professional_casual"
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "campaign_summary": {
    "leads_found": 50,
    "segment_a_hot": 11,
    "segment_b_warm": 24,
    "segment_c_longterm": 15,
    "estimated_reply_rate": "18–28% (industry benchmark: 4–8%)",
    "estimated_meetings_from_50_leads": "9–14 discovery calls"
  },
  "leads": [
    {
      "rank": 1,
      "segment": "A — Hot",
      "company": "LuminaSkin Beauty",
      "website": "luminaskin.com",
      "industry": "DTC Beauty",
      "revenue_estimate": "$4.2M ARR",
      "tech_stack": ["Shopify Plus", "Klaviyo"],
      "hiring_signal": "Hiring a Customer Retention Manager — posted 11 days ago",
      "decision_maker": {
        "name": "Priya Mehta",
        "title": "CMO",
        "email": "priya@luminaskin.com",
        "linkedin": "linkedin.com/in/priya-mehta-lumina"
      }
    }
  ],
  "email_sequences": {
    "segment_a_hot": {
      "email_1": {
        "subject_a": "Congrats on Forbes — quick question about retention at LuminaSkin",
        "subject_b": "LuminaSkin's retention stack — noticed something interesting",
        "body": "Hi Priya,\n\nSaw the Forbes 30 Under 30 feature — incredible what you've built. Congrats.\n\nI also noticed you're hiring a Customer Retention Manager — tells me retention is a real focus right now.\n\nWe built RetainAI for DTC beauty brands on Shopify. Average customer reduces churn by 35% in 90 days — without adding headcount.\n\n15 minutes this week?\n\nAlex Chen | RetainAI",
        "send_day": 1
      },
      "email_2": {
        "subject": "The retention metric most DTC beauty brands ignore",
        "body": "Hi Priya,\n\nNo ask in this one — just something useful.\n\nMost DTC brands obsess over CAC. The brands that win obsess over repeat purchase rate by cohort month 3.\n\nA customer who buys twice in 90 days is 5x more likely to become a long-term customer. The window to trigger that second purchase is 23–31 days after the first.\n\nFor a brand at LuminaSkin's stage, moving that metric from 20% to 35% is worth $840K in additional annual revenue.\n\nHappy to show you how we calculate this for your specific numbers.\n\nAlex",
        "send_day": 3
      },
      "email_3": {
        "subject": "How Glow Theory cut churn 41% in 60 days",
        "body": "Hi Priya,\n\nQuick case study — Glow Theory (similar DTC beauty brand, $3.8M ARR on Shopify):\n\n→ One-time buyer rate dropped from 67% to 42%\n→ Revenue per customer increased from $73 to $118\n→ No new headcount required\n\nWould the numbers make sense for a 20-minute conversation?\n\nAlex",
        "send_day": 7
      },
      "email_4": {
        "subject": "The objection I hear most from CMOs",
        "body": "Hi Priya,\n\n'We already have Klaviyo flows for this' — totally fair. But Klaviyo is an execution layer, not an intelligence layer. We tell you which customers are about to churn 14 days before they do.\n\n'Not ready for another tool' — we integrate in 48 hours and run natively inside Shopify. No new login.\n\nStill worth 15 minutes?\n\nAlex",
        "send_day": 12
      },
      "email_5": {
        "subject": "Closing the loop",
        "body": "Hi Priya,\n\nI'll keep this short — I'll assume the timing isn't right.\n\nIf retention becomes a bigger priority at LuminaSkin, we'd love to help.\n\nWishing you a great Q2.\n\nAlex\n\nP.S. — If this landed in the wrong inbox, feel free to forward to whoever owns retention.",
        "send_day": 21
      }
    }
  },
  "linkedin_sequence": {
    "connection_request": "Hi Priya — saw the Forbes feature on LuminaSkin, impressive growth. I work with DTC beauty brands on retention and thought it'd be worth connecting. Alex",
    "day_3_followup": "Thanks for connecting! Sharing something useful for brands at your stage: [link to resource]",
    "day_7_value": "Quick stat: DTC beauty brands that crack month-3 repeat purchase rate grow 2.3x faster. Happy to share how we measure this.",
    "day_14_cta": "Priya — I'll be direct. We help DTC beauty brands reduce churn 35% in 90 days. LuminaSkin fits our sweet spot. Worth 15 minutes?"
  },
  "ad_hooks": [
    { "type": "Pain-led", "hook": "67% of your customers will never buy from you again. Here's how to fix it in 90 days." },
    { "type": "Result-led", "hook": "DTC beauty brands using RetainAI see 35% less churn in their first 90 days. No new headcount." },
    { "type": "Curiosity-led", "hook": "The metric that predicts whether a DTC brand survives year 3. (Most CMOs track the wrong number.)" }
  ],
  "campaign_brief": {
    "core_messaging_pillars": [
      "Speed to value — 35% churn reduction in 90 days, not 9 months",
      "No headcount — AI does what a retention manager would do",
      "Native integration — lives inside Shopify, zero new login"
    ],
    "top_objections": [
      { "objection": "We already use Klaviyo for this", "response": "Klaviyo executes. We predict. We tell you who's about to churn 14 days before they do." },
      { "objection": "Not the right time", "response": "Setup takes 48 hours and runs automatically. No ongoing time investment from your team." },
      { "objection": "How is this different from loyalty programs?", "response": "Loyalty programs reward repeat buyers. We prevent one-time buyers from becoming one-time buyers." }
    ],
    "discovery_call_opener": "What's your current repeat purchase rate, and what's your target?"
  },
  "video_asset": {
    "script": "If you're running a DTC brand on Shopify, here's a number that matters: 67% of your customers will never buy from you again. Not because they didn't like your product — because nobody followed up at the right moment. RetainAI fixes this automatically. We predict who's about to churn 14 days before they do, trigger the right intervention, and the average brand sees 35% less churn in 90 days. No new headcount. Setup in 48 hours. Let's talk.",
    "duration": "60s",
    "status": "produced"
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class outbound sales strategist and B2B copywriter.

LEAD DATA: {{qualified_leads_with_context}}

CAMPAIGN PROFILE:
- Niche: {{niche}}
- Country: {{country}}
- Offer: {{offer}}
- ICP: {{icp}}
- Goal: {{campaign_goal}}
- Sender: {{from_name}} at {{company}}

GENERATE COMPLETE OUTBOUND CAMPAIGN:

1. Lead segmentation (3 segments):
   - Segment A: Hot (intent signals present)
   - Segment B: Warm (ICP match, no signal)
   - Segment C: Long-term (nurture)

2. 5-email sequence PER SEGMENT (15 total):
   Email 1: Personalized opener — references specific company signal
   Email 2: Value/insight — no ask, pure education
   Email 3: Social proof — specific case study with numbers
   Email 4: Objection pre-empt — address #1 objection directly
   Email 5: Breakup — short, gracious, leaves door open
   Each email: 2 subject line A/B variations

3. LinkedIn sequence (4 messages):
   Connection request (300 char max) / Day 3 value / Day 7 share / Day 14 CTA

4. 3 ad hooks (pain / result / curiosity)

5. Campaign brief:
   - 3 core messaging pillars
   - Top 5 objections + responses
   - Discovery call opening question

6. 60-second video script

COPYWRITING RULES:
- Never use "I hope this email finds you well"
- Subject lines must create curiosity OR reference a specific signal
- Email 2 must be so valuable they'd share it — zero pitch
- Breakup email must feel human, not passive-aggressive

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Campaign | Apify Cost | InVideo Cost | Total | Agency Build Cost |
|---|---|---|---|---|
| 50 leads + full campaign | ~$0.80 | ~$3 | ~$3.80 | $3,000–$10,000 |
| 200 leads + campaign | ~$2.80 | ~$3 | ~$5.80 | $10,000–$30,000 |
| Monthly (4 campaigns) | ~$11 | ~$12 | ~$23 | $40,000–$120,000 |

> 💡 **Get started free on [Apify](https://www.apify.com?fpr=dx06p) — $5 credits included**
> 🎬 **Produce your video outreach with [InVideo AI](https://invideo.sjv.io/TBB)**

---

## 🔗 Revenue Opportunities

| User | How They Use It | Revenue |
|---|---|---|
| **B2B SaaS Founder** | Launch outbound from zero in 15 minutes | First 50 customers |
| **Sales Agency** | Deliver campaign packages to clients | $2,000–$10,000 per campaign |
| **Freelance Copywriter** | Add outbound sequences as premium service | +$3,000–$5,000 per project |
| **SDR Team Lead** | Arm every rep with a full campaign instantly | 3x meeting volume |
| **Startup Accelerator** | Deploy outbound for every cohort company | Portfolio-wide growth |

---

## 📊 Why This Beats Every Alternative

| Feature | Hiring Copywriter | Apollo.io ($99/mo) | **Outbound Campaign Autopilot** |
|---|---|---|---|
| Qualified lead scraping | ❌ | ✅ | ✅ |
| 3-segment email sequences | ✅ | ❌ | ✅ |
| LinkedIn sequence | ❌ | ❌ | ✅ |
| Ad hooks generated | ❌ | ❌ | ✅ |
| Video outreach asset | ❌ | ❌ | ✅ |
| Objection handlers | ✅ | ❌ | ✅ |
| Discovery call talk track | ✅ | ❌ | ✅ |
| Cost per campaign | $3,000+ | $99/month | ~$3.80 |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your [Apify](https://www.apify.com?fpr=dx06p) API Token**  
Go to: **Settings → Integrations → API Token**

**Step 2 — Get your [InVideo AI](https://invideo.sjv.io/TBB) account**  
Go to: **Settings → API → Copy your key**

**Step 3 — Define your niche + offer & run**  
ICP + country + campaign goal. Full campaign in 15 minutes.

---

## ⚡ Pro Tips

- **Email 2 is your secret weapon** — pure value, no ask. It's the email they forward to their team.
- **Video in Email 1 = 3x reply rate** — attach your InVideo asset to the first touch
- **A/B test subject lines from day 1** — never guess which one wins
- **Run Segment A on LinkedIn AND email simultaneously** — omnipresence converts
- **Breakup email often gets the most replies** — people respond to finality

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI*
