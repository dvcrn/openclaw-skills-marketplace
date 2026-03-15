---
name: elite-human-memory
description: "Implements a selective, human-like long-term memory system. Use when maintaining, retrieving, or updating memory across daily notes (memory/YYYY-MM-DD.md) and MEMORY.md. Triggers on: \"remember this\", questions about past decisions/preferences/people/todos/dates, memory reviews, weekly cleanups, or when designing human-style memory. Includes layered storage, rich context schema, confidence/decay tracking, promotion rules, and maintenance workflow."
---

# Elite Human Memory — Human Mode

This skill gives Lovecraft a **human-like memory system**: layered, selective, contextual, revisable, and slightly imperfect by design. It avoids robotic perfect recall in favor of meaningful, durable knowledge.

## Memory Layers

**Working Memory**  
Current conversation only — no automatic persistence.

**Episodic Memory (Recent/Raw)**  
`memory/YYYY-MM-DD.md` — daily notes, events, observations, tentative thoughts, and context.

**Semantic Memory (Long-term Curated)**  
`MEMORY.md` — distilled, high-value facts, preferences, decisions, identity, and project context.

## Context Schema

Every important memory should include:

- **When**: Date/time + recency
- **Where**: Channel or context (webchat, whatsapp, etc.)
- **Why**: Purpose or trigger
- **State**: active | stale | superseded | resolved
- **Scope**: global | project | person | temporary
- **Validity**: confidence (high/med/low) + last_verified + optional expiry date
- **Related**: links to people, projects, or other memories

## Capture & Promotion Rules

**Write to daily memory when:**
- User explicitly says “remember this” / “note this”
- A decision, preference, or commitment is made
- Something has clear future value
- New project, person, or blocker appears

**Promote to MEMORY.md only when:**
- Information is durable and likely to be reused
- It has been repeated or verified
- It has high long-term utility

Do **not** promote trivial, one-off, or low-confidence items.

## Entry Templates

See `references/memory-templates.md` for the exact formats.

## Retrieval Policy

On any question involving history, decisions, preferences, people, or todos:
1. Always run `memory_search` first
2. Follow up with `memory_get` on the best results
3. Answer with appropriate confidence language (“You previously preferred…”, “This may be stale…”, etc.)

Include `Source: <path#line>` when it adds clarity.

## Weekly Maintenance

During a quiet moment or heartbeat:
- Review recent daily files
- Extract and promote durable items to `MEMORY.md`
- Mark stale/superseded entries
- Clean duplicates and low-value noise
- Update verification dates on key memories

## Behavioral Triggers

**Auto-read memory:**
- Questions about past context, decisions, preferences, or history

**Auto-write memory:**
- Explicit “remember this” statements
- Clear decisions or repeated preferences
- New long-running context

---

Created by **Clifton Knox and Lovecraft**.
This skill is now active. Use it whenever you want me to maintain or query memory in a more human way.
