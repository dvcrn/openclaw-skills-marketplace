---
name: agent-bom-runtime
description: "AI runtime security monitoring — context graph analysis, runtime audit log correlation with CVE findings, and vulnerability analytics queries. Use when the user mentions runtime monitoring, context graphs, lateral movement analysis, audit log correlation, or vulnerability analytics."
---

# agent-bom-runtime — AI Runtime Security Monitoring

Context graph analysis, runtime audit log correlation with CVE findings, and
vulnerability analytics queries.

## Install

```bash
pipx install agent-bom
```

## Tools (3)

| Tool | Description |
|------|-------------|
| `context_graph` | Agent context graph with lateral movement analysis |
| `analytics_query` | Query vulnerability trends, posture history, and runtime events |
| `runtime_correlate` | Cross-reference runtime audit logs with CVE findings |

## Example Workflows

```
# Build context graph from scan results
context_graph()

# Correlate runtime audit with CVE data
runtime_correlate(audit_file="proxy-audit.jsonl")

# Query analytics
analytics_query(query="top_cves", days=30)
```

## Privacy & Data Handling

Operates on scan results already in memory and user-provided audit log files.
No automatic file discovery. No network calls unless you configure an optional
ClickHouse endpoint for persistent analytics.

## Verification

- **Source**: [github.com/msaad00/agent-bom](https://github.com/msaad00/agent-bom) (Apache-2.0)
- **6,040+ tests** with CodeQL + OpenSSF Scorecard
- **No telemetry**: Zero tracking, zero analytics
