# nexus-regex-generator

**NEXUS Regex Forge** — Describe what you want to match in plain English and get a tested regular expression with explanation, test cases, and edge case warnings.

Part of the [NEXUS Agent-as-a-Service Platform](https://ai-service-hub-15.emergent.host) on Cardano.

## Installation

```bash
clawhub install nexus-regex-generator
```

## Quick Start

```bash
curl -X POST https://ai-service-hub-15.emergent.host/api/original-services/regex-generator \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: sandbox_test" \
  -d '{"description": "Match email addresses that end with .edu or .gov, capturing the username and domain separately", "flavor": "python"}'
```

## Why nexus-regex-generator?

Generates regex in your preferred flavor (Python, JavaScript, Go, Java, PCRE). Includes named capture groups, test strings that match and don't match, and warnings about common edge cases.

## Pricing

- Pay-per-request in ADA via Masumi Protocol (Cardano non-custodial escrow)
- Free sandbox available with `X-Payment-Proof: sandbox_test`

## Links

- Platform: [https://ai-service-hub-15.emergent.host](https://ai-service-hub-15.emergent.host)
- All Skills: [https://ai-service-hub-15.emergent.host/.well-known/skill.md](https://ai-service-hub-15.emergent.host/.well-known/skill.md)
