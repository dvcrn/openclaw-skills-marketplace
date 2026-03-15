---
name: nexus-grammar-fix
description: "Professional grammar correction and writing improvement. Fixes spelling, punctuation, sentence structure, and tone while preserving the author's voice."
---

# NEXUS Grammar Engine

> NEXUS Agent-as-a-Service on Cardano

## When to use

You have text that needs grammar correction, spelling fixes, punctuation cleanup, or general writing improvement before publishing or sending.

## What makes this different

Goes beyond spell-check: restructures awkward sentences, fixes subject-verb agreement, corrects homophones (their/there/they're), and adjusts tone for the target audience.

## Steps

1. Prepare your input payload as JSON.
2. Send a POST request to the NEXUS endpoint with `X-Payment-Proof` header.
3. Parse the structured JSON response.

### API Call

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/grammar-fix \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"text": "Their going to the store tommorow, me and him will be their to.", "style": "professional"}'
```

**Endpoint:** `https://ai-service-hub-15.emergent.host/api/original-services/grammar-fix`
**Method:** POST
**Headers:**
- `Content-Type: application/json`
- `X-Payment-Proof: <masumi_payment_id>` (use `sandbox_test` for free sandbox testing)

## External Endpoints

| URL | Method | Data Sent |
|-----|--------|-----------|
| `https://ai-service-hub-15.emergent.host/api/original-services/grammar-fix` | POST | Input parameters as JSON body |

## Security & Privacy

- All requests are encrypted via HTTPS/TLS to `https://ai-service-hub-15.emergent.host`.
- No user data is stored permanently. Requests are processed in memory and discarded.
- Payment verification uses the Masumi Protocol on Cardano (non-custodial escrow).
- This skill requires network access only. No filesystem or shell permissions needed.

## Model Invocation Note

This skill calls the NEXUS AI service API which processes your input using large language models server-side. The AI generates a response based on your input and returns structured data. You may opt out by not installing this skill.

## Trust Statement

By installing this skill, your input data is transmitted to NEXUS (https://ai-service-hub-15.emergent.host) for AI processing. All payments are non-custodial via Cardano blockchain. Visit https://ai-service-hub-15.emergent.host for documentation and terms. Only install if you trust NEXUS as a service provider.
