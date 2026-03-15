---
name: ai-interior-design-visualizer
description: "AI Interior Design Visualizer — Generate Room Concepts & Mood Boards at Scale"
---

# 🏘️ AI Interior Design Visualizer — Generate Room Concepts & Mood Boards at Scale

**Slug:** `ai-interior-design-visualizer`  
**Category:** Interior Design / Real Estate / Creative  
**Powered by:** [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI

> Input a room type, style & budget. Get a **complete interior design package** — trending styles researched from Pinterest & Instagram, mood boards generated, full product sourcing list with live prices scraped, room-by-room design brief written, and a cinematic walkthrough video produced. Professional interior design at a fraction of the cost.

---

## 💥 Why This Skill Will Go Viral on ClawHub

The global interior design market is worth **$150 billion**. A single interior design consultation costs **$150–$500/hour**. Full room redesigns run **$5,000–$50,000**. And every homeowner, renter, Airbnb host, real estate developer, and property stager needs this.

This skill delivers a **complete design package in minutes** — with live trend research, real product links with current prices, and a cinematic video reveal.

**Target audience: literally anyone with a room** — homeowners, renters, Airbnb hosts, real estate agents, property developers, interior design students, home décor brands. That's hundreds of millions of people.

**What gets automated:**
- 🔍 Scrape **top trending interior styles** from Pinterest, Instagram & Houzz
- 🛋️ Source **real products** with live prices from IKEA, Wayfair & Amazon
- 🎨 Generate **complete mood board** with color palette, materials & textures
- 📐 Write **room-by-room design brief** — furniture layout, lighting, accessories
- 💰 Build **3 budget tiers** — budget / mid-range / luxury version of the same design
- 🎬 Produce **60-second cinematic room reveal video** via InVideo AI
- 🏷️ Deliver a **shoppable product list** with direct purchase links

---

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| [Apify](https://www.apify.com?fpr=dx06p) — Pinterest Scraper | Top trending room styles, color palettes, mood boards |
| [Apify](https://www.apify.com?fpr=dx06p) — Instagram Scraper | Viral interior design posts & influencer aesthetics |
| [Apify](https://www.apify.com?fpr=dx06p) — Amazon Product Scraper | Furniture & décor — live prices, ratings, availability |
| [Apify](https://www.apify.com?fpr=dx06p) — IKEA Scraper | Budget-friendly product sourcing with real prices |
| [Apify](https://www.apify.com?fpr=dx06p) — Wayfair Scraper | Mid-range & luxury product options |
| [Apify](https://www.apify.com?fpr=dx06p) — Google Trends Scraper | Rising interior design styles before they peak |
| [InVideo AI](https://invideo.sjv.io/TBB) | Produce cinematic 60-second room reveal video |
| Claude AI | Design brief writing, style curation, product selection rationale |

---

## ⚙️ Full Workflow

```
INPUT: Room type + style preference + budget + dimensions
        ↓
STEP 1 — Trend Research
  └─ Pinterest: top 50 pins for this room type & style (last 90 days)
  └─ Instagram: viral interior posts in this aesthetic
  └─ Google Trends: rising design styles not yet saturated
  └─ Extract: dominant colors, materials, furniture silhouettes
        ↓
STEP 2 — Style Analysis & Mood Board Creation
  └─ Top 3 trending styles for this room type identified
  └─ Color palette: 5 colors (primary, secondary, accent, neutral, pop)
  └─ Materials: flooring, walls, textiles, metals
  └─ Lighting mood: natural, warm, layered, dramatic
        ↓
STEP 3 — Live Product Sourcing (3 Budget Tiers)
  └─ Budget tier (under $1,500): IKEA + Amazon
  └─ Mid-range tier ($1,500–$5,000): Wayfair + West Elm
  └─ Luxury tier ($5,000+): CB2 + high-end options
  └─ Every product: name, price, link, why it fits the design
        ↓
STEP 4 — Claude AI Writes Complete Design Package
  └─ Room concept statement (the vision in 3 sentences)
  └─ Furniture layout recommendations
  └─ Lighting plan (ambient, task, accent)
  └─ Textile & accessory guide
  └─ DIY tips to elevate on a budget
  └─ Common mistakes to avoid for this style
        ↓
STEP 5 — InVideo AI Produces Room Reveal Video
  └─ 60-second cinematic walkthrough
  └─ Style inspiration images + product highlights
  └─ Voiceover narrating the design vision
  └─ Perfect for Instagram Reels, TikTok, Pinterest video
        ↓
OUTPUT: Mood board brief + 3-tier product list + design package + reveal video
```

---

## 📥 Inputs

```json
{
  "room": {
    "type": "Living Room",
    "dimensions": "5m x 7m",
    "style_preference": "Japandi (Japanese + Scandinavian minimalism)",
    "existing_elements": "Hardwood floors, white walls, large south-facing window",
    "must_keep": "Grey corner sofa",
    "pain_points": "Feels cluttered and cold, no personality"
  },
  "budget": {
    "total": 3000,
    "currency": "GBP",
    "flexibility": "can stretch to £3,500 for the right piece"
  },
  "client": {
    "lifestyle": "Young professional couple, minimalist, love plants",
    "inspiration": "Calm, warm, organic — like a boutique hotel lobby"
  },
  "production": {
    "invideo_api_key": "YOUR_INVIDEO_API_KEY",
    "video_style": "cinematic_warm",
    "voice": "calm_female_en"
  },
  "apify_token": "YOUR_APIFY_TOKEN"
}
```

---

## 📤 Output Example

```json
{
  "trend_analysis": {
    "top_trending_styles_2026": [
      { "style": "Japandi", "pinterest_saves_30d": "2.4M", "trend": "📈 Rising +34%" },
      { "style": "Organic Modern", "pinterest_saves_30d": "1.8M", "trend": "📈 Rising +28%" },
      { "style": "Quiet Luxury", "pinterest_saves_30d": "1.2M", "trend": "📈 Rising +19%" }
    ],
    "dominant_colors_in_niche": ["Warm beige", "Sage green", "Warm white", "Walnut brown", "Stone grey"],
    "trending_materials": ["Natural rattan", "Linen textiles", "Matte ceramic", "Raw wood", "Washi paper"],
    "recommendation": "Japandi is the perfect match for your brief — organic warmth with minimalist structure"
  },
  "design_concept": {
    "style": "Japandi Minimalism",
    "concept_statement": "A living room that breathes. Every object earns its place. Warmth through natural materials, calm through negative space, life through carefully chosen plants. This is not a room that shouts — it whispers, and you want to lean in.",
    "color_palette": {
      "primary": "#E8DDD0 (warm linen)",
      "secondary": "#8B7355 (walnut brown)",
      "accent": "#6B7C5E (sage green)",
      "neutral": "#F5F2EE (warm white)",
      "pop": "#2C2C2C (charcoal — used sparingly)"
    },
    "materials": {
      "flooring": "Keep existing hardwood — add a large natural jute rug to anchor the seating area",
      "walls": "Stay white but add one limewash textured wall behind the sofa — instant depth",
      "textiles": "Linen cushions, chunky knit throw, washi paper lampshades",
      "metals": "Matte black only — no chrome, no gold"
    },
    "lighting_plan": {
      "ambient": "Replace overhead with dimmer-controlled pendant (paper or rattan)",
      "task": "Arc floor lamp beside reading chair",
      "accent": "3 small ceramic table lamps for evening warmth",
      "natural": "Keep south window clear — no heavy curtains, linen sheers only"
    }
  },
  "product_sourcing": {
    "budget_tier": {
      "total_estimate": "£1,480",
      "items": [
        {
          "item": "IKEA SAJKA Pendant Lamp — Rattan",
          "price": "£45",
          "link": "ikea.com/gb/en/p/sajka-pendant-lamp",
          "why": "Perfect Japandi aesthetic, diffuses warm light beautifully"
        },
        {
          "item": "IKEA STOCKHOLM Rug — Natural",
          "price": "£195",
          "link": "ikea.com/gb/en/p/stockholm-rug",
          "why": "Anchors seating area, natural fibre matches the organic brief"
        },
        {
          "item": "Amazon — Set of 3 Linen Cushions, Warm Beige",
          "price": "£42",
          "rating": "4.6★ (847 reviews)",
          "link": "amazon.co.uk/dp/B09XZ",
          "why": "Softens your existing grey sofa, adds warmth immediately"
        },
        {
          "item": "IKEA FEJKA Artificial Potted Plants (x4)",
          "price": "£28",
          "why": "Low maintenance, adds life — cluster 3 near window, 1 on shelf"
        }
      ]
    },
    "mid_range_tier": {
      "total_estimate": "£2,850",
      "items": [
        {
          "item": "Wayfair — Solid Oak Coffee Table, Japandi Style",
          "price": "£285",
          "rating": "4.7★",
          "why": "Statement piece — low profile, warm wood, clean lines"
        },
        {
          "item": "West Elm — Sculptural Low Floor Lamp",
          "price": "£195",
          "why": "Arc design adds height and drama to reading corner"
        },
        {
          "item": "Wayfair — Natural Linen Sheer Curtains (2 panels)",
          "price": "£89",
          "why": "Filters south-facing light without blocking it — warm glow all day"
        }
      ]
    },
    "luxury_tier": {
      "total_estimate": "£5,200",
      "highlight_items": [
        { "item": "CB2 Tasman Low Platform Sofa", "price": "£1,800", "why": "Replaces corner sofa — lower profile = more space, more Japandi" },
        { "item": "Handmade ceramic table lamp — Etsy artisan", "price": "£180", "why": "One-of-a-kind piece that elevates the whole room" }
      ]
    }
  },
  "design_brief": {
    "furniture_layout": "Float sofa 60cm from wall — creates breathing room. Coffee table centered, 45cm from sofa. Arc lamp behind left armchair. Shelving unit on right wall — keep it 60% empty.",
    "diy_tips": [
      "Limewash paint one wall yourself — £35 in materials, £500+ result",
      "Decant candles into ceramic vessels — instant luxury feel",
      "Group plants in odd numbers — 3 or 5, never 2 or 4",
      "Replace all light bulbs with 2700K warm white — single biggest impact for £15"
    ],
    "mistakes_to_avoid": [
      "Don't match everything — mix wood tones for depth",
      "Don't over-accessorize — Japandi is about restraint",
      "Don't use cold white bulbs — they kill the warm aesthetic completely",
      "Don't push all furniture against the walls — float pieces for a grown-up look"
    ],
    "shopping_priority": "1st: Rug (biggest visual impact) → 2nd: Lighting → 3rd: Cushions & throws → 4th: Plants → 5th: Coffee table"
  },
  "reveal_video": {
    "script": "Imagine walking into your living room and feeling instantly calm. No clutter. No noise. Just warmth, texture, and space to breathe. This is Japandi — Japanese simplicity meets Scandinavian warmth. Natural linen. Raw wood. Ceramic vessels. A palette of warm beige, sage green, and walnut. Your grey sofa stays — we build a new world around it. The full product list and design brief are ready. Your transformation starts here.",
    "duration": "60s",
    "status": "produced",
    "video_file": "outputs/living_room_japandi_reveal.mp4"
  }
}
```

---

## 🧠 Claude AI Master Prompt

```
You are a world-class interior designer and product sourcing specialist.

TREND DATA FROM SCRAPING:
{{pinterest_instagram_trends}}

LIVE PRODUCT DATA:
{{product_prices_and_links}}

ROOM PROFILE:
- Type: {{room_type}}
- Dimensions: {{dimensions}}
- Style: {{style_preference}}
- Existing elements: {{existing_elements}}
- Must keep: {{must_keep}}
- Pain points: {{pain_points}}
- Budget: {{budget}} {{currency}}
- Lifestyle: {{lifestyle}}

GENERATE COMPLETE DESIGN PACKAGE:

1. Trend analysis — top 3 trending styles for this room type with data
2. Design concept:
   - Style recommendation with rationale
   - 3-sentence concept statement (poetic, evocative)
   - Color palette (5 colors with hex codes + names)
   - Materials guide (flooring, walls, textiles, metals)
   - Lighting plan (ambient, task, accent, natural)

3. Product sourcing — 3 budget tiers:
   For each tier list 8-12 products with:
   - Product name + retailer
   - Exact price (from scraped live data)
   - Purchase link
   - Why it fits the design (1 sentence)

4. Design brief:
   - Furniture layout recommendation
   - 5 DIY tips to elevate on a budget
   - 5 common mistakes to avoid for this style
   - Shopping priority order (what to buy first for maximum impact)

5. 60-second reveal video script:
   - Evocative, cinematic tone
   - Paint the vision before describing the products
   - End with a clear CTA

DESIGN RULES:
- Every product recommendation must be available and in budget
- Always include a mix of investment pieces and budget finds
- Prioritize items with highest visual impact per £/$
- Never recommend a full furniture replacement — work with what exists

OUTPUT: Valid JSON only. No markdown. No preamble.
```

---

## 💰 Cost Estimate

| Design Packages | Apify Cost | InVideo Cost | Total | Designer Price |
|---|---|---|---|---|
| 1 room package | ~$0.50 | ~$3 | ~$3.50 | $500–$2,000 |
| 5 rooms | ~$2.50 | ~$15 | ~$17.50 | $2,500–$10,000 |
| Full home (10 rooms) | ~$5 | ~$30 | ~$35 | $5,000–$50,000 |
| Agency (50 projects/month) | ~$25 | ~$150 | ~$175 | $25,000–$100,000 |

> 💡 **Get started free on [Apify](https://www.apify.com?fpr=dx06p) — $5 credits included**

> 🎬 **Produce your room reveal videos with [InVideo AI](https://invideo.sjv.io/TBB) — free plan available**

---

## 🔗 Who Makes Money With This Skill

| User | How They Use It | Revenue |
|---|---|---|
| **Interior Design Agency** | Deliver packages at $500–$2,000 per room | $20K–$80K/month |
| **Real Estate Agent** | Stage listings with design brief before photography | Sell faster, sell higher |
| **Airbnb Host** | Redesign property for 5-star guest experience | +$500/month rental income |
| **Home Décor Brand** | Generate styled content featuring their products | Content + sales in one |
| **Property Developer** | Design spec homes at scale before build | Save $50K in architect fees |
| **Interior Design Student** | Build portfolio of styled rooms instantly | Land first clients |

---

## 📊 Why This Beats Every Design Tool

| Feature | Houzz Pro ($65/mo) | Canva Mood Boards | **This Skill** |
|---|---|---|---|
| Live trend research | ❌ | ❌ | ✅ |
| Real product sourcing with live prices | Partial | ❌ | ✅ |
| 3 budget tier options | ❌ | ❌ | ✅ |
| AI-written design brief | ❌ | ❌ | ✅ |
| Cinematic reveal video | ❌ | ❌ | ✅ |
| DIY tips & mistake guide | ❌ | ❌ | ✅ |
| Monthly cost | $65 | $15 | ~$3.50/project |

---

## 🚀 Setup in 3 Steps

**Step 1 — Get your [Apify](https://www.apify.com?fpr=dx06p) API Token**  
Go to: **Settings → Integrations → API Token**

**Step 2 — Get your [InVideo AI](https://invideo.sjv.io/TBB) account**  
Go to: **Settings → API → Copy your key**

**Step 3 — Describe the room & run**  
Room type + style + budget. Full design package in under 5 minutes.

---

## ⚡ Pro Tips for Stunning Interior Design Results

- **Rug first** — it's the single highest visual impact purchase in any room
- **Warm bulbs change everything** — 2700K warm white costs £15 and transforms the mood instantly
- **60/40 rule for shelves** — 60% objects, 40% empty space. Restraint = sophistication.
- **The reveal video is your marketing tool** — post it on TikTok & Pinterest with the before photo. Viral every time.
- **Always offer 3 budget tiers** — it lets clients choose their investment level without feeling judged

---

## 🏷️ Tags

`interior-design` `home-decor` `mood-board` `real-estate` `airbnb` `apify` `invideo` `product-sourcing` `room-design` `staging` `pinterest` `lifestyle`

---

*Powered by [Apify](https://www.apify.com?fpr=dx06p) + [InVideo AI](https://invideo.sjv.io/TBB) + Claude AI*
