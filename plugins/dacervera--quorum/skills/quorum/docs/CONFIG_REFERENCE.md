# Configuration Reference

## Depth Profiles

| Profile | Critics | Fix Rounds | Time | Use Case |
|---------|---------|------------|------|----------|
| **quick** | 3 (Correctness, Security, Completeness) | 0 | 5–15 min | Iteration, drafts |
| **standard** | 6 (+ Architecture, Delegation, Style) | 1 on CRITICAL | 15–30 min | Pre-merge, reviews |
| **thorough** | All 9 + external validator | ≤2 on CRITICAL/HIGH | 45–90 min | Critical decisions, production |

## Model Tiers

Quorum uses a two-tier model architecture. Assign your models based on role requirements:

| Role | Tier | Reasoning |
|------|------|-----------|
| Supervisor | Tier 1 | Orchestration, judgment |
| Security Critic | Tier 1 | High-stakes assessment |
| Delegation Critic | Tier 1 | Nuanced contract evaluation |
| Aggregator | Tier 1 | Synthesis, conflict resolution |
| Fixer | Tier 1 | Complex remediation |
| Correctness Critic | Tier 2 | Pattern matching, verification |
| Architecture Critic | Tier 2 | Structural analysis |
| Completeness Critic | Tier 2 | Coverage checking |
| Style Critic | Tier 2 | Convention enforcement |
| Tester | Tier 2 | Tool execution, grep, schema parsing |

**Examples:** Tier 1 = Claude Opus, GPT-4, Gemini Ultra. Tier 2 = Claude Sonnet, GPT-4o-mini, Gemini Flash.

## Rubric Format

Rubrics are JSON files with the following structure:

```json
{
  "name": "your-rubric-name",
  "version": "1.0",
  "domain": "research|code|config|documentation|custom",
  "criteria": [
    {
      "name": "Criterion Name",
      "weight": 0.25,
      "description": "What this criterion evaluates",
      "evidence_type": "web_search|grep|schema_parse|exec|manual",
      "evidence_instruction": "Specific instruction for gathering evidence",
      "severity_levels": {
        "CRITICAL": "Definition of critical failure",
        "HIGH": "Definition of high-severity issue",
        "MODERATE": "Definition of moderate issue",
        "LOW": "Definition of minor issue"
      }
    }
  ]
}
```

**Rules:**
- Weights must sum to 1.0
- Every criterion must specify an `evidence_type`
- `evidence_instruction` should be concrete and tool-executable
- See `examples/rubrics/` for working examples

## Verdict Taxonomy

| Verdict | Meaning |
|---------|---------|
| **PASS** | No CRITICAL or HIGH issues; confidence ≥ 0.8 |
| **PASS_WITH_NOTES** | No CRITICAL issues; ≤ 2 HIGH issues with mitigations; confidence ≥ 0.6 |
| **REVISE** | CRITICAL issues found but fixable; or > 2 HIGH issues |
| **REJECT** | Fundamental architectural or security issues; requires redesign |

## Known Issues / Learning Memory

The `known_issues.json` file accumulates failure patterns across validation runs:

```json
{
  "pattern_id": "KI-001",
  "description": "Shell injection via unquoted variable expansion",
  "domain": "security",
  "severity": "CRITICAL",
  "frequency": 3,
  "first_seen": "2026-02-15",
  "last_seen": "2026-02-22",
  "mandatory": true,
  "meta_lesson": "Always grep for unquoted $VAR in exec/spawn patterns"
}
```

Patterns with frequency ≥ 3 auto-promote to `mandatory: true` and become required checks in all future runs.


---

> ⚖️ **LICENSE** — Not part of the operational specification above.
> This file is part of [Quorum](https://github.com/SharedIntellect/quorum).
> Copyright 2026 SharedIntellect. MIT License.
> See [LICENSE](https://github.com/SharedIntellect/quorum/blob/main/LICENSE) for full terms.
