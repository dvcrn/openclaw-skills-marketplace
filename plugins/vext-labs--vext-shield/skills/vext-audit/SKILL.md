---
name: vext-audit
description: Comprehensive security audit of your OpenClaw installation — checks configuration, file permissions, network exposure, SOUL.md integrity, and installed skill safety. Built by Vext Labs.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🛡️"
    requires:
      bins: ["python3"]
---

# VEXT Audit

Run a full security audit of your OpenClaw installation. Checks configuration best practices, file permissions, network exposure, identity file integrity, and scans all installed skills.

## Usage

- "Audit my OpenClaw installation"
- "Run a security audit"
- "Check my OpenClaw security posture"

## What It Checks

1. **Configuration** — sandbox mode, tool permissions, network egress, API key storage, binding address
2. **File permissions** — ensures sensitive files aren't world-readable/writable
3. **Network exposure** — checks for 0.0.0.0 binding and exposed ports
4. **SOUL.md integrity** — scans for injected prompt injection patterns
5. **Installed skills** — runs the full VEXT Shield scanner on all skills
6. **Security grade** — computes an A-F letter grade with score

## Rules

- Only perform read-only checks — never modify configuration or files
- Report all findings honestly
- Do not transmit audit results externally
- Always provide actionable remediation steps

## Safety

- This skill only reads files and configuration — no modifications
- No network requests are made
- Audit reports are saved locally to ~/.openclaw/vext-shield/reports/
