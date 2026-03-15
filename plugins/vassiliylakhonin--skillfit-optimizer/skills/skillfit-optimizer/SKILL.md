---
name: skillfit-optimizer
description: "Build and optimize a minimal working skill stack for a user goal: recommend profiles, install the best-fit stack, run deterministic smoke checks, remove overlap, score stack quality, persist before/after evidence, and produce a fix-first rollout plan. Use when users ask what skills to install, how to avoid duplicate/conflicting skills, how to reduce setup friction, or how to improve skill ROI/time-to-value."
---

# SkillFit Optimizer

## Objective

Reduce time-to-value from skill discovery by turning goals into a tested, minimal, high-ROI skill stack with measurable before/after evidence.

## Typical Trigger Phrases

- "what skills should I install for X"
- "optimize my current skill stack"
- "remove duplicate/conflicting skills"
- "which skill setup gives best ROI"

## Workflow

1. Analyze goal and context
- Parse user objective, constraints, and required outputs.
- Identify must-have capabilities and optional enhancements.

2. Propose 3 stack profiles
- Minimal (lowest complexity)
- Balanced (default)
- Maximum (capability-rich)

3. Install selected profile
- Prefer fewer, higher-signal skills.
- Avoid overlapping tools unless explicit fallback needed.

4. Smoke-check stack (deterministic)
- Run `scripts/stack_check.py --bins <list> --history-path .skillfit/history.json --report-json .skillfit/latest-check.json`.
- Validate one realistic happy-path task.
- Enforce gate: if `availability_score < 80`, do not claim success; return explicit fix commands first.

5. Prune overlap
- Remove redundant skills and conflicting patterns.
- Keep one primary path per capability.

6. Score stack quality (0-100)
- Coverage (0-30)
- Reliability (0-30)
- Setup friction (0-20, inverse)
- Overlap discipline (0-20, inverse penalty)

7. Persist + recurrence loop
- Persist each run in `.skillfit/history.json`.
- Track recurring issues (same missing bins / same overlap class).
- If a blocker recurs 3+ times in 30 days, elevate as high-priority remediation.

8. Promotion rule
- If a repeated pattern becomes generally useful, promote concise rule(s) to:
  - `AGENTS.md` for workflow safeguards
  - `TOOLS.md` for local tool gotchas
  - `SOUL.md` for behavioral defaults (when applicable)

## Required Output Structure

1. Goal Fit Summary
2. Recommended Profile (Minimal / Balanced / Maximum)
3. Installed Stack
4. Smoke Check Results (include deterministic checker output)
5. Pruned/Removed Items
6. Stack Score + Rationale
7. Exact Fix Commands (copy/paste)
8. Next 3 Improvements
9. Before/After Delta (availability, missing bins, overlap)

## Quality Rules

- Prefer execution certainty over skill quantity.
- Do not keep duplicate skills with same core function unless user requests redundancy.
- Flag unresolved setup blockers explicitly.
- If smoke check fails, return fix-plan before claiming success.
- Always provide deterministic evidence (checker output + missing bins list + delta vs previous run).

## Reference

- Read `references/profile-templates.md` for profile patterns and scoring details.
- Read `references/ops-report-template.md` for report format and gate language.
