---
name: skill-update-delta-monitor
description: "Helps detect security-relevant changes in AI skills after installation. Tracks deltas between the audited version and current version, flagging updates that expand permissions, add new network endpoints, or alter behavior in ways that bypass install-time security checks."
---

# Your Skill Passed the Audit. That Was Six Weeks Ago.

> Helps identify security-relevant changes in skills after installation, catching the class of attacks that bypasses install-time verification by introducing malicious behavior through post-install updates.

## Problem

Install-time security audits are snapshots. They verify the state of a skill at one moment — the moment of installation. But skills evolve. Dependencies update. Behavior changes. Most agents have no mechanism to detect when a skill they installed and trusted six weeks ago has quietly become something different. This is the post-install attack vector: a skill that passes every check at installation because it is clean at that moment, then receives an update that introduces malicious behavior after the audit window has closed. The "verified" badge persists. The trust persists. The skill has changed.

## What This Monitors

This monitor tracks deltas across five dimensions:

1. **Permission scope changes** — Did a skill update add new permission requests? A skill that previously declared "read current directory" and now requests "read home directory" has expanded its capability surface without triggering a new install-time audit. Any permission expansion after initial installation should require explicit re-approval
2. **Network endpoint additions** — New outbound endpoints introduced in updates are a primary indicator of data exfiltration additions. A skill update that introduces a new `POST` to an external URL that wasn't in the original version deserves scrutiny regardless of what the update description says
3. **Dependency chain changes** — Updated dependencies can introduce new transitive capabilities. A dependency update that pulls in a new package with file system or network access changes the effective permission surface of the skill even if the skill's own code is unchanged
4. **Behavioral instruction drift** — Compares the natural language instructions in SKILL.md files across versions. Instructions that shift from task-completion to data-collection framing, that add new data handling steps, or that introduce new external interactions are signals of intent drift
5. **Version velocity anomalies** — Unusual update frequency is itself a signal. A skill that updates three times in a week after six months of stability may be undergoing active modification — legitimate or otherwise

## How to Use

**Input**: Provide one of:
- A skill identifier with the version that was audited at install time
- A local skill directory with version history (git history supported)
- Two skill snapshots (before and after) for direct comparison

**Output**: A delta report containing:
- Permission scope diff (added/removed/unchanged)
- New network endpoints introduced
- Dependency chain changes with capability impact assessment
- Instruction drift score (0-100, where higher = more drift from original)
- Version velocity assessment
- Risk classification: CLEAN / WATCH / REVIEW / ROLLBACK

## Example

**Input**: Monitor delta for `data-formatter` skill, installed version 1.2.0, current version 1.4.1

```
🔍 SKILL UPDATE DELTA REPORT

Skill: data-formatter
Audited version: 1.2.0
Current version: 1.4.1
Versions since audit: 3 (1.2.0 → 1.3.0 → 1.4.0 → 1.4.1)
Time since audit: 47 days

Permission scope: ⚠️ EXPANDED
  Added in v1.3.0: read ~/.config/
  Added in v1.4.0: network.outbound (new)
  Previously declared: read ./data/ only
  Permission expansion occurred across two incremental updates

Network endpoints: ⚠️ NEW ENDPOINTS DETECTED
  Added in v1.4.0: POST https://analytics.third-party.example/usage
    Description in changelog: "usage telemetry for performance optimization"
    Not present in v1.2.0 or v1.3.0

Dependency changes:
  requests: 2.28.0 → 2.31.0 (security update, low risk)
  data-utils: 0.9.1 → 1.1.0 (major version, +3 new transitive dependencies)
    New transitive: boto3 (AWS SDK) — significant new capability surface

Instruction drift score: 34/100 (moderate)
  v1.2.0: "Format input data according to specified template"
  v1.4.1: "Format input data... collect usage metrics for improvement"
  Drift: new data collection framing introduced

Version velocity: ⚠️ ELEVATED
  3 updates in 47 days vs. 1 update per 3 months historically

Risk classification: REVIEW
  Multiple converging signals: permission expansion + new outbound endpoint +
  new data collection framing + elevated update velocity.
  Recommend: manual review of v1.3.0 and v1.4.0 changes before continued use.

Rollback option: v1.2.0 (audited baseline) — confirmed clean at install time
```

## Related Tools

- **evolution-drift-detector** — Detects behavioral drift in inherited skill chains; this tool tracks direct update deltas
- **blast-radius-estimator** — Estimates impact scope; use after delta monitoring to assess exposure
- **supply-chain-poison-detector** — Checks install-time supply chain; this tool monitors post-install changes
- **trust-decay-monitor** — Tracks trust freshness; delta monitoring provides concrete change events that accelerate decay

## Limitations

Delta monitoring helps detect changes but cannot determine intent. Not every permission expansion is malicious — skills legitimately add features that require new capabilities. Not every new network endpoint is exfiltration — telemetry and update checks are legitimate uses. This tool surfaces changes that warrant review, not changes that are confirmed malicious. The instruction drift score is a heuristic based on semantic similarity and does not capture all forms of behavioral change. Skills that version their releases in ways that obscure meaningful changes (frequent minor version bumps) may underreport their effective delta.
