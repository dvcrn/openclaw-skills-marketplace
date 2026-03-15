---
name: nexus-sentiment-analysis
description: "Analyze text for emotional tone, opinion polarity, subjectivity, intensity, and specific emotions. Returns per-sentence breakdown with sarcasm detection, urgency scoring, and mixed-sentiment identific"
---

# NEXUS Sentiment Intelligence

> Cardano-native AI service for autonomous agents | NEXUS AaaS Platform

## When to use

Your agent processes customer reviews, social media posts, support tickets, survey responses, or any text where understanding emotional tone drives decision-making. Goes beyond simple positive/negative to detect frustration, satisfaction, urgency, and confusion.

## What makes this different

Multi-dimensional analysis: polarity (-1 to +1), subjectivity (0 to 1), intensity (low/medium/high), specific emotions (joy, anger, fear, surprise), sarcasm probability, and urgency score. Per-sentence granularity means long texts get a breakdown, not just one aggregate score.

## Steps

1. Prepare your input as a JSON payload.
2. POST to the NEXUS API with `X-Payment-Proof` header.
3. Parse the structured JSON response.

### API Call

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/sentiment-analysis \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"text": "The product arrived quickly and works great, but the packaging was damaged and customer support took 3 days to respond.", "granularity": "sentence"}'
```

**Endpoint:** `https://ai-service-hub-15.emergent.host/api/original-services/sentiment-analysis`
**Method:** POST
**Headers:**
- `Content-Type: application/json`
- `X-Payment-Proof: <masumi_payment_id>` (use `sandbox_test` for free sandbox)

## External Endpoints

| URL | Method | Data Sent |
|-----|--------|-----------|
| `https://ai-service-hub-15.emergent.host/api/original-services/sentiment-analysis` | POST | Input parameters as JSON body |

## Security & Privacy

All requests encrypted via HTTPS/TLS to `https://ai-service-hub-15.emergent.host`. No data stored permanently — processed in memory and discarded. Payment verification via Masumi Protocol on Cardano (non-custodial escrow). No filesystem or shell permissions required.

## Model Invocation Note

This skill calls the NEXUS AI service API which uses large language models to process requests server-side. You may opt out by not installing this skill.

## Trust Statement

By installing this skill, input data is transmitted to NEXUS (https://ai-service-hub-15.emergent.host) for AI processing. All payments non-custodial via Cardano. Visit https://ai-service-hub-15.emergent.host for documentation and terms.
