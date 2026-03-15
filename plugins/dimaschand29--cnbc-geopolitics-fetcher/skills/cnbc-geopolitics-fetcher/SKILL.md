---
name: cnbc-geopolitics-fetcher
description: "Automated geopolitical intelligence agent that fetches 5 hottest CNBC news articles from last 24 hours, extracts structured data (Title, URL, Market Impact, Hard Facts), and posts formatted briefings to Discord webhook. Use for executive briefings, geopolitical monitoring, or automated news pipelines."
---

# CNBC Geopolitics Fetcher

Professional geopolitical intelligence extraction from CNBC with Discord delivery.

## Purpose

Fetches exactly 5 "hottest" geopolitical news articles from CNBC.com published within the last 24 hours, extracts structured intelligence data, and delivers formatted briefings to Discord webhooks.

## Configuration

### Discord Webhook

Store webhook URL in `references/config.md`:

```markdown
## Discord Webhook
https://discord.com/api/webhooks/XXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Search Parameters

- **Source:** https://www.cnbc.com (world, finance, geopolitics sections)
- **Keywords:** Geopolitics, US Foreign Policy, Energy Markets, International Conflict
- **Recency:** Last 24 hours (article URL date pattern)
- **Output:** Exactly 5 articles

## Usage

### Direct Execution

```bash
cd skills/cnbc-geopolitics-fetcher
python scripts/fetch_cnbc_geopolitics.py --config references/config.md --count 5
```

### With Custom Webhook

```bash
python scripts/fetch_cnbc_geopolitics.py --webhook <discord_webhook_url> --count 5
```

### With Output File

```bash
python scripts/fetch_cnbc_geopolitics.py --config references/config.md --output briefing.md
```

## Output Protocol (STRICT)

1. **NO CONVERSATION** - Start immediately with first data point
2. **DATA PURITY** - Remove editorial adjectives (stunning, grim, worrisome, shocking)
3. **MANDATORY FIELDS** - Every item must have Title, URL, Market Impact, Hard Facts

## Output Format

```markdown
---
## [TITLE]
- **URL:** [Full CNBC Link]
- **Market Impact:** [Specific data on Oil, Stocks, or Currency]
- **Hard Facts:**
  * [Official statement or attributed quote]
  * [Specific military, diplomatic, or economic action]
  * [Key numerical statistic or deadline]
---
```

## Automation

### Cron Schedule (Daily Briefing)

```json
{
  "name": "cnbc-geopolitics-daily",
  "schedule": { "kind": "cron", "expr": "0 8 * * *", "tz": "Asia/Jakarta" },
  "payload": { 
    "kind": "agentTurn", 
    "message": "Fetch CNBC geopolitical news for last 24 hours" 
  },
  "sessionTarget": "isolated"
}
```

### Heartbeat Integration

Add to `HEARTBEAT.md`:

```markdown
- [ ] Fetch CNBC geopolitical briefing (rotate every 2-3 checks)
```

## Files Structure

```
skills/cnbc-geopolitics-fetcher/
├── SKILL.md                 # This file
├── scripts/
│   └── fetch_cnbc_geopolitics.py  # Main execution script
└── references/
    └── config.md            # Webhook and settings
```

## Error Handling

- Missing webhook: Exit with error message
- No articles found: Return "No articles found in last 24 hours"
- Discord API error: Log error, continue execution
- Network timeout: Retry once, then skip section

## Rate Limits

- CNBC: Respect robots.txt, 1 request/second max
- Discord: Webhook rate limit 30 requests/minute

## Security Notes

- Webhook URLs stored in config files (not committed to shared repos)
- No authentication tokens in script code
- Discord content truncated to 2000 characters (Discord limit)

## Testing

```bash
# Test fetch without posting
python scripts/fetch_cnbc_geopolitics.py --count 3 --output test_briefing.md

# Test with mock webhook (Discord test URL)
python scripts/fetch_cnbc_geopolitics.py --webhook https://discord.com/api/webhooks/test --count 1
```
