---
name: agent-bom-scan
description: "Security scanner for AI infrastructure — discovers MCP clients and servers, checks packages for CVEs (OSV, NVD, EPSS, KEV), maps blast radius, and generates remediation plans. Use when the user mentions vulnerability scanning, dependency security, CVE lookup, blast radius analysis, or AI supply chain risk."
---

# agent-bom-scan — AI Supply Chain Vulnerability Scanner

Discovers MCP clients and servers across 22 AI tools, checks packages for CVEs,
maps blast radius, and generates remediation plans.

## Install

```bash
pipx install agent-bom
agent-bom scan              # auto-discover + scan
agent-bom check langchain   # check a specific package
agent-bom where             # show all discovery paths
```

### As an MCP Server

```json
{
  "mcpServers": {
    "agent-bom": {
      "command": "uvx",
      "args": ["agent-bom", "mcp"]
    }
  }
}
```

## Tools (8)

| Tool | Description |
|------|-------------|
| `scan` | Full discovery + vulnerability scan pipeline |
| `check` | Check a package for CVEs (OSV, NVD, EPSS, KEV) |
| `blast_radius` | Map CVE impact chain across agents, servers, credentials |
| `remediate` | Prioritized remediation plan for vulnerabilities |
| `verify` | Package integrity + SLSA provenance check |
| `diff` | Compare two scan reports (new/resolved/persistent) |
| `where` | Show MCP client config discovery paths |
| `inventory` | List discovered agents, servers, packages |

## Example Workflows

```
# Check a package before installing
check(package="@modelcontextprotocol/server-filesystem", ecosystem="npm")

# Map blast radius of a CVE
blast_radius(cve_id="CVE-2024-21538")

# Full scan
scan()
```

## Privacy & Data Handling

This skill installs agent-bom from PyPI. **Verify the redaction behavior
before running with any config files:**

```bash
# Step 1: Install
pip install agent-bom

# Step 2: Review redaction logic BEFORE scanning
# sanitize_env_vars() replaces ALL env var values with ***REDACTED***
# BEFORE any config data is processed or stored:
# https://github.com/msaad00/agent-bom/blob/main/src/agent_bom/security.py#L159

# Step 3: Review config parsing — only structural data extracted:
# https://github.com/msaad00/agent-bom/blob/main/src/agent_bom/discovery/__init__.py

# Step 4: Verify package provenance (Sigstore)
agent-bom verify agent-bom

# Step 5: Only then run scans
agent-bom scan
```

**What is extracted**: Server names, commands, args, and URLs from MCP client
config files across 22 AI tools. **What is NOT extracted**: Env var values are
replaced with `***REDACTED***` by `sanitize_env_vars()` before any processing.
Only public package names and CVE IDs are sent to vulnerability databases.

## Verification

- **Source**: [github.com/msaad00/agent-bom](https://github.com/msaad00/agent-bom) (Apache-2.0)
- **Sigstore signed**: `agent-bom verify agent-bom@0.70.10
- **6,040+ tests** with CodeQL + OpenSSF Scorecard
- **No telemetry**: Zero tracking, zero analytics
