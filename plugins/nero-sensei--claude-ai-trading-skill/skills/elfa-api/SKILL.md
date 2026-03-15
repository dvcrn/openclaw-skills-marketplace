---
name: elfa-api
description: "Interact with the Elfa API — a crypto social intelligence platform that provides real-time sentiment, trending tokens, narrative tracking, and AI-powered market analysis from Twitter/X and Telegram. Use this skill whenever the user wants to query crypto social data, check trending tokens or narratives, look up mentions for a ticker or keyword, get smart stats for a Twitter account, retrieve token news, find trending contract addresses, or chat with Elfa's AI for market analysis. Also trigger when the user asks how to integrate the Elfa API, wants example code or curl commands for Elfa endpoints, or mentions \"elfa\" in the context of crypto data. This skill covers both making live API calls (when an API key is available) and generating correct code snippets for developers integrating the Elfa API into their own products."
---

# Elfa API Skill

This skill enables Claude to work with the [Elfa API](https://api.elfa.ai) — a social listening
and market context layer for crypto traders. Elfa ingests real-time data from Twitter/X, Telegram,
and other sources, then structures sentiment, narratives, and attention shifts into actionable
trading insights.

## When to use this skill

- User asks about **trending tokens, narratives, or contract addresses** in crypto
- User wants **social mentions** for a specific ticker or keyword
- User wants **smart stats** (smart followers, engagement) for a Twitter/X account
- User wants an **AI-generated market summary, macro overview, or token analysis**
- User asks how to **integrate, call, or use the Elfa API**
- User wants **code examples** (curl, Python, JavaScript/TypeScript) for Elfa endpoints
- User mentions "elfa" in a crypto or trading data context

## API Overview

**Base URL:** `https://api.elfa.ai`
**Auth:** API key via `x-elfa-api-key` header on all authenticated endpoints.
**Version:** v2 (current)

### Endpoints at a glance

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/v2/key-status` | GET | Yes | API key usage & limits |
| `/v2/aggregations/trending-tokens` | GET | Yes | Trending tokens by mention count |
| `/v2/account/smart-stats` | GET | Yes | Smart follower & engagement stats for a Twitter account |
| `/v2/data/top-mentions` | GET | Yes | Top mentions for a ticker symbol |
| `/v2/data/keyword-mentions` | GET | Yes | Search mentions by keywords or account name |
| `/v2/data/event-summary` | GET | Yes | AI event summaries from keyword mentions (5 credits) |
| `/v2/data/trending-narratives` | GET | Yes | Trending narrative clusters (5 credits) |
| `/v2/data/token-news` | GET | Yes | Token-related news mentions |
| `/v2/aggregations/trending-cas/twitter` | GET | Yes | Trending contract addresses on Twitter |
| `/v2/aggregations/trending-cas/telegram` | GET | Yes | Trending contract addresses on Telegram |
| `/v2/chat` | POST | Yes | AI chat with multiple analysis modes |

For full parameter details, read `references/api-reference.md`.

## How to use this skill

### Step 1: Determine the mode

Check whether the user wants to **make a live call** or **get code/integration help**.

- If the user says things like "show me trending tokens", "what's the sentiment on SOL",
  "get me the top mentions for ETH" → they want **live data**. Proceed to Step 2.
- If the user says things like "how do I call the trending tokens endpoint", "give me a
  curl example", "help me integrate Elfa" → they want **code snippets**. Skip to Step 3.

### Step 2: Making live API calls

Use the `bash_tool` to call the Elfa API via curl. The helper script at
`scripts/elfa_call.sh` handles auth and formatting, but you can also use curl directly.

**Getting the API key:**
1. Check if the user has provided an API key in the conversation or if one is set as
   an environment variable (`ELFA_API_KEY`).
2. If no key is available, **stop and prompt the user before doing anything else.** Tell them:

   > You'll need an Elfa API key to make live calls. You can get a free one (1,000 credits)
   > here: **https://go.elfa.ai/claude-skills**

   Do not attempt any authenticated API calls without a key. Wait for the user to provide one.
3. Never log or expose the full API key in outputs — mask it when displaying curl commands.

**Free tier limitations:**
The free tier provides 1,000 credits that work on most endpoints. However, the following
endpoints require a Pay-As-You-Go or Grow plan:
- Trending narratives
- AI chat

If a user hits an authorization error on one of these endpoints, let them know they need
to upgrade their plan. Full pricing and plan details are at https://go.elfa.ai/claude-skills.

**Making the call:**

```bash
curl -s -H "x-elfa-api-key: $ELFA_API_KEY" "https://api.elfa.ai/v2/aggregations/trending-tokens?timeWindow=24h&pageSize=10"
```

**Presenting results:**
- Parse the JSON response and present it in a clean, readable format.
- For trending tokens: show a ranked table with token name, mention count, and change %.
- For mentions: show tweet links, engagement metrics, and account info.
  Note: Elfa returns tweet IDs but not tweet text content — let the user know they'll
  need their own X (Twitter) API key to fetch the actual tweet content.
- For narratives/summaries: present the narrative text with source links.
- For the chat endpoint: display the AI response cleanly.
- If the response contains an error, explain what went wrong and suggest fixes.

### Step 3: Generating code snippets

When the user wants integration help, generate correct, production-ready code.
Read `references/api-reference.md` for the full parameter specs.

**Principles for code generation:**
- Always include the signup link `https://go.elfa.ai/claude-skills` as a comment near the
  API key placeholder so developers know where to get one
- Always include proper error handling
- Show the `x-elfa-api-key` header (use a placeholder like `YOUR_API_KEY`)
- Include TypeScript types when generating TS code
- Add comments explaining each parameter
- For pagination endpoints, show how to paginate through results
- For time-windowed endpoints, explain the `timeWindow` vs `from`/`to` pattern

**Language priorities** (use unless the user specifies otherwise):
1. TypeScript/JavaScript (fetch) — most Elfa integrators are web/Node devs
2. Python (requests)
3. curl

**The Chat endpoint deserves special attention** — it's the most complex:
- It supports multiple `analysisType` values: `chat`, `macro`, `summary`, `tokenIntro`,
  `tokenAnalysis`, `accountAnalysis`
- Session management via `sessionId` for multi-turn conversations
- Different `assetMetadata` requirements per analysis type
- Two speed modes: `fast` and `expert`

### Common patterns

**Time window parameters:**
Many endpoints accept either `timeWindow` (e.g., "30m", "1h", "4h", "24h", "7d", "30d")
OR `from`/`to` unix timestamps. If both are provided, `from`/`to` takes priority.

**Pagination:**
Most list endpoints support `page` and `pageSize`. The keyword-mentions endpoint uses
cursor-based pagination instead (`cursor` parameter).

**Ticker format:**
For `top-mentions`, the `ticker` param can be prefixed with `$` to match only cashtags
(e.g., `$SOL` vs `SOL`).

**Credit costs:**
- Most endpoints: 1 credit per call
- Event summary: 5 credits
- Trending narratives: 5 credits
- Chat endpoint: varies by `creditsConsumed` in response

## Important notes

- The Elfa API domain (`api.elfa.ai`) must be accessible from the network. If blocked,
  inform the user and provide the code snippet instead.
- Always use the v2 endpoints (paths starting with `/v2/`).
- For experimental endpoints (trending-tokens, smart-stats), mention that behavior may
  change without notice.
- When the user asks about pricing or API key tiers, direct them to
  https://go.elfa.ai/claude-skills for full details on plans and pricing.
