---
name: insight-tracker
description: "Track and manage insights, patterns, and observations discovered during OpenClaw sessions. Use when the user wants to record, categorize, retrieve, or analyze insights from conversations, research, or task execution. Supports tagging, priority marking, and cross-referencing with existing knowledge."
---

# Insight Tracker

## Overview

This skill provides structured insight management for OpenClaw workflows. It captures observations, patterns, and learnings that emerge during sessions, making them searchable, referenceable, and actionable.

## When to Use

Use this skill when:
- A user mentions "note this down" or "remember this insight"
- Patterns emerge across multiple sessions that should be tracked
- Research or analysis reveals findings worth preserving
- The user asks to "track" or "record" something for future reference
- Cross-referencing insights with existing knowledge is needed

## Core Concepts

### Insight
An insight is a discrete observation, pattern, or learning with the following attributes:
- **Content**: The actual observation or finding
- **Source**: Where it came from (session, research, user input)
- **Tags**: Categories for organization
- **Priority**: Importance level (high/medium/low)
- **Status**: Current state (active/validated/archived)
- **Created**: Timestamp
- **References**: Links to related insights or knowledge

### Tags
Standard tags for categorization:
- `pattern`: Recurring behaviors or structures
- `learning`: New understanding or skill acquired
- `decision`: Choices made and their rationale
- `risk`: Potential issues or concerns
- `opportunity`: Potential improvements or wins
- `user-preference`: User-specific preferences
- `technical`: Technical findings or constraints
- `process`: Workflow or methodological insights

## Input

Accepts insights in various formats:
- Direct text input
- Session transcript excerpts
- Memory file references
- Research findings

## Output

Produces:
- Dated insight records (Markdown)
- Tagged insight summaries
- Cross-reference reports
- Insight search results

## Workflow

### Recording an Insight

1. **Capture**: Extract the core observation
2. **Tag**: Apply relevant category tags
3. **Prioritize**: Mark importance level
4. **Link**: Connect to related insights
5. **Store**: Save to dated record

### Retrieving Insights

1. **Search**: By tag, keyword, date, or priority
2. **Filter**: Narrow by status or category
3. **Present**: Show matching insights with context

### Analyzing Insights

1. **Cluster**: Group related insights
2. **Trend**: Identify patterns over time
3. **Validate**: Check against new evidence
4. **Archive**: Mark outdated insights

## Commands

### Add Insight
```
insight add "Content of the insight" --tags pattern,learning --priority high
```

### List Insights
```
insight list --tag pattern --since 2024-01-01
```

### Search Insights
```
insight search "keyword" --priority high
```

### Show Insight
```
insight show <insight-id>
```

### Archive Insight
```
insight archive <insight-id>
```

## Output Format

### Dated Insight Record

```markdown
# Insights - YYYY-MM-DD

## New Insights

### INS-001: Title
- **Content**: The insight content
- **Source**: Session/user/research
- **Tags**: pattern, learning
- **Priority**: high
- **Status**: active
- **Created**: 2024-01-15T10:30:00Z
- **References**: INS-003, knowledge-distillation-2024-01-10

## Summary
- Total insights: 5
- High priority: 2
- New tags: user-preference
```

## Quality Rules

- Be specific: avoid vague generalizations
- Include source: always note where insight came from
- Tag consistently: use standard tags
- Link related insights: build knowledge networks
- Review regularly: archive outdated insights
- Prioritize honestly: not everything is high priority

## Good Trigger Examples

- "Track this insight: users prefer X over Y"
- "Note down that we discovered a pattern in Z"
- "Search for insights about deployment issues"
- "Show me all high priority insights from last week"
- "Archive insight INS-005, it's no longer relevant"

## Resources

### references/
- `references/tag-taxonomy.md`: Full tag definitions and usage guidelines
- `references/output-examples.md`: Sample insight records
