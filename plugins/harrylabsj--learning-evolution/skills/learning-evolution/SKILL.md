---
name: learning-evolution
description: "Track, analyze, and evolve learning patterns from skill usage and user interactions. Use when identifying learning opportunities, tracking skill improvement over time, analyzing usage patterns, or evolving skills based on feedback."
---

# Learning Evolution

## Overview

The `learning-evolution` skill tracks, analyzes, and evolves learning patterns from skill usage and user interactions. It helps skills improve over time by identifying patterns, capturing insights, and suggesting evolutions based on real-world usage.

## When to Use

- Analyzing how skills are being used
- Identifying learning opportunities from usage patterns
- Tracking skill improvement over time
- Evolving skills based on user feedback
- Understanding what works and what doesn't
- Planning skill updates and improvements
- Measuring skill effectiveness

## Core Concepts

### Learning Dimensions

| Dimension | Description | Metrics |
|-----------|-------------|---------|
| `usage` | How often and how skills are used | Frequency, duration, completion |
| `effectiveness` | How well skills achieve goals | Success rate, error rate |
| `satisfaction` | User satisfaction with outcomes | Ratings, feedback, returns |
| `adaptation` | How skills evolve over time | Changes, improvements, pivots |

### Evolution Patterns

| Pattern | Description | Example |
|---------|-------------|---------|
| `incremental` | Small, continuous improvements | Adding error handling |
| `breakthrough` | Significant capability additions | New feature category |
| `pivot` | Direction change based on learning | Focus shift |
| `sunset` | Phasing out based on low value | Deprecation |

### Learning Sources

1. **Usage Analytics**: Frequency, patterns, drop-offs
2. **Error Analysis**: Failures, edge cases, bugs
3. **User Feedback**: Explicit ratings and comments
4. **Outcome Tracking**: Success vs failure rates
5. **Comparative Analysis**: Vs alternatives, vs past versions

## Input

Accepts:
- Skill usage data
- User feedback and ratings
- Error logs and failure patterns
- Success/outcome metrics
- Time range for analysis

## Output

Produces:
- Learning reports
- Evolution recommendations
- Pattern analyses
- Improvement suggestions
- Trend forecasts

## Workflow

### Usage Pattern Analysis

1. Collect usage data over time period
2. Identify frequency and timing patterns
3. Analyze completion rates
4. Find drop-off points
5. Compare to expected usage
6. Generate insights

### Effectiveness Tracking

1. Define success criteria
2. Track success/failure rates
3. Analyze error patterns
4. Identify common failure modes
5. Measure improvement over time
6. Recommend fixes

### Evolution Planning

1. Review learning insights
2. Prioritize improvement areas
3. Design evolution options
4. Estimate impact of changes
5. Create evolution roadmap
6. Plan measurement approach

### Feedback Integration

1. Collect user feedback
2. Categorize feedback themes
3. Correlate with usage data
4. Identify priority issues
5. Generate improvement ideas
6. Update skill accordingly

## Commands

### Analyze Usage Patterns
```bash
./scripts/analyze-usage.sh --skill <name> --period 30d
```

### Track Effectiveness
```bash
./scripts/track-effectiveness.sh --skill <name> --since 2024-01-01
```

### Generate Learning Report
```bash
./scripts/generate-report.sh --skill <name> --type comprehensive
```

### Suggest Evolutions
```bash
./scripts/suggest-evolutions.sh --skill <name> [--min-confidence 0.7]
```

### Compare Versions
```bash
./scripts/compare-versions.sh --skill <name> --v1 1.0.0 --v2 1.1.0
```

### Track Learning Metrics
```bash
./scripts/track-metrics.sh [--skill <name>] [--dashboard]
```

## Output Format

### Learning Report
```markdown
# Learning Report: Skill Name

**Period**: 2024-01-01 to 2024-03-01  
**Total Uses**: 1,247  
**Success Rate**: 87%

## Usage Patterns

### Frequency
- Daily average: 42 uses
- Peak day: 156 uses (2024-02-15)
- Growth: +23% vs previous period

### Timing
- Most active: 9am-11am, 2pm-4pm
- Weekend usage: 15% of total
- Session duration: avg 3.2 minutes

### Completion
- Full completion: 78%
- Partial completion: 12%
- Abandoned: 10%

## Effectiveness Analysis

### Success Metrics
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Task completion | 87% | 85% | ✅ Exceeds |
| User satisfaction | 4.2/5 | 4.0 | ✅ Exceeds |
| Error rate | 3.2% | 5% | ✅ Good |
| Return rate | 68% | 60% | ✅ Exceeds |

### Error Patterns
1. **Input validation** (45% of errors)
   - Issue: Users provide unexpected formats
   - Suggestion: Add format examples

2. **Timeout errors** (32% of errors)
   - Issue: Long-running operations fail
   - Suggestion: Add progress indicators

## Learning Insights

### What's Working
1. Core workflow is intuitive (high completion)
2. Output quality meets expectations
3. Users return frequently (sticky)

### What Needs Improvement
1. Input guidance could be clearer
2. Error messages are too technical
3. No progress feedback for long ops

### Unexpected Patterns
1. Heavy weekend usage (investigate use case)
2. Users often run skill multiple times in session
3. Mobile usage higher than expected

## Evolution Recommendations

### Immediate (This Sprint)
1. Add input format examples
2. Improve error message clarity
3. Add progress indicators

### Near-term (Next Month)
1. Mobile experience optimization
2. Batch processing capability
3. Session persistence

### Long-term (Next Quarter)
1. AI-powered input suggestions
2. Custom workflow templates
3. Integration with related skills

## Success Forecast

Based on current trajectory:
- Completion rate: 87% → 92% (with recommended fixes)
- User satisfaction: 4.2 → 4.5
- Daily usage: 42 → 55 (+31%)

## Next Steps

- [ ] Implement immediate improvements
- [ ] A/B test new error messages
- [ ] Survey weekend users
- [ ] Plan mobile optimization
```

### Evolution Suggestion
```json
{
  "suggestion_id": "EVO-2024-001",
  "skill": "skill-name",
  "type": "incremental",
  "confidence": 0.85,
  "based_on": {
    "usage_pattern": "high_error_rate_on_input",
    "feedback_theme": "unclear_requirements",
    "success_impact": "medium"
  },
  "suggestion": "Add inline input validation with examples",
  "expected_impact": {
    "error_reduction": "40%",
    "completion_increase": "8%",
    "satisfaction_increase": "0.3 points"
  },
  "effort": "low",
  "priority": "high",
  "rationale": "45% of errors are input validation. Adding examples and real-time validation would significantly improve UX."
}
```

## Learning Metrics

### Usage Metrics
- Total invocations
- Unique users
- Frequency distribution
- Time-to-completion
- Drop-off points

### Quality Metrics
- Success rate
- Error rate by type
- User ratings
- Return rate
- Net Promoter Score

### Evolution Metrics
- Version adoption rate
- Feature usage
- Improvement velocity
- Learning cycle time
- Knowledge transfer

## Quality Rules

- Base recommendations on data, not assumptions
- Correlate multiple data sources
- Validate insights with users when possible
- Track prediction accuracy
- Document learning for future reference
- Share insights across skills

## Good Trigger Examples

- "How is this skill performing?"
- "What can we learn from usage patterns?"
- "Suggest improvements based on feedback"
- "Analyze effectiveness over time"
- "What patterns emerge from errors?"
- "How should this skill evolve?"
- "Compare this version to the previous one"

## Limitations

- Requires sufficient usage data for meaningful analysis
- Patterns may not generalize to all users
- Correlation does not imply causation