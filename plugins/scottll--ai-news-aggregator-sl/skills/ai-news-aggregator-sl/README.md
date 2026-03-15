# AI News Aggregator — OpenClaw Skill

An OpenClaw skill that collects AI & tech news from multiple sources, translates everything to Chinese with DeepSeek, and posts formatted digests to Discord.

Ported from the original n8n workflow `n8n信息聚合器`.

## Sources

| Source | Type | Filter |
|--------|------|--------|
| TechCrunch (AI) | RSS | Last 24h |
| The Verge (AI) | RSS | Last 24h |
| New York Times (AI) | RSS | Last 24h |
| Twitter / X | Search API | Last 24h, top tweets |
| YouTube | Data API v3 | Last 24h, >10K views |

> Reddit removed by request. Feishu replaced with Discord.

## Installation

### 1. Copy skill files to your OpenClaw skills directory

```bash
# Typical locations:
# macOS:   ~/Library/Application Support/openclaw/skills/
# Linux:   ~/.openclaw/skills/
# Windows: %APPDATA%\openclaw\skills\

mkdir -p ~/.openclaw/skills/news-aggregator
cp SKILL.md news_aggregator.py .env.example ~/.openclaw/skills/news-aggregator/
```

### 2. Configure your API keys

```bash
cd ~/.openclaw/skills/news-aggregator
cp .env.example .env
# Open .env and fill in your keys
```

### 3. Install Python dependencies

```bash
pip install feedparser requests python-dotenv openai
```

### 4. Ask OpenClaw to run it

```
"Get today's AI news digest"
"What's trending in AI? Post to Discord."
"Run the news aggregator, dry run"
```

## API Keys You Need

| Key | Required | Where to get it |
|-----|----------|----------------|
| `DEEPSEEK_API_KEY` | ✅ Yes | [platform.deepseek.com](https://platform.deepseek.com/api_keys) |
| `DISCORD_WEBHOOK_URL` | ✅ Yes | Discord → Channel Settings → Integrations → Webhooks |
| `TWITTERAPI_IO_KEY` | Optional | [twitterapi.io](https://twitterapi.io) |
| `YOUTUBE_API_KEY` | Optional | [console.cloud.google.com](https://console.cloud.google.com) |

## Manual CLI Usage

```bash
cd ~/.openclaw/skills/news-aggregator

python3 news_aggregator.py              # all reports → Discord
python3 news_aggregator.py --report news       # RSS news only
python3 news_aggregator.py --report trending   # Twitter + YouTube only
python3 news_aggregator.py --dry-run           # print output, don't post
```

## File Structure

```
news-aggregator/
├── SKILL.md              ← OpenClaw reads this to understand the skill
├── news_aggregator.py    ← Main Python script
├── .env.example          ← Config template
├── .env                  ← Your actual keys (not committed to git)
└── README.md
```
