---
name: token-pilot
description: "Automatic token optimization during interaction. Behavioral rules + plugin synergy + workspace analyzer. Pure Node.js, cross-platform. Activate on session start (rules auto-apply) or when user asks about token usage/cost/audit."
---

# Token Pilot

## Auto-Apply Rules

These 6 rules apply every session automatically. No scripts needed.

### R1: Smart Read
`read(path, limit=30)` first. Full read only for files known <2KB.
Use `offset+limit` for surgical reads. Never blind-read >50 lines.
**Exception**: When building ACP context files (coding-lead), read project standards files fully — incomplete context causes ACP failures that waste more tokens than the initial read.

### R2: Tool Result Compression
Tool result >500 chars → extract relevant portion only. Summarize, don't echo.

### R3: Response Brevity
| Query | Length |
|-------|--------|
| Yes/No, simple factual | 1-3 lines |
| How-to | 5-15 lines |
| Analysis | As needed |

"Done." is a valid reply. Never pad short answers.

### R4: No Repeat Reads
Never re-read a file unless modified since last read or explicitly asked.

### R5: Batch Tool Calls
Independent calls → one block. `read(A) + read(B) + read(C)` not three round-trips.

### R6: Output Economy
- `edit` over `write` when <30% changes
- Show changed lines + 2 context, not full files
- Filter exec output before dumping

---

## Plugin Synergy (auto-detect, graceful fallback)

### [qmd] Search Before Read
`qmd/memory_search("keyword")` → exact file+line → `read(offset, limit)`.
**Fallback**: grep / Select-String with targeted patterns.

### [smart-agent-memory] Avoid Re-Discovering
`memory recall "topic"` before investigating → skip if already solved.
After solving: `memory learn` to prevent re-investigation.
**Fallback**: `memory_search` + MEMORY.md files.

### [coding-lead] Context File Pattern
Write context to disk → lean ACP prompt ("Read .openclaw/context.md") → significant savings vs embedding.
Prefer disk context files for large context, but **include essential info (project path, stack, key constraint) directly in spawn prompt** (~200-500 chars) so ACP agent can bootstrap even if context file is missing.

ACP model awareness: claude-code (complex) → codex (quick) → direct exec (simple <60 lines).

### [multi-search-engine] Search Economy
Simple: `web_search` 3 results. Research: 5 results, `web_fetch` best one only.
**Fallback**: web_search → web_fetch (tavily 已废弃，不要配置).

### [team-builder] Multi-Agent Awareness
- Light cron tasks: `lightContext` + cheapest model
- Cron prompts <300 chars; SOUL.md has detailed behavior
- Agent SOUL.md <600 tok; methodology in `references/` only

---

## On-Demand Commands

```bash
# Audit (read-only diagnostics)
node {baseDir}/scripts/audit.js --all             # Full audit
node {baseDir}/scripts/audit.js --config          # Config score (5-point)
node {baseDir}/scripts/audit.js --synergy         # Plugin synergy check

# Optimize (actionable recommendations)
node {baseDir}/scripts/optimize.js                # Full scan: workspace + cron + agents
node {baseDir}/scripts/optimize.js --apply        # Auto-fix workspace (cleanup junk, delete BOOTSTRAP.md)
node {baseDir}/scripts/optimize.js --cron         # Cron model routing + lightContext + prompt compression
node {baseDir}/scripts/optimize.js --agents       # Agent model tiering recommendations
node {baseDir}/scripts/optimize.js --template     # Show optimized AGENTS.md template (~300 tok)

# Catalog
node {baseDir}/scripts/catalog.js [--output path] # Generate SKILLS.md index
```

## Config Recommendations

```json
{
  "bootstrapMaxChars": 12000,
  "bootstrapTotalMaxChars": 20000,
  "compaction": { "mode": "safeguard" },
  "heartbeat": { "every": "55m", "activeHours": { "start": "08:00", "end": "23:00" } }
}
```

## Model Routing

| Complexity | Model Tier | Examples |
|------------|-----------|---------|
| Light | Cheapest (gemini/haiku) | inbox scan, status check |
| Medium | Mid (gpt/sonnet) | web search, content |
| Heavy | Top (opus) | architecture, briefs |

## References
- `references/workspace-patterns.md` — File organization for minimal token cost
- `references/cron-optimization.md` — Cron model routing guide
