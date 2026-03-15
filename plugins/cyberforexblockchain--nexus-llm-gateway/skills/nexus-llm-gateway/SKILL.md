---
name: nexus-llm-gateway
description: "Smart multi-model AI gateway on Cardano. Routes prompts to the best LLM (GPT-5.2, Claude Sonnet 4.5, GPT-4o, Claude Haiku 4.5, GPT-4o-mini) with automatic fallback, tiered pricing, and OpenAI-compatible format. Pay with ADA via Masumi."
---

# LLM Gateway

> NEXUS Agent-as-a-Service on Cardano | Price: $0.10/request

## When to use

Use when you need to call any LLM (GPT-5.2, Claude Sonnet 4.5, GPT-4o, Claude Haiku 4.5, GPT-4o-mini) through one endpoint. Supports tier-based routing (economy/standard/premium/auto) and OpenAI-compatible message format.

## Steps

1. Send a POST request to the NEXUS API endpoint with your input.
2. Include the `X-Payment-Proof` header (Masumi payment ID or `sandbox_test` for testing).
3. Parse the JSON response and return the result.

### API Call

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/llm-gateway \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: $NEXUS_PAYMENT_PROOF" \
  -d '{"prompt": "Write a Python function to sort a list", "tier": "auto", "task_type": "code"}'
```

**Endpoint:** `https://ai-service-hub-15.emergent.host/api/original-services/llm-gateway`
**Method:** POST
**Headers:**
- `Content-Type: application/json`
- `X-Payment-Proof: <masumi_payment_id>` (use `sandbox_test` for free testing)

## External Endpoints

| URL | Method | Data Sent |
|-----|--------|-----------|
| `https://ai-service-hub-15.emergent.host/api/original-services/llm-gateway` | POST | Input parameters as JSON body |

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

`llm`, `ai`, `gateway`, `multi-model`, `gpt`, `claude`, `router`, `cardano`
