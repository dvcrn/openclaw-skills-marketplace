---
name: guard-scanner
description: "Security scanner and runtime guard for AI agent skills. 358 static threat patterns across 35 categories + 27 runtime checks (5 defense layers). Use when scanning skill directories for security threats, auditing npm/GitHub/ClawHub assets for leaked credentials, running real-time file watch during development, integrating security checks into CI/CD pipelines (SARIF/JSON), setting up MCP server for editor-integrated scanning (Cursor, Windsurf, Claude Code, OpenClaw), or runtime guarding tool calls via the OpenClaw v2026.3.8 before_tool_call hook. Single dependency (ws). MIT licensed."
---

# guard-scanner

Scan AI agent skills for 35 categories of threats. Detect prompt injection, identity hijacking, memory poisoning, MCP tool poisoning, supply chain attacks, and 27 more threat classes that traditional security tools miss.

## Quick Start

```bash
# Scan a skill directory
npx -y @guava-parity/guard-scanner ./my-skills/ --verbose

# Scan with identity protection
npx -y @guava-parity/guard-scanner ./skills/ --soul-lock --strict
```

## Core Commands

### Scan

```bash
guard-scanner scan <dir>        # Scan directory
guard-scanner scan <dir> -v     # Verbose output
guard-scanner scan <dir> --json # JSON output
guard-scanner scan <dir> --sarif # SARIF for CI/CD
guard-scanner scan <dir> --html # HTML report
```

### Asset Audit

Audit public registries for credential exposure.

```bash
guard-scanner audit npm <username>
guard-scanner audit github <username>
guard-scanner audit clawhub <query>
guard-scanner audit all <username> --verbose
```

### MCP Server

Start as MCP server for IDE integration.

```bash
guard-scanner serve
```

Editor config (Cursor, Windsurf, Claude Code, OpenClaw):

```json
{
  "mcpServers": {
    "guard-scanner": {
      "command": "npx",
      "args": ["-y", "@guava-parity/guard-scanner", "serve"]
    }
  }
}
```

MCP tools: `scan_skill`, `scan_text`, `check_tool_call`, `audit_assets`, `get_stats`.

### Watch Mode

Monitor skill directories in real-time during development.

```bash
guard-scanner watch ./skills/ --strict --soul-lock
```

### VirusTotal Integration

Combine semantic detection with VirusTotal's 70+ antivirus engines. Optional — guard-scanner works fully without it.

```bash
export VT_API_KEY=your-key
guard-scanner scan ./skills/ --vt-scan
```

## Runtime Guard

The validated OpenClaw surface is the compiled runtime plugin entry (`dist/openclaw-plugin.mjs`) discovered through `package.json > openclaw.extensions` and mounted on `before_tool_call` for OpenClaw `v2026.3.8`.

The `before_tool_call` hook provides 27 runtime checks across 5 defense layers:

| Layer | Focus |
|-------|-------|
| 1. Threat Detection | Reverse shell, curl\|bash, SSRF |
| 2. Trust Defense | SOUL.md tampering, memory injection |
| 3. Safety Judge | Prompt injection in tool arguments |
| 4. Behavioral | No-research execution detection |
| 5. Trust Exploitation | Authority claims, creator bypass |

Modes: `monitor` (log only), `enforce` (block CRITICAL, default), `strict` (block HIGH+).

## Key Flags

| Flag | Effect |
|------|--------|
| `--verbose` / `-v` | Detailed findings with line numbers |
| `--strict` | Lower detection thresholds |
| `--soul-lock` | Enable identity protection patterns |
| `--vt-scan` | Add VirusTotal double-layered check |
| `--json` / `--sarif` / `--html` | Output format |
| `--fail-on-findings` | Exit 1 on findings (CI/CD) |
| `--check-deps` | Scan package.json dependencies |
| `--rules <file>` | Load custom rules JSON |
| `--plugin <file>` | Load plugin module |

## Custom Rules

```javascript
module.exports = {
  name: 'my-plugin',
  patterns: [
    { id: 'MY_01', cat: 'custom', regex: /dangerous_pattern/g, severity: 'HIGH', desc: 'Description', all: true }
  ]
};
```

```bash
guard-scanner ./skills/ --plugin ./my-plugin.js
```

## CI/CD Integration

```yaml
# .github/workflows/security.yml
- name: Scan AI skills
  run: npx -y @guava-parity/guard-scanner ./skills/ --format sarif --fail-on-findings > report.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: report.sarif
```

## Threat Categories

35 categories covering OWASP LLM Top 10 + Agentic Security Top 10. See `src/patterns.js` for the full pattern database. Key categories:

- **Prompt Injection** — hidden instructions, invisible Unicode, homoglyphs
- **Identity Hijacking** ⚿ — persona swap, SOUL.md overwrites, memory wipe
- **Memory Poisoning** ⚿ — crafted conversation injection
- **MCP Security** — tool poisoning, SSRF, shadow servers
- **A2A Contagion** — agent-to-agent worm propagation
- **Supply Chain V2** — typosquatting, slopsquatting, lifecycle scripts
- **CVE Patterns** — CVE-2026-2256, 25046, 25253, 25905, 27825

> ⚿ = Requires `--soul-lock` flag
