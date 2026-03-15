---
name: agent-evals-lab
description: "Evaluate agent quality and reliability with practical scorecards: accuracy, relevance, actionability, risk flags, tool-call failures, regression checks, and prioritized fix plans. Use when users ask to audit agent quality, compare prompt/config/model changes, investigate failures, or validate performance after updates."
---

# Agent Evals Lab

## Objective

Turn subjective “agent feels better/worse” into measurable quality signals and actionable fixes.

## Quickstart (5 minutes)

```bash
python3 scripts/eval_score.py \
  --input references/eval-cases.sample.json \
  --risk medium \
  --strict \
  --out /tmp/evals_report.json
```

Expected output: deterministic scorecard with Go/Conditional Go/No-Go verdict, gate reasons, and by-task deltas.

## Use Cases

- Audit current agent quality before production rollout
- Compare baseline vs changed prompt/config/toolchain
- Catch regressions after updates
- Prioritize highest-impact fixes for next sprint

Typical trigger phrases:
- "evaluate this agent" / "audit agent quality"
- "did the last prompt change improve results?"
- "compare model A vs model B"
- "why is this workflow failing?"
- "run regression checks after update"
- "is this ready for production?"

## Inputs

Collect or infer:
- Agent purpose and target tasks
- 10-30 representative test cases (prompt + expected outcome)
- Constraints (latency/cost/risk tolerance)
- Environment notes (models/tools/channels)

If test cases are missing, generate a minimal starter set and label as synthetic.

## Evaluation Dimensions (required)

Score each case on:
1. Correctness
2. Relevance
3. Actionability
4. Risk flags (safety, compliance, irreversible-action risk)
5. Tool reliability (wrong tool, failed execution, silent fallback)

Use 1-5 scale + short evidence note per dimension.

## Execution Workflow

1. Build evaluation set
- Use real cases first, then synthetic gaps.
- Tag each case by task type and risk level.

2. Run baseline evaluation (deterministic)
- Capture outputs + tool behavior.
- Score all required dimensions.
- Run `scripts/eval_score.py --input <cases.json> --risk <low|medium|high> --strict`.

3. Identify failure clusters
- Factual errors
- Reasoning gaps
- Tool-call failure patterns
- Over/under-asking clarifications
- Hallucinated confidence

4. Propose fixes
- Prompt/process/tool changes
- Rank by expected impact vs effort

5. Re-run focused regression set
- Validate top fixes on high-risk/high-frequency cases

## Deterministic Gates

- Hard gate: high-risk workflows cannot be Go if critical minimum score < threshold.
- Hard gate: tool reliability average below threshold => no Go.
- Hard gate: synthetic-only evidence in high-risk mode => no Go.
- Strict mode applies deterministic thresholds before final recommendation.

## Required Output Format

1. Executive Summary
- Overall score snapshot
- Top strengths
- Top failure modes

2. Scorecard
- Dimension averages
- By task-type breakdown
- By risk-level breakdown
- Deterministic scorer output snapshot

3. Failure Map
- Cluster name
- Frequency
- User impact
- Root-cause hypothesis

4. Top 5 Fixes (prioritized)
- Change
- Expected impact
- Effort (S/M/L)
- Owner
- Validation test
- Exact implementation command(s) where applicable

5. Regression Plan (1-2 weeks)
- Cases to rerun
- Success thresholds
- Rollback trigger

6. Go/No-Go Recommendation
- Go / Conditional Go / No-Go
- Conditions and next checkpoint date

7. Before/After Delta
- overall delta
- critical delta
- tool reliability delta
- by-task delta

## Quality Rules

- Prefer measured evidence over intuition.
- Separate facts, inferences, and recommendations.
- Never claim improvement without before/after evidence.
- For high-risk workflows, require explicit human-in-the-loop checkpoints.
- Include deterministic aggregate evidence before final Go/No-Go when case data is available.

## Reference

- Read `references/eval-templates.md` for reusable case templates and scoring rubrics.
- Read `references/ops-report-template.md` for the release memo format.
