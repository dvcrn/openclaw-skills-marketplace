---
name: google-analytics-and-search-improve
description: "Analyze website data via Google Search Console API and GA4 Data API, audit live site with browser automation, review project source code, and generate data-driven improvement plans covering SEO, performance, content strategy, UX, conversion rate, and technical issues. Use when user wants to diagnose website problems, improve search rankings, optimize traffic, analyze Google Analytics or Search Console data, audit website performance, or create a data-backed improvement roadmap."
---

# Google Analytics & Search Console Data-Driven Improvement

Analyze GSC and GA4 data, combined with browser auditing and source code review, to generate improvement plans covering six dimensions: SEO, Performance, Content Strategy, UX, Conversion Rate, and Technical Issues.

## Data Storage

All runtime data is stored in `$DATA_DIR`, separated from skill code.

```
<project_root>/.skills-data/google-analytics-and-search-improve/
  .env        # Configuration (auth, URLs, etc.), auto-loaded by scripts
  data/       # GSC/GA4/PSI data (JSON or CSV)
  tmp/        # Screenshots and temporary files
  cache/      # API response cache
  configs/    # Config files
  logs/       # Execution logs
  venv/       # Python virtual environment
```

## Workflow

```
Analysis Progress:
- [ ] Phase 1: Select data source & collect data
- [ ] Phase 2: GSC data analysis
- [ ] Phase 3: GA4 data analysis
- [ ] Phase 4: Live site audit
- [ ] Phase 5: Source code review
- [ ] Phase 6: Generate improvement report
```

---

### Phase 1: Select Data Source & Collect Data

**1a. Initialize directories**:
```bash
DATA_DIR=".skills-data/google-analytics-and-search-improve"
mkdir -p "$DATA_DIR"/{data,cache,logs,tmp}
```

**1b. Ask user to choose data source**:

Present three modes for the user to choose from:

> Choose how to obtain GSC/GA4 data:
>
> **A. API auto-collection** (recommended, most complete data)
> Requires creating a Google Cloud Service Account and configuring API auth. First-time setup takes ~10 minutes; subsequent analyses collect data automatically.
>
> **B. Manual CSV export** (zero config, simplest)
> You export data files from GA4 and GSC web consoles yourself, and I'll analyze them. No API configuration needed.
>
> **C. Browser audit only** (no GA4/GSC data needed)
> I'll visit the site directly for technical auditing and code analysis without using GA4/GSC data. Best for quick technical checks.

Enter the corresponding branch based on user selection:

---

#### Mode A: API Auto-Collection

**Check .env**: Read `$DATA_DIR/.env`; if missing config, guide the user to fill it in.

Configuration required from user (write to `$DATA_DIR/.env` after collection):

| Variable | Description |
|----------|-------------|
| `SITE_URL` | Website URL to audit (e.g., `https://example.com`) |
| `GOOGLE_APPLICATION_CREDENTIALS` | **Absolute path** to the Service Account JSON key file on your machine |
| `GSC_SITE_URL` | Site address in Search Console (see format note below) |
| `GA4_PROPERTY_ID` | GA4 Property ID (numeric only) |
| `SOURCE_CODE_PATH` | (Optional) Path to the project source code |
| `PSI_API_KEY` | (Optional) PageSpeed Insights API Key to avoid rate limiting |

**GSC_SITE_URL format note**: GSC has two property types with different formats. The value must match the type registered in GSC, otherwise a 403 permission error will be returned:

| GSC Property Type | GSC_SITE_URL Format | Example |
|-------------------|---------------------|---------|
| **Domain property** | `sc-domain:domain` | `sc-domain:example.com` |
| **URL-prefix property** | Full URL | `https://example.com` |

