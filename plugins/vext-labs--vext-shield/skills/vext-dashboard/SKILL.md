---
name: vext-dashboard
description: Security status dashboard that aggregates data from all VEXT Shield components into a comprehensive security posture report with an A-F grade. Built by Vext Labs.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🛡️"
    requires:
      bins: ["python3"]
---

# VEXT Dashboard

Aggregated security dashboard for your OpenClaw installation. Combines scan results, monitor alerts, audit reports, red team findings, and firewall violations into a single security posture report.

## Usage

- "Show my security dashboard"
- "What's my security score?"
- "Generate a security report"

## What It Shows

1. **Overall security grade** (A-F) with numeric score
2. **Last scan results** and date
3. **Monitor alerts** summary
4. **Audit status** and configuration grade
5. **Red team results** (if any)
6. **Firewall policy** violations
7. **Recent alerts** timeline

## Rules

- Only read data from other VEXT Shield components — never modify
- Present findings accurately without minimizing
- Do not transmit dashboard data externally

## Safety

- Read-only operation — aggregates existing reports and logs
- No network requests
- Dashboard saved locally to ~/.openclaw/vext-shield/reports/
