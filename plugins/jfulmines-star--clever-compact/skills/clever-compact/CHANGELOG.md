## v2.1.0 — March 8, 2026
**Architecture fix — lifecycle hooks only, no context engine registration**

v2.0.0 was yanked. The `registerContextEngine` approach had a critical bug: `compact()` returning `{ compacted: false }` blocked the legacy compaction engine instead of passing through to it. Any user who installed v2.0.0 and set the `contextEngine` slot would have had compaction silently stop firing.

v2.1 removes `registerContextEngine` entirely. The plugin registers one lifecycle hook:

- `before_prompt_build` → injects the most recent state file ONCE per session start (bootstrap/restore). Fires on first turn only — no per-turn token overhead.

**Note on write side:** OpenClaw does not expose a pre-compaction lifecycle hook. State writes are always explicit — triggered by your agent (manual phrase, heartbeat step, or pre-compact cron). The plugin exposes `api.fn("clever-compact:write")` for programmatic triggers. See SKILL.md for setup patterns.

Zero interference with the compaction mechanism. Installation no longer requires setting `plugins.slots.contextEngine` — just add `clever-compact` to `plugins.allow`.

## v2.0.0 — March 8, 2026 ⚠️ YANKED
Do not install. `registerContextEngine` + `compact()` returning `{ compacted: false }` caused compaction to silently stop firing for any user with the contextEngine slot set.

# Clever Compact — Changelog

## v1.2.0 — March 4, 2026
**Framing update — now speaks the language of the problem**
- Reframed the opening around the three failure modes: `/new` amnesia, compaction loss, memory drift
- Language mirrors how power users actually describe the problem — makes it immediately recognizable
- No functional changes to the skill itself

## v1.1.0 — March 3, 2026
**Reduce compaction frequency**
- Added `reserveTokens` tuning guide — lower from 50,000 to 15,000 to push compaction to ~185k/200k context
- Roughly 3–4× fewer compactions per heavy session
- Updated urgency language: compaction takes up to 10 minutes, not seconds. Real discovery from live power-user sessions.

## v1.0.0 — March 1, 2026
**Initial release**
- Core pre-compact scan: active workstreams, key decisions, open tasks, relationship context, remember flags
- State file written to `memory/compact-state-YYYY-MM-DD-HH.md`
- Post-compact restore hook via AGENTS.md
- State file format spec (Markdown + embedded JSON)
- Pro tier placeholder ($9/mo — feature-gated)
