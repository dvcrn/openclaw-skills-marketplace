# nexus-sentiment-analysis

**NEXUS Sentiment Analyzer** — Analyze text for emotional tone, opinion polarity, subjectivity, and intensity. Returns sentiment scores with per-sentence breakdown and detected emotions.

Part of the [NEXUS Agent-as-a-Service Platform](https://ai-service-hub-15.emergent.host) on Cardano.

## Installation

```bash
clawhub install nexus-sentiment-analysis
```

## Quick Start

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/sentiment-analysis \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"text": "The product arrived quickly and works great, but the packaging was damaged and customer support took 3 days to respond.", "granularity": "sentence"}'
```

## Why nexus-sentiment-analysis?

Goes beyond positive/negative: detects mixed sentiment, sarcasm indicators, urgency levels, and specific emotions (frustration, satisfaction, confusion). Provides per-sentence breakdown for long texts.

## Pricing

- Pay-per-request in ADA via Masumi Protocol (Cardano non-custodial escrow)
- Free sandbox available with `X-Payment-Proof: sandbox_test`

## Links

- Platform: [https://ai-service-hub-15.emergent.host](https://ai-service-hub-15.emergent.host)
- All Skills: [https://ai-service-hub-15.emergent.host/.well-known/skill.md](https://ai-service-hub-15.emergent.host/.well-known/skill.md)
