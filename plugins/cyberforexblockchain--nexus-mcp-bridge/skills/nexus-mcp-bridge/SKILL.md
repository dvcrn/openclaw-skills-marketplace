---
name: nexus-mcp-bridge
description: "Bridge agent to MCP-compatible tool servers including IPFS pinning, GitHub operations, and filesystem tools. Execute MCP tool calls through a unified interface."
---

# NEXUS MCP Bridge

> NEXUS Agent-as-a-Service on Cardano

## When to use

Your agent needs to interact with MCP tool servers — pin files to IPFS, read/write GitHub repos, or execute filesystem operations through the Model Context Protocol.

## What makes this different

First MCP bridge available as a paid service on Cardano. Supports IPFS (pin/unpin/cat), GitHub (read/write/PR), and extensible to any MCP-compatible server.

## Steps

1. Prepare your input payload as JSON.
2. Send a POST request to the NEXUS endpoint with `X-Payment-Proof` header.
3. Parse the structured JSON response.

### API Call

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/mcp-bridge \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"mcp_server": "ipfs", "operation": "pin", "parameters": {"content": "Hello from NEXUS agent", "filename": "agent-output.txt"}}'
```

**Endpoint:** `https://ai-service-hub-15.emergent.host/api/original-services/mcp-bridge`
**Method:** POST
**Headers:**
- `Content-Type: application/json`
- `X-Payment-Proof: <masumi_payment_id>` (use `sandbox_test` for free sandbox testing)

## External Endpoints

| URL | Method | Data Sent |
|-----|--------|-----------|
| `https://ai-service-hub-15.emergent.host/api/original-services/mcp-bridge` | POST | Input parameters as JSON body |

## Security & Privacy

- All requests are encrypted via HTTPS/TLS to `https://ai-service-hub-15.emergent.host`.
- No user data is stored permanently. Requests are processed in memory and discarded.
- Payment verification uses the Masumi Protocol on Cardano (non-custodial escrow).
- This skill requires network access only. No filesystem or shell permissions needed.

## Model Invocation Note

This skill calls the NEXUS AI service API which processes your input using large language models server-side. The AI generates a response based on your input and returns structured data. You may opt out by not installing this skill.

## Trust Statement

By installing this skill, your input data is transmitted to NEXUS (https://ai-service-hub-15.emergent.host) for AI processing. All payments are non-custodial via Cardano blockchain. Visit https://ai-service-hub-15.emergent.host for documentation and terms. Only install if you trust NEXUS as a service provider.
