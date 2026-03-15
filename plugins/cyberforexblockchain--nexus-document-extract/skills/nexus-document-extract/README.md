# nexus-document-extract

**NEXUS Document Extractor** — Extract structured data (names, dates, amounts, entities) from unstructured text documents using AI. Returns clean JSON with extracted fields.

Part of the [NEXUS Agent-as-a-Service Platform](https://ai-service-hub-15.emergent.host) on Cardano.

## Installation

```bash
clawhub install nexus-document-extract
```

## Quick Start

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/document-extract \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"text": "Invoice #1234 from Acme Corp. Due: March 15, 2026. Amount: $5,400.00 for consulting services.", "extract_fields": ["company", "date", "amount", "service"]}'
```

## Why nexus-document-extract?

Unlike general summarizers, this service returns machine-readable JSON with typed fields. Ideal for data pipelines and automated document processing workflows.

## Pricing

- Pay-per-request in ADA via Masumi Protocol (Cardano non-custodial escrow)
- Free sandbox available with `X-Payment-Proof: sandbox_test`

## Links

- Platform: [https://ai-service-hub-15.emergent.host](https://ai-service-hub-15.emergent.host)
- All Skills: [https://ai-service-hub-15.emergent.host/.well-known/skill.md](https://ai-service-hub-15.emergent.host/.well-known/skill.md)
