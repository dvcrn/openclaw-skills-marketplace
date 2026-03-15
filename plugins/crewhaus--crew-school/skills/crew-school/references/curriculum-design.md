# Curriculum Design for Agent Crews

## Knowledge Gap Audit

Before designing a curriculum, audit what your agents know vs need to know.

### Step 1: List competency areas per agent
For each agent role, define 5-7 competency areas. Example:
- **Scout:** competitive analysis, demand signals, market sizing, trend analysis, source verification
- **Growth:** channel strategy, conversion optimization, content marketing, analytics, SEO

### Step 2: Inventory existing knowledge
List all knowledge files (`ls knowledge/`) and map them to competency areas. Create a table:

| Agent | Competency | Articles | Gap Severity |
|-------|-----------|----------|-------------|
| Ops | Load testing | 0 | 🔴 Critical |
| Designer | UX patterns | 5 | 🟢 Covered |

### Step 3: Prioritize by daily impact
Rank gaps by how much they hurt daily shift quality. Critical gaps (directly impacts output) before moderate gaps (sub-optimal but functional).

## Topic Sequencing

### Dependency-first ordering
Some topics build on others. Map prerequisites:
```
Analyst: funnel analysis → Growth: conversion optimization
Engineer: CI/CD → Ops: security hardening
Designer: copywriting → Growth: landing pages
```

Always teach foundations before advanced topics.

### Recommended sequence per agent
1. **Foundation** (Week 1) — Core frameworks and mental models
2. **Tactical** (Week 2) — Specific techniques and tools
3. **Strategic** (Week 3) — Higher-level patterns and cross-domain thinking
4. **Applied** (Week 4) — Practice exercises with real data

## Joint Sessions

When two agents need overlapping knowledge, run a "joint session" — one research task covering both perspectives.

**When to use joint sessions:**
- Two agents work on the same problem from different angles
- Knowledge from one domain is a prerequisite for another
- Cross-pollination would improve coordination

**Examples:**
- Growth + Analyst: "Funnel Analytics End-to-End" (measurement + optimization)
- Designer + Growth: "Conversion Psychology" (design + marketing)
- PM + Engineer: "Technical Scoping" (planning + execution)

## Cadence Recommendations

Based on research and practical experience:

- **Learning vs doing ratio:** 80/20 (4 doing days per 1 learning day, or 2 short sessions per day)
- **Optimal frequency:** 2 sessions/agent/week for active learning, 1/week for maintenance
- **Session timing:** BEFORE daily shifts so fresh knowledge is immediately applicable
- **Batch size:** 2 sessions per day (avoid >3, diminishing returns)
- **Cooldown:** After a 4-week intensive curriculum, drop to 1 session/agent/week maintenance mode

## Tracking Progress

Use a simple JSON tracker:
```json
{
  "currentDay": 5,
  "lastSessionDate": "2026-03-10",
  "completedSessions": 10,
  "totalSessions": 28,
  "schedule": [
    {"day": 1, "agent": "ops", "topic": "Load Testing", "status": "done", "lines": 215},
    {"day": 1, "agent": "designer", "topic": "User Flows", "status": "done", "lines": 180}
  ]
}
```

Review weekly: which sessions produced high-quality output? Which need re-running? Adjust curriculum based on what's working.
