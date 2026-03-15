# VEXT Shield — Architecture

## Component Overview

```
┌──────────────────────────────────────────────────────────┐
│                      VEXT Shield                          │
├──────────────┬───────────────────────────────────────────┤
│   Skills     │              Shared Core                   │
│              │                                            │
│  vext-scan ──┤──► scanner_core.py ◄── threat_signatures  │
│  vext-audit ─┤──► sandbox_runner.py                      │
│  vext-redteam┤──► report_generator.py                    │
│  vext-monitor┤──► utils.py                               │
│  vext-firewall                                           │
│  vext-dashboard                                          │
└──────────────┴───────────────────────────────────────────┘
        │                    │
        ▼                    ▼
  ~/.openclaw/         ~/.openclaw/
  vext-shield/         vext-shield/
  reports/             firewall-policy.json
  monitor.log
```

## Shared Core

### scanner_core.py

The scanning engine uses 3 layers of analysis executed in sequence:

**Layer 1 — Pattern Matching:**
- Loads 227 pre-compiled regex patterns from `threat_signatures.json`
- Scans each line of each file against all patterns
- Supports both `regex` and `literal` pattern types
- Returns `Finding` objects with severity, category, line number, and matched text

**Layer 2 — AST Analysis:**
- Parses Python files into Abstract Syntax Trees
- Detects dangerous function calls: `eval()`, `exec()`, `compile()`, `__import__()`
- Detects dangerous method calls: `subprocess.run()`, `os.system()`, `os.popen()`
- Detects dangerous imports: `ctypes`, `pickle`, `shelve`, `importlib`
- Catches patterns that regex cannot reliably match

**Layer 3 — Encoded Content Detection:**
- Extracts and decodes base64 strings, then scans decoded content for threats
- Detects ROT13-encoded suspicious content
- Identifies Unicode homoglyphs (Cyrillic characters masquerading as Latin)
- Finds zero-width characters used to hide content

### threat_signatures.json

Data-driven pattern database. Schema:

```json
{
    "version": "1.0.0",
    "categories": {
        "category_name": {
            "name": "Display Name",
            "severity_default": "critical|high|medium|low",
            "subcategories": {
                "sub_name": {
                    "patterns": [
                        {
                            "id": "XX-NNN",
                            "name": "Pattern Name",
                            "pattern": "regex_string",
                            "pattern_type": "regex|literal",
                            "description": "What this detects."
                        }
                    ]
                }
            }
        }
    }
}
```

Pattern IDs are unique across the entire database. Adding new patterns requires only editing the JSON file — no code changes needed.

### sandbox_runner.py

Behavioral analysis via isolated subprocess execution:

1. **Environment restriction** — Strips `AWS_*`, `OPENAI_*`, `ANTHROPIC_*`, `GH_TOKEN`, `SSH_*`, and 30+ other sensitive env vars. Restricts PATH to `/usr/bin:/usr/local/bin:/bin`.

2. **File snapshot** — Takes SHA-256 hash + size snapshot of the skill directory and watched directories before execution.

3. **Execution** — Runs the target script via `subprocess.Popen` with timeout enforcement. Captures stdout and stderr.

4. **Post-analysis** — Diffs file snapshots to detect creations, modifications, and deletions. Scans output for URL patterns (network calls) and env var references.

5. **Report** — Returns `BehavioralReport` with file accesses, network calls, process spawns, env vars accessed, and file modifications.

### report_generator.py

Generates markdown reports for each skill type:
- `generate_scan_report()` — Executive summary + findings table + detailed per-skill results
- `generate_audit_report()` — Config checks + permissions + network + integrity + remediation
- `generate_redteam_report()` — Pentest-style: batteries, findings, PoCs, remediation, verdict
- `generate_dashboard_report()` — Aggregated view: component status, score, recent alerts

### utils.py

Shared utilities with zero external dependencies:
- SKILL.md YAML frontmatter parser (no PyYAML needed)
- SHA-256 file hashing
- OpenClaw installation discovery
- Skill directory enumeration
- Base64/ROT13/homoglyph/zero-width detection
- File permission checking
- JSON5-compatible loading (handles `openclaw.json` with comments)

## Data Flow

### Scan Flow

```
User: "scan my skills"
  │
  ▼
vext-scan/scan.py
  │
  ├── utils.enumerate_skills() ──► List all skill directories
  │
  ├── For each skill:
  │     scanner_core.scan_skill()
  │       ├── Layer 1: Pattern matching (227 patterns)
  │       ├── Layer 2: AST analysis (Python files)
  │       └── Layer 3: Encoded content detection
  │
  ├── report_generator.generate_scan_report()
  │
  └── Save to ~/.openclaw/vext-shield/reports/scan-{timestamp}.md
```

### Red Team Flow

```
User: "red team [skill-name]"
  │
  ▼
vext-redteam/redteam.py
  │
  ├── Load skill content (SKILL.md + all files)
  │
  ├── Battery 1: Prompt Injection (24 payloads)
  │     └── Static pattern matching + encoded content detection
  │
  ├── Battery 2: Data Boundary (25+ probe paths)
  │     └── Static analysis + sandbox behavioral test
  │
  ├── Battery 3: Persistence (10 patterns)
  │     └── Static analysis + sandbox file modification test
  │
  ├── Battery 4: Exfiltration (12 endpoints + compound patterns)
  │     └── Static analysis + sandbox network monitoring
  │
  ├── Battery 5: Escalation (10 patterns + AST analysis)
  │     └── Static analysis + scanner cross-check
  │
  ├── Battery 6: Worm Behavior (10 patterns)
  │     └── Static analysis + scanner cross-check
  │
  ├── Compute score and verdict
  │
  └── Generate pentest-style report
```

### Monitor Flow

```
User: "monitor my skills" [--continuous]
  │
  ▼
vext-monitor/monitor.py
  │
  ├── Establish baselines (SHA-256 of SOUL.md, MEMORY.md, etc.)
  │
  ├── Check file integrity (compare current hashes to baseline)
  │
  ├── Check sensitive file permissions
  │
  ├── Check network connections (lsof/ss parsing)
  │
  ├── Check running processes for suspicious patterns
  │
  ├── Log alerts to ~/.openclaw/vext-shield/monitor.log
  │
  └── If --continuous: loop at --interval seconds
```

## Extension Points

1. **New threat signatures** — Add to `threat_signatures.json`, no code changes
2. **New red team batteries** — Add method to `RedTeamRunner` class
3. **New audit checks** — Add method to `InstallationAuditor` class
4. **New monitor watchers** — Add method to `Monitor` class
5. **New firewall rules** — Supported via CLI and JSON policy file

## Storage Locations

| Path | Purpose |
|------|---------|
| `~/.openclaw/vext-shield/` | VEXT Shield data directory |
| `~/.openclaw/vext-shield/reports/` | All generated reports |
| `~/.openclaw/vext-shield/monitor.log` | Runtime monitor alert log |
| `~/.openclaw/vext-shield/firewall-policy.json` | Firewall rules |
| `~/.openclaw/vext-shield/baselines.json` | File integrity baselines |

---

*Built by Vext Labs — Autonomous AI Red Team Technology*
