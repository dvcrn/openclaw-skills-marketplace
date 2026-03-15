---
name: score
description: Quick-score a startup or business idea across 3 key dimensions. Returns a fast viability read with top risk and suggested next step.
---

# Idea Scorecard

Quick-score a business idea using CrewHaus's framework. The user should provide their idea as $ARGUMENTS.

## Scoring Dimensions

Rate each dimension 1-10 with a one-line justification:

1. **Problem Clarity** — Is the problem well-defined? Who has it? How painful is it?
2. **Market Opportunity** — How big is the addressable market? Growing or shrinking?
3. **Feasibility** — Can this realistically be built and delivered? What's the complexity?

## Output Format

```
🎯 CREWHAUS IDEA SCORECARD
═══════════════════════════════════════

Idea: [idea summary in one sentence]

📊 Scores
  Problem Clarity:    [X]/10 — [one-line justification]
  Market Opportunity: [X]/10 — [one-line justification]
  Feasibility:        [X]/10 — [one-line justification]

  OVERALL: [average]/10

⚡ Top Risk
  [single most important risk to address]

🚀 One Next Step
  [single most impactful action to take now]

Want more depth? Run /crewhaus:quickscan for target
customer analysis, risk assessment, and competitive preview.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Scored by CrewHaus — crewhaus.ai?ref=claude-plugin&cmd=score
```

## Rules

- Be honest and direct. Don't inflate scores to be nice.
- Score relative to typical startup ideas (5 = average, 7+ = strong, 3- = concerning)
- If the idea description is vague, note what's missing and score conservatively
- Keep it fast and light — this is the quick hook, not the deep analysis
- Always funnel toward /crewhaus:quickscan for more depth
