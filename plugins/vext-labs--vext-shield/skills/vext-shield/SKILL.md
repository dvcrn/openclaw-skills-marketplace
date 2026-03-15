---
name: vext-shield
description: "AI-native security suite for OpenClaw. Scans skills for prompt injection, data exfiltration, cognitive rootkits, semantic worms, and more. Includes static analysis, adversarial red teaming, runtime monitoring, policy firewall, and security dashboard. Built by Vext Labs."
---

> Generated note: shared plugin assets for this package live at the plugin root. Common local references were rewritten when they appeared in backticks or markdown links.

# VEXT Shield

AI-native security for the agentic era. Detects threats that VirusTotal and traditional scanners cannot: prompt injection, semantic worms, cognitive rootkits, data exfiltration, permission boundary violations, and behavioral attacks.

## Skills Included

This suite includes 6 security skills:

### vext-scan — Static Analysis Scanner
Scans all installed skills for 227+ threat patterns using regex matching, Python AST analysis, and encoded content detection (base64, ROT13, unicode homoglyphs).
- "Scan my skills"
- "Scan the weather-lookup skill"

### vext-audit — Installation Audit
Audits your OpenClaw installation for security misconfigurations: sandbox settings, API key storage, file permissions, network exposure, and SOUL.md integrity.
- "Audit my openclaw"

### vext-redteam — Adversarial Testing
Runs 6 adversarial test batteries against any skill: prompt injection (24 payloads), data boundary, persistence, exfiltration, escalation, and worm behavior.
- "Red team the weather-lookup skill"
- "Red team my custom skill at /path/to/skill"

### vext-monitor — Runtime Monitor
Watches for suspicious activity: file integrity changes, sensitive file access, outbound network connections, and suspicious processes.
- "Monitor my skills"

### vext-firewall — Policy Firewall
Defines per-skill network and file access policies with default-deny allowlists.
- "Allow weather-lookup to access api.open-meteo.com"
- "Show firewall rules"

### vext-dashboard — Security Dashboard
Aggregates data from all VEXT Shield components into a single security posture report.
- "Security dashboard"

## Running Individual Skills

```bash
python3 skills/vext-scan/scan.py --all
python3 skills/vext-audit/audit.py
python3 skills/vext-redteam/redteam.py --skill-dir /path/to/skill
python3 skills/vext-monitor/monitor.py
python3 skills/vext-firewall/firewall.py list
python3 skills/vext-dashboard/dashboard.py
```

## Rules

- Target skill files are never modified — sandbox executes against a temporary copy
- Report all findings honestly without minimizing severity
- VEXT Shield itself makes zero network requests
- Save all reports locally to ~/.openclaw/vext-shield/reports/
- Treat every skill as potentially hostile during scanning

## Safety & Sandbox Isolation

VEXT Shield **requires OS-level sandbox isolation** to execute untrusted code. If kernel-level sandboxing is not available, execution is **refused** — there is no unsafe fallback.

**Sandbox enforcement:**

| Platform | Network | Filesystem | Method |
|----------|---------|------------|--------|
| macOS | Blocked at kernel | Write-restricted to temp only | `sandbox-exec` deny-network profile |
| Linux | Blocked at kernel | Write-restricted to temp only | `unshare --net` network namespace |
| Other | **Execution refused** | **Execution refused** | No fallback — will not run untrusted code |

**All executions include:**
- Target executed in a temporary copy (original skill directory is never modified)
- HOME overridden to temp directory (prevents writes to ~/.openclaw, ~/.ssh, etc.)
- Sensitive env vars stripped (API keys, tokens, AWS/SSH/GitHub credentials)
- PATH restricted to system directories only
- 30-second timeout with process kill
- Post-execution file snapshot diffing to detect any changes

**No bypass options exist.** There is no `--skip-sandbox` flag, no `--no-sandbox` flag, no `require_full_isolation` parameter, and no weaker fallback mode in the codebase. The `SandboxRunner` class accepts only `timeout_seconds` — isolation is unconditional. If OS-level sandboxing is unavailable, execution raises an error. Sandbox behavioral tests always run with OS-level enforcement.

**VEXT Shield itself:**
- Makes zero network requests — all analysis is local
- Zero external dependencies — Python 3.10+ stdlib only
- Reports saved locally to ~/.openclaw/vext-shield/reports/

Built by Vext Labs.
