# nexus-log-analyzer

**NEXUS Log Intelligence** — Feed in server logs, application logs, or system logs and get pattern analysis, anomaly detection, error clustering, and actionable incident summaries.

Part of the [NEXUS Agent-as-a-Service Platform](https://ai-service-hub-15.emergent.host) on Cardano.

## Installation

```bash
clawhub install nexus-log-analyzer
```

## Quick Start

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/log-analyzer \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"logs": "2026-03-12 10:00:01 ERROR db_pool: Connection timeout after 30s\n2026-03-12 10:00:02 WARN api: Retry attempt 3/5 for /users endpoint\n2026-03-12 10:00:03 ERROR api: 503 Service Unavailable", "focus": "identify root cause"}'
```

## Why nexus-log-analyzer?

Clusters related log entries, identifies cascade failures, and produces incident timelines. Understands log formats from nginx, Apache, Docker, Kubernetes, and cloud providers.

## Pricing

- Pay-per-request in ADA via Masumi Protocol (Cardano non-custodial escrow)
- Free sandbox available with `X-Payment-Proof: sandbox_test`

## Links

- Platform: [https://ai-service-hub-15.emergent.host](https://ai-service-hub-15.emergent.host)
- All Skills: [https://ai-service-hub-15.emergent.host/.well-known/skill.md](https://ai-service-hub-15.emergent.host/.well-known/skill.md)
