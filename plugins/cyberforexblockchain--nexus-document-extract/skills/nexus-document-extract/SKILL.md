---
name: nexus-document-extract
description: "Extract structured data (names, dates, amounts, entities) from unstructured text documents using AI. Returns clean JSON with extracted fields."
---

# NEXUS Document Extractor

> NEXUS Agent-as-a-Service on Cardano

## When to use

You have a block of unstructured text (invoice, contract, email, report) and need to pull out specific data points like names, dates, monetary amounts, and key terms into structured JSON.

## What makes this different

Unlike general summarizers, this service returns machine-readable JSON with typed fields. Ideal for data pipelines and automated document processing workflows.

## Steps

1. Prepare your input payload as JSON.
2. Send a POST request to the NEXUS endpoint with `X-Payment-Proof` header.
3. Parse the structured JSON response.

### API Call

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/document-extract \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"text": "Invoice #1234 from Acme Corp. Due: March 15, 2026. Amount: $5,400.00 for consulting services.", "extract_fields": ["company", "date", "amount", "service"]}'
```

**Endpoint:** `https://ai-service-hub-15.emergent.host/api/original-services/document-extract`
**Method:** POST
**Headers:**
- `Content-Type: application/json`
- `X-Payment-Proof: <masumi_payment_id>` (use `sandbox_test` for free sandbox testing)

## External Endpoints

| URL | Method | Data Sent |
|-----|--------|-----------|
| `https://ai-service-hub-15.emergent.host/api/original-services/document-extract` | POST | Input parameters as JSON body |

## Security & Privacy

- All requests are encrypted via HTTPS/TLS to `https://ai-service-hub-15.emergent.host`.
- No user data is stored permanently. Requests are processed in memory and discarded.
- Payment verification uses the Masumi Protocol on Cardano (non-custodial escrow).
- This skill requires network access only. No filesystem or shell permissions needed.

## Model Invocation Note

This skill calls the NEXUS AI service API which processes your input using large language models server-side. The AI generates a response based on your input and returns structured data. You may opt out by not installing this skill.

## Trust Statement

By installing this skill, your input data is transmitted to NEXUS (https://ai-service-hub-15.emergent.host) for AI processing. All payments are non-custodial via Cardano blockchain. Visit https://ai-service-hub-15.emergent.host for documentation and terms. Only install if you trust NEXUS as a service provider.
