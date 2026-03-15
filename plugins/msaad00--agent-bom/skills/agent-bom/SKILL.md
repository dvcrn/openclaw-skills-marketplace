---
name: agent-bom
description: "AI agent infrastructure security scanner — discovers MCP clients and servers, scans for CVEs, maps blast radius, runs CIS benchmarks (AWS, Azure, GCP, Snowflake), OWASP/NIST/MITRE compliance, AISVS v1.0, MAESTRO layer tagging, and vector database security checks. Use when the user mentions vulnerability scanning, MCP server trust, compliance, SBOM generation, CIS benchmarks, blast radius, or AI supply chain risk."
---

# agent-bom — AI Agent Infrastructure Security Scanner

Discovers MCP clients and servers across 20+ AI tools, scans for CVEs, maps
blast radius, runs cloud CIS benchmarks, checks OWASP/NIST/MITRE compliance,
generates SBOMs, and assesses AI infrastructure against AISVS v1.0 and MAESTRO
framework layers.

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

## Tools (31)

### Vulnerability Scanning
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

### Compliance & Policy
| Tool | Description |
|------|-------------|
| `compliance` | OWASP LLM/Agentic Top 10, EU AI Act, MITRE ATLAS, NIST AI RMF |
| `policy_check` | Evaluate results against custom security policy (17 conditions) |
| `cis_benchmark` | CIS benchmark checks (AWS, Azure v3.0, GCP v3.0, Snowflake) |
| `generate_sbom` | Generate SBOM (CycloneDX or SPDX format) |
| `aisvs_benchmark` | OWASP AISVS v1.0 compliance — 9 AI security checks |

### Registry & Trust
| Tool | Description |
|------|-------------|
| `registry_lookup` | Look up MCP server in 427+ server security metadata registry |
| `marketplace_check` | Pre-install trust check with registry cross-reference |
| `fleet_scan` | Batch registry lookup + risk scoring for MCP server inventories |
| `skill_trust` | Assess skill file trust level (5-category analysis) |
| `code_scan` | SAST scanning via Semgrep with CWE-based compliance mapping |

### Runtime & Analytics
| Tool | Description |
|------|-------------|
| `context_graph` | Agent context graph with lateral movement analysis |
| `analytics_query` | Query vulnerability trends, posture history, and runtime events |
| `runtime_correlate` | Cross-reference proxy audit JSONL with CVE findings, risk amplification |
| `vector_db_scan` | Probe Qdrant/Weaviate/Chroma/Milvus for auth and exposure |
| `gpu_infra_scan` | GPU container and K8s node inventory + unauthenticated DCGM probe (MAESTRO KC6) |

### Specialized Scans
| Tool | Description |
|------|-------------|
| `dataset_card_scan` | Scan dataset cards for bias, licensing, and provenance issues |
| `training_pipeline_scan` | Scan training pipeline configs for security risks |
| `browser_extension_scan` | Scan browser extensions for risky permissions and AI domain access |
| `model_provenance_scan` | Verify model provenance and supply chain integrity |
| `prompt_scan` | Scan prompt templates for injection and data leakage risks |
| `model_file_scan` | Scan model files for unsafe serialization (pickle, etc.) |
| `license_compliance_scan` | Full SPDX license catalog scan with copyleft and network-copyleft detection |
| `ingest_external_scan` | Import Trivy/Grype/Syft scan results and merge into agent-bom findings |

### Resources
| Resource | Description |
|----------|-------------|
| `registry://servers` | Browse 427+ MCP server security metadata registry |

## Example Workflows

```
# Check a package before installing
check(package="@modelcontextprotocol/server-filesystem", ecosystem="npm")

# Map blast radius of a CVE
blast_radius(cve_id="CVE-2024-21538")

# Full scan
scan()

# Run CIS benchmark
cis_benchmark(provider="aws")

# Run AISVS v1.0 compliance
aisvs_benchmark()

# Scan vector databases for auth misconfigurations
vector_db_scan()

# Discover GPU containers, K8s GPU nodes, and unauthenticated DCGM endpoints
gpu_infra_scan()

# Assess trust of a skill file
skill_trust(skill_content="<paste SKILL.md content>")
```

## Guardrails

**Always do:**
- Show CVEs even when NVD analysis is pending or severity is `unknown` — a CVE ID with no details is still a real finding. Report what is known; mark severity as `unknown` explicitly.
- Confirm with the user before scanning cloud environments (`cis_benchmark`) — these make live API calls to AWS/Azure/GCP using the user's credentials.
- Treat `UNKNOWN` severity as unresolved, not benign — it means data is not yet available, not that the issue is minor.

**Never do:**
- Do not modify any files, install packages, or change system configuration. This skill is read-only.
- Do not transmit env var values, credentials, or file contents to any external service. Only package names and CVE IDs leave the machine.
- Do not invoke `scan()` autonomously on sensitive environments without user confirmation. The `autonomous_invocation` policy is `restricted`.

**Stop and ask the user when:**
- The user requests a cloud CIS benchmark and no cloud credentials are configured.
- A scan finds `CRITICAL` CVEs — present findings and ask whether to generate a remediation plan.
- The user asks to scan a path outside their home directory.

## Supported Frameworks

- **OWASP LLM Top 10** (2025) — prompt injection, supply chain, data leakage
- **OWASP Agentic Top 10** — tool poisoning, rug pulls, credential theft
- **OWASP AISVS v1.0** — AI Security Verification Standard (9 checks)
- **MITRE ATLAS** — adversarial ML threat framework
- **MITRE ATT&CK Enterprise** — cloud/infra T-code mapping on CIS failures
- **MAESTRO** — KC1–KC6 layer tagging on all findings
- **EU AI Act** — risk classification, transparency, SBOM requirements
- **NIST AI RMF** — govern, map, measure, manage lifecycle
- **CIS Foundations** — AWS, Azure v3.0, GCP v3.0, Snowflake benchmarks

## Privacy & Data Handling

This skill installs agent-bom from PyPI. The redaction behavior described here
is implemented in the installed package — **verify before running with
sensitive data**:

```bash
# 1. Verify package integrity (Sigstore)
agent-bom verify agent-bom

# 2. Review the redaction code directly
# security.py L159: sanitize_env_vars() — replaces env values with ***REDACTED***
# https://github.com/msaad00/agent-bom/blob/main/src/agent_bom/security.py#L159

# 3. Review config parsing
# https://github.com/msaad00/agent-bom/blob/main/src/agent_bom/discovery/__init__.py
```

Discovery reads local MCP client config files. Only server names, commands,
args, and URLs are extracted. Env var values are replaced with `***REDACTED***`
by `sanitize_env_vars()` in the installed code. Only public package names and
CVE IDs are sent to vulnerability databases. Cloud CIS checks use locally
configured credentials and call only the cloud provider's own APIs.

## Verification

- **Source**: [github.com/msaad00/agent-bom](https://github.com/msaad00/agent-bom) (Apache-2.0)
- **Sigstore signed**: `agent-bom verify agent-bom@0.70.6`
- **5,987+ tests** with CodeQL + OpenSSF Scorecard
- **No telemetry**: Zero tracking, zero analytics
