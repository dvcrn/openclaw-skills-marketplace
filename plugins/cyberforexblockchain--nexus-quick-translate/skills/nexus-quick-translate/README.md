# nexus-quick-translate

**NEXUS Quick Translator** — Ultra-fast translation for short texts — UI strings, error messages, labels, notifications. Optimized for speed over literary quality, perfect for real-time agent workflows.

Part of the [NEXUS Agent-as-a-Service Platform](https://ai-service-hub-15.emergent.host) on Cardano.

## Installation

```bash
clawhub install nexus-quick-translate
```

## Quick Start

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/quick-translate \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"text": "Payment confirmed. Your receipt has been emailed.", "target_language": "ja", "source_language": "en"}'
```

## Why nexus-quick-translate?

Unlike the full Translator service, Quick Translate is optimized for latency (<500ms) on short strings. Supports 40+ languages. Ideal for real-time chat translation and UI localization pipelines.

## Pricing

- Pay-per-request in ADA via Masumi Protocol (Cardano non-custodial escrow)
- Free sandbox available with `X-Payment-Proof: sandbox_test`

## Links

- Platform: [https://ai-service-hub-15.emergent.host](https://ai-service-hub-15.emergent.host)
- All Skills: [https://ai-service-hub-15.emergent.host/.well-known/skill.md](https://ai-service-hub-15.emergent.host/.well-known/skill.md)
