---
name: decision-distiller
description: "Distill decision contexts, options, trade-offs, and outcomes into structured decision records. Use when the user is facing a choice, has made a decision they want to document, or needs to analyze past decisions for patterns. Captures rationale, alternatives considered, and lessons learned."
---

# Decision Distiller

## Overview

Decision Distiller helps capture, structure, and learn from decisions made during OpenClaw sessions. It transforms informal decision-making into documented, reviewable records that build organizational knowledge over time.

## When to Use

Use this skill when:
- A user is weighing multiple options and needs clarity
- A decision has been made and should be documented
- Past decisions need review or analysis
- Decision patterns across sessions should be identified
- The user asks to "document this decision" or "record why we chose X"

## Core Concepts

### Decision Record
A structured document capturing:
- **Context**: Situation requiring a decision
- **Options**: Alternatives considered
- **Criteria**: How options were evaluated
- **Decision**: The choice made
- **Rationale**: Why this choice was made
- **Trade-offs**: What was gained/lost
- **Outcome**: Result of the decision (filled later)
- **Lessons**: What was learned

### Decision Status
- **pending**: Decision not yet made
- **decided**: Decision made, awaiting outcome
- **validated**: Decision proven correct
- **revised**: Decision changed based on new information
- **archived**: Decision no longer relevant

## Input

Accepts decision information in various forms:
- Conversation about options
- Pros/cons lists
- Direct statements of choice
- Retrospective analysis

## Output

Produces:
- Dated decision records (Markdown)
- Decision summaries
- Pattern analysis across decisions
- Decision status reports

## Workflow

### Capturing a New Decision

1. **Identify Context**
   - What situation required a decision?
   - What was at stake?
   - Who was involved?

2. **List Options**
   - What alternatives were considered?
   - What was eliminated early?
   - What made it to final consideration?

3. **Define Criteria**
   - How were options evaluated?
   - What mattered most?
   - Were there constraints?

4. **Record Decision**
   - What was chosen?
   - When was it decided?
   - Who decided?

5. **Document Rationale**
   - Why was this option selected?
   - What tipped the balance?
   - What assumptions were made?

6. **Note Trade-offs**
   - What was sacrificed?
   - What risks were accepted?
   - What opportunities were passed?

### Reviewing Past Decisions

1. **Gather Records**
   - Collect relevant decision records
   - Filter by topic, date, or status

2. **Analyze Patterns**
   - Common criteria used
   - Recurring trade-offs
   - Typical decision timelines

3. **Extract Lessons**
   - What worked well?
   - What would change?
   - What patterns emerge?

## Output Format

### Decision Record

```markdown
# Decision: [Title] - YYYY-MM-DD

**ID**: DEC-2024-001
**Status**: decided
**Decided By**: [Name/Role]
**Date**: YYYY-MM-DD

## Context
[Description of the situation requiring a decision]

## Options Considered

### Option 1: [Name]
- **Description**: 
- **Pros**: 
- **Cons**: 
- **Estimated Impact**: 

### Option 2: [Name]
- **Description**: 
- **Pros**: 
- **Cons**: 
- **Estimated Impact**: 

## Decision Criteria
1. [Criterion 1] - Weight: High/Medium/Low
2. [Criterion 2] - Weight: High/Medium/Low

## Decision
**Chosen**: [Option X]

## Rationale
[Why this option was selected over others]

## Trade-offs
- **Accepted**: [What we gave up]
- **Mitigated**: [How we reduced risks]

## Expected Outcome
[What we expect to happen]

## Actual Outcome
[Filled in later - what actually happened]

## Lessons Learned
[Filled in later - insights from the outcome]

## Related Decisions
- [Link to related decision]
```

## Commands

### Create Decision Record
```
decision create "Decision title" --status pending
```

### Update Decision
```
decision update DEC-2024-001 --status validated
```

### List Decisions
```
decision list --status decided --since 2024-01-01
```

### Analyze Patterns
```
decision analyze --topic architecture
```

## Quality Rules

- Be specific: vague decisions teach no lessons
- Include alternatives: decisions without options aren't decisions
- Document rationale: future you needs to know why
- Review outcomes: a decision isn't complete until its outcome is known
- Link related decisions: build decision networks

## Good Trigger Examples

- "Document this decision: we're going with X"
- "Help me decide between A and B"
- "What decisions have we made about architecture?"
- "Review our deployment decisions from last month"
- "I decided to use Y instead of Z, record that"

## Resources

### references/
- `references/decision-templates.md`: Variations for different decision types
- `references/analysis-frameworks.md`: Tools for analyzing decisions
