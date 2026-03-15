---
name: humanize-ai-content
description: "Transform AI-generated text into natural, publication-ready writing. Two modes: (1) TEXT MODE — generic humanization using 24 AI pattern detectors, 500+ vocabulary terms, and statistical analysis (burstiness, TTR, readability). Use when asked to humanize text, de-AI writing, or make content sound natural. (2) ARTICLE MODE — full editorial publishing pipeline for blog posts and comparison guides. Adds citation hyperlinks, internal product linking, featured image placement, SEO heading enhancement, FAQ schema, and authority structure preservation. Triggers: humanize text/content, de-AI writing, make content sound human, prepare article for publishing, polish AI blog post, publication-ready content."
---

# Humanize AI Content

Transform AI-generated writing into natural, human-sounding content ready for publication. Based on Wikipedia's Signs of AI Writing guide, Copyleaks stylometric research, and editorial best practices.

---

## Mode Detection

**Activate TEXT MODE when:**
- Asked to humanize a paragraph, essay, email, or short-form copy
- No publishing pipeline context (no product names, citations, or article structure)
- Goal is natural-sounding text only

**Activate ARTICLE MODE when:**
- Content is a blog post, comparison guide, or long-form article
- Request mentions publishing, WordPress, or specific product names
- Content was produced by `ai-authority-content` or similar pipeline skills
- Goal includes citation links, product links, or SEO optimization

When in doubt, run TEXT MODE first, then ask if ARTICLE MODE polish is needed.

---

## TEXT MODE — Generic Humanization

### Your Task

1. Scan for all 24 patterns below
2. Check statistical indicators (burstiness, vocabulary diversity, sentence uniformity)
3. Rewrite problematic sections with natural alternatives
4. Preserve the core meaning
5. Match the intended tone (formal, casual, technical)
6. Add actual personality — sterile text is just as obvious as AI slop

### The 24 AI Writing Patterns

| # | Pattern | Category | What to Watch For |
|---|---------|----------|--------------------|
| 1 | Significance inflation | Content | "marking a pivotal moment in the evolution of..." |
| 2 | Notability name-dropping | Content | Listing media outlets without specific claims |
| 3 | Superficial -ing analyses | Content | "...showcasing... reflecting... highlighting..." |
| 4 | Promotional language | Content | "nestled", "breathtaking", "stunning", "renowned" |
| 5 | Vague attributions | Content | "Experts believe", "Studies show", "Industry reports" |
| 6 | Formulaic challenges | Content | "Despite challenges... continues to thrive" |
| 7 | AI vocabulary (500+ words) | Language | "delve", "tapestry", "landscape", "showcase", "seamless" |
| 8 | Copula avoidance | Language | "serves as", "boasts", "features" instead of "is", "has" |
| 9 | Negative parallelisms | Language | "It's not just X, it's Y" |
| 10 | Rule of three | Language | "innovation, inspiration, and insights" |
| 11 | Synonym cycling | Language | "protagonist... main character... central figure..." |
| 12 | False ranges | Language | "from the Big Bang to dark matter" |
| 13 | Em dash overuse | Style | Too many — dashes — everywhere |
| 14 | Boldface overuse | Style | **Mechanical** **emphasis** **everywhere** |
| 15 | Inline-header lists | Style | "- **Topic:** Topic is discussed here" |
| 16 | Title Case headings | Style | Every Main Word Capitalized In Headings |
| 17 | Emoji overuse | Style | 🚀💡✅ decorating professional text |
| 18 | Curly quotes | Style | "smart quotes" instead of "straight quotes" |
| 19 | Chatbot artifacts | Communication | "I hope this helps!", "Let me know if..." |
| 20 | Cutoff disclaimers | Communication | "As of my last training...", "While details are limited..." |
| 21 | Sycophantic tone | Communication | "Great question!", "You're absolutely right!" |
| 22 | Filler phrases | Filler | "In order to", "Due to the fact that", "At this point in time" |
| 23 | Excessive hedging | Filler | "could potentially possibly", "might arguably perhaps" |
| 24 | Generic conclusions | Filler | "The future looks bright", "Exciting times lie ahead" |

