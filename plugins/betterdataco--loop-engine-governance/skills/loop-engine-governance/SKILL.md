---
name: loop-engine-governance
description: "Loop Engine — Governed Loops for OpenClaw"
---

# loop-engine-governance

Add governed decision loops to any OpenClaw workflow — human approval gates,
AI confidence guards, and full audit trails without changing your agent logic.

## Source and maintainer

- **Package:** `@loop-engine/adapter-openclaw` on npm
- **Source:** https://github.com/loopengine/loop-engine/tree/main/packages/adapter-openclaw
- **Maintainer:** Better Data, Inc. (https://betterdata.co)
- **Docs:** https://loopengine.io/docs/integrations/openclaw
- **License:** Apache-2.0 (Loop Engine packages) / MIT-0 (this skill)

## Required environment variables

This skill includes four examples. Each requires different credentials:

| Example | Required env var | Provider |
|---|---|---|
| `example-expense-approval.ts` | None | No external API calls |
| `example-ai-replenishment-claude.ts` | `ANTHROPIC_API_KEY` | Anthropic |
| `example-infrastructure-change-openai.ts` | `OPENAI_API_KEY` | OpenAI |
| `example-fraud-review-grok.ts` | `XAI_API_KEY` | xAI |

Only set the env var for the example you intend to run.
The expense approval example requires no API key and is the recommended starting point.

## Install

```bash
# Core (required for all examples)
npm install @loop-engine/sdk @loop-engine/adapter-memory @loop-engine/adapter-openclaw

# For the Claude example only
npm install @loop-engine/adapter-anthropic @anthropic-ai/sdk

# For the OpenAI example only
npm install @loop-engine/adapter-openai openai

# For the Grok example only
npm install @loop-engine/adapter-grok openai
```

Verify package maintainers before installing:
- `@loop-engine/*` — published by the `betterdata` npm org
- `@loop-engine/adapter-openclaw` — published by the `betterdata` npm org
- `@anthropic-ai/sdk` — published by Anthropic
- `openai` — published by OpenAI

## Data sent to external providers

**Read this before running the AI examples.**

The AI examples send structured context to external LLM provider APIs as part
of the loop actor submission. This includes whatever you pass as `evidence`
to `createSubmission()`.

The included examples use synthetic illustrative data only:
- `example-ai-replenishment-claude.ts` — fictional inventory figures
- `example-infrastructure-change-openai.ts` — fictional infrastructure metadata
- `example-fraud-review-grok.ts` — fictional transaction and cardholder data

**Before using in production:**
- Do not send real PII, cardholder data, or regulated information to LLM
  providers without reviewing their data processing agreements
- Review your LLM provider's data retention and training policies
- For regulated industries (healthcare, finance, pharma), confirm your
  provider agreement covers the data classification you intend to send
- Consider redacting or tokenizing sensitive fields before passing as evidence

Loop Engine captures evidence in its local audit trail. The evidence object
is also sent to the LLM provider API as part of the actor prompt. These are
two separate destinations — plan accordingly.
Loop Engine itself never transmits data externally. Only the AI provider adapter calls send data — and only what you explicitly pass as `evidence`.

## What this skill does

Wires [Loop Engine](https://loopengine.io) into OpenClaw so that any workflow
step can be governed by:

- **Human approval gates** — transitions only a named human actor can trigger
- **AI confidence guards** — block AI recommendations below a threshold
- **Evidence capture** — attach structured context to every decision
- **Audit trail** — every transition is attributed, timestamped, and immutable

## How it works with OpenClaw

```
OpenClaw agent proposes action
        ↓
Loop Engine evaluates guards       ← @loop-engine/adapter-openclaw
        ↓
Human approves (if policy requires)
        ↓
OpenClaw executes the approved action
```

Guards are enforced at the runtime level — not in prompts.

## How governance weighting works

Three types of weighting evaluated in sequence — all must pass:

**1. Confidence threshold (numeric gate)**
Every AI actor submission carries a 0–1 confidence score. The guard blocks
the transition if the score falls below the configured threshold.

**2. Guard priority (hard vs soft)**
Hard failures block the transition regardless of everything else.
A human-only guard is an absolute block — no confidence score overrides it.

**3. Evidence completeness (structural gate)**
The evidence-required guard checks for specific fields before allowing a
transition. Missing any required field blocks the transition.

**Evaluation order:**
```
1. Actor authorized for this signal?
2. Required evidence fields present?
3. Confidence score above threshold?
4. All hard guards pass?
```

## Quick start (no API key required)

```typescript
import { createLoopSystem, parseLoopYaml, CommonGuards } from '@loop-engine/sdk'
import { MemoryAdapter } from '@loop-engine/adapter-memory'

const definition = parseLoopYaml(`
  loopId: approval.workflow
  name: Approval Workflow
  version: 1.0.0
  initialState: pending
  states:
    - stateId: pending
      label: Pending Approval
    - stateId: approved
      label: Approved
      terminal: true
  transitions:
    - transitionId: approve
      from: pending
      to: approved
      signal: approve
      allowedActors: [human]
      guards: [human-only]
`)

const system = createLoopSystem({
  storage: new MemoryAdapter(),
  guards: CommonGuards,
})

const loop = await system.startLoop({ definition, context: {} })

await system.transition({
  loopId: loop.loopId,
  signalId: 'approve',
  actor: { id: 'alice', type: 'human' },
  evidence: { reviewNote: 'Approved' },
})
```

## Examples included

| File | Provider | API key |
|---|---|---|
| `example-expense-approval.ts` | None | Not required |
| `example-ai-replenishment-claude.ts` | Anthropic Claude | `ANTHROPIC_API_KEY` |
| `example-infrastructure-change-openai.ts` | OpenAI GPT-4o | `OPENAI_API_KEY` |
| `example-fraud-review-grok.ts` | xAI Grok 3 | `XAI_API_KEY` |

All examples use synthetic data. Do not use real PII or regulated data
without reviewing your provider's data processing agreements.

## License

MIT-0 — free to use, modify, and redistribute. No attribution required.

`@loop-engine/*` packages: Apache-2.0
Provider SDKs: licensed by their respective maintainers