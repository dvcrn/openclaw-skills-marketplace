# Amazon Product Research

Find profitable Amazon products, analyze markets, and track competitors using natural language. No complex tools - just describe what you need.

## What You Can Achieve

- **Discover winning products** - Find high-demand, low-competition items
- **Validate product ideas** - Check market potential before investing
- **Track competitors** - Monitor pricing, sales, and strategies
- **Save hours of research** - Get insights in seconds, not days

## Quick Start

### 1. Setup (30 seconds)
Just provide your APIClaw.io key once:
```
You: My APIClaw key is xxxxxx
Agent: ✅ Ready! Your product research assistant is now active.
```

### 2. Start Researching
Simply describe what you need:
```bash
# Find products
python scripts/apiclaw_nl.py "find wireless headphones under $50"

# Analyze market
python scripts/apiclaw_nl.py "analyze market for kitchen appliances"

# Track competitor
python scripts/apiclaw_nl.py "show me details for ASIN B08N5WRWNW"
```

Or use interactive mode:
```bash
python scripts/apiclaw_nl.py --interactive
```

## Example Queries

### Find Profitable Products
```
"find wireless headphones under $50"
"search for products with 4.5+ stars"
"top 20 products by monthly sales"
```

### Analyze Markets
```
"analyze market for wireless earbuds"
"how competitive is headphones market"
```

### Track Competitors
```
"search by brand Anker"
"show me details for ASIN B08N5WRWNW"
```

## What Makes This Different

- ✅ **No learning curve** - Natural language, no complex filters
- ✅ **Instant results** - Get answers in seconds
- ✅ **Actionable insights** - Clear recommendations, not just raw data
- ✅ **Scalable** - Research one product or one hundred

## Setup

**Don't have an APIClaw key?** Get one at https://APIClaw.io

Once you have your key, just tell the agent:
```
My APIClaw key is sk-xxxxxxxx
```

The agent will automatically:
- ✅ Save your key securely
- ✅ Confirm when ready

## Files

- `scripts/apiclaw_nl.py` - Main entry point
- `scripts/apiclaw_nlu.py` - Natural language understanding
- `scripts/apiclaw_client.py` - API client
- `.env` - API credentials (auto-created, not tracked by git)

## License

MIT