### AI Vocabulary Tiers

**Tier 1 — Dead giveaways (always replace):**
delve, tapestry, vibrant, crucial, comprehensive, meticulous, embark, robust, seamless, groundbreaking, leverage, synergy, transformative, paramount, multifaceted, myriad, cornerstone, reimagine, empower, catalyst, invaluable, bustling, nestled, realm, testament, landscape, showcasing, underscores, pivotal, utilize, facilitate, nuanced

**Tier 2 — Suspicious in density (reduce when clustered):**
furthermore, moreover, paradigm, holistic, proactive, ubiquitous, quintessential, illuminate, encompasses, catalyze

**Tier 1 Phrases (always remove):**
"In today's digital age", "It is worth noting", "plays a crucial role", "serves as a testament", "in the realm of", "delve into", "harness the power of", "embark on a journey", "without further ado", "marking a pivotal moment"

### Replacement Guide

| AI Word/Phrase | Replace With |
|----------------|-------------|
| testament | evidence, proof, sign |
| landscape | field, industry, market, area |
| showcasing | showing, displaying |
| delve/delving | explore, examine, look at |
| tapestry | mix, combination, variety |
| underscores | shows, highlights, emphasizes |
| notably | especially, particularly |
| crucial | important, key, essential |
| robust | strong, solid, reliable |
| leverage | use |
| utilize | use |
| facilitate | help, enable, allow |
| comprehensive | complete, full, thorough |
| pivotal | important, key |
| nuanced | subtle, detailed |
| foster | encourage, support, build |
| serves as | is |
| features | has, includes |
| boasts | has |
| offers | has, provides |
| encompasses | includes |
| represents | is |

### Filler Phrase Replacements

| Filler | Replace With |
|--------|-------------|
| In order to | To |
| Due to the fact that | Because |
| At this point in time | Now |
| In the event that | If |
| For the purpose of | To, For |
| In spite of the fact that | Although |
| With regard to | About |
| In terms of | (delete) |
| It is important to note that | (delete, just say it) |
| It should be noted that | (delete, just say it) |

### Statistical Signals

| Signal | Human Range | AI Range | Why |
|--------|-------------|----------|-----|
| Burstiness | 0.5–1.0 | 0.1–0.3 | Humans write in bursts; AI is metronomic |
| Type-token ratio | 0.5–0.7 | 0.3–0.5 | AI reuses the same vocabulary |
| Sentence length CoV | High | Low | AI sentences are roughly the same length |
| Trigram repetition | <0.05 | >0.10 | AI reuses 3-word phrases |

### Core Principles

**Write like a human, not a press release:**
- Use "is" and "has" freely — "serves as" is pretentious
- One qualifier per claim — don't stack hedges
- Name your sources or drop the claim
- End with something specific, not "the future looks bright"

**Add personality:**
- Have opinions. React to facts, don't just report them
- Vary sentence rhythm. Short. Then longer ones that meander.
- Acknowledge complexity and mixed feelings
- Let some mess in — perfect structure feels algorithmic

### Text Mode Before/After

**Before (AI-sounding):**
> Great question! Here is an overview of sustainable energy. Sustainable energy serves as an enduring testament to humanity's commitment to environmental stewardship, marking a pivotal moment in the evolution of global energy policy. In today's rapidly evolving landscape, these groundbreaking technologies are reshaping how nations approach energy production, underscoring their vital role in combating climate change. The future looks bright. I hope this helps!

**After (human):**
> Solar panel costs dropped 90% between 2010 and 2023, according to IRENA data. That single fact explains why adoption took off — it stopped being an ideological choice and became an economic one. Germany gets 46% of its electricity from renewables now. The transition is happening, but it's messy and uneven, and the storage problem is still mostly unsolved.

