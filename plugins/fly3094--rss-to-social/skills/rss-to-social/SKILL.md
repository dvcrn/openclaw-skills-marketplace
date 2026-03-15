---
name: rss-to-social
description: "Automatically monitor RSS feeds and post to social media. Schedule content, generate posts with AI, and publish to Twitter/LinkedIn."
---

# RSS to Social Media Auto-Poster 📰

Automatically monitor RSS feeds, generate engaging social media posts with AI, and publish on schedule.

## What It Does

- 📰 **RSS Monitoring**: Track multiple RSS feeds for new content
- 🤖 **AI Content Generation**: Create platform-optimized posts automatically
- ⏰ **Scheduled Publishing**: Post at optimal times (configurable interval)
- 🔄 **Multi-Platform**: Support Twitter, LinkedIn, or both
- 📊 **Smart Deduplication**: Never post the same content twice
- 🔗 **Auto Linking**: Include original article links

## Installation

```bash
clawhub install rss-to-social
```

## Configuration

### Required Environment Variables

```bash
# RSS feeds to monitor (comma-separated)
export RSS_FEED_URLS="https://techcrunch.com/feed/,https://news.ycombinator.com/rss"

# Target platforms: twitter, linkedin, or all
export SOCIAL_PLATFORMS="twitter"

# Hours between posts (default: 4)
export POST_INTERVAL_HOURS="4"
```

### Optional Environment Variables

```bash
# AI model for content generation
export AI_MODEL="default"

# Include hashtags (true/false)
export INCLUDE_HASHTAGS="true"

# Twitter-specific (if direct posting enabled)
export TWITTER_API_KEY="your_key"
export TWITTER_API_SECRET="your_secret"
export TWITTER_ACCESS_TOKEN="your_token"
export TWITTER_ACCESS_TOKEN_SECRET="your_token_secret"

# LinkedIn-specific (if direct posting enabled)
export LINKEDIN_ACCESS_TOKEN="your_token"
```

## Usage

### One-Time Post
```
Check RSS feeds and post latest content to social media
```

### Start Continuous Monitoring
```
Start RSS monitoring and auto-posting every 4 hours
```

### Check Status
```
Show RSS monitoring status and recent posts
```

### Stop Monitoring
```
Stop RSS auto-posting
```

### Platform-Specific
```
Post to LinkedIn only from RSS feeds
```

## Output Examples

### Twitter Post
```
🚀 New: OpenClaw Releases Major Update

Key features:
• New skill marketplace
• Improved browser automation  
• 50% performance boost

Read more: https://techcrunch.com/article

#OpenClaw #AI #Automation
```

### LinkedIn Post
```
Exciting developments in AI automation!

OpenClaw just announced a major update with three game-changing features:

1️⃣ New skill marketplace with 100+ integrations
2️⃣ Improved browser automation for complex workflows
3️⃣ 50% performance improvement across all operations

This is a significant step forward for personal AI assistants.

What features are you most excited about?

Read the full announcement: https://techcrunch.com/article

#ArtificialIntelligence #Automation #Productivity #Tech
```

## Scheduling Options

### Using OpenClaw Scheduler
```
Every 4 hours, check RSS and post new content
```

### Using Cron
```bash
# Add to crontab (every 4 hours)
0 */4 * * * cd /path/to/workspace && openclaw run "Check RSS and post"
```

### Using Systemd Timer
```ini
# /etc/systemd/system/rss-to-social.timer
[Unit]
Description=RSS to Social Auto-Poster

[Timer]
OnBootSec=5min
OnUnitActiveSec=4h
Unit=rss-to-social.service

[Install]
WantedBy=timers.target
```

## Features

### Smart Content Generation
- **Hook Optimization**: AI generates attention-grabbing openings
- **Platform Formatting**: Adapts length and style per platform
- **Hashtag Suggestions**: Relevant tags based on content
- **Link Shortening**: Optional URL shortening for cleaner posts

### Deduplication
- Tracks posted URLs in `.rss-to-social/posted.json`
- Never posts the same content twice
- Maintains 30-day history by default

### Multi-Feed Support
- Monitor unlimited RSS feeds
- Priority ordering (first feed = highest priority)
- Category-based filtering

## Integration

### Works With
- ✅ social-media-automator (this skill can trigger it)
- ✅ Buffer/Hootsuite (via API)
- ✅ Twitter API (direct posting)
- ✅ LinkedIn API (direct posting)
- ✅ Telegram/WhatsApp (for approval workflow)

### Approval Workflow (Optional)
For sensitive accounts, enable approval before posting:

```
When new RSS content found, send to Telegram for approval before posting
```

## Troubleshooting

### No Posts Generated
- Check RSS_FEED_URLS format (comma-separated, valid URLs)
- Verify feeds have new content
- Check AI model availability

### Posting Failures
- Verify API credentials
- Check rate limits
- Review platform-specific requirements

### Duplicate Posts
- Clear `.rss-to-social/posted.json` if needed
- Adjust deduplication window

## Use Cases

### Tech News Aggregator
Monitor tech blogs, auto-share to Twitter for thought leadership.

### Industry Updates
Track industry RSS feeds, share insights on LinkedIn.

### Content Curation
Build a curated news account for your niche.

### Personal Branding
Automate your social presence while maintaining quality.

## Monetization

This skill powers LobsterLabs content automation services:
- **Setup + Configuration**: $299 one-time
- **Monthly Management**: $499/month (includes monitoring, optimization, reporting)
- **Custom Integrations**: $150/hour

Contact: PayPal 492227637@qq.com

## Changelog

### 1.0.0 (2026-03-07)
- Initial release
- RSS feed monitoring
- AI content generation
- Twitter/LinkedIn support
- Deduplication system
- Scheduling integration
