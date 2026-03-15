---
name: multi-platform-publisher
description: "Publish content to X/Twitter, LinkedIn, WeChat Official Account, and Xiaohongshu with one command. Automatically adapts content format for each platform — threads for Twitter, professional articles for LinkedIn, HTML drafts for WeChat, emoji notes for Xiaohongshu. Triggers: publish content, social media, twitter post, linkedin post, wechat article, xiaohongshu note, cross-platform publish, multi-platform"
---

# Multi-Platform Social Media Publisher

Publish content to multiple social media platforms with a single command. Supports X/Twitter, LinkedIn, WeChat Official Account (微信公众号), and Xiaohongshu (小红书).

## Prerequisites

Install dependencies:

```bash
pip3 install requests tweepy Pillow
```

Set credentials via environment variables:

```bash
# Twitter / X
export TWITTER_API_KEY="your-api-key"
export TWITTER_API_SECRET="your-api-secret"
export TWITTER_ACCESS_TOKEN="your-access-token"
export TWITTER_ACCESS_TOKEN_SECRET="your-access-token-secret"

# LinkedIn
export LINKEDIN_ACCESS_TOKEN="your-linkedin-token"
export LINKEDIN_PERSON_URN="urn:li:person:abc123"   # optional

# WeChat Official Account
export WECHAT_APPID="your-appid"
export WECHAT_APPSECRET="your-appsecret"

# Xiaohongshu
export XHS_COOKIE="your-cookie-string"
```

Or configure via `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "multi-platform-publisher": {
        "env": {
          "TWITTER_API_KEY": "...",
          "LINKEDIN_ACCESS_TOKEN": "...",
          "WECHAT_APPID": "...",
          "XHS_COOKIE": "..."
        }
      }
    }
  }
}
```

## Quick Start

```bash
# Publish to all configured platforms
python3 {baseDir}/main.py publish --content "Your post content here" --platforms all

# Specific platforms
python3 {baseDir}/main.py publish --content "Your content" --platforms twitter,linkedin

# Publish from a Markdown file
python3 {baseDir}/main.py publish --file /path/to/article.md --platforms all

# Twitter thread for long content
python3 {baseDir}/main.py publish --content "Long article..." --platforms twitter --thread

# Attach images
python3 {baseDir}/main.py publish --content "Check this out!" --platforms all --images photo.jpg

# Preview without publishing (dry run)
python3 {baseDir}/main.py publish --content "Test" --platforms all --dry-run

# Validate credentials
python3 {baseDir}/main.py validate

# List configured platforms
python3 {baseDir}/main.py list-platforms
```

## Supported Platforms

| Platform | Auth Method | Features |
|---|---|---|
| X/Twitter | OAuth 1.0a | Tweets, Threads, Images |
| LinkedIn | OAuth 2.0 | Posts, Articles, Images |
| WeChat Official Account | API Token | Draft creation, Images |
| Xiaohongshu (小红书) | MCP / Cookie | Notes, Images |

## Content Adaptation

Content is automatically adapted for each platform:

- **X/Twitter** — Strips Markdown, splits into 280-char tweets, creates numbered threads for long content
- **LinkedIn** — Formats as professional post, up to 3,000 chars, clean paragraphs
- **WeChat** — Converts to styled HTML article (draft, requires manual publish in dashboard)
- **Xiaohongshu** — Casual tone, emoji injection, topic tags, 1,000 char limit

## Project Structure

```
main.py                  # CLI entry point
adapters/
  base_adapter.py        # Abstract base class
  twitter_adapter.py     # X / Twitter (OAuth 1.0a)
  linkedin_adapter.py    # LinkedIn (OAuth 2.0)
  wechat_adapter.py      # WeChat Official Account
  xiaohongshu_adapter.py # Xiaohongshu (MCP/Cookie)
utils/
  config_loader.py       # Credential loading (env > openclaw.json > config.json)
  content_adapter.py     # Platform-specific content transformation
  image_handler.py       # Image resize/validate before upload
  logger.py              # Stderr logger
```
