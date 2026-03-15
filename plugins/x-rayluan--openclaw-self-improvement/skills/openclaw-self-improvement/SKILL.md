---
name: openclaw-self-improvement
description: "This skill should be used when the user asks to capture learnings, log recurring errors, record feature gaps, improve agent workflows over time, operationalize corrections, or build a self-improving OpenClaw or ClawLite operating loop with Karen, Mission Control, and Obsidian vault support."
---

# OpenClaw / ClawLite Self-Improvement

Use this skill to turn mistakes, corrections, blockers, and better approaches into durable operating knowledge.

## What problem this solves
AI ops often repeat the same failures because mistakes stay in chat history instead of becoming system rules. This skill creates a lightweight improvement loop:
- log failures and learnings
- separate errors from feature requests
- promote important patterns into AGENTS.md / TOOLS.md / SOUL.md
- write operator notes into Obsidian vault
- support stricter acceptance via Karen / Mission Control

## When to use
Use this skill when the user asks:
- "make the agent improve itself"
- "capture learnings"
- "log mistakes so we do not repeat them"
- "record blockers / corrections / feature gaps"
- "build a self-improving OpenClaw workflow"
- "operationalize lessons learned"

## Files this skill uses
- `.learnings/LEARNINGS.md`
- `.learnings/ERRORS.md`
- `.learnings/FEATURE_REQUESTS.md`
- Obsidian vault note under `ClawLite/Operations/Learnings/`

## Command examples
```bash
node {baseDir}/scripts/log-learning.mjs learning "Summary" "Details" "Suggested action"
node {baseDir}/scripts/log-learning.mjs error "Summary" "Error details" "Suggested fix"
node {baseDir}/scripts/log-learning.mjs feature "Capability name" "User context" "Suggested implementation"
node {baseDir}/scripts/promote-learning.mjs workflow "Rule text"
```

## Categories
### learning
Use for:
- user corrections
- better recurring workflows
- tool gotchas
- operational lessons

### error
Use for:
- command failures
- integration failures
- runtime blockers
- broken release / deploy behavior

### feature
Use for:
- missing capability requests
- operator workflow gaps
- recurring requests that deserve a build item

## Promotion targets
- `AGENTS.md` → workflow / delegation / execution rules
- `TOOLS.md` → tool gotchas, secrets locations, environment routing rules
- `SOUL.md` → behavior / communication / non-negotiable principles
- Obsidian vault → reusable operator log and content proof asset

## Karen / Mission Control compatibility
This skill is designed to work with stricter ops governance:
- Karen can reference learnings when repeated failures happen
- Mission Control can treat promoted learnings as new operating rules
- recurring blockers can be elevated from chat into tracked operational knowledge

## Output goal
A good use of this skill should produce one of:
- a durable learning entry
- a durable error entry
- a durable feature request entry
- a promoted rule in AGENTS.md / TOOLS.md / SOUL.md
- an Obsidian vault operations note

## Important limits
- Logging is not the same as fixing.
- Do not treat a learning entry as closure for a broken deliverable.
- Use this skill to reduce repeated mistakes, not to excuse them.

## References
- `{baseDir}/references/schema.md`
- `{baseDir}/references/promotion-guide.md`
