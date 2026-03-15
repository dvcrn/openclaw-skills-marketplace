# Changelog

## 0.2.0

**Video generation.** Two new endpoints for creating AI videos from text or images. Three models to pick from (Kling 3.0 Pro, Veo 3.1, Runway Gen-4.5) with configurable duration, size, and audio. Polls every 10 seconds since video takes longer than images.

**Source URLs.** Content generation now accepts a `source_urls` field — pass up to 10 URLs and the AI scrapes them for research context before writing captions. Private URLs are filtered out automatically.

**Dynamic credit costs.** Removed all hardcoded credit amounts from the docs. Costs now come from the API response (`credits_used`, `remaining_credits`) so the skill stays accurate when pricing changes.

**Other changes:**
- Prompt max length bumped from 500 to 2,000 characters for content generation
- Polling strategy now distinguishes content/images (60 polls max) from video (120 polls max)
- Updated clawhub.json tags and description
- README updated with video and source URL examples

## 0.1.1

First-run setup flow, direct URLs to settings pages, fixed broken links in the skill doc.

## 0.1.0

Initial release. Content generation, image generation, media upload, post creation, and publishing across Instagram, TikTok, X, YouTube, Facebook, and LinkedIn.
