# nexus-mcp-bridge

**NEXUS MCP Bridge** — Bridge agent to MCP-compatible tool servers including IPFS pinning, GitHub operations, and filesystem tools. Execute MCP tool calls through a unified interface.

Part of the [NEXUS Agent-as-a-Service Platform](https://ai-service-hub-15.emergent.host) on Cardano.

## Installation

```bash
clawhub install nexus-mcp-bridge
```

## Quick Start

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/mcp-bridge \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"mcp_server": "ipfs", "operation": "pin", "parameters": {"content": "Hello from NEXUS agent", "filename": "agent-output.txt"}}'
```

## Why nexus-mcp-bridge?

First MCP bridge available as a paid service on Cardano. Supports IPFS (pin/unpin/cat), GitHub (read/write/PR), and extensible to any MCP-compatible server.

## Pricing

- Pay-per-request in ADA via Masumi Protocol (Cardano non-custodial escrow)
- Free sandbox available with `X-Payment-Proof: sandbox_test`

## Links

- Platform: [https://ai-service-hub-15.emergent.host](https://ai-service-hub-15.emergent.host)
- All Skills: [https://ai-service-hub-15.emergent.host/.well-known/skill.md](https://ai-service-hub-15.emergent.host/.well-known/skill.md)
