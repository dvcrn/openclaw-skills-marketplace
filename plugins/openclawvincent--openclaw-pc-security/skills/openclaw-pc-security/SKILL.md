---
name: openclaw-pc-security
description: "OpenClaw personal-PC security self-check (Windows posture + local audit + optional target probing). Use this skill whenever the user needs to check Windows security posture, detect outdated OpenClaw/npm versions, or investigate security risks like token leaks and exposed ports."
---

# OpenClaw PC Security (Windows)

## Description

Security self-check and risk alerting for personal computers running OpenClaw, focusing on:
- Windows posture (version, last security update date, support status, patch lag)
- OpenClaw/npm outdated warnings
- Optional port probing and weak-credential/exposure checks for local/LAN OpenClaw targets (authorized use only)

Currently the Windows posture path is the primary completed scope; other OS and more checks can be added later.

## When to use

Use this skill when you need to:
- Check whether Windows is out of support or significantly behind patch cadence
- Detect outdated OpenClaw/npm versions that may cause security concerns
- Investigate token/config leaks, exposed ports, and weak-password brute-force risks

## Input
- Local Windows information (version/build, last hotfix date)
- Optional target host/IP and ports for OpenClaw probing

## Output
- Severity-based findings (Info/Medium/High/Critical)
- HTML/JSON report under `openclaw-pc-security/output/`
  - `openclaw-pc-security/output/scan_report.html`
  - `openclaw-pc-security/output/scan_report.json`

## Steps

### 1) Local audit
```bash
python scripts/main.py --audit --npm-view-latest-openclaw --out-dir openclaw-pc-security/output
```

### 2) Scan a target (authorized environments only)
```bash
python scripts/main.py <target-ip> --ports 18789,18790,18792 --out-dir openclaw-pc-security/output
```

## Notes
- **Critical**: The active probing functionality (including port scanning, weak credential testing, and sensitive path exposure checks) is intrusive by design and must ONLY be used in authorized environments where you have explicit permission to test the target systems.
- **DO NOT** use the scanning functionality against any system you do not own or have explicit authorization to test.
- **DO NOT** upload tokens, credentials, or reports (output/) to public repositories.
- Reports are written under `openclaw-pc-security/output/` when using the provided scripts.
- If Windows 10 is detected: consider upgrading to Windows 11; if not eligible, enroll in Windows 10 ESU to continue receiving updates until 2026-10.
- If OpenClaw is outdated: after upgrading, some or all functions may be unavailable; assess carefully.
- After the HTML report is generated, print the report path in the chat for the user's reference. Do NOT upload or send the report file unless the user explicitly requests it and provides a secure destination. Reports may contain sensitive information, so always handle them with caution.