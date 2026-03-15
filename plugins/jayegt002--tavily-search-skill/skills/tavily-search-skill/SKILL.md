---
name: tavily-search-skill
description: "Tavily API integration with real-time quota management and paid mode toggle. Use when web search is needed."
---

# Tavily Search Skill 🔍

OpenClaw Skill for performing high-quality web searches using the Tavily API.

## Features

- **Smart Search** - Call Tavily API with structured results
- **Real-time Quota Management** - Auto-update quota after each search
- **Free/Paid Quota Distinction** - Display free and paid quotas separately
- **Paid Mode Toggle** - Switch between free and paid quota priority
- **Comprehensive Error Handling** - Network failures, insufficient quota, etc.

## Usage

### Prerequisites ⚠️

**Environment variable required (user must configure):**
```bash
export TAVILY_API_KEY="your_api_key"
```

Get API Key: https://app.tavily.com/api-keys

> ⚠️ Note: This skill requires users to provide their own Tavily API Key.

### Basic Search

```bash
./search.sh "search query"
```

### Specify Result Count

```bash
./search.sh "query" 10
```

### Include Images

```bash
./search.sh "query" 5 true
```

### Check Usage

```bash
./search.sh --usage
```

### Toggle Paid Mode

```bash
./search.sh --toggle-paid-mode
```

### Check Status

```bash
./search.sh --status
```

## Output Format

Results in JSON format:

```json
{
  "query": "keyword",
  "results": [
    {
      "title": "Result Title",
      "url": "link",
      "content": "summary"
    }
  ],
  "quota_info": {
    "plan": "free",
    "total": 1000,
    "used": 15,
    "remaining": 985
  }
}
```

## Dependencies

- `curl` - HTTP requests
- `jq` - JSON processing

### Install Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install curl jq
```

**macOS:**
```bash
brew install curl jq
```

## Limits

- Free plan: 1000 requests/month
- Max 20 results per search