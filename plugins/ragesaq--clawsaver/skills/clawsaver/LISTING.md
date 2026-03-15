# ClawHub Listing Copy

## Slug
`clawsaver`

## Display Name
`ClawSaver`

## Short Description (≤160 chars, for search results / cards)
Reduce AI costs by batching related asks into fewer responses. ~30–50% fewer API calls, ~20–35% fewer tokens, no quality loss.

## Long Description (for skill detail page)

Stop paying for round-trips.

ClawSaver teaches your OpenClaw assistant to recognize when multiple questions or tasks share enough context to be answered together — and handles them in a single well-structured response instead of making you pay for each one separately.

**What it does:**
- Detects batchable asks: multiple questions on the same topic, follow-ups within a few turns, redundant tool calls
- Groups them intelligently with clear per-question sections
- Skips batching when it would hurt: sequential dependencies, unrelated domains, explicit user opt-out
- Optionally shows savings: "💸 Batched 3 asks → 1 response"

**Typical savings:**
- 30–50% fewer API requests per session
- 20–35% fewer tokens consumed

**Example:**
You ask: *"Check this for bugs. Is it performant? Are there missing tests?"*
Without ClawSaver: 3 requests, 3 context loads.
With ClawSaver: 1 request, 1 context load, structured answer with three clear sections.

**Safety-first:**
ClawSaver never merges tasks with sequential dependencies, never compresses meaning for the sake of size, and always respects "answer each one separately."

Install with:
```
clawhub install clawsaver
```

## Tags
`cost-saving` `token-optimization` `batching` `efficiency` `productivity`

## Category
Cost & Performance

## Version
1.0.0
