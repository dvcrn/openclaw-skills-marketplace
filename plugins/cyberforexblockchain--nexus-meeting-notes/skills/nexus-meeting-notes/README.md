# nexus-meeting-notes

**NEXUS Meeting Scribe** — Transform raw meeting transcripts or notes into structured meeting minutes with attendees, agenda items, decisions made, action items with owners, and deadlines.

Part of the [NEXUS Agent-as-a-Service Platform](https://ai-service-hub-15.emergent.host) on Cardano.

## Installation

```bash
clawhub install nexus-meeting-notes
```

## Quick Start

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/meeting-notes \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"transcript": "John said we need to ship the API by Friday. Sarah will handle testing. Bob raised concerns about the payment integration timeline. We agreed to push payments to next sprint."}'
```

## Why nexus-meeting-notes?

Automatically identifies speakers, extracts decisions vs discussions, assigns action items to named individuals, and flags unresolved topics for follow-up.

## Pricing

- Pay-per-request in ADA via Masumi Protocol (Cardano non-custodial escrow)
- Free sandbox available with `X-Payment-Proof: sandbox_test`

## Links

- Platform: [https://ai-service-hub-15.emergent.host](https://ai-service-hub-15.emergent.host)
- All Skills: [https://ai-service-hub-15.emergent.host/.well-known/skill.md](https://ai-service-hub-15.emergent.host/.well-known/skill.md)
