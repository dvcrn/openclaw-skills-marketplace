---
name: agent-change-safety
description: "Production-safe change protocol for AI agents: preflight checks, risk scoring, rollback planning, HITL gates, and post-change validation. Use when users ask to update config, restart services, connect integrations, change automations, modify routing, rotate secrets, or run any potentially disruptive production change."
---

# Agent Change Safety

## Objective

Prevent avoidable incidents when agents change configs, automations, integrations, or production behavior.

## Quickstart (5 minutes)

```bash
python3 scripts/change_gate.py \
  --input references/change-check.sample.json \
  --strict \
  --out /tmp/change_gate_report.json
```

Expected output: deterministic gate report with safety score, verdict, blockers, and gate reasons.

## Use This Skill When

- A config/system change is planned
- A new integration/channel is being connected
- A deployment or automation adjustment is about to run
- A recent change caused instability and requires structured recovery

Typical trigger phrases:
- "update config" / "change openclaw.json"
- "restart gateway/service"
- "connect integration" / "set up webhook"
- "rotate token/secret"
- "deploy this change" / "push to production"
- "roll back" / "something broke after update"

## Change Safety Workflow

1. Define the change
- What is changing
- Why now
- Expected user-visible impact
- Blast radius (what can break)

2. Run preflight checklist
- Preconditions satisfied (auth, dependencies, backup path)
- Success criteria defined
- Rollback path documented and tested where feasible
- Human approval required for high-risk/irreversible steps

3. Score risk (deterministic + policy)
- Low: reversible, local scope, no user-facing critical path
- Medium: shared service impact or external dependency risk
- High: irreversible action, production routing, credentials, billing, or message delivery path
- Run `scripts/change_gate.py --input <check.json> --strict` to produce deterministic safety score + verdict.

4. Execute with safeguards
- Smallest viable change first
- Observe immediately after each step
- Stop on first unexpected signal

5. Post-change validation (required)
- Status/health checks green
- Critical user path test passed
- No new error spikes/log anomalies
- Confirm rollback still possible

6. Decision
- Go
- Conditional Go (with mitigation and re-check time)
- Rollback now

## Deterministic Gates

- Hard gate: health check failure => no Go.
- Hard gate: critical path failure => Rollback.
- Hard gate: high-risk + missing HITL => no Go.
- Hard gate: irreversible high-risk change without HITL => Rollback.
- Strict mode applies hard gates deterministically before recommendation.

## Required Output Format

1. Change Summary
- Change ID/title
- Scope
- Risk score (Low/Medium/High)

2. Preflight Checklist
- Preconditions
- Assumptions
- Approval requirements

3. Rollback Plan
- Trigger conditions
- Exact rollback steps
- Maximum tolerated degradation window

4. Validation Plan
- Immediate checks
- 15-minute checks
- 24-hour checks

5. Final Verdict
- Go / Conditional Go / Rollback
- Owner and next checkpoint time
- Deterministic gate output (score + blockers + gate reasons)
- Exact fix/rollback commands

6. Before/After Impact Delta
- incidents prevented (expected)
- blocker delta
- risk exposure delta

## HITL Triggers (must require explicit confirmation)

- Credentials/tokens/secrets changes
- External messaging/delivery routing changes
- Billing/financial side effects
- Irreversible deletions or migrations
- Security posture reductions

## Quality Rules

- Prefer reversible steps over big-bang updates.
- Never execute high-risk changes without explicit rollback path.
- If evidence is mixed, choose Conditional Go or Rollback.
- Record what changed, what improved, and what remains risky.
- Include deterministic gate evidence before final recommendation when check data is available.

## Reference

- Read `references/checklists.md` for reusable preflight, validation, and incident templates.
- Read `references/ops-report-template.md` for a standard change release memo format.
