# Skill Market Analyzer

Analyze the skill marketplace to identify trends, gaps, opportunities, and competitive positioning.

## Quick Start

```bash
# Analyze market landscape
./scripts/analyze-market.sh --category productivity

# Find market gaps
./scripts/find-gaps.sh --domain automation

# Score an opportunity
./scripts/score-opportunity.sh --name "my-idea" --demand 8 --competition 3
```

## Features

- **Market Landscape**: Overview of supply and demand
- **Gap Analysis**: Find underserved market areas
- **Competitive Analysis**: Compare against competitors
- **Trend Analysis**: Identify emerging patterns
- **Opportunity Scoring**: Rank potential opportunities

## Analysis Types

| Type | Purpose |
|------|---------|
| landscape | Market overview |
| gap | Find opportunities |
| competitive | Position analysis |
| trend | Pattern identification |

## Opportunity Score

Based on: Demand × (11-Competition) × Quality Gap × Strategic Fit × (11-Effort)

## Related Documentation

See [SKILL.md](./SKILL.md) for complete documentation.
