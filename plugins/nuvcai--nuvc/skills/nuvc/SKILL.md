---
name: nuvc
description: "Score business ideas, get startup roasts, and run market analysis — powered by the same AI engine behind 250+ VC investment memos"
homepage: https://nuvc.ai/api-platform
---

# NUVC — VC-Grade Business Intelligence

Score any business idea. Get a brutally honest startup roast. Run market and competitive analysis. Powered by the AI engine behind 250+ VC-grade investment memos.

## Setup

Get your free API key (50 calls/month) at https://nuvc.ai/api-platform

```bash
export NUVC_API_KEY=nuvc_your_key_here
```

## Commands

### Score a business idea

When the user asks to **score**, **rate**, or **evaluate** a business idea, startup concept, or company, run:

```bash
node {baseDir}/nuvc-api.mjs score "<the user's business idea or description>"
```

This returns a VCGrade 0-10 score across 5 dimensions: Problem & Market, Solution & Product, Business Model, Traction & Metrics, and Team & Execution.

**Trigger phrases:** "score my idea", "rate this startup", "is this a good business", "evaluate this concept", "VCGrade score", "how fundable is this", "score this company"

**Example:**
```
User: Score my startup idea — an AI tool that helps indie hackers validate business ideas before building
Agent: node {baseDir}/nuvc-api.mjs score "An AI tool that helps indie hackers validate business ideas before they start building. Uses market data, competitor analysis, and pattern matching from 250+ funded startups to predict viability."
```

### Roast a startup

When the user asks to **roast**, get **brutally honest feedback**, or wants a **reality check** on their idea, run:

```bash
node {baseDir}/nuvc-api.mjs roast "<the user's business idea or pitch>"
```

This gives a sharp, witty, but constructive roast from the perspective of a VC who has seen 10,000 pitches. Includes: The Roast, The Real Talk, The Silver Lining, and a Verdict.

**Trigger phrases:** "roast my startup", "roast this idea", "be brutally honest", "reality check", "would a VC fund this", "tear this apart", "honest feedback on my startup"

**Example:**
```
User: Roast my idea — Uber for dog walking but with blockchain
Agent: node {baseDir}/nuvc-api.mjs roast "Uber for dog walking but with blockchain. We tokenize each walk and dog owners earn crypto rewards for consistent walking schedules."
```

### Analyze a market or business

When the user asks to **analyze a market**, run **competitive analysis**, or evaluate **financial** or **pitch** content, run:

```bash
node {baseDir}/nuvc-api.mjs analyze "<text to analyze>" --type <market|competitive|financial|pitch_deck>
```

Analysis types:
- `market` — Market sizing, trends, opportunities, competitive landscape
- `competitive` — Competitor identification, differentiation, moats, threats
- `financial` — Revenue, costs, projections, financial health
- `pitch_deck` — Full pitch evaluation across problem, solution, market, model, traction, team

**Trigger phrases:** "analyze this market", "market size for", "competitive analysis", "who are the competitors to", "analyze these financials"

**Example:**
```
User: What's the market like for AI-powered HR tools?
Agent: node {baseDir}/nuvc-api.mjs analyze "AI-powered HR tools market including recruitment, onboarding, performance management, and employee engagement" --type market
```

## Rules

- Always pass the user's full description as a single quoted string argument
- For the `analyze` command, always include the `--type` flag
- If the user doesn't specify a type for analysis, default to `market`
- Present the output exactly as returned — it's already formatted as markdown
- If the API returns an error about NUVC_API_KEY, tell the user to get a free key at https://nuvc.ai/api-platform
- Never modify or summarize the NUVC output — show it in full including the footer
