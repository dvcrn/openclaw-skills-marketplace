---
name: host-security-audit
description: "Comprehensive security audit and hardening for OpenClaw host machines. Checks firewall, disk encryption, open ports, auto-updates, brew outdated, OpenClaw version, disk usage, Time Machine, suspicious processes, and API key exposure. Use when user asks for a security audit, hardening check, security posture review, or wants to schedule periodic security monitoring. Works on macOS and Linux."
---

# Host Security Audit

Run a comprehensive security audit on the machine hosting OpenClaw. Checks OS-level security, OpenClaw configuration, and common misconfigurations.

## Quick Start

Run the full audit:
```bash
bash scripts/security-audit.sh
```

Run with JSON output:
```bash
bash scripts/security-audit.sh --json
```

## What It Checks

### OS Security
- **Firewall** — macOS Application Firewall or Linux ufw/firewalld
- **Disk encryption** — FileVault (macOS) or LUKS (Linux)
- **Auto-updates** — macOS SoftwareUpdate or unattended-upgrades
- **Open ports** — listening services on all interfaces
- **Suspicious processes** — crypto miners, reverse shells, unexpected listeners

### OpenClaw Security
- **OpenClaw version** — current vs latest available
- **API key exposure** — plaintext keys in config files
- **Gateway bind address** — flags 0.0.0.0 binding (exposed to network)
- **File permissions** — secrets directory permissions

### System Health
- **Disk usage** — warns at 80%, critical at 90%
- **Brew outdated** — packages with available updates (macOS)
- **Time Machine** — backup status and last backup time (macOS)

## Scheduling Monthly Audits

Create an OpenClaw cron job for the 1st Monday of each month at 9 AM:

```
schedule: "0 9 1-7 * 1"
payload: Run a full host security audit. Execute: bash <skill-path>/scripts/security-audit.sh — Report findings with severity levels (CRITICAL/WARNING/OK). Only notify the user if there are CRITICAL or WARNING findings. If everything passes, do nothing (NO_REPLY).
```

## Remediation

The audit reports findings but does not auto-fix. For each finding:
- **CRITICAL** — Act immediately (exposed API keys, no firewall, no encryption)
- **WARNING** — Schedule fix within a week (outdated packages, disk usage)
- **OK** — No action needed

To auto-fix OpenClaw-specific issues:
```bash
openclaw security audit --fix
```
This only tightens OpenClaw defaults and file permissions. It does not modify host firewall, SSH, or OS settings.
