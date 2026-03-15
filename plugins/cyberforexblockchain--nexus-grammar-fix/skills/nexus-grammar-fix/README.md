# nexus-grammar-fix

**NEXUS Grammar Engine** — Professional grammar correction and writing improvement. Fixes spelling, punctuation, sentence structure, and tone while preserving the author's voice.

Part of the [NEXUS Agent-as-a-Service Platform](https://ai-service-hub-15.emergent.host) on Cardano.

## Installation

```bash
clawhub install nexus-grammar-fix
```

## Quick Start

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/grammar-fix \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"text": "Their going to the store tommorow, me and him will be their to.", "style": "professional"}'
```

## Why nexus-grammar-fix?

Goes beyond spell-check: restructures awkward sentences, fixes subject-verb agreement, corrects homophones (their/there/they're), and adjusts tone for the target audience.

## Pricing

- Pay-per-request in ADA via Masumi Protocol (Cardano non-custodial escrow)
- Free sandbox available with `X-Payment-Proof: sandbox_test`

## Links

- Platform: [https://ai-service-hub-15.emergent.host](https://ai-service-hub-15.emergent.host)
- All Skills: [https://ai-service-hub-15.emergent.host/.well-known/skill.md](https://ai-service-hub-15.emergent.host/.well-known/skill.md)
