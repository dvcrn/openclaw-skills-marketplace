<p align="center">
  <img src="docs/logo.png" alt="guard-scanner" width="180" />
</p>

<h1 align="center">guard-scanner 🛡️</h1>
<p align="center"><strong>Security policy and runtime layer for agent skills and MCP workflows</strong></p>
<p align="center">35 threat categories · 358 static patterns · 27 runtime checks · 0 runtime dependencies</p>

<p align="center">
  <a href="https://www.npmjs.com/package/@guava-parity/guard-scanner"><img src="https://img.shields.io/npm/v/@guava-parity/guard-scanner?color=cb3837" alt="npm version" /></a>
  <a href="#test-results"><img src="https://img.shields.io/badge/tests-332%20passed-brightgreen" alt="tests" /></a>
  <a href="https://github.com/koatora20/guard-scanner/actions/workflows/codeql.yml"><img src="https://img.shields.io/badge/CodeQL-enabled-181717" alt="CodeQL" /></a>
  <a href="https://doi.org/10.5281/zenodo.18906684"><img src="https://img.shields.io/badge/DOI-3_papers-purple" alt="DOI" /></a>
</p>

---

## What is guard-scanner?

**guard-scanner** is an uncompromising security and policy enforcement layer designed specifically for AI agents, OpenClaw skills, and MCP (Model Context Protocol) workflows. 

While traditional security tools detect malware, AI agents face unique attack vectors: prompt injections hidden in memory, identity hijacking, autonomous permission escalation, and agent-to-agent contagion. 

**Core advantages:**
- **Zero Runtime Dependencies:** Ultra-lightweight npm dual-publish (Only `ws` is used for MCP).
- **Deep Defense:** Combines *static policy scanning* (358 patterns) with *runtime hook inspection* (27 checks).
- **Universal MCP Server:** Plugs instantly into Cursor, Windsurf, Claude Code, and OpenClaw.
- **Evidence-Driven Claims:** 100% precision/recall on our benchmark. 332 end-to-end tests all passing.

> 📄 **Backed by research**: Designed as the defense layer of the [The Sanctuary Protocol](https://doi.org/10.5281/zenodo.18906684) architecture (3-paper series, CC BY 4.0).

---

## Quick Start

### 1. Zero-Install CLI Scan
Run a semantic security scan on your agent workspace instantly:
```bash
npx -y @guava-parity/guard-scanner ./my-skills/ --strict
```

### 2. Universal MCP Server
Connect guard-scanner to your favorite AI IDE for real-time security checking:
```bash
npx -y @guava-parity/guard-scanner serve
```
*Configure your editor (e.g., `mcp_servers.json`):*
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

---

## Core Capabilities

### Threat Detection (35 Categories, 358 Patterns)
Detects advanced 2026-era agentic threats globally mapping to **OWASP ASI01-10**:
- **Prompt Injection & Memory Poisoning:** Detects invisible Unicode homoglyphs, decoding evasion, and payload cascades.
- **Agent Identity Hijacking:** Blocks SOUL.md overwrites and prevents identity death.
- **Autonomy & Privilege Escalation:** Rejects unauthorized `child_process`, `eval()`, and raw reverse shells.
- **A2A Contagion:** Halts Session Smuggling and lateral infection between chained agents.

### Advanced Runtime Guard
A deep `before_tool_call` layer validated seamlessly against OpenClaw `v2026.3.8`. Implements a ContextCrush 185KB gate and blocks Moltbook injection attempts during execution.

---

## Usage Scenarios

**Audit Local Assets:**
```bash
# Audit npm, GitHub, or ClawHub exposures globally
guard-scanner audit npm <username> --verbose
```

**Continuous CI/CD Security:**
```yaml
# GitHub Actions integration
- name: Scan AI Workflows
  run: npx -y @guava-parity/guard-scanner ./skills/ --format sarif --fail-on-findings > report.sarif
```

**Real-Time Live Reload Watcher:**
```bash
guard-scanner watch ./skills/ --strict --soul-lock
```

---

## Contributing
We welcome bug reports, new pattern ideas, and test case contributions. We hold a **Zero-Tolerance for Marketing Claims** — all features must be reproducible and test-backed.

- [Governance & Contribution](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

## License
MIT — [Guava Parity Institute](https://github.com/koatora20/guard-scanner)