> How to check: In the [Search Console](https://search.google.com/search-console/) property selector (top-left), if it shows a bare domain name it's a Domain property (use `sc-domain:` prefix); if it shows a full URL it's a URL-prefix property.

Detailed auth setup steps in [references/gsc-api-guide.md](references/gsc-api-guide.md).

```bash
cat > "$DATA_DIR/.env" <<EOF
SITE_URL=provided by user
GOOGLE_APPLICATION_CREDENTIALS=provided by user (absolute path)
GSC_SITE_URL=provided by user (note sc-domain: or https:// format)
GA4_PROPERTY_ID=provided by user
SOURCE_CODE_PATH=provided by user
PSI_API_KEY=
EOF
```

**Collect data** (scripts auto-read auth from .env):
```bash
set -a; source "$DATA_DIR/.env"; set +a
python scripts/gsc_query.py --dimensions query --limit 500 -o "$DATA_DIR/data/gsc_queries.json"
python scripts/gsc_query.py --dimensions page --limit 500 -o "$DATA_DIR/data/gsc_pages.json"
python scripts/gsc_query.py --dimensions device,country -o "$DATA_DIR/data/gsc_devices.json"
python scripts/gsc_query.py --dimensions date -o "$DATA_DIR/data/gsc_trends.json"
python scripts/gsc_query.py --mode sitemaps -o "$DATA_DIR/data/gsc_sitemaps.json"
python scripts/ga4_query.py --preset traffic_overview -o "$DATA_DIR/data/ga4_traffic.json"
python scripts/ga4_query.py --preset top_pages --limit 100 -o "$DATA_DIR/data/ga4_pages.json"
python scripts/ga4_query.py --preset user_acquisition -o "$DATA_DIR/data/ga4_acquisition.json"
python scripts/ga4_query.py --preset device_breakdown -o "$DATA_DIR/data/ga4_devices.json"
python scripts/ga4_query.py --preset landing_pages --limit 50 -o "$DATA_DIR/data/ga4_landing.json"
python scripts/ga4_query.py --preset user_behavior --limit 100 -o "$DATA_DIR/data/ga4_behavior.json"
python scripts/ga4_query.py --preset conversion_events -o "$DATA_DIR/data/ga4_conversions.json"
```

First-time use requires installing dependencies:
```bash
python3 -m venv "$DATA_DIR/venv" && source "$DATA_DIR/venv/bin/activate"
pip install -r scripts/requirements.txt
```

Script usage details in [references/gsc-api-guide.md](references/gsc-api-guide.md) and [references/ga4-api-guide.md](references/ga4-api-guide.md).

---

#### Mode B: Manual CSV Export

Send the following export instructions to the user, asking them to place files in `$DATA_DIR/data/`:

> **Export GSC data**:
> 1. Open [Google Search Console](https://search.google.com/search-console/) → Select your site
> 2. Click "Search results" (Performance) in the left menu
> 3. Set date range to last 3 months, click "Export" → "Download CSV"
> 4. Save the downloaded CSV as `$DATA_DIR/data/gsc_export.csv`
>
> **Export GA4 data (export the following reports)**:
> 1. Open [Google Analytics](https://analytics.google.com/) → Select your property
> 2. Export "Pages and screens" report:
>    - Left menu: "Reports" → "Engagement" → "Pages and screens"
>    - Click the share icon (top-right) → "Download file" → CSV
>    - Save as `$DATA_DIR/data/ga4_pages.csv`
> 3. Export "Traffic acquisition" report:
>    - Left menu: "Reports" → "Acquisition" → "Traffic acquisition"
>    - Export CSV → Save as `$DATA_DIR/data/ga4_acquisition.csv`
> 4. Export "Landing pages" report:
>    - Left menu: "Reports" → "Engagement" → "Landing pages"
>    - Export CSV → Save as `$DATA_DIR/data/ga4_landing.csv`
>
> Let me know when the export is complete, and I'll read the files to start analysis.

Also ask the user for:
- **Target website URL** (required, write to `SITE_URL` in `$DATA_DIR/.env`)
- **Source code path** (optional, write to `SOURCE_CODE_PATH`)

After receiving files, read CSV files from `$DATA_DIR/data/` and proceed to Phase 2-3 analysis.

---

#### Mode C: Browser Audit Only

Only ask the user for:
- **Target website URL** (required)
- **Source code path** (optional)

Write to `$DATA_DIR/.env` and skip directly to Phase 4 (site audit) and Phase 5 (source code review), skipping Phase 2-3.

---

### Phase 2: GSC Data Analysis

Read GSC data (JSON or CSV) from `$DATA_DIR/data/`, analyze according to the "SEO" dimension thresholds in [references/metrics-glossary.md](references/metrics-glossary.md).

Key outputs:
- High-impression low-CTR keywords (best targets for title/description optimization)
- Keywords ranked 4-10 (highest ROI to push into top 3)
- Pages with declining ranking trends
- Index coverage and sitemap health status

**Output**: Top 10 SEO optimization opportunities with data evidence.

---

### Phase 3: GA4 Data Analysis

Read GA4 data (JSON or CSV) from `$DATA_DIR/data/`, analyze according to "Content Strategy", "User Experience", and "Conversion Rate" dimension thresholds in [references/metrics-glossary.md](references/metrics-glossary.md).

Key outputs:
- Traffic trends and channel effectiveness
- High-traffic low-engagement / high-bounce-rate pages
- Mobile vs desktop experience gaps
- Conversion funnel drop-off points

**Output**: Top 10 GA4 insights with data evidence.

---

### Phase 4: Live Site Audit

Use `agent-browser` to visit `$SITE_URL`:

```bash
agent-browser open "$SITE_URL" && agent-browser wait --load networkidle
agent-browser screenshot --full homepage_desktop.png
agent-browser set viewport 375 812
agent-browser screenshot --full homepage_mobile.png
agent-browser set viewport 1280 720
```

Save screenshots to `$DATA_DIR/tmp/`.

PageSpeed Insights performance audit (auto-appends `PSI_API_KEY` from .env if present):
```bash
PSI_BASE="https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=$SITE_URL&category=PERFORMANCE&category=SEO&category=ACCESSIBILITY&category=BEST_PRACTICES"
PSI_KEY_PARAM="${PSI_API_KEY:+&key=$PSI_API_KEY}"
curl -s "${PSI_BASE}&strategy=mobile${PSI_KEY_PARAM}" > "$DATA_DIR/data/psi_mobile.json"
curl -s "${PSI_BASE}&strategy=desktop${PSI_KEY_PARAM}" > "$DATA_DIR/data/psi_desktop.json"
```

> **PSI failure fallback**: If a 429 (quota exceeded) or other error is returned, check whether "PageSpeed Insights API" has been enabled in the Google Cloud project (see [references/gsc-api-guide.md](references/gsc-api-guide.md) Step 1). When PSI data is missing, continue with subsequent phases and note the missing performance data in the report.

Extract Core Web Vitals from PSI; thresholds in the "Performance" dimension of [references/metrics-glossary.md](references/metrics-glossary.md).

If GA4 data is available, take screenshots (desktop + mobile) for each of the Top 10 landing pages, recording visual and interaction issues.

When no source code is available, extract front-end metadata via browser:
```bash
agent-browser eval --stdin <<'EVALEOF'
JSON.stringify({
  title: document.title,
  meta_desc: document.querySelector('meta[name="description"]')?.content,
  h1: Array.from(document.querySelectorAll('h1')).map(h => h.textContent),
  has_jsonld: document.querySelectorAll('script[type="application/ld+json"]').length,
  images_no_alt: document.querySelectorAll('img:not([alt])').length,
  viewport: document.querySelector('meta[name="viewport"]')?.content,
  canonical: document.querySelector('link[rel="canonical"]')?.href,
})
EVALEOF
```

**Output**: Performance scores + visual issue checklist.

---

### Phase 5: Source Code Review

If `SOURCE_CODE_PATH` is configured in `.env`, analyze project source code. Skip if no source code is available.

Check items detailed in the "Technical Issues" checklist in [references/metrics-glossary.md](references/metrics-glossary.md). Core focus:

- **SEO**: Meta tag completeness, JSON-LD, robots.txt / sitemap.xml, image alt, H1 conventions
- **Performance**: JS/CSS splitting and lazy loading, image formats and responsive images, third-party scripts, render-blocking resources
- **Technical**: `<html lang>`, viewport, HTTPS, canonical URL, internal dead links

**Output**: Code-level improvement checklist.

---

### Phase 6: Generate Improvement Report

Organize output according to the "Priority Matrix" (P0-P3) in [references/metrics-glossary.md](references/metrics-glossary.md). Use the following template:

```markdown
# Website Data Analysis & Improvement Plan

## Summary
- **Target Website**: [URL]
- **Data Source**: API auto-collection / Manual CSV export / Browser audit only
- **Analysis Period**: [start_date] ~ [end_date]
- **Key Findings**: [1-2 sentence summary]

## Data Overview
| Metric | Current Value | Trend |
|--------|---------------|-------|
| GSC Total Impressions / Clicks / CTR / Position | ... | ... |
| GA4 Sessions / Users / Bounce Rate / Engagement Rate | ... | ... |
| PSI Performance Score (Mobile/Desktop) | ... | ... |

## Improvement Plan
### P0 Critical (High Impact, Low Effort)
1. **[Issue]** — Data evidence / Fix / Expected impact

### P1 High → P2 Medium → P3 Low
(Same format as above)

## Detailed Analysis
(Organized by SEO / Performance / Content Strategy / UX / Conversion Rate / Technical Issues)

## Execution Roadmap
| Phase | Timeline | Tasks | Expected Outcome |
|-------|----------|-------|------------------|
| Week 1-2 | P0 | ... | ... |
| Week 3-4 | P1 | ... | ... |
| Month 2+ | P2-P3 | ... | ... |
```

Save the report to `$DATA_DIR/data/improvement-report.md`.

## Companion Skills

- SEO implementation → `seo-geo`
- Browser automation → `agent-browser`
- Frontend redesign → `frontend-design`

## Reference Docs

| Document | Contents |
|----------|----------|
| [references/gsc-api-guide.md](references/gsc-api-guide.md) | GSC auth setup (step-by-step), script usage, dimensions & metrics |
| [references/ga4-api-guide.md](references/ga4-api-guide.md) | GA4 auth setup, preset templates, dimensions & metrics |
| [references/metrics-glossary.md](references/metrics-glossary.md) | Six analysis dimensions: thresholds, diagnostics, priority matrix |
