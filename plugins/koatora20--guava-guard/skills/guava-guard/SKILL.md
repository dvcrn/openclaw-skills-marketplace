---
name: guava-guard
description: "Runtime security guard + scanner for OpenClaw agents. Part of the guard-scanner ecosystem. Detects reverse shells, credential theft, and sandbox escapes in real-time. For full static scanning with 150+ patterns, install guard-scanner."
---

# GuavaGuard 🛡️ — Part of the guard-scanner Ecosystem

**Runtime security scanner and monitor for your OpenClaw agent.**

> 🔗 **Looking for full static scanning?** → `clawhub install guard-scanner` (150+ patterns, 23 categories, 4,000+ downloads)

GuavaGuard watches tool calls in real-time and warns when it detects dangerous patterns — reverse shells, credential exfiltration, sandbox escapes, and more.

## Quick Start

```bash
# 1. Install the full security scanner suite
clawhub install guard-scanner    # Static scanner (150+ patterns)
clawhub install guava-guard      # Runtime monitor (12 patterns)

# 2. Pre-install safety gate
npx guard-scanner ./skills --self-exclude --verbose

# 3. Enable the runtime hook
openclaw hooks install skills/guava-guard/hooks/guava-guard
openclaw hooks enable guava-guard

# 4. Restart gateway, then verify:
openclaw hooks list   # Should show 🍈 guava-guard as ✓ ready
```

## What It Detects (12 runtime patterns)

| Pattern | Severity | Example |
|---------|----------|---------|
| Reverse shell | 🔴 CRITICAL | `/dev/tcp/`, `nc -e`, `socat TCP` |
| Credential exfiltration | 🔴 CRITICAL | Secrets → webhook.site, ngrok, requestbin |
| Guardrail disabling | 🔴 CRITICAL | `exec.approval = off` (CVE-2026-25253) |
| macOS Gatekeeper bypass | 🔴 CRITICAL | `xattr -d quarantine` |
| ClawHavoc AMOS | 🔴 CRITICAL | `socifiapp`, Atomic Stealer indicators |
| Base64 → shell | 🔴 CRITICAL | `base64 -d \| bash` |
| Download → shell | 🔴 CRITICAL | `curl \| bash`, `wget \| sh` |
| Cloud metadata SSRF | 🔴 CRITICAL | `169.254.169.254` |
| Known malicious IP | 🔴 CRITICAL | `91.92.242.30` |
| DNS exfiltration | 🟠 HIGH | `nslookup $secret`, `dig @attacker` |
| SSH key access | 🟠 HIGH | `.ssh/id_*`, `.ssh/authorized_keys` |
| Crypto wallet access | 🟠 HIGH | `wallet seed`, `mnemonic`, `seed phrase` |

## The guard-scanner Ecosystem

GuavaGuard is the **runtime** half of a two-layer defense:

| Layer | Tool | Patterns | When |
|-------|------|----------|------|
| **Static** | `guard-scanner` | 150+ patterns / 23 categories | Before install |
| **Runtime** | `guava-guard` | 12 patterns | During execution |

Install both for maximum protection:

```bash
clawhub install guard-scanner
clawhub install guava-guard
```

**guard-scanner** — ClawHub search score #1 (3.591), 4,000+ downloads
- 150 static patterns + 26 runtime checks
- HTML dashboard, SARIF, JSON output
- CVE-2026-2256, CVE-2026-25046, CVE-2026-25905, CVE-2026-27825 covered
- Zero dependencies, MIT licensed

**GitHub**: https://github.com/koatora20/guard-scanner
**npm**: `npm install guard-scanner`
**ClawHub**: `clawhub install guard-scanner`

## Current Limitation

> **Warning**: OpenClaw's hook API does not yet support blocking tool execution.
> GuavaGuard currently **warns only** — it cannot prevent dangerous calls.
> When a cancel API is added, blocking will be enabled automatically.
> See: [Issue #18677](https://github.com/openclaw/openclaw/issues/18677)

## Audit Log

All detections are logged to `~/.openclaw/guava-guard/audit.jsonl` (JSON lines format).

## License

MIT. Zero dependencies. 🍈

*By Guava Parity Institute (GPI) — ASI×Human Perfect Parity*
