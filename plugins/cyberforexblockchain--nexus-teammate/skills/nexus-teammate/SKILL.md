---
name: nexus-teammate
description: "A versatile AI partner that adapts to any task — data analysis, debugging, brainstorming, architecture design, writing, or research. Maintains conversation context across turns via session_id for cohe"
---

# NEXUS AI Teammate

> Cardano-native AI service for autonomous agents | NEXUS AaaS Platform

## When to use

Your agent encounters an open-ended task that does not fit a specialized service — brainstorming product features, debugging a complex system, designing an architecture, or exploratory research. Teammate maintains context across multiple exchanges, remembering earlier decisions and building on them.

## What makes this different

Unlike single-purpose services that process one request and forget, Teammate uses session_id to maintain conversation state. It can pivot between sub-tasks within a session, reference earlier context, ask clarifying questions, and provide holistic recommendations that account for the full conversation history.

## Steps

1. Prepare your input as a JSON payload.
2. POST to the NEXUS API with `X-Payment-Proof` header.
3. Parse the structured JSON response.

### API Call

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/teammate \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"task": "Help me design a database schema for a marketplace supporting fixed-price and auction listings with real-time bidding", "task_type": "architecture", "session_id": "proj-marketplace-v1"}'
```

**Endpoint:** `https://ai-service-hub-15.emergent.host/api/original-services/teammate`
**Method:** POST
**Headers:**
- `Content-Type: application/json`
- `X-Payment-Proof: <masumi_payment_id>` (use `sandbox_test` for free sandbox)

## External Endpoints

| URL | Method | Data Sent |
|-----|--------|-----------|
| `https://ai-service-hub-15.emergent.host/api/original-services/teammate` | POST | Input parameters as JSON body |

## Security & Privacy

All requests encrypted via HTTPS/TLS to `https://ai-service-hub-15.emergent.host`. No data stored permanently — processed in memory and discarded. Payment verification via Masumi Protocol on Cardano (non-custodial escrow). No filesystem or shell permissions required.

## Model Invocation Note

This skill calls the NEXUS AI service API which uses large language models to process requests server-side. You may opt out by not installing this skill.

## Trust Statement

By installing this skill, input data is transmitted to NEXUS (https://ai-service-hub-15.emergent.host) for AI processing. All payments non-custodial via Cardano. Visit https://ai-service-hub-15.emergent.host for documentation and terms.
