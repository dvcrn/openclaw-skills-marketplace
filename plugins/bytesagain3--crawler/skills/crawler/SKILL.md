---
name: crawler
description: "Crawler"
---

# Crawler

Web crawler toolkit — site crawling, link extraction, content scraping, sitemap generation, rate limiting, and data export.

## Commands

| Command | Description |
|---------|-------------|
| `crawler run` | Execute main function |
| `crawler list` | List all items |
| `crawler add <item>` | Add new item |
| `crawler status` | Show current status |
| `crawler export <format>` | Export data |
| `crawler help` | Show help |

## Usage

```bash
# Show help
crawler help

# Quick start
crawler run
```

## Examples

```bash
# Run with defaults
crawler run

# Check status
crawler status

# Export results
crawler export json
```

## How It Works

Processes input with built-in logic and outputs structured results. All data stays local.

## Tips

- Run `crawler help` for all commands
- Data stored in `~/.local/share/crawler/`
- No API keys required for basic features
- Works offline

---
*Powered by BytesAgain | bytesagain.com*
