---
name: ai-hiring-signal-sales-engine
description: "AI Hiring Signal Sales Engine — Turn Job Postings Into Qualified Sales Leads in 10 Minutes"
---

# 💼 AI Hiring Signal Sales Engine — Turn Job Postings Into Qualified Sales Leads in 10 Minutes

---

## 📋 ClawHub Info

**Slug:** `ai-hiring-signal-sales-engine`

**Display Name:** `AI Hiring Signal Sales Engine — Turn Job Postings Into Qualified Sales Leads in 10 Minutes`

**Changelog:** `v1.0.0 — Scrapes LinkedIn, Indeed & job boards in real-time to detect companies hiring for roles that signal they need YOUR product, scores each lead by hiring urgency and budget signals, finds decision maker contacts, generates role-specific outreach tied to the exact job posting, and produces a prospecting video via InVideo AI. Powered by Apify + InVideo AI + Claude AI.`

**Tags:** `hiring-signals` `job-postings` `b2b-sales` `lead-generation` `apify` `invideo` `sales-intelligence` `linkedin` `intent-data` `pipeline` `outreach` `sdr`

---

**Category:** Sales Intelligence / B2B Lead Generation  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

> Every job posting is a buying signal in disguise. A company hiring a "Head of Sales Operations" needs a CRM. Hiring "5 SDRs" needs outbound software. Hiring a "Data Analyst" needs a BI tool. This skill scrapes every relevant job posting in real-time, decodes the hidden buying signal inside each one, and delivers personalized outreach to the decision maker — before your competitors even notice the posting.

---

## 💥 Why This Skill Will Explode on ClawHub

The **Job Market Intelligence** skill already has **325 views** — one of the top on the platform. This skill takes that data and turns it into direct revenue.

Job postings are the most underused source of B2B intent data in existence. Every single day, thousands of companies publicly announce exactly what they're struggling with, what they're investing in, and what they need — through their job descriptions.

This skill is the only one on ClawHub that **decodes job postings as sales intelligence** and turns them into a full outreach campaign automatically.

**Target audience:** Every B2B SaaS company, agency, consultant, and service business. If a company hiring a specific role means they need your product — this skill is your unfair advantage.

**What gets automated:**
- 🔍 Scrape **LinkedIn, Indeed & job boards** for role-specific hiring signals daily
- 🧠 Decode **hidden buying signal** in every job posting — what tool/service does this role require?
- 💰 Score each company by **budget signals** — headcount growth + funding = real spend
- 👤 Find **decision maker** — not the person being hired, the person doing the hiring
- ✍️ Write **job-specific outreach** that references the exact role they're hiring for
- 🎬 Produce **prospecting video** via [InVideo AI](https://invideo.sjv.io/TBB) for high-value targets
- 📅 Build **daily pipeline** — fresh hiring signals every morning

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| [Apify](https://www.apify.com?fpr=dx06p) — LinkedIn Jobs Scraper | Real-time job postings — role, company, requirements, date posted |
| [Apify](https://www.apify.com?fpr=dx06p) — Indeed Scraper | Job board coverage — catch companies not on LinkedIn |
| [Apify](https://www.apify.com?fpr=dx06p) — LinkedIn Company Scraper | Company headcount, growth rate, recent news |
| [Apify](https://www.apify.com?fpr=dx06p) — LinkedIn Profile Scraper | Decision maker identification + contact signals |
| [Apify](https://www.apify.com?fpr=dx06p) — Crunchbase Scraper | Funding rounds — who has budget right now |
| [Apify](https://www.apify.com?fpr=dx06p) — Google News Scraper | Company news — expansion, launches, new contracts |
| [InVideo AI](https://invideo.sjv.io/TBB) | Produce personalized video for high-value prospect outreach |
| Claude AI | Signal decoding, lead scoring, outreach personalization |

---

## ⚙️ The Hiring Signal Decoder Library

The skill uses a **pre-built signal decoder** that maps job titles to buying intent:

```
HIRING SIGNAL → YOUR PRODUCT OPPORTUNITY

"Head of Sales Operations" or "RevOps Manager"
→ They're scaling sales process = need CRM, sales intelligence, forecasting tools

"5x SDR / BDR roles posted at once"
→ Building outbound from scratch = need sequencing, dialer, lead gen tools

"Data Engineer" or "Analytics Engineer"
→ Building data infrastructure = need BI tools, data warehouse, ETL platforms

"Head of Customer Success" (first CS hire)
→ Scaling post-product-market-fit = need CS software, NPS tools, onboarding platforms

"Performance Marketing Manager"
→ Scaling paid acquisition = need attribution, ad management, landing page tools

"Cybersecurity Engineer" or "CISO"
→ Security investment = need compliance, endpoint, identity tools

"Head of Finance" or "VP of Finance" (first hire)
→ Financial operations scaling = need ERP, billing, expense management

"Recruiter" or "Head of Talent" (multiple roles)
→ Hiring surge = need ATS, HRIS, employer branding tools

"IT Manager" or "Head of IT"
→ Tech stack formalizing = need MDM, SSO, IT management tools

"Content Manager" + "SEO Specialist"
→ Building content engine = need SEO tools, CMS, content platforms
```

---

## ⚙️ Full Workflow

```
INPUT: Your product/service + the hiring signals that indicate need
        ↓
STEP 1 — Daily Hiring Signal Scrape
  └─ LinkedIn Jobs: posted in last 24-48 hours matching signal roles
  └─ Indeed: same signals on broader job board
  └─ Filter: company size, industry, location, posting date
        ↓
STEP 2 — Signal Decoding
  └─ Match job title + requirements to YOUR buying signal library
  └─ Read full job description for additional context signals
  └─ Detect urgency: "ASAP", "immediate start", multiple roles = high urgency
        ↓
STEP 3 — Company Intelligence
  └─ Headcount growth: hiring 10% of team = scaling fast
  └─ Funding: recent raise = budget unlocked
  └─ News: new contract, expansion, product launch = growth phase
  └─ Tech stack: what tools are they already using?
        ↓
STEP 4 — Decision Maker Identification
  └─ NOT the role being hired — the person hiring them
  └─ e.g. Hiring Sales Ops → find VP of Sales or CRO
  └─ e.g. Hiring Data Engineer → find VP of Engineering or CTO
  └─ Extract: name, title, LinkedIn, email
        ↓
STEP 5 — Lead Scoring (0–100)
  └─ Signal strength (35%): how directly does this role indicate need?
  └─ Budget signal (30%): funding + headcount growth + company size
  └─ Urgency (20%): posting recency + volume of similar roles
  └─ Decision maker accessibility (15%): contactable + active?
        ↓
STEP 6 — Claude AI Writes Job-Specific Outreach
  └─ Email references THE specific job posting by title
  └─ Connects the hiring need to your product's value
  └─ Makes them feel understood — you see what they're building
  └─ LinkedIn DM: shorter, references same signal
        ↓
STEP 7 — InVideo AI Produces Prospecting Video
  └─ For top 5 highest-score leads
  └─ 60-second "we see what you're building" video
  └─ References their growth phase + your solution
  └─ Converts 4x better than text for enterprise targets
        ↓
OUTPUT: Daily lead list ranked by score + outreach per lead + video for top targets
```

---

## 📥 Inputs

```json
{
  "your_product": {
    "name": "PipelineIQ",
    "type": "Sales intelligence and forecasting platform",
    "solves": "Sales teams can't forecast revenue accurately — missing quota by 30%+ every quarter",
    "key_result": "Customers improve forecast accuracy from 61% to 89% in 90 days",
    "target_buyer": "VP of Sales, CRO, Head of Revenue Operations"
  },
  "hiring_signals": {
    "primary_signals": [
      "Head of Sales Operations",
      "Revenue Operations Manager",
      "Sales Enablement Manager",
      "VP of Sales (first hire)",
      "Sales Analyst"
    ],
    "secondary_signals": [
      "5+ SDR roles simultaneously",
      "Head of Revenue",
      "Go-to-Market Lead"
    ],
    "company_filters": {
      "size": "50–500 employees",
      "industries": ["SaaS", "Fintech", "Healthcare Tech", "E-commerce"],
      "locations": ["United States", "United Kingdom"],
      "funding_stages": ["Series A", "Series B", "Series C"]
    }
  },
  "limits": {
    "max_leads_per_day": 30,
    "lookback_hours": 48,
    "video_for_top_n_leads": 5
  },
  "production": {
    "invideo_api_key": "YOUR_INVIDEO_API_KEY",
    "video_style": "confident_b2b_saas"
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "daily_pipeline_summary": {
    "date": "2026-03-03",
    "signals_detected": 847,
    "qualified_leads": 28,
    "hot_leads_score_80_plus": 9,
    "warm_leads_score_50_79": 19,
    "estimated_pipeline_value": "$840,000 (at your avg deal size of $30K)"
  },
  "top_leads": [
    {
      "rank": 1,
      "lead_score": 97,
      "urgency": "🔴 HOT — Contact within 2 hours",
      "company": {
        "name": "Vaultify",
        "website": "vaultify.io",
        "industry": "Fintech SaaS",
        "size": "180 employees",
        "funding": "Series B — $22M raised 6 weeks ago",
        "headcount_growth_6mo": "+34%"
      },
      "hiring_signal": {
        "job_title": "Head of Revenue Operations",
        "posted": "14 hours ago",
        "key_requirements_from_jd": [
          "Build forecasting infrastructure from scratch",
          "Own pipeline reporting and accuracy",
          "Evaluate and implement RevOps toolstack"
        ],
        "signal_decoded": "They don't have RevOps infrastructure yet. They're hiring to build it. This is the exact moment to offer a tool — before the new hire arrives and makes their own toolstack decisions.",
        "urgency_signals": ["14 hours old posting", "Series B fresh capital", "First RevOps hire"]
      },
      "company_intelligence": {
        "recent_news": "Vaultify announced European expansion 3 weeks ago — new markets = new revenue forecasting complexity",
        "tech_stack_detected": ["HubSpot CRM", "Outreach", "Gong"],
        "integrations_we_support": "Native HubSpot + Gong integrations — plug in, no migration needed"
      },
      "decision_maker": {
        "name": "Daniel Frost",
        "title": "CRO (Chief Revenue Officer)",
        "linkedin": "linkedin.com/in/daniel-frost-vaultify",
        "email": "daniel.frost@vaultify.io",
        "last_linkedin_post": "3 days ago: 'Excited to build out the RevOps function — big things coming at Vaultify'",
        "best_contact_time": "Tuesday–Thursday 8–9am EST"
      },
      "outreach": {
        "email_subject": "Vaultify's RevOps hire — we can give them a head start",
        "email_body": "Hi Daniel,\n\nSaw you're hiring a Head of RevOps — and your LinkedIn post about building out the function.\n\nMost RevOps hires spend their first 90 days evaluating tools before anything gets built. We can collapse that entirely.\n\nPipelineIQ plugs into your existing HubSpot and Gong stack — no migration, no rip-and-replace. Your new RevOps lead walks in on day 1 with forecast accuracy data already running.\n\nAverage customer improves forecast accuracy from 61% to 89% in 90 days. Especially relevant with European expansion adding new forecasting complexity.\n\nWorth a 20-minute call before your new hire starts?\n\n[Your name] | PipelineIQ",
        "linkedin_dm": "Daniel — congrats on building out RevOps at Vaultify. Most RevOps hires spend 90 days picking tools. We can give yours a head start — PipelineIQ plugs into HubSpot + Gong, zero migration. Forecast accuracy from 61% to 89% in 90 days. Worth a quick chat before they start?",
        "best_channel": "LinkedIn DM first — Daniel posted 3 days ago, he's active"
      },
      "video_outreach": {
        "script": "Daniel — I saw Vaultify is hiring a Head of RevOps. Here's the thing: most RevOps hires spend their first 90 days evaluating tools. We can change that. PipelineIQ already integrates with your HubSpot and Gong stack. Your new hire walks in on day 1 with revenue forecasting already running. We took similar-stage companies from 61% to 89% forecast accuracy in 90 days. With European expansion on the horizon, the timing makes a lot of sense. Let's talk before your new hire starts.",
        "status": "produced",
        "file": "outputs/video_vaultify_daniel.mp4"
      }
    },
    {
      "rank": 2,
      "lead_score": 91,
      "urgency": "🔴 HOT",
      "company": {
        "name": "ScaleHQ",
        "industry": "HR Tech SaaS",
        "size": "95 employees",
        "funding": "Series A — $8M, 10 weeks ago"
      },
      "hiring_signal": {
        "job_title": "Sales Operations Manager",
        "posted": "31 hours ago",
        "signal_decoded": "First Sales Ops hire + Series A fresh = classic 'we're scaling sales now' signal"
      },
      "decision_maker": {
        "name": "Priya Nair",
        "title": "VP of Sales",
        "email": "priya.nair@scalehq.com"
      },
      "outreach": {
        "email_subject": "ScaleHQ's Sales Ops hire — the tool they'll want on day 1",
        "email_body": "Hi Priya,\n\nCongrats on the Series A — and I see you're building out Sales Ops for the first time.\n\nThe biggest challenge new Sales Ops hires face: no historical forecast data to work with. They spend months just building baselines.\n\nPipelineIQ gives them that baseline in 48 hours — retroactive forecast modeling from your HubSpot data.\n\nWorth a quick call this week?"
      }
    }
  ],
  "daily_pipeline": {
    "new_leads_today": 28,
    "estimated_new_arr_opportunity": "$840,000",
    "recommended_action": "Contact top 9 hot leads before end of business today — hiring signals are freshest in first 48 hours"
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class B2B sales intelligence analyst specializing in hiring signal decoding.

JOB POSTING DATA: {{scraped_job_postings}}
COMPANY INTELLIGENCE: {{funding_headcount_news_techstack}}
DECISION MAKER DATA: {{linkedin_profiles_and_contacts}}

YOUR PRODUCT:
- Name: {{product_name}}
- Solves: {{problem}}
- Key result: {{result}}
- Target buyer: {{buyer_title}}
- Integrations: {{integrations}}

HIRING SIGNALS TO DECODE: {{signal_library}}

FOR EACH JOB POSTING:
1. Decode the buying signal:
   - What does hiring this role tell you about their current pain?
   - What tool/service gap does this role reveal?
   - What is the EXACT moment in their growth this represents?

2. Lead score (0–100):
   - Signal strength (35%): direct vs indirect buying signal
   - Budget signal (30%): funding recency + headcount growth + company size
   - Urgency (20%): posting age + volume of similar roles + urgency language in JD
   - Decision maker accessibility (15%): contactable + recently active?

3. Company intelligence summary:
   - Recent news relevant to your product
   - Tech stack detected + your integration advantage
   - Growth phase interpretation

4. Decision maker (the HIRING manager, not the role being hired):
   - Name, title, LinkedIn, email
   - Recent activity for personalization
   - Best contact channel + timing

5. Outreach (references the SPECIFIC job posting):
   - Email: job title in subject, decode their growth stage, your integration advantage, outcome
   - LinkedIn DM: 80 words max
   - Best channel based on recent activity

6. 60-second video script for top 5 leads:
   - Opens with their company name + the specific hiring signal
   - Connects their growth moment to your solution
   - Ends with timing-based urgency (before the new hire starts)

GOLDEN RULE: "I saw you're hiring a [role]" is the most powerful cold email opener in B2B.
It proves you're paying attention. Use it every single time.

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Daily Run | Apify Cost | InVideo Cost | Total | Pipeline Value Generated |
|---|---|---|---|---|
| 30 leads/day | ~$0.60 | ~$5 | ~$5.60 | $500K–$1M ARR opportunity |
| Weekly (5 days) | ~$3 | ~$25 | ~$28 | Fresh pipeline all week |
| Monthly automation | ~$12 | ~$100 | ~$112 | $10M+ pipeline sourced |

> 💡 **Start free on [Apify](https://www.apify.com?fpr=dx06p) — $5 credits included**
> 🎬 **Produce your prospect videos with [InVideo AI](https://invideo.sjv.io/TBB)**

---

## 🔗 Revenue Opportunities

| User | How They Use It | Revenue Impact |
|---|---|---|
| **B2B SaaS SDR** | Replace 4 hours of manual research with 10-minute daily run | 5x more qualified meetings |
| **Sales Team Lead** | Arm every rep with fresh hiring signal leads daily | 3x pipeline velocity |
| **Agency Owner** | Sell hiring signal prospecting as a service | $2,000–$5,000/month per client |
| **SaaS Founder** | Self-serve pipeline at scale from day 1 | First 100 customers |
| **Marketing Agency** | Trigger paid ads to companies posting key roles | Highest-intent ad audiences |

---

## 📊 Why This Beats Every Alternative

| Feature | Bombora ($30K/yr) | LinkedIn Sales Nav ($1,200/yr) | **AI Hiring Signal Sales Engine** |
|---|---|---|---|
| Real-time job posting signals | ❌ | Partial | ✅ |
| Signal decoding (what it means) | ❌ | ❌ | ✅ |
| Decision maker identification | ❌ | Manual | ✅ |
| Job-specific outreach written | ❌ | ❌ | ✅ |
| Video prospecting produced | ❌ | ❌ | ✅ |
| Daily pipeline automation | ❌ | ❌ | ✅ |
| Annual cost | $30,000 | $1,200 | ~$1,344 |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your [Apify](https://www.apify.com?fpr=dx06p) API Token**  
Go to: **Settings → Integrations → API Token**

**Step 2 — Get your [InVideo AI](https://invideo.sjv.io/TBB) account**  
Go to: **Settings → API → Copy your key**

**Step 3 — Define your hiring signals & run daily**  
Product + signal roles + company filters. Fresh pipeline every morning.

---

## ⚡ Pro Tips

- **"I saw you're hiring a [role]" is the #1 cold email opener** — it's specific, it's relevant, it works
- **Contact within 48 hours of posting** — the signal is freshest, the pain is most acute
- **Target the hiring manager, not the role** — the VP of Sales reading your email knows exactly why they're hiring
- **Video for enterprise targets** — a 60-second "we see what you're building" video closes enterprise deals
- **Run it daily, not weekly** — hiring signals are time-sensitive, first mover wins every time

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI*
