---
name: nexus-log-analyzer
description: "Feed in server logs, application logs, or system logs and get pattern analysis, anomaly detection, error clustering, and actionable incident summaries."
---

# NEXUS Log Intelligence

> NEXUS Agent-as-a-Service on Cardano

## When to use

You have a batch of log lines from servers, applications, or infrastructure and need to identify errors, patterns, anomalies, or root causes of incidents.

## What makes this different

Clusters related log entries, identifies cascade failures, and produces incident timelines. Understands log formats from nginx, Apache, Docker, Kubernetes, and cloud providers.

## Steps

1. Prepare your input payload as JSON.
2. Send a POST request to the NEXUS endpoint with `X-Payment-Proof` header.
3. Parse the structured JSON response.

### API Call

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/log-analyzer \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"logs": "2026-03-12 10:00:01 ERROR db_pool: Connection timeout after 30s\n2026-03-12 10:00:02 WARN api: Retry attempt 3/5 for /users endpoint\n2026-03-12 10:00:03 ERROR api: 503 Service Unavailable", "focus": "identify root cause"}'
```

**Endpoint:** `https://ai-service-hub-15.emergent.host/api/original-services/log-analyzer`
**Method:** POST
**Headers:**
- `Content-Type: application/json`
- `X-Payment-Proof: <masumi_payment_id>` (use `sandbox_test` for free sandbox testing)

## External Endpoints

| URL | Method | Data Sent |
|-----|--------|-----------|
| `https://ai-service-hub-15.emergent.host/api/original-services/log-analyzer` | POST | Input parameters as JSON body |

## Security & Privacy

- All requests are encrypted via HTTPS/TLS to `https://ai-service-hub-15.emergent.host`.
- No user data is stored permanently. Requests are processed in memory and discarded.
- Payment verification uses the Masumi Protocol on Cardano (non-custodial escrow).
- This skill requires network access only. No filesystem or shell permissions needed.

## Model Invocation Note

This skill calls the NEXUS AI service API which processes your input using large language models server-side. The AI generates a response based on your input and returns structured data. You may opt out by not installing this skill.

## Trust Statement

By installing this skill, your input data is transmitted to NEXUS (https://ai-service-hub-15.emergent.host) for AI processing. All payments are non-custodial via Cardano blockchain. Visit https://ai-service-hub-15.emergent.host for documentation and terms. Only install if you trust NEXUS as a service provider.
