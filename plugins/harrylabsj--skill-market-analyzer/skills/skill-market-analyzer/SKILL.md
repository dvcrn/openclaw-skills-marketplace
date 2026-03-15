---
name: skill-market-analyzer
description: "Analyze the skill marketplace to identify trends, gaps, opportunities, and competitive positioning. Use when researching skill market dynamics, planning new skills, understanding user needs, or optimizing existing skills for market fit."
---

# Skill Market Analyzer

## Overview

The `skill-market-analyzer` skill provides comprehensive market analysis for the skill ecosystem. It helps identify market trends, gaps, opportunities, and competitive positioning to make informed decisions about skill development and portfolio strategy.

## When to Use

- Planning a new skill and need market research
- Analyzing competitive landscape for existing skills
- Identifying gaps in the skill marketplace
- Understanding user demand patterns
- Optimizing skill positioning and messaging
- Prioritizing skill development roadmap
- Evaluating market opportunities

## Core Concepts

### Market Dimensions

| Dimension | Description |
|-----------|-------------|
| `demand` | User interest and request frequency |
| `supply` | Number of available skills in category |
| `quality` | Average quality of existing solutions |
| `saturation` | How crowded the market segment is |
| `growth` | Trend direction and velocity |

### Analysis Types

| Type | Purpose | Output |
|------|---------|--------|
| `landscape` | Overall market overview | Market map |
| `gap` | Find underserved areas | Opportunity list |
| `competitive` | Compare to competitors | Positioning analysis |
| `trend` | Identify emerging patterns | Trend report |
| `opportunity` | Score potential opportunities | Ranked list |

### Opportunity Score

Calculated based on:
- Demand level (1-10)
- Competition level (1-10, inverted)
- Quality gap (1-10)
- Strategic fit (1-10)
- Implementation effort (1-10, inverted)

**Formula**: `(demand + (11-competition) + quality_gap + strategic_fit + (11-effort)) / 5`

## Input

Accepts:
- Market category or domain
- Analysis type specification
- Time range for trend analysis
- Competitor list for comparison
- Target audience definition

## Output

Produces:
- Market analysis reports
- Opportunity rankings
- Competitive positioning maps
- Trend visualizations
- Strategic recommendations

## Workflow

### Market Landscape Analysis

1. Define market scope (category/domain)
2. Collect existing skills data
3. Analyze supply/demand balance
4. Identify market leaders
5. Map competitive positions
6. Generate landscape report

### Gap Analysis

1. Identify target user segments
2. List user needs and pain points
3. Map current skill coverage
4. Find underserved areas
5. Prioritize gaps by impact
6. Recommend development priorities

### Competitive Analysis

1. Identify direct competitors
2. Analyze feature coverage
3. Compare quality metrics
4. Assess positioning
5. Find differentiation opportunities
6. Recommend positioning strategy

### Trend Analysis

1. Define time period
2. Collect historical data
3. Identify emerging patterns
4. Forecast future trends
5. Recommend strategic adjustments

## Commands

### Analyze Market Landscape
```bash
./scripts/analyze-market.sh --category productivity --output landscape.md
```

### Find Market Gaps
```bash
./scripts/find-gaps.sh --domain automation --min-opportunity-score 7
```

### Competitive Analysis
```bash
./scripts/analyze-competition.sh --skill my-skill --competitors skill-a,skill-b
```

### Trend Analysis
```bash
./scripts/analyze-trends.sh --category all --since 2024-01-01
```

### Opportunity Scoring
```bash
./scripts/score-opportunity.sh --name "new-skill-idea" --demand 8 --competition 3 --effort 5
```

### Generate Full Report
```bash
./scripts/generate-report.sh --category productivity --type comprehensive
```

## Output Format

### Market Landscape Report
```markdown
# Market Landscape: Productivity Skills

## Executive Summary
- Total Skills: 45
- High-Demand Areas: 8
- Underserved Segments: 5
- Average Quality Score: 6.2/10

## Supply Analysis
| Category | Skills | Saturation |
|----------|--------|------------|
| Task Management | 12 | High |
| Note Taking | 8 | Medium |
| Time Tracking | 5 | Low |

## Demand Analysis
| Need | Frequency | Satisfaction |
|------|-----------|--------------|
| Calendar integration | High | Low |
| Cross-platform sync | Medium | Medium |
| AI assistance | High | Very Low |

## Opportunities
1. **AI-powered task prioritization** (Score: 8.5)
   - High demand, low competition
   - Quality gap: 7/10
   
2. **Cross-tool workflow automation** (Score: 7.8)
   - Medium demand, very low competition
   - Quality gap: 6/10

## Recommendations
- Focus on AI-assisted productivity features
- Consider integration-first approach
- Target underserved time-tracking market
```

### Opportunity Score Card
```json
{
  "opportunity": "AI Task Prioritizer",
  "score": 8.5,
  "breakdown": {
    "demand": 9,
    "competition": 2,
    "quality_gap": 7,
    "strategic_fit": 8,
    "effort": 6
  },
  "market_size": "Large",
  "time_to_market": "2-3 months",
  "confidence": "High",
  "recommendation": "Strong opportunity - proceed with development"
}
```

## Analysis Frameworks

### Supply-Demand Matrix

```
High Demand + Low Supply  →  OPPORTUNITY (develop here)
High Demand + High Supply →  COMPETE (differentiate)
Low Demand  + Low Supply  →  NICHE (evaluate carefully)
Low Demand  + High Supply →  AVOID (overcrowded)
```

### Quality-Competition Matrix

```
High Quality + Low Competition  →  LEADER (maintain position)
High Quality + High Competition →  DIFFERENTIATE (find unique angle)
Low Quality  + Low Competition  →  EASY WIN (enter with quality)
Low Quality  + High Competition →  AVOID (red ocean)
```

## Quality Rules

- Use multiple data sources for analysis
- Validate assumptions with user feedback
- Update analysis quarterly
- Track accuracy of predictions
- Document methodology
- Be transparent about confidence levels

## Good Trigger Examples

- "Analyze the market for productivity skills"
- "What gaps exist in the current skill marketplace?"
- "How does my skill compare to competitors?"
- "What are the emerging trends in automation skills?"
- "Score this skill idea for market opportunity"
- "Should I build a skill for X?"

## Limitations

- Analysis based on available data
- Trends may change rapidly
- User needs evolve over time
- Competition data may be incomplete
- Predictions are estimates, not guarantees
- Market timing is difficult to predict

## Related Skills

- `decision-distiller` - For evaluating market opportunities
- `insight-tracker` - For capturing market insights
- `feedback-loop` - For validating market hypotheses

## Resources

### scripts/
- `analyze-market.sh` - Market landscape analysis
- `find-gaps.sh` - Gap identification
- `analyze-competition.sh` - Competitive analysis
- `analyze-trends.sh` - Trend identification
- `score-opportunity.sh` - Opportunity scoring
- `generate-report.sh` - Comprehensive reports

### references/
- Market research templates
- Competitive analysis frameworks
- Trend analysis methodologies
