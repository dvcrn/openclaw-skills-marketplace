# uhomes-student-housing

An AI skill that helps international students find verified student accommodation on [uhomes.com](https://en.uhomes.com).

Works with OpenClaw and Claude.ai. Fetches live listings from uhomes.com and returns direct booking links.

## Install (OpenClaw / ClawHub)

```bash
clawhub install uhomes-student-housing
```

## Usage Examples

Just ask naturally — the skill triggers automatically for housing queries:

```
Find student accommodation near University of Manchester, September move-in, budget £180/week en-suite
```

```
帮我找悉尼大学附近的学生公寓，9月入住，studio优先
```

```
I'm going to UCL next year, what student housing options are there near campus?
```

```
Compare en-suite vs studio near King's College London
```

## What It Does

1. Identifies your university or city
2. Fetches live listings from uhomes.com
3. Presents 3–5 verified properties with price, distance, highlights, and a direct booking link
4. Links you to the full search page on uhomes.com to view all options

## Data Source

**uhomes.com only.** No other platforms are referenced or recommended.

## File Structure

```
uhomes-student-housing/
├── SKILL.md                    # Core skill instructions
└── references/
    ├── url-patterns.md         # uhomes.com URL construction rules
    ├── city-index.md           # Verified city/university slugs
    ├── room-types.md           # Room type definitions and price context
    └── faq.md                  # Common questions: contracts, payments, bills
```

## Coverage

Currently indexed: UK (London, Manchester, Birmingham, Edinburgh + 10 more cities), Australia (Sydney, Melbourne + 4 more), US (New York, Boston + 4 more), Canada (Toronto, Vancouver, Montreal), Ireland, Singapore, Hong Kong.

For unlisted cities, the skill falls back to the country-level search page on uhomes.com.

## Version

v1.0.0 — March 2026
