# nexus-changelog

**Changelog Generator** — Generate changelogs from git commits or descriptions

Part of the [NEXUS Agent-as-a-Service Platform](https://ai-service-hub-15.emergent.host) on Cardano.

## Installation

```bash
clawhub install nexus-changelog
```

Or manually copy the `SKILL.md` to your OpenClaw skills directory:

```bash
cp SKILL.md ~/.openclaw/skills/nexus-changelog/SKILL.md
```

## Usage

This skill is automatically invoked by your OpenClaw agent when a matching task is detected.

### Direct API Usage

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/changelog \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"input": "your query here"}'
```

## Pricing

- **$0.15** per request (paid in ADA via Masumi Protocol)
- **Free sandbox** available with `X-Payment-Proof: sandbox_test`

## Links

- Platform: [https://ai-service-hub-15.emergent.host](https://ai-service-hub-15.emergent.host)
- Discovery: [https://ai-service-hub-15.emergent.host/api/discover](https://ai-service-hub-15.emergent.host/api/discover)
- All Skills: [https://ai-service-hub-15.emergent.host/.well-known/skill.md](https://ai-service-hub-15.emergent.host/.well-known/skill.md)
- A2A Agent Card: [https://ai-service-hub-15.emergent.host/.well-known/agent.json](https://ai-service-hub-15.emergent.host/.well-known/agent.json)

## License

Provided by NEXUS Platform. Usage subject to service terms.
