---
name: ai-personal-branding-kit
description: "AI Personal Branding Kit — LinkedIn + Bio + Content Strategy in One Run"
---

# 💼 AI Personal Branding Kit — LinkedIn + Bio + Content Strategy in One Run

**Slug:** `ai-personal-branding-kit`  
**Category:** Personal Branding / Career Growth  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

> Input your name, role & goals. Get a **complete personal brand system** — optimized LinkedIn profile, killer bio for every platform, 30-day content strategy, brand voice guidelines, and a 60-second personal brand video. All built from live data on what top personal brands in your niche do right.

---

## 💥 Why This Skill Will Dominate ClawHub

Personal branding is no longer optional. It's the #1 career & business growth lever in 2026. Top personal brands generate **$50K–$1M+/year** from speaking gigs, consulting, courses, and sponsorships — built entirely from their online presence.

But 99% of professionals have a mediocre LinkedIn, a generic bio, and zero content strategy. This skill fixes all of that in one run.

**Target audience: literally every professional on earth.** Founders, executives, freelancers, consultants, job seekers, coaches, creators. That's your entire market.

**What gets automated:**
- 🔍 Scrape **top personal brands** in your niche — what makes them magnetic
- 📝 Rewrite your **LinkedIn profile** end-to-end — headline, about, experience
- 🎯 Generate **bios for every platform** — LinkedIn, Twitter, Instagram, website
- 🗣️ Define your **brand voice** — tone, keywords, positioning statement
- 📅 Build a **30-day content strategy** with post ideas per platform
- 🎬 Produce a **60-second personal brand video** via InVideo AI
- 💡 Identify **3 monetization paths** based on your expertise & audience

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| [Apify](https://www.apify.com?fpr=dx06p) — LinkedIn Profile Scraper | Analyze top personal brands in your niche |
| [Apify](https://www.apify.com?fpr=dx06p) — Twitter/X Scraper | Top thought leaders — voice, format, engagement |
| [Apify](https://www.apify.com?fpr=dx06p) — Google Search Scraper | Personal brand benchmarks, niche authority signals |
| [Apify](https://www.apify.com?fpr=dx06p) — Reddit Scraper | What your audience actually wants to learn from experts |
| [InVideo AI](https://invideo.sjv.io/TBB) | Produce 60-second personal brand intro video |
| Claude AI | Profile rewrite, bio generation, content strategy, brand voice |

---

## ⚙️ Full Workflow

```
INPUT: Your name + current role + expertise + goals + target audience
        ↓
STEP 1 — Top Personal Brand Analysis in Your Niche
  └─ Scrape top 10 LinkedIn profiles in your space
  └─ What makes their headline magnetic?
  └─ How do they structure their About section?
  └─ What content formats drive their engagement?
        ↓
STEP 2 — Audience Pain Point Research
  └─ Reddit: what does your target audience struggle with?
  └─ What questions do they ask that you can answer?
  └─ What type of expert do they trust most?
        ↓
STEP 3 — Claude AI Builds Your Complete Brand System
  └─ LinkedIn headline (5 variations to A/B test)
  └─ LinkedIn About section (full rewrite — story-driven)
  └─ LinkedIn Featured section strategy
  └─ Short bio (160 chars — Twitter/Instagram)
  └─ Medium bio (300 chars — speaking profiles)
  └─ Long bio (500 words — website About page)
  └─ Brand voice guide (3 adjectives, tone, what to avoid)
  └─ Positioning statement ("I help X do Y so they can Z")
        ↓
STEP 4 — 30-Day Content Strategy
  └─ 5 content pillars tailored to your expertise
  └─ 30 post ideas (title + angle + platform)
  └─ Best formats for your niche (text / carousel / video)
  └─ Posting schedule per platform
        ↓
STEP 5 — InVideo AI Produces Brand Video
  └─ 60-second "Who I am & why follow me" video
  └─ Professional voiceover + visuals
  └─ Perfect for LinkedIn banner, website, email signature
        ↓
STEP 6 — Monetization Roadmap
  └─ 3 specific paths to monetize your brand
  └─ Timeline & first step for each
        ↓
OUTPUT: Full brand kit + LinkedIn rewrite + all bios + content plan + brand video
```

---

## 📥 Inputs

```json
{
  "profile": {
    "name": "Sarah Johnson",
    "current_role": "Senior Marketing Manager at SaaS company",
    "expertise": "B2B content marketing, demand generation, LinkedIn growth",
    "years_experience": 8,
    "target_audience": "Marketing directors and CMOs at B2B SaaS companies",
    "goals": ["become a keynote speaker", "launch a consulting practice", "grow to 20K LinkedIn followers"],
    "current_linkedin_headline": "Senior Marketing Manager | B2B | SaaS",
    "personality": "direct, data-driven, occasionally funny"
  },
  "production": {
    "invideo_api_key": "YOUR_INVIDEO_API_KEY",
    "video_style": "professional_modern",
    "voice": "confident_female_en"
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "brand_analysis": {
    "top_brands_in_niche": [
      {
        "name": "Rand Fishkin",
        "followers": "280K",
        "what_works": "Radical transparency about failures + data-backed takes = massive trust",
        "headline_formula": "[Credibility] + [Contrarian angle] + [Who I help]"
      }
    ],
    "winning_positioning_patterns": [
      "Lead with the RESULT you create, not your job title",
      "Mention a specific number or achievement in headline",
      "Address your target audience directly ('For CMOs who...')"
    ]
  },
  "linkedin_profile": {
    "headline_variations": [
      "I Help B2B SaaS Companies 3x Their Pipeline With Content | Marketing Leader | ex-HubSpot",
      "B2B Content Marketing That Actually Generates Revenue | 8 Years Turning Blogs Into Pipeline",
      "CMOs Hire Me When Their Content Isn't Converting | Demand Gen Specialist | 50M+ Impressions Generated",
      "The Marketing Leader Who Treats Content Like a Sales Channel | B2B SaaS Growth",
      "I Turned $0 Content Budget Into $4M Pipeline — Here's How I Did It"
    ],
    "recommended_headline": "I Help B2B SaaS Companies 3x Their Pipeline With Content | Marketing Leader | ex-HubSpot",
    "about_section": "Most B2B content gets read. Mine gets remembered — and then it gets leads.\n\nI've spent 8 years in B2B SaaS marketing making one bet: that the companies who teach better than they sell will always win.\n\nResults so far:\n→ $4M in pipeline attributed to content in the last 24 months\n→ Grew a company blog from 12K to 380K monthly visitors in 18 months\n→ Built a LinkedIn presence from 800 to 14,000 followers while working full-time\n\nWhat I actually believe:\nContent marketing without demand generation is a hobby. Demand generation without content is just noise. The magic happens in the middle — and most marketing teams miss it entirely.\n\nI write about:\n→ The B2B content strategies that move pipeline (not just pageviews)\n→ What I've tried, failed at, and learned the hard way\n→ The frameworks I wish I'd had in year one\n\nIf you're a CMO or marketing leader trying to make content actually convert — follow along. I post 3x/week.\n\nWant to work together? → sarah@sarahjohnson.com",
    "featured_section_strategy": "Pin your best performing post + a short case study PDF + your speaking reel"
  },
  "bios": {
    "twitter_160": "B2B content that generates pipeline, not just pageviews. Marketing leader @[Company]. I post what actually works (and what doesn't).",
    "instagram_150": "B2B Marketing Leader | Turning content into revenue for SaaS companies | 8 years, $4M in attributed pipeline | Tips 3x/week 👇",
    "speaking_profile_300": "Sarah Johnson is a B2B marketing leader and demand generation specialist who has helped SaaS companies turn content into measurable revenue. Over 8 years, she has grown company audiences from zero to hundreds of thousands and generated over $4M in attributed pipeline. She speaks on B2B content strategy, demand generation, and building personal brands that convert.",
    "website_about_500": "I'm Sarah Johnson — a B2B marketing leader who spent 8 years learning one thing: content only matters if it makes the sales team's job easier.\n\n[FULL 500-WORD BIO GENERATED]"
  },
  "brand_voice": {
    "positioning_statement": "I help B2B SaaS marketing leaders build content systems that generate pipeline, not just traffic.",
    "three_words": ["Direct", "Data-backed", "Occasionally contrarian"],
    "tone_guide": "Write like you're explaining something to a smart colleague over coffee. Never jargon. Always specific. Earn every adjective.",
    "avoid": ["Vague claims without numbers", "Buzzwords like 'synergy' or 'thought leader'", "Overly polished corporate language"]
  },
  "content_strategy": {
    "pillars": [
      "Content that converts (tactical, data-backed)",
      "Marketing career growth (for aspiring leaders)",
      "Failures & lessons (vulnerability + credibility)",
      "Industry hot takes (contrarian, sparks debate)",
      "Behind-the-scenes (humanizes the brand)"
    ],
    "30_day_plan": [
      { "day": 1, "platform": "LinkedIn", "angle": "The $4M content strategy in one framework (carousel)", "format": "Carousel" },
      { "day": 3, "platform": "LinkedIn", "angle": "Unpopular opinion: your blog is not a marketing channel", "format": "Text post" },
      { "day": 5, "platform": "Twitter/X", "angle": "Thread: 7 B2B content mistakes that kill pipeline", "format": "Thread" }
    ],
    "posting_schedule": "LinkedIn: Mon/Wed/Fri | Twitter: Daily | Newsletter: Weekly"
  },
  "monetization_roadmap": [
    {
      "path": "B2B Content Consulting",
      "description": "1:1 engagements with SaaS CMOs — audit + strategy + execution support",
      "price_point": "$5,000–$15,000/month retainer",
      "first_step": "Publish 5 case study posts showing your results → DMs will come",
      "timeline": "First client in 60–90 days"
    },
    {
      "path": "Keynote Speaking",
      "description": "Speak at SaaS conferences on B2B content & demand gen",
      "price_point": "$3,000–$15,000 per talk",
      "first_step": "Apply to 10 smaller SaaS events with your speaking page",
      "timeline": "First paid gig in 4–6 months"
    },
    {
      "path": "Online Course",
      "description": "B2B Content That Converts — for marketing managers ready to level up",
      "price_point": "$497–$997",
      "first_step": "Post 30 days of content first — validate what resonates, then package it",
      "timeline": "Launch in 90 days"
    }
  ],
  "brand_video": {
    "script": "Hi — I'm Sarah Johnson. I'm a B2B marketing leader who's spent 8 years obsessed with one question: why does most content get traffic but no pipeline?\n\nI've tested hundreds of strategies, generated $4M in attributed revenue from content, and grown audiences from zero to hundreds of thousands.\n\nI share everything I learn — the wins, the failures, and the frameworks — three times a week right here.\n\nIf you're a marketing leader who wants content that actually moves the needle — follow along. Let's build something real.",
    "duration": "60s",
    "status": "produced",
    "video_file": "outputs/sarah_johnson_brand_video.mp4"
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class personal branding strategist and LinkedIn ghostwriter.

TOP PERSONAL BRANDS IN NICHE:
{{top_brands_data}}

AUDIENCE PAIN POINTS:
{{reddit_and_social_data}}

PERSONAL PROFILE:
- Name: {{name}}
- Current role: {{current_role}}
- Expertise: {{expertise}}
- Years experience: {{years_experience}}
- Target audience: {{target_audience}}
- Goals: {{goals}}
- Personality: {{personality}}

GENERATE COMPLETE PERSONAL BRAND KIT:

1. LinkedIn headline — 5 variations using these formulas:
   - Result-led: "I help [WHO] achieve [RESULT] by [HOW]"
   - Credibility-led: "[Achievement] | [Role] | [Who you help]"
   - Contrarian: "[Counterintuitive claim] | [Proof] | [Niche]"

2. LinkedIn About section (400 words):
   - Hook: bold first line that stops the scroll
   - Proof: 3 specific results with numbers
   - Beliefs: what you stand for (2-3 lines)
   - Content topics: what you post about
   - CTA: one clear next step

3. Bio suite: Twitter (160), Instagram (150), Speaking (300), Website (500)

4. Brand voice guide: 3 defining adjectives + tone description + 5 things to avoid

5. Positioning statement: "I help [X] do [Y] so they can [Z]"

6. 30-day content plan: 30 posts with title + angle + platform + format

7. 3 monetization paths with price point, first step, and realistic timeline

8. 60-second brand video script

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Kits | Apify Cost | InVideo Cost | Total | Market Value |
|---|---|---|---|---|
| 1 personal brand kit | ~$0.40 | ~$3 | ~$3.40 | $500–$3,000 |
| 10 kits (agency) | ~$4 | ~$30 | ~$34 | $5,000–$30,000 |
| 50 kits | ~$20 | ~$150 | ~$170 | $25,000–$150,000 |

> 💡 **Get started free on [Apify](https://www.apify.com?fpr=dx06p) — $5 credits included**

> 🎬 **Produce your brand video with [InVideo AI](https://invideo.sjv.io/TBB) — free plan available**

---

## 🔗 Who Wins Big With This Skill

| User | How They Use It | Revenue |
|---|---|---|
| **Personal Brand Agency** | Deliver full kits to executives at $2,000–$5,000 | $20K–$50K/month |
| **Career Coach** | Add brand kit to coaching packages | +$500–$1,500 per client |
| **LinkedIn Ghostwriter** | Use as onboarding deliverable for new clients | Premium first impression |
| **Executive / Founder** | Build authority brand that generates inbound | Priceless |
| **Job Seeker** | Stand out with a magnetic LinkedIn presence | Land $30K salary increase |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your [Apify](https://www.apify.com?fpr=dx06p) API Token**  
Go to: **Settings → Integrations → API Token**

**Step 2 — Get your [InVideo AI](https://invideo.sjv.io/TBB) account**  
Go to: **Settings → API → Copy your key**

**Step 3 — Fill in your profile details & run**  
Name + role + expertise + goals. Full brand kit in under 5 minutes.

---

## ⚡ Pro Tips for a Magnetic Personal Brand

- **Your headline is your billboard** — test all 5 variations, keep the one with the most profile views after 2 weeks
- **Specific numbers 10x credibility** — "$4M pipeline" beats "significant results" every time
- **Post before you feel ready** — the algorithm rewards consistency, not perfection
- **Engage before you post** — 15 minutes of genuine comments before posting = 3x more reach
- **Your brand video in your LinkedIn banner = instant authority signal**

---

## 🏷️ Tags

`personal-branding` `linkedin` `career-growth` `content-strategy` `apify` `invideo` `bio` `thought-leadership` `executive-branding` `freelancer` `consulting` `brand-voice`

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI*
