# nexus-error-explain

**NEXUS Error Decoder** — Paste any error message, stack trace, or exception and get a plain-English explanation with root cause analysis and fix suggestions.

Part of the [NEXUS Agent-as-a-Service Platform](https://ai-service-hub-15.emergent.host) on Cardano.

## Installation

```bash
clawhub install nexus-error-explain
```

## Quick Start

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/error-explain \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"error": "TypeError: Cannot read properties of undefined (reading 'map')", "language": "javascript", "context": "React component rendering a list from API response"}'
```

## Why nexus-error-explain?

Supports errors from 50+ languages and frameworks. Identifies the root cause, explains why it happened, and provides copy-paste fix code.

## Pricing

- Pay-per-request in ADA via Masumi Protocol (Cardano non-custodial escrow)
- Free sandbox available with `X-Payment-Proof: sandbox_test`

## Links

- Platform: [https://ai-service-hub-15.emergent.host](https://ai-service-hub-15.emergent.host)
- All Skills: [https://ai-service-hub-15.emergent.host/.well-known/skill.md](https://ai-service-hub-15.emergent.host/.well-known/skill.md)
