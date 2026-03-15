---
name: seo-content-engine
description: "Automated SEO content research, outline generation, and first draft writing. Perfect for content creators and marketing agencies."
---

# SEO Content Engine 📝

Automated SEO content creation skill for OpenClaw. Researches topics, generates optimized outlines, and writes first drafts.

## What It Does

- 🔍 **Topic Research**: Analyzes top-ranking content for any keyword
- 📋 **Outline Generation**: Creates SEO-optimized article structures
- ✍️ **First Draft**: Writes 1500-2500 word articles with proper heading hierarchy
- 🎯 **Keyword Integration**: Suggests and integrates primary/secondary keywords
- 📊 **Competitor Analysis**: Identifies content gaps vs top 5 ranking pages

## Commands

### Research a Topic
```
Research "[keyword/topic]" for SEO content
```

### Generate Outline
```
Create outline for "[article title]" targeting "[primary keyword]"
```

### Write Draft
```
Write draft for "[article title]" using outline, 2000 words, tone: [professional/casual/technical]
```

### Full Workflow
```
Create SEO article about "[topic]" - research, outline, and draft (2000 words)
```

## Output Format

Each article includes:
- Meta title (50-60 chars)
- Meta description (150-160 chars)
- H1 title
- Introduction (150-200 words)
- H2/H3 sections with proper hierarchy
- Conclusion with CTA
- Suggested internal/external links
- FAQ section (3-5 questions)

## Configuration

Optional environment variables:
- `CONTENT_TONE`: Default tone (professional|casual|technical|friendly)
- `DEFAULT_LENGTH`: Default word count (default: 2000)
- `INCLUDE_FAQ`: Include FAQ section (true|false, default: true)

## Example Usage

**User**: Create SEO article about "best AI automation tools for small business" - 2500 words

**Assistant**: 
1. Researching top 10 ranking pages for "AI automation tools small business"...
2. Analyzing content gaps and keyword opportunities...
3. Generating optimized outline...
4. Writing 2500-word draft with proper H2/H3 structure...
5. Adding meta tags and FAQ section...

✅ Article ready! [View draft]

## Pricing Integration

This skill powers LobsterLabs content services:
- Single article: $300-500
- Monthly pack (4 articles): $1,500-2,500
- White-label: $3,000+/month

Contact: PayPal 492227637@qq.com

## Changelog

### 0.1.0 (2026-03-06)
- Initial release
- Basic research + outline + draft workflow
- SEO optimization features
