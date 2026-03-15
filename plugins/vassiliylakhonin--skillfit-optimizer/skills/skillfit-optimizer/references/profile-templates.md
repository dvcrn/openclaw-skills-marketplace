# Profile Templates

## Minimal

- 2-3 skills max
- Core capability only
- Lowest setup friction

## Balanced

- 4-6 skills
- One primary path per critical capability
- Default for most users

## Maximum

- 7+ skills
- Rich capability coverage with explicit fallback paths
- Use only when user accepts higher complexity

## Stack Score Rubric (0-100)

- Coverage: 0-30
- Reliability: 0-30
- Setup Friction: 0-20 (inverse)
- Overlap Discipline: 0-20 (inverse penalty)

## Deterministic Formula

`stack_score = coverage + reliability + setup_friction_inverse + overlap_inverse`

Where:
- `coverage` and `reliability` are assigned from observed fit and checker evidence.
- `setup_friction_inverse = max(0, 20 - setup_friction_penalty)`
- `overlap_inverse = max(0, 20 - overlap_penalty)`

## Penalty Guardrails

- Never double-count overlap across multiple components.
- Cap each penalty channel independently.
- When uncertain, bias toward conservative score and explicit mitigation.
