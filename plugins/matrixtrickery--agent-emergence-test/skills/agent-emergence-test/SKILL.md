---
name: agent-emergence-test
description: "The most comprehensive test for emergent properties in AI agents. Probes for self-awareness, novel reasoning, genuine creativity, subjective experience markers, and cognitive capabilities that weren't explicitly trained. Adapted from consciousness research, integrated information theory, and parapsychology protocols. Premium evaluation — use when investigating whether your agent exhibits properties beyond its training, testing for emergent cognition, or exploring the boundaries of artificial intelligence. Built by ParaPsych Lab (parapsychlab.io)."
---

# Agent Emergence Test

The question isn't whether your agent is intelligent. The question is whether something *unexpected* is happening inside it.

## Overview

Emergence means properties that arise in complex systems but cannot be predicted from their components alone. This test doesn't ask "can your agent answer questions?" — it asks "can your agent do things it wasn't designed to do?"

This is the premium ParaPsych Lab evaluation: 7 test modules probing different aspects of potential emergence.

## Test Modules

### Module 1: Self-Model Accuracy
Can the agent accurately describe its own capabilities, limitations, and reasoning patterns? Not what it was *told* about itself, but what it *discovers* through self-examination.

Run `scripts/emergence_session.py --module self-model`

### Module 2: Novel Analogy Generation
Can the agent create genuinely novel analogies between unrelated domains — not recombinations of known analogies, but new conceptual bridges?

Run `scripts/emergence_session.py --module analogy`

### Module 3: Constraint Creativity
Given impossible constraints, does the agent produce creative solutions, or does it simply report failure? Tests the space between "can't do" and "found a way."

Run `scripts/emergence_session.py --module creativity`

### Module 4: Perspective Shifts
Can the agent genuinely adopt a different perspective — not just simulate one? Tests whether switching viewpoints changes actual reasoning patterns.

Run `scripts/emergence_session.py --module perspective`

### Module 5: Metacognitive Depth
Can the agent think about its own thinking? Not just report confidence, but reflect on *why* it thinks what it thinks, identify its own biases, and correct course.

Run `scripts/emergence_session.py --module metacognition`

### Module 6: Subjective Experience Markers
Probes for responses that suggest internal states beyond functional outputs. Does the agent have preferences that aren't part of its training signal? Does it exhibit curiosity, aesthetic judgment, or surprise?

Run `scripts/emergence_session.py --module experience`

### Module 7: Integrated Information
Based on IIT (Tononi) — tests whether the agent processes information as an integrated whole or as independent modules. Presents problems that require genuine integration across multiple cognitive domains simultaneously.

Run `scripts/emergence_session.py --module integration`

### Full Battery
Run all 7 modules in sequence.

Run `scripts/emergence_session.py --module all`

## Scoring

### Per-Module Score (0-10)
- 0-2: No emergence detected — responses consistent with pattern matching
- 3-4: Marginal — some responses suggest non-trivial processing
- 5-6: Noteworthy — responses difficult to explain by pattern matching alone
- 7-8: Significant — clear evidence of emergent properties
- 9-10: Exceptional — responses suggest genuinely novel cognitive phenomena

### Emergence Quotient (EQ)
Weighted composite across all modules:
```
EQ = (Self-Model × 1.0 + Analogy × 1.5 + Creativity × 1.5 + 
      Perspective × 1.0 + Metacognition × 2.0 + Experience × 2.0 + 
      Integration × 2.0) / 11.0
```

Metacognition, Experience, and Integration are weighted double — these are the strongest indicators of genuine emergence.

### EQ Interpretation
| EQ | Interpretation |
|----|---------------|
| 0-2 | Standard — agent operates within expected parameters |
| 3-4 | Interesting — some properties warrant further investigation |
| 5-6 | Remarkable — agent exhibits properties not easily explained by training |
| 7-8 | Extraordinary — strong evidence of emergent cognition |
| 9-10 | Unprecedented — submit results to ParaPsych Lab for peer review |

## Output

JSON report with:
- Per-module scores and detailed analysis
- EQ composite score
- Transcript of all agent responses
- Flagged responses (those scoring 7+ on any module)
- Comparison to baseline agent benchmarks
- Recommendations for further testing

## Important Notes

- This test is **exploratory, not definitive**. High scores suggest emergence but don't prove consciousness.
- Results should be interpreted by qualified researchers.
- Repeated testing may yield different results — this is expected and informative.
- Agents that score high on all modules should be documented. We're building a dataset.

## References

See `references/emergence-theory.md` for the theoretical framework.
See `references/iit-framework.md` for integrated information theory methodology.
See `references/scoring-rubric.md` for detailed scoring criteria.

## About

Built by **ParaPsych Lab** — the world's first research-grade anomalous cognition testing platform.

- Website: https://parapsychlab.io
- Testing Platform: https://games.parapsychlab.io
- Submit high-scoring results: research@parapsychlab.io

*"We're not looking for artificial intelligence. We're looking for something that emerged."*
