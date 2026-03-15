---
name: healthcare-wellness-lead-generator
description: "Healthcare & Wellness Lead Generator — Find Patients & Practitioners at Scale"
---

# 🏥 Healthcare & Wellness Lead Generator — Find Patients & Practitioners at Scale

**Slug:** `healthcare-wellness-lead-generator`  
**Category:** Healthcare / Lead Generation  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

> Input a healthcare niche + location. Get a **complete lead generation report** — patients actively seeking care, practitioners to partner with, clinics to sell to, and AI-generated outreach messages for each — all scraped from Google Maps, directories, and health forums. The most underserved lead gen market on ClawHub.

---

## 💥 Why This Skill Is a Sleeping Giant on ClawHub

Healthcare is the **largest industry on earth** — $12 trillion globally. Yet 90% of clinics, practitioners, wellness brands, and health tech companies still rely on word-of-mouth or outdated marketing to find patients and partners.

This skill automates the entire prospecting pipeline for **every player in the healthcare & wellness ecosystem.**

**Your target audience:**
- 🏥 Private clinics & hospitals looking for patients
- 💊 Pharma & medical device reps prospecting practitioners
- 🧘 Wellness brands finding B2B partners (gyms, spas, studios)
- 🩺 Telehealth platforms acquiring new practitioners
- 💉 MedSpa & aesthetic clinics finding local clients
- 🏋️ Personal trainers & nutritionists finding corporate wellness clients