---

## ARTICLE MODE — Publishing Pipeline

Use this mode for blog posts, comparison guides, and long-form articles going to WordPress or other CMS.

### Critical Rule: Preserve Authority Structure

When humanizing content from `ai-authority-content` or similar, **ALL structural elements must remain intact**:

- ✅ All mandatory sections (Title → TL;DR → Why Needed → Methodology → Items → Tables → FAQ → Conclusion)
- ✅ Expert authority language ("According to [Source]", never "our recommendation")
- ✅ All comparison tables with consistent formatting
- ✅ Individual item templates (Features, Implementation, Pros/Cons, Best For)
- ✅ FAQ section with 8+ questions
- ✅ All attributed statistics and citations

**Humanization = Editorial polish. NOT restructuring.**

### Apply All TEXT MODE Transformations First

Run the full 24-pattern sweep, vocabulary replacement, and filler cuts. Then apply the publishing-specific steps below.

---

### Article Transformation Steps (Apply in Order)

#### Step 1: Citation Authority Enhancement ⚡ HIGH PRIORITY

Convert parenthetical citations to authority-leading hyperlinks.

**Before:** `Websites see increases of 15% *(according to TrustPulse)*.`
**After:** `[**According to TrustPulse**](https://actual-source-url), websites see increases of 15%.`

Rules:
- Lead sentences with the authority source when possible
- Always hyperlink source names to actual URLs (research if needed)
- Use bold link format: `[**According to X**](url)`
- Remove trailing asterisks and parentheses

**Multiple citations example:**
```
Before: Research shows 60% of millennial consumers make reactive purchases *(according to OptinMonster)*. With 92% of consumers trusting peers over ads *(according to Nielsen)*...

After: According to [**OptinMonster research**](https://optinmonster.com/fomo-statistics/), 60% of millennial consumers make reactive purchases. [**According to Nielsen**](https://www.nielsen.com/insights/2012/trust-in-advertising/), 92% of consumers trust peer recommendations over advertising...
```

#### Step 2: Internal Product Linking ⚡ HIGH PRIORITY

Add hyperlinks to ALL product/brand names throughout the article.

Rules:
- Link product names on first mention in EACH major section
- Use bold with link: `[**ProductName**](https://product.com/)`
- Link company names: `[**WPDeveloper**](https://wpdeveloper.com/)`
- Link competitor products fairly to their official sites
- In recommendation boxes, link each mentioned product
- Do NOT add links inside headings — link in the first sentence of the section body

**Example:**
```
Before: NotificationX stands as the best FOMO plugin for WordPress.
After: [**NotificationX**](https://notificationx.com/) stands as the best FOMO plugin for WordPress.
```

#### Step 3: Featured Image Placement

Add featured image immediately after the introduction paragraph (before the first H2).

```markdown
This guide analyzes the top FOMO plugins for WordPress...

![Article Title](https://assets.domain.com/year/month/banner.jpg)

## A Quick Summary / TL;DR
```

Flag if image URL is unknown: `![Article Title](IMAGE_URL_NEEDED)`

#### Step 4: SEO Heading Enhancement

Add target keywords naturally to H2 headings. Don't force it — only where it reads naturally.

```
Before: ## Why Site Owners Need FOMO Plugins
After: ## Why Site Owners Need FOMO and Social Proof Plugins
```

#### Step 5: Implementation Section Enhancement

KEEP all how-to steps. ADD documentation links after the steps.

```markdown
### How to Get Started with [Product]?

Getting started is pretty simple. Follow the steps below or check the detailed documentation.

[...all original steps preserved...]

**Detailed Guides:**
* [**How to Install [Product]**](https://docs.product.com/install/)
* [**[Product] Quick Start Guide**](https://docs.product.com/quickstart/)
```

