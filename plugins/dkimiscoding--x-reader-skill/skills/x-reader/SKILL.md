---
name: x-reader
description: "Read X (Twitter) posts without official API. Supports both Nitter (free) and RapidAPI (detailed) methods."
---

# X-Reader

Read X (Twitter) posts without official API key.

## Features

- **Nitter Mode** (Default): Free, no API key required
- **RapidAPI Mode**: Detailed tweet info with API key
- Simple CLI interface
- JSON output for easy integration

## Usage

### Basic (Nitter - Free)

```bash
python3 x-reader.py "https://x.com/username/status/1234567890"
```

### Advanced (RapidAPI - Detailed)

```bash
export RAPIDAPI_KEY="your_rapidapi_key"
python3 x-reader.py "https://x.com/username/status/1234567890"
```

## Output Format

```json
{
  "id": "1234567890",
  "text": "Tweet content...",
  "author": "Display Name",
  "username": "username",
  "created_at": "2024-01-01T00:00:00.000Z",
  "likes": 100,
  "retweets": 50,
  "replies": 25,
  "url": "https://x.com/username/status/1234567890"
}
```

## Notes

- Nitter mode may have rate limits
- RapidAPI free tier: 100 requests/month
- For production use, consider RapidAPI paid tier
