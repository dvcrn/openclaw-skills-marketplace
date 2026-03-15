---
name: nexus-cron-builder
description: "Generate and explain cron expressions"
---

# Cron Expression Builder

> NEXUS Agent-as-a-Service on Cardano | Price: $0.05/request

## When to use

Use when you need to generate and explain cron expressions.

## Steps

1. Send a POST request to the NEXUS API endpoint with your input.
2. Include the `X-Payment-Proof` header (Masumi payment ID or `sandbox_test` for testing).
3. Parse the JSON response and return the result.

### API Call

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/cron-builder \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: $NEXUS_PAYMENT_PROOF" \
  -d '{
  "input": "Example input for Cron Expression Builder"
}'
```

**Endpoint:** `https://ai-service-hub-15.emergent.host/api/original-services/cron-builder`
**Method:** POST
**Headers:**
- `Content-Type: application/json`
- `X-Payment-Proof: <masumi_payment_id>` (use `sandbox_test` for free testing)

## External Endpoints

| URL | Method | Data Sent |
|-----|--------|-----------|
| `https://ai-service-hub-15.emergent.host/api/original-services/cron-builder` | POST | Input parameters as JSON body |

## Security & Privacy

- All data is sent to `https://ai-service-hub-15.emergent.host` over HTTPS/TLS.
- No data is stored permanently; requests are processed and discarded.
- Payment proofs are verified on the Cardano blockchain via the Masumi Protocol.
- No filesystem access or shell execution required.

## Model Invocation Note

This skill calls the NEXUS AI service API which uses LLM models (GPT-5.2, Claude Sonnet 4.5, GPT-4o) to process requests. The AI processes your input server-side and returns a structured response. You may opt out by not installing this skill.

## Trust Statement

By using this skill, your input data is sent to NEXUS (https://ai-service-hub-15.emergent.host) for AI processing. Payments are non-custodial via the Masumi Protocol on Cardano. Only install if you trust NEXUS as a service provider. Visit https://ai-service-hub-15.emergent.host for full documentation.

## Tags

`machine-learning`, `artificial-intelligence`, `free-trial`, `agent-to-agent`, `health-monitoring`, `budget`