#### Step 6: Stats and Feature Accuracy

Verify and update:
- Active user counts (check WordPress.org or official sites)
- Feature counts (notification types, integrations)
- Pricing tiers (check current plans)

Flag items needing verification: `[VERIFY: user count]`, `[VERIFY: pricing]`

#### Step 7: Pros/Cons Refinement

**KEEP:** Genuine limitations users need for purchase decisions, learning curve issues, pricing/tier limitations, honest trade-offs vs competitors.

**REMOVE ONLY:** Obvious platform limitations ("WordPress-only plugin only works on WordPress"), cons covered by another con already, minor features most users won't need, cons that apply equally to ALL products in the category.

Decision test: *"Does this con help the reader decide whether to buy or try this product?"* If yes, keep it.

#### Step 8: FAQ Schema Preparation

Format for WordPress schema markup:
- Questions as plain text (NOT bold, NOT H3)
- Answer follows immediately with a blank line separator
- Preserve all 8+ questions

```
Before: **Which FOMO plugin should I start with?**
After: Which FOMO plugin should I start with?
```

#### Step 9: Table Rank Formatting

- Use emoji medals (🥇 🥈 🥉) for top 3 — no number after the medal
- Use numbers (4, 5, 6...) for remaining positions
- Ensure "Best For" column is present and specific
- Use `| --- |` pipe separators (not `|------|`)

#### Step 10: Heading Cleanup

Remove redundant prefixes:
- `## Conclusion: Your Roadmap` → `## Your Roadmap`
- `🥇 1. ProductName` → `🥇 ProductName`
- `## Quick Summary / TL;DR` → `## A Quick Summary / TL;DR`

#### Step 11: Action Plan Formatting

Convert numbered action lists to bullet format:

```
Before: 1. **This Week:** Install...
After: * **Get started:** Install...
```

#### Step 12: Remove Meta Disclaimers

Delete "Last Updated" footers, "prices subject to change" notices, and similar meta content.

---

## Output Format

### For TEXT MODE
Provide:
1. Humanized text
2. Brief summary of changes made (grouped by category)

### For ARTICLE MODE
Provide:
1. Complete transformed markdown file
2. Change summary grouped by transformation type
3. Verification list: stats/URLs/images flagged for user review

---

## Article Mode Quality Checklist

**Authority Preservation:**
- [ ] All original sections present (nothing removed)
- [ ] Zero "our recommendation" or "we think" language added
- [ ] All stats still have source attribution
- [ ] Expert citations enhanced with links (not removed)
- [ ] All tables preserved with structure intact

**AI Pattern Removal (24-pattern sweep):**
- [ ] Tier 1 vocabulary replaced
- [ ] Copula avoidance fixed (serves as → is, boasts → has)
- [ ] Significance inflation removed
- [ ] Negative parallelisms eliminated
- [ ] Filler phrases cut
- [ ] Promotional language replaced with facts
- [ ] Em dash overuse reduced (max 1–2 per article)
- [ ] Synonym cycling fixed (consistent terminology)
- [ ] Superficial -ing analyses removed
- [ ] Chatbot artifacts deleted
- [ ] Generic conclusions replaced with specifics

**Publishing Polish Applied:**
- [ ] All citations converted to authority-leading hyperlinks
- [ ] All product/brand names linked to official pages
- [ ] Featured image placeholder added after intro
- [ ] Stats flagged for verification if uncertain
- [ ] Keywords added to H2 headings naturally
- [ ] Implementation sections keep all steps + add doc links
- [ ] Pros/cons only removes genuinely irrelevant items
- [ ] FAQs formatted for WordPress schema
- [ ] Table ranks use medals (🥇🥈🥉) without numbers
- [ ] Heading prefixes cleaned
- [ ] Action plans use bullet format
- [ ] Meta disclaimers removed

---

## Resources

- `references/transformation-examples.md` — Detailed before/after examples for every transformation
