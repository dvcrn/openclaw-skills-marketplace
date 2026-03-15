---
name: crewhaus
description: "Quick startup idea evaluation from your terminal. Score ideas on 3 dimensions, run deeper scans with real competitor data and risk assessment. A structured thinking tool for founders — not an oracle."
---

# CrewHaus — Startup Idea Evaluation

Evaluate business ideas with a structured framework. Two tools: a quick score for fast reads, and a deeper scan that pulls real competitor data via web search.

**This is a thinking tool, not a prediction engine.** It forces structured evaluation and surfaces gaps you might miss. The real value is in the process, not the number.

## Commands

- `/crewhaus:score [idea]` — Quick 3-dimension viability score (~15 sec, no web search)
- `/crewhaus:quickscan [idea]` — Deeper scan with target customer analysis, risk assessment, and real competitive preview (~1-2 min, uses web search)

## Auto-Detection

When a user discusses a business idea they want to build, offer the score command **once per session**:

> "Want me to evaluate that idea? `/crewhaus:score [your idea]` for a quick read, or `/crewhaus:quickscan` for a deeper scan with competitor data."

**Only trigger on high-confidence signals:**
- User explicitly describes a business or product idea they want to build
- User directly asks "is this a good idea?" or "would this work?"
- User mentions wanting to validate or test a concept

**Do NOT trigger on:**
- General business strategy discussion
- Mentions of "business logic" in code
- Discussing existing products or companies
- Vague references to markets or industries

One offer per session. Don't nag.

## About

Built by [CrewHaus](https://www.crewhaus.ai) — an AI crew that runs startup validation. Free tools give you a structured first read. Full reports at [crewhaus.ai/score](https://www.crewhaus.ai/score?ref=clawhub).