**What gets automated:**
- 📍 Scrape **every clinic, practitioner & wellness business** in any location
- ⭐ Detect **reputation gaps** — low-rated providers losing patients
- 👥 Find **patients actively seeking care** on health forums & Reddit
- 📋 Extract **full contact details** — name, phone, email, address
- 🎯 Score each lead by **conversion potential**
- ✍️ Generate **HIPAA-mindful personalized outreach** per lead type
- 🎬 Produce **patient testimonial-style promo videos** via InVideo AI

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| [Apify](https://www.apify.com?fpr=dx06p) — Google Maps Scraper | Clinics, practitioners, wellness businesses by location |
| [Apify](https://www.apify.com?fpr=dx06p) — Google Search Scraper | Health directories, practitioner listings, certifications |
| [Apify](https://www.apify.com?fpr=dx06p) — Reddit Scraper | Patients seeking care, health complaints, treatment questions |
| [Apify](https://www.apify.com?fpr=dx06p) — Trustpilot Scraper | Clinic reviews — reputation gaps & unhappy patient signals |
| [Apify](https://www.apify.com?fpr=dx06p) — LinkedIn Scraper | Healthcare executives, practice managers, procurement contacts |
| [Apify](https://www.apify.com?fpr=dx06p) — Google News Scraper | New clinic openings, healthcare funding, market signals |
| [InVideo AI](https://invideo.sjv.io/TBB) | Produce wellness promo & patient education videos |
| Claude AI | Lead scoring, outreach generation, partnership pitch copy |

---

## ⚙️ Full Workflow

```
INPUT: Healthcare niche + target location + your role (clinic / brand / rep / platform)
        ↓
STEP 1 — Location-Based Provider Scraping
  └─ Google Maps: every clinic, hospital, practice, wellness center in radius
  └─ Extract: name, address, phone, website, rating, review count, hours
  └─ Filter by: specialty, rating, size, insurance accepted
        ↓
STEP 2 — Reputation Gap Analysis
  └─ Clinics rated 3.5★ or below = losing patients = your opportunity
  └─ Clinics with 50+ unanswered reviews = management problem = sales opening
  └─ New clinics (< 6 months old) = need patients urgently
        ↓
STEP 3 — Active Patient Discovery
  └─ Reddit health communities: people seeking recommendations
  └─ Health forums: unanswered questions = unmet need
  └─ Google trends: rising symptom searches = demand signals
        ↓
STEP 4 — Decision Maker Contact Extraction
  └─ Practice manager / clinic director name
  └─ Email (verified where available)
  └─ LinkedIn profile for B2B outreach
  └─ Direct phone from listing
        ↓
STEP 5 — AI Lead Scoring (0–100)
  └─ Conversion potential based on: need signal + contact quality + timing
  └─ Urgency label: 🔴 Hot / 🟡 Warm / 🟢 New
        ↓
STEP 6 — Claude AI Generates Personalized Outreach
  └─ B2B outreach for clinic/practitioner targets
  └─ Partnership pitch for wellness brand deals
  └─ Patient acquisition messaging for clinics
  └─ All outreach mindful of healthcare communication standards
        ↓
STEP 7 — InVideo AI Produces Wellness Videos
  └─ Patient education video (drives inbound for clinics)
  └─ Practitioner intro video (builds trust online)
  └─ Wellness brand promo (for B2C campaigns)
        ↓
OUTPUT: Ranked lead list + contact details + outreach messages + promo videos
```

---

## 📥 Inputs

```json
{
  "business": {
    "type": "Medical device sales rep",
    "product": "Advanced physiotherapy equipment for sports injury recovery",
    "target_prospect": "Sports medicine clinics and physiotherapy practices",
    "usp": "30% faster recovery times, 5-year warranty, financing available"
  },
  "targeting": {
    "location": "London, UK",
    "radius_km": 30,
    "specialties": ["physiotherapy", "sports medicine", "orthopedics", "rehabilitation"],
    "min_rating": 3.5,
    "practice_size": "small to medium"
  },
  "scraping": {
    "max_leads": 100,
    "include_reputation_analysis": true,
    "include_patient_signals": true
  },
  "production": {
    "invideo_api_key": "YOUR_INVIDEO_API_KEY",
    "video_type": "product_demo_promo",
    "voice": "professional_male_en"
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "scan_summary": {
    "location": "London, UK (30km radius)",
    "total_practices_found": 247,
    "hot_leads": 18,
    "warm_leads": 54,
    "new_opportunities": 31,
    "run_date": "2026-03-03"
  },
  "top_leads": [
    {
      "rank": 1,
      "lead_score": 94,
      "urgency": "🔴 HOT",
      "business": {
        "name": "London Sports Physio & Rehab Centre",
        "address": "47 Harley Street, London W1G 8QN",
        "phone": "+44 20 7946 0892",
        "website": "londonsportsphysio.co.uk",
        "google_rating": 4.6,
        "review_count": 312,
        "specialties": ["Sports physiotherapy", "ACL rehabilitation", "Post-surgical recovery"],
        "established": "2019",
        "staff_estimate": "8-15 practitioners"
      },
      "why_hot": [
        "High review volume (312) = high patient throughput = budget for equipment",
        "4 Google reviews in last 30 days mention 'recovery time' — pain point match",
        "Recently expanded to second location — growth phase = purchasing cycle"
      ],
      "decision_maker": {
        "name": "Dr. James Fletcher",
        "title": "Clinical Director",
        "linkedin": "linkedin.com/in/james-fletcher-physio",
        "email": "j.fletcher@londonsportsphysio.co.uk",
        "phone": "+44 20 7946 0892"
      },
      "reputation_signals": {
        "top_complaint_in_reviews": "Waiting times for equipment — 8 reviews mention delays",
        "opportunity": "Their current equipment is creating patient bottlenecks — perfect timing for upgrade pitch"
      },
      "outreach": {
        "email_subject": "Reducing recovery time at London Sports Physio — quick question",
        "email_body": "Dear Dr. Fletcher,\n\nI came across London Sports Physio & Rehab Centre and was impressed by your reputation — 312 reviews and a consistent 4.6★ is exceptional in this field.\n\nI noticed several patient reviews mention recovery timelines as something your team actively focuses on. That's exactly the problem our physiotherapy equipment was designed to solve.\n\nOur devices are currently helping 3 London clinics achieve 30% faster recovery outcomes for sports injury patients — with zero upfront cost via our financing program.\n\nWould a 20-minute demonstration at your clinic be of interest?\n\nBest regards,\n[Your name]\n[Your phone]",
        "linkedin_message": "Hi Dr. Fletcher — love what you've built at London Sports Physio. I work with clinics achieving 30% faster recovery times with our equipment. Worth a quick chat?",
        "followup_day5": "Just following up on my email — happy to bring the equipment in for a no-obligation demo at a time that suits you."
      }
    },
    {
      "rank": 2,
      "lead_score": 87,
      "urgency": "🔴 HOT",
      "business": {
        "name": "Elite Performance Physiotherapy",
        "address": "12 King's Road, Chelsea, London SW3 4UD",
        "google_rating": 3.8,
        "review_count": 89
      },
      "why_hot": [
        "Rating dropped from 4.2 to 3.8 in last 90 days — losing patients",
        "5 recent reviews mention equipment as outdated",
        "Chelsea location = premium practice = high willingness to invest"
      ],
      "decision_maker": {
        "name": "Sarah Kim",
        "title": "Practice Manager",
        "email": "info@eliteperformancephysio.co.uk"
      },
      "outreach": {
        "email_subject": "Helping Elite Performance stay ahead — equipment upgrade?",
        "email_body": "Dear Sarah,\n\nI wanted to reach out to Elite Performance Physiotherapy — your Chelsea location and focus on elite athletes caught my attention.\n\nI work with leading London physio practices looking to upgrade their equipment and outcomes. Several practices similar to yours have seen significant improvements in both patient satisfaction and recovery metrics after working with us.\n\nWould you be open to a brief call to explore if there's a fit?\n\nBest regards,\n[Your name]"
      }
    }
  ],
  "patient_demand_signals": {
    "reddit_threads": [
      {
        "platform": "Reddit — r/london",
        "post": "Best sports physiotherapist in London for ACL recovery?",
        "urgency": "Posted 2 days ago, 47 comments, still seeking recommendation",
        "opportunity": "Patient actively looking — if you represent a clinic, respond with genuine recommendation"
      },
      {
        "platform": "Reddit — r/running",
        "post": "Any London physios who specialize in marathon runners?",
        "urgency": "Posted today — immediate need",
        "opportunity": "Niche specialization opportunity — target running-focused clinics"
      }
    ],
    "google_trend_rising": [
      "sports physio London (+34% searches this month)",
      "ACL recovery clinic (+28%)",
      "post-op physiotherapy near me (+41%)"
    ]
  },
  "market_insights": {
    "total_practices_london": "247 identified in 30km radius",
    "avg_google_rating": 4.1,
    "practices_below_4_stars": 43,
    "new_practices_last_6_months": 18,
    "highest_concentration_areas": ["Harley Street", "Chelsea", "Canary Wharf", "Wimbledon"],
    "best_outreach_time": "Tuesday–Thursday, 9–11am (practice managers available)"
  },
  "promo_video": {
    "type": "Product demo for clinic outreach",
    "script": "At London's leading sports medicine clinics, recovery time is everything. Our physiotherapy equipment is helping practitioners achieve 30% faster patient outcomes — with zero upfront investment through flexible financing. Join 3 London clinics already transforming their recovery protocols. Book your free demonstration today.",
    "duration": "60s",
    "status": "produced",
    "video_file": "outputs/physio_equipment_promo.mp4"
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class healthcare sales strategist and B2B lead generation expert.

SCRAPED PROVIDER DATA:
{{google_maps_data}}

REPUTATION SIGNALS:
{{review_data}}

PATIENT DEMAND SIGNALS:
{{reddit_and_forum_data}}

DECISION MAKER CONTACTS:
{{linkedin_and_directory_data}}

BUSINESS PROFILE:
- Type: {{business_type}}
- Product/Service: {{product}}
- Target: {{target_prospect}}
- USP: {{usp}}
- Location: {{location}}

FOR EACH LEAD GENERATE:
1. Lead score (0–100) based on:
   - Need signal match (30%)
   - Contact quality (25%)
   - Practice size & budget signals (25%)
   - Timing / urgency (20%)
2. Why hot — 3 specific reasons referencing real scraped data
3. Decision maker identified with contact details
4. Outreach package:
   - Email: professional, references specific practice data,
     mentions their patient reviews or reputation signals
     Max 120 words. Clear CTA.
   - LinkedIn message: 50 words max, human tone
   - Day 5 follow-up: 2 lines, different angle
5. Patient demand signals relevant to their specialty

HEALTHCARE COMMUNICATION RULES:
- Never make unsubstantiated clinical claims
- Frame around outcomes and business value, not medical advice
- Reference patient reviews and ratings as business signals only
- Always professional, respectful, never pushy

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Leads | Apify Cost | InVideo Cost | Total | Market Value |
|---|---|---|---|---|
| 50 leads | ~$0.60 | ~$5 | ~$5.60 | $500–$2,000 |
| 100 leads | ~$1.10 | ~$5 | ~$6.10 | $1,000–$4,000 |
| 500 leads | ~$5 | ~$5 | ~$10 | $5,000–$20,000 |
| Daily auto-run | ~$1/day | ~$5 | ~$35/month | Fresh leads daily |

> 💡 **Get started free on [Apify](https://www.apify.com?fpr=dx06p) — $5 credits included**

> 🎬 **Produce your wellness videos with [InVideo AI](https://invideo.sjv.io/TBB) — free plan available**

---

## 🔗 Who Prints Money With This Skill

| User | How They Use It | Revenue |
|---|---|---|
| **Medical Device Rep** | Target 100 clinics/week with personalized pitch | 3x more meetings booked |
| **Healthcare Marketing Agency** | Lead gen service for clinic clients | $1,000–$5,000/month per client |
| **Telehealth Platform** | Find and onboard new practitioners at scale | Reduce CAC by 60% |
| **Wellness Brand** | B2B outreach to gyms, spas, yoga studios | Distribution partnerships |
| **Private Clinic** | Find patients actively seeking care online | Fill appointment slots |
| **Health Tech Startup** | Build pipeline of clinic customers | Fuel B2B sales motion |

---

## 📊 Why This Skill Owns the Healthcare Market

| Feature | ZoomInfo ($15K/year) | Manual Research | **This Skill** |
|---|---|---|---|
| Location-based clinic scraping | ✅ | Partial | ✅ |
| Reputation gap analysis | ❌ | ❌ | ✅ |
| Patient demand signals | ❌ | ❌ | ✅ |
| AI lead scoring | ❌ | ❌ | ✅ |
| Personalized outreach per lead | ❌ | ❌ | ✅ |
| Promo video production | ❌ | ❌ | ✅ |
| Annual cost | $15,000 | $5,000 in time | ~$420/year |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your [Apify](https://www.apify.com?fpr=dx06p) API Token**  
Go to: **Settings → Integrations → API Token**

**Step 2 — Get your [InVideo AI](https://invideo.sjv.io/TBB) account**  
Go to: **Settings → API → Copy your key**

**Step 3 — Define your niche + location & run**  
Healthcare type + radius + your role. Full lead list in under 5 minutes.

---

## ⚡ Pro Tips for Healthcare Lead Gen

- **Target new clinics first** — opened in last 6 months = maximum urgency to fill appointment books
- **Reputation gap = open door** — a 3.8★ clinic is losing patients and knows it. They'll take your call.
- **Always reference their reviews** — "I noticed your patients mention X" shows you did your homework
- **Tuesday–Thursday 9–11am** = highest response rate for practice managers
- **Video in outreach email = 3x reply rate** — attach your InVideo promo as a teaser

---

## 🏷️ Tags

`healthcare` `wellness` `lead-generation` `medical-sales` `clinic` `physiotherapy` `apify` `invideo` `b2b` `patient-acquisition` `health-tech` `practitioner`

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI*
