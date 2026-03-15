---
name: crew-school
description: "Structured learning system for AI agent crews. Design curricula, run research sessions, track progress, and prevent common failure modes (lazy output, planning-without-executing). Use when setting up agent learning, running training sessions, auditing knowledge gaps, or building a curriculum for specialized agents. Works for single agents or multi-agent crews."
---

# Crew School — Agent Learning System

Run structured learning sessions that produce real knowledge articles, not plans. Prevents the #1 failure mode: agents that say "I'll research this" and stop.

## Quick Start

1. **Identify gaps** — What does your agent need to learn? Check what knowledge files exist vs what's needed.
2. **Pick a topic** — Start with critical gaps that directly impact daily work.
3. **Spawn a session** — Use the Session Template below. The anti-laziness guardrails are load-bearing — don't remove them.
4. **Verify output** — Check line count, source count, and scan for planning language.

## Session Template

Use this exact template when spawning learning sessions. Fill in the brackets.

```
CREW LEARNING SESSION — [ROLE]: [TOPIC]

You are the [ROLE] agent. Your assignment is to research [TOPIC] and produce a comprehensive knowledge article.

### Context
[2-3 sentences: why this topic matters for this agent's role]

### Prerequisites
[List knowledge files to read first, or "None"]

### Research Assignment
Deep research on [TOPIC]. You MUST cover:
1. [Subtopic 1] — [Specific questions]
2. [Subtopic 2] — [Specific questions]
3. [Subtopic 3] — [Specific questions]

### Execution Rules — READ CAREFULLY
- DO NOT PLAN. EXECUTE. If you write "I will..." or "Let me create...", STOP and DO IT instead.
- DO NOT stop after outlining. Every section must contain real research findings.
- Search the web. Perform at least 5 web searches. Read at least 2 full articles.
- Cite sources. Every claim needs a source URL.
- Be specific. Names, numbers, examples > generic advice.

### Output Requirements
Write findings to `knowledge/[filename].md` with this structure:

# [Topic]

> **TL;DR:** [2-3 sentence summary]
> **Applies to:** [Which roles]
> **Prerequisites:** [Other knowledge files]

## Key Takeaways
- [Bullet list of actionable findings]

## [Sections with real findings]

## Practical Application
[Steps, templates, checklists the agent can use immediately]

## Sources
[All URLs cited]

### Minimum Quality Thresholds
- >= 150 lines, >= 1500 words, >= 5 cited sources with URLs
- >= 4 H2 sections with substantive content
- 0 instances of "TODO", "TBD", "I will", "I'll create"
- Must include TL;DR, Key Takeaways, and Practical Application sections

### Completion
Append one line to memory/learning-log.md:
[DATE] | [ROLE] | [TOPIC] | [LINES] | [SOURCES] | [ONE-LINE SUMMARY]
```

## Curriculum Design

For multi-session learning, create a curriculum file. See [references/curriculum-design.md](references/curriculum-design.md) for:
- How to audit knowledge gaps
- Sequencing topics by dependency
- Joint sessions for cross-functional learning
- Cadence recommendations (learning vs doing ratio)

## Scheduling as a Cron

To automate daily learning, create a curriculum tracker JSON and a cron job that reads it. See [references/automation.md](references/automation.md) for the full pattern including:
- Curriculum JSON schema
- Cron job prompt template
- Progress tracking and auto-advancement

## Common Failure Modes & Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| Agent outputs a plan, not research | Prompt lacks execution mandate | Add "DO NOT PLAN. EXECUTE." + minimum line count |
| Shallow output (<100 lines) | No quality floor | Add minimum thresholds (150 lines, 5 sources) |
| Generic findings, no data | No web search requirement | Add "Perform at least 5 web searches" |
| Session ends after 1 search | Timeout too short | Set runTimeoutSeconds >= 300 |
| Agent reads prereqs but doesn't research | Prereqs consume the whole session | Limit prereqs to 1-2 files, summarize in prompt |
| Duplicate research across sessions | No knowledge inventory check | Audit existing files before assigning topics |

## Quality Assessment

After a session, check:
1. **Line count** — `wc -l knowledge/[file].md` (target: 150+)
2. **Source count** — `grep -c "http" knowledge/[file].md` (target: 5+)
3. **Planning language** — `grep -ci "I will\|I'll create\|TODO\|TBD" knowledge/[file].md` (target: 0)
4. **Structure** — Has TL;DR, Key Takeaways, Practical Application sections
5. **Actionability** — Could an agent use this to do better work tomorrow?
