# Checklists

## Preflight (before change)

- [ ] Scope and objective written in 1-2 lines
- [ ] Dependencies and auth verified
- [ ] Backup/export snapshot completed
- [ ] Success criteria measurable
- [ ] Rollback steps documented
- [ ] HITL approval captured if high risk

## Immediate Validation (0-5 min)

- [ ] Service status/health green
- [ ] Core user path works
- [ ] No critical errors in logs
- [ ] No unexpected permission failures

## Short-Horizon Validation (15-60 min)

- [ ] Error rate stable
- [ ] Latency/cost within threshold
- [ ] Notifications/messages deliver correctly
- [ ] No user-visible regressions

## Recommended Gate Inputs

```json
{
  "risk": "medium",
  "preflight_ok": true,
  "rollback_ready": true,
  "health_ok": true,
  "critical_path_ok": true,
  "hitl_confirmed": true,
  "irreversible": false,
  "messaging_path_changed": false,
  "credentials_changed": false,
  "billing_side_effects": false,
  "security_posture_reduced": false
}
```

## Deterministic Gate Interpretation

- Go: no blockers, safety score high, all hard gates pass.
- Conditional Go: blockers exist but no rollback hard-trigger.
- Rollback: any hard-trigger violation (critical path failure, severe high-risk/HITL violation).

## Incident Note Template

- Change:
- Time:
- Symptoms:
- Impact:
- Root-cause hypothesis:
- Mitigation applied:
- Rollback executed? (Y/N):
- Prevention for next change:
