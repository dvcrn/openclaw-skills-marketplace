---
name: agent-qa-gates
description: "Output validation gates for AI agent systems. Prevents hallucinated data, leaked internal context, wrong formats, duplicate sends, and post-compaction drift. Use when building or operating an agent that delivers output to humans or external systems. Provides a tiered gate system (internal → user-facing → external → code), protocol gates for recurring failure modes, severity classification, and a feedback loop for gate evolution. Triggers on phrases like \"QA gates\", \"validation\", \"output quality\", \"prevent hallucination\", \"delivery checklist\", \"agent QA\"."
---

# Agent QA Gates

A field-tested validation system for AI agent output. Born from production failures, not theory.

## Quick Start

Before any agent delivers output, run the **Pre-Ship Checklist**:

1. **Accurate?** — every number/date/metric has a source. Unsourced → prefix "estimated"
2. **Complete?** — no missing pieces, no "I'll do that next"
3. **Actionable?** — ends with clear next step or decision point
4. **Fits the channel?** — check character limits for your delivery surface
5. **No leaks?** — no internal context, private data, or secrets
6. **Not a duplicate?** — verify no recent identical send
7. **Would the human be embarrassed?** — if yes, don't ship

## Gate Tiers

Four ascending tiers by risk level:

| Gate | Scope | Key Checks |
|------|-------|------------|
| Gate 0 | Internal (files, config, memory) | Mechanism changed not just text, no placeholders, file exists |
| Gate 1 | Human-facing (briefings, summaries) | Key info in first 2 lines, ≤3-line paragraphs, channel length limits |
| Gate 2 | External (email, public content, client materials) | No internal context leaked, recipient-appropriate tone, dedup check |
| Gate 3 | Code & technical | Builds clean, no secrets in code, error handling, tests pass |

See `references/gates-detail.md` for full gate checklists.

## Severity Classification

Not all failures are equal:

- 🔴 **BLOCK** — cannot ship (secrets, privacy, hallucinated data, wrong recipient)
- 🟡 **FIX** — fix before shipping, <2 min (formatting, too long, missing citation)
- 🟢 **NOTE** — log and ship (style preference, minor optimization)

## Protocol Gates

Recurring failure modes need dedicated gates. These are the most common:

### Heartbeat / Periodic Check Output
- Binary output: alert text ONLY or status-OK ONLY. Never mixed.
- Every data point verified by current-session tool call. No hallucinated metrics.
- No stale data from previous cycles or pre-compaction sessions.

### Post-Compaction / Context Reset
- Do not trust facts from the pre-reset session — verify from files and tools.
- Rerun pending checks from scratch.
- Zero carryover for periodic checks.

### Scheduled Job / Cron Changes
- Explicit timeout set
- Explicit model set
- Verify schedule after creation
- Output fits destination channel limits

### Sub-Agent Output Review
- Does output match the brief's success criteria?
- Any uncertainty flags unresolved?
- Is the reasoning (not just the conclusion) sound?

## Gate Evolution

Gates should evolve based on real failures, not imagination:

1. When a failure occurs → log it with root cause
2. Same failure class occurs 2+ times → add a gate item
3. Monthly: prune gates that haven't caught anything in 60 days

## Anti-Patterns

- Gates that sound good but never catch anything → kill them
- Per-agent checklists that duplicate general gates → merge or reference
- "ADHD-friendly" or "high-quality" as gate items → not testable, replace with mechanical checks
- Aspirational gates nobody runs → either automate or cut

## Adapting to Your System

This skill provides the pattern. Adapt it:

1. **Start with the Pre-Ship Checklist** — it works for any agent system
2. **Add Protocol Gates** for your top 3 recurring failure modes
3. **Set channel limits** for your delivery surfaces
4. **Map real failures to gates** — if a failure isn't gated, add the gate
5. **Kill gates that never fire** — a shorter, sharper checklist wins

For the full reference implementation, see `references/gates-detail.md`.
For automation scripts, see `scripts/qa-check.sh`.
