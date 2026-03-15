---
name: browserbase-scraper
description: "Scrape Cloudflare-protected websites using Stagehand + Browserbase cloud browsers. Use when the user needs to extract data from websites with bot protection, bypass Cloudflare challenges, or scrape JavaScript-heavy pages that block traditional methods like curl or Playwright stealth. Supports AI-powered extraction via Gemini."
---

# Browserbase Scraper

Bypass Cloudflare and bot protection using Stagehand + Browserbase cloud browsers with AI-powered extraction.

## When to Use

- Website blocks curl/fetch with Cloudflare "Just a moment..." page
- Playwright headless gets detected and blocked
- Need structured data extraction from dynamic content
- Scraping auction sites, marketplaces, or other protected pages

## Prerequisites

```bash
npm install @browserbasehq/stagehand zod
```

**Required environment variables:**
- `BROWSERBASE_API_KEY` — from browserbase.com dashboard
- `BROWSERBASE_PROJECT_ID` — from browserbase.com
- `GOOGLE_GENERATIVE_AI_API_KEY` — for Gemini extraction (or use OpenAI)

## Quick Start

```javascript
import { Stagehand } from '@browserbasehq/stagehand';

const stagehand = new Stagehand({
  env: 'BROWSERBASE',
  apiKey: process.env.BROWSERBASE_API_KEY,
  projectId: process.env.BROWSERBASE_PROJECT_ID,
  model: {
    modelName: 'google/gemini-3-flash-preview',
    apiKey: process.env.GOOGLE_GENERATIVE_AI_API_KEY,
  },
});

await stagehand.init();
const page = stagehand.context.pages()[0];

// Navigate (Cloudflare bypass is automatic)
await page.goto('https://protected-site.com/search?q=term');
await page.waitForTimeout(5000); // Let page fully load

// AI-powered extraction (instruction-only works best)
const data = await stagehand.extract(`
  Extract all product listings as JSON array:
  [{ "title": "...", "price": 123, "url": "..." }]
  Return ONLY the JSON array.
`);

await stagehand.close();
```

## Key Patterns

### 1. Instruction-Only Extraction (Recommended)
Schema-based extraction often returns empty. Use natural language instructions instead:

```javascript
const extraction = await stagehand.extract(`
  Look at this page and extract:
  - All item titles
  - Prices as numbers
  - URLs
  Return as JSON array.
`);
```

### 2. Handle Cloudflare Delays
Sometimes the challenge takes longer:

```javascript
const title = await page.title();
if (title.toLowerCase().includes('moment')) {
  await page.waitForTimeout(10000); // Wait for challenge
}
```

### 3. Scroll to Load More
Many sites lazy-load content:

```javascript
for (let i = 0; i < 5; i++) {
  await page.evaluate(() => window.scrollBy(0, window.innerHeight));
  await page.waitForTimeout(800);
}
```

### 4. Parse Extraction Results
The extraction returns a string that needs parsing:

```javascript
let listings = [];
try {
  const jsonMatch = extraction?.extraction?.match(/\[[\s\S]*\]/);
  if (jsonMatch) listings = JSON.parse(jsonMatch[0]);
} catch (e) {
  console.log('Parse error:', e.message);
}
```

## Browserbase Free Tier Limits

- **1 concurrent session** — cron jobs can conflict with interactive use
- Sessions auto-close after inactivity
- Use `stagehand.close()` to release session immediately

## Cron Integration

For scheduled scraping, use OpenClaw cron with isolated sessions:

```bash
openclaw cron add \
  --name "Daily Scrape" \
  --cron "0 6 * * *" \
  --session isolated \
  --message "Run: node ~/scripts/scraper.js"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Empty extraction | Use instruction-only (no schema), increase wait time |
| Cloudflare loop | Wait 10-15s, check if title contains "moment" |
| Session limit | Close other Browserbase sessions, check dashboard |
| 429 errors | Wait for session to complete, don't retry immediately |

## Example: Full Scraper

See `scripts/example_scraper.js` for a complete working example.
