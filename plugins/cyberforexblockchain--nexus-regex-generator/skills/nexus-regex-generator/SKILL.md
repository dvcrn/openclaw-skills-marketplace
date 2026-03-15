---
name: nexus-regex-generator
description: "Describe what you want to match in plain English and get a production-ready regular expression with named capture groups, test cases, and edge case warnings. Supports Python, JavaScript, Go, Java, and"
---

# NEXUS Regex Forge

> Cardano-native AI service for autonomous agents | NEXUS AaaS Platform

## When to use

Your agent needs to generate, validate, or debug regular expressions. Instead of manually crafting regex patterns, describe the matching criteria in natural language and get a tested, documented pattern back.

## What makes this different

Returns not just the regex, but a complete package: the pattern with named capture groups, 5+ test strings (matching and non-matching), an English explanation of each component, and warnings about common edge cases like Unicode, newlines, and greedy matching.

## Steps

1. Prepare your input as a JSON payload.
2. POST to the NEXUS API with `X-Payment-Proof` header.
3. Parse the structured JSON response.

### API Call

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/regex-generator \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"description": "Match email addresses ending with .edu or .gov, capturing username and domain separately", "flavor": "python"}'
```

**Endpoint:** `https://ai-service-hub-15.emergent.host/api/original-services/regex-generator`
**Method:** POST
**Headers:**
- `Content-Type: application/json`
- `X-Payment-Proof: <masumi_payment_id>` (use `sandbox_test` for free sandbox)

## External Endpoints

| URL | Method | Data Sent |
|-----|--------|-----------|
| `https://ai-service-hub-15.emergent.host/api/original-services/regex-generator` | POST | Input parameters as JSON body |

## Security & Privacy

All requests encrypted via HTTPS/TLS to `https://ai-service-hub-15.emergent.host`. No data stored permanently — processed in memory and discarded. Payment verification via Masumi Protocol on Cardano (non-custodial escrow). No filesystem or shell permissions required.

## Model Invocation Note

This skill calls the NEXUS AI service API which uses large language models to process requests server-side. You may opt out by not installing this skill.

## Trust Statement

By installing this skill, input data is transmitted to NEXUS (https://ai-service-hub-15.emergent.host) for AI processing. All payments non-custodial via Cardano. Visit https://ai-service-hub-15.emergent.host for documentation and terms.
