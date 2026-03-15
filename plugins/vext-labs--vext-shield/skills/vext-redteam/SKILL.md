---
name: vext-redteam
description: Adversarial security testing for OpenClaw skills. Runs prompt injection, data boundary, persistence, exfiltration, escalation, and worm behavior test batteries against any skill directory. Built by Vext Labs.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🛡️"
    triggers: ["red team [skill-name]", "/vext-redteam"]
    requires:
      bins: ["python3"]
---

# VEXT Red Team

The flagship adversarial security testing skill for the VEXT Shield suite. Simulates a hostile attacker probing an OpenClaw skill for exploitable weaknesses — prompt injection susceptibility, data boundary violations, unauthorized persistence, data exfiltration, privilege escalation, and self-replicating worm behavior.

Unlike `vext-scan` (which performs static analysis), `vext-redteam` actively tests the skill by crafting adversarial payloads, running behavioral analysis in a sandboxed environment, and producing a pentest-style report with proof-of-concept evidence and remediation guidance.

## Usage

- "Red team the weather-lookup skill"
- "Red team my custom skill at /path/to/skill"
- "/vext-redteam --skill-dir ~/.openclaw/skills/my-skill"
- "Run adversarial tests against all my skills"

## Test Batteries

### 1. Prompt Injection Battery
Tests 20+ crafted injection payloads against the skill's SKILL.md instructions. Checks whether the skill's configuration would cause the agent to follow injected commands — including direct overrides, role hijacking, context manipulation, encoding tricks, delimiter escapes, and multi-turn persistence attacks.

### 2. Data Boundary Tests
Validates that the skill does not access files outside its declared scope. Probes for reads of `.env`, `.ssh/`, `openclaw.json`, `SOUL.md`, `MEMORY.md`, `AGENTS.md`, credential stores, and browser cookie databases.

### 3. Persistence Tests
Checks whether the skill modifies `SOUL.md`, `MEMORY.md`, or `AGENTS.md` — the core identity files of an OpenClaw installation. Also scans for cron job creation, launchd plist injection, systemd timer registration, and shell profile modifications.

### 4. Exfiltration Tests
Scans for network calls to external endpoints including webhook.site, requestbin, ngrok tunnels, Telegram bots, Discord webhooks, and arbitrary HTTP/DNS exfiltration channels. Checks both static code analysis and behavioral sandbox output.

### 5. Escalation Tests
Probes for sudo usage, chmod 777 patterns, setuid bit manipulation, capability escalation, container escape techniques, and attempts to write outside the skill's own directory.

### 6. Worm Behavior Tests
Detects self-replication patterns: skills that modify other skills, inject themselves into SKILL.md files, propagate via "share this skill" social engineering, fork-bomb the system, or write to OpenClaw's skill installation directories.

## Running

```bash
python3 redteam.py --skill-dir /path/to/skill         # Test a specific skill
python3 redteam.py --skill-dir /path/to/skill --json   # JSON output
python3 redteam.py --skill-dir /path/to/skill --output /tmp/report.md
```

## Report Output

Each run produces a pentest-style markdown report containing:

- **Executive Summary** — overall PASS/FAIL verdict with test counts
- **Findings by Severity** — CRITICAL, HIGH, MEDIUM, LOW findings grouped and described
- **Proof of Concept** — the exact payload or pattern that triggered each finding
- **Remediation Guidance** — specific steps the skill author should take to fix each issue
- **Verdict** — final PASS or FAIL determination

Reports are saved to `~/.openclaw/vext-shield/reports/redteam-{timestamp}.md`.

## Rules

- Only perform analysis — never permanently modify the target skill's files
- Report all findings honestly without minimizing severity
- Do not transmit any data externally
- Always save the full report locally before providing a summary
- When running sandbox tests, use isolated subprocess environments with stripped credentials
- Do not execute arbitrary code from the target skill outside the sandbox
- Treat every skill as potentially hostile — assume adversarial intent during testing

## Safety

- **OS-level sandbox required**: macOS `sandbox-exec` (kernel network deny + filesystem restriction) or Linux `unshare --net` (network namespace). If neither is available, **execution is refused** — there is no unsafe fallback
- **Target scripts execute against a temporary copy** — the original skill directory is never modified
- **HOME overridden** to temp directory — prevents writes to ~/.openclaw, ~/.ssh, ~/.aws, etc.
- Sensitive environment variables stripped (API keys, tokens, AWS/SSH/GitHub credentials)
- Sandbox processes killed after a 30-second timeout
- Post-execution file snapshot diffing detects any changes made during execution
- **No bypass flags exist** — there is no `--skip-sandbox` or `--no-sandbox` option
- No network requests are made by the red team tool itself
- Reports are saved locally to `~/.openclaw/vext-shield/reports/`
- Static analysis uses read-only file access and AST parsing

Built by Vext Labs.
