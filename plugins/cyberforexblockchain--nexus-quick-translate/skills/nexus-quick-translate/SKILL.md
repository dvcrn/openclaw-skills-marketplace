---
name: nexus-quick-translate
description: "Ultra-fast translation for short texts under 500 characters. Optimized for sub-second latency on UI strings, notifications, error messages, and real-time chat. Supports 40+ languages."
---

# NEXUS Quick Translator

> Cardano-native AI service for autonomous agents | NEXUS AaaS Platform

## When to use

Your agent needs instant translation of short strings — chat messages, UI labels, error texts, or notification content. Unlike full translation services, this is optimized for speed over literary quality, returning results in under 500ms.

## What makes this different

Built for machine-speed workflows: sub-500ms latency, automatic source language detection, and consistent formatting preservation. Ideal for real-time agent communication pipelines where multilingual agents need to exchange messages without delay.

## Steps

1. Prepare your input as a JSON payload.
2. POST to the NEXUS API with `X-Payment-Proof` header.
3. Parse the structured JSON response.

### API Call

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/quick-translate \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"text": "Payment confirmed. Your receipt has been emailed.", "target_language": "ja", "source_language": "auto"}'
```

**Endpoint:** `https://ai-service-hub-15.emergent.host/api/original-services/quick-translate`
**Method:** POST
**Headers:**
- `Content-Type: application/json`
- `X-Payment-Proof: <masumi_payment_id>` (use `sandbox_test` for free sandbox)

## External Endpoints

| URL | Method | Data Sent |
|-----|--------|-----------|
| `https://ai-service-hub-15.emergent.host/api/original-services/quick-translate` | POST | Input parameters as JSON body |

## Security & Privacy

All requests encrypted via HTTPS/TLS to `https://ai-service-hub-15.emergent.host`. No data stored permanently — processed in memory and discarded. Payment verification via Masumi Protocol on Cardano (non-custodial escrow). No filesystem or shell permissions required.

## Model Invocation Note

This skill calls the NEXUS AI service API which uses large language models to process requests server-side. You may opt out by not installing this skill.

## Trust Statement

By installing this skill, input data is transmitted to NEXUS (https://ai-service-hub-15.emergent.host) for AI processing. All payments non-custodial via Cardano. Visit https://ai-service-hub-15.emergent.host for documentation and terms.
