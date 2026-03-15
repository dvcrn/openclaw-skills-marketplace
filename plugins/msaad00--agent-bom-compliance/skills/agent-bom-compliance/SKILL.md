---
name: agent-bom-compliance
description: "AI compliance and policy engine — evaluate scan results against OWASP LLM Top 10, MITRE ATLAS, EU AI Act, NIST AI RMF, and custom policy-as-code rules. Generate SBOMs in CycloneDX or SPDX format. Use when the user mentions compliance checking, security policy enforcement, SBOM generation, or regulatory frameworks."
---

# agent-bom-compliance — AI Compliance & Policy Engine

Evaluate AI infrastructure scan results against security frameworks and enforce
policy-as-code rules. Generate SBOMs in standard formats.

## Install

```bash
pipx install agent-bom
agent-bom compliance        # run compliance check on latest scan
agent-bom generate-sbom     # generate CycloneDX SBOM
```

## Tools (4)

| Tool | Description |
|------|-------------|
| `compliance` | OWASP LLM/Agentic Top 10, EU AI Act, MITRE ATLAS, NIST AI RMF |
| `policy_check` | Evaluate results against custom security policy (17 conditions) |
| `cis_benchmark` | Run CIS benchmark checks against cloud accounts |
| `generate_sbom` | Generate SBOM (CycloneDX or SPDX format) |

## Supported Frameworks

- **OWASP LLM Top 10** (2025) — prompt injection, supply chain, data leakage
- **OWASP Agentic Top 10** — tool poisoning, rug pulls, credential theft
- **MITRE ATLAS** — adversarial ML threat framework
- **EU AI Act** — risk classification, transparency, SBOM requirements
- **NIST AI RMF** — govern, map, measure, manage lifecycle
- **CIS Foundations** — AWS, Azure v3.0, GCP v3.0, Snowflake benchmarks

## Example Workflows

```
# Run compliance check
compliance(frameworks=["owasp_llm", "eu_ai_act"])

# Enforce custom policy
policy_check(policy={"max_critical": 0, "max_high": 5})

# Generate SBOM
generate_sbom(format="cyclonedx")
```

## Privacy & Data Handling

**OWASP, NIST, EU AI Act, MITRE ATLAS, SBOM generation, and policy checks**
run entirely locally on scan data already in memory. No network calls, no
credentials needed for these features.

**CIS benchmark checks** (optional, user-initiated) call cloud provider APIs
using your locally configured credentials. These are read-only API calls to
AWS, Azure, GCP, or Snowflake. No data is stored or transmitted beyond the
cloud provider's own API. You must explicitly run `cis_benchmark(provider=...)`
and confirm before any cloud API calls are made.

## Verification

- **Source**: [github.com/msaad00/agent-bom](https://github.com/msaad00/agent-bom) (Apache-2.0)
- **6,040+ tests** with CodeQL + OpenSSF Scorecard
- **No telemetry**: Zero tracking, zero analytics
