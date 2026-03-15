---
name: drip-billing
description: "Track AI agent usage and costs with Drip metered billing. Use when integrating @drip-sdk/node for usage metrics (`trackUsage`), run events (`recordRun`, `startRun`, `emitEvent`, `endRun`), and framework auto-tracking (LangChain callbacks, middleware). Send sanitized metadata only, never raw prompts/outputs/PII/secrets, and prefer least-privilege `pk_` keys."
---

# Drip Billing Skill

Integrate Drip billing telemetry with strict data-minimization and key-safety rules.

## Quick Reference

| Situation | Action |
|-----------|--------|
| Need credentials | Require `DRIP_API_KEY`; optionally set `DRIP_BASE_URL`, `DRIP_WORKFLOW_ID` |
| Choosing key type | Use `pk_` keys by default; use `sk_` only for trusted server-side admin flows |
| Handling secret keys | Never provide `sk_` keys to untrusted agents, browser/mobile clients, or third-party runtimes |
| Sending telemetry | Send usage quantities, customer IDs, run lifecycle events, and sanitized operational metadata only |
| Auto-tracking setup | Always pass explicit `metadataAllowlist` and `redactMetadataKeys` |
| Before production | Verify installed SDK version still enforces metadata sanitization in callback/middleware paths |
| Installing SDK | Pin package version and lockfile; verify npm package provenance before use |
| Registry metadata check | Ensure published/registry metadata marks `DRIP_API_KEY` as required and deploy tooling exports it |

## Instruction Scope

This skill is limited to billing and telemetry integration:

- `trackUsage` for metered usage quantities
- `recordRun` for complete run summaries
- `startRun` / `emitEvent` / `endRun` for streaming run timelines
- Auto-tracking wrappers (LangChain callback handlers and middleware)

This skill does not cover business logic, auth design, or non-Drip observability stacks.

## Safety Contract

### Data allowed

- Usage quantities (meter + numeric quantity)
- Customer identifiers (`customerId`, `externalCustomerId`)
- Run lifecycle and event types (status, duration, step type)
- Sanitized operational metadata (for example model family, latency, status code, hashed IDs)

### Data forbidden

- Raw prompts, completions, or model outputs
- PII, passwords, tokens, API keys, secrets, environment variables
- Raw request/response bodies, file contents, or source code

### Metadata rules

- Use explicit allowlists; drop keys not explicitly permitted.
- Redact sensitive keys even if accidentally present.
- Drop non-primitive metadata values.
- Truncate long metadata strings.
- Prefer hashed values (for example `queryHash`) over raw user content.

## Install & Provenance Policy

`@drip-sdk/node` is fetched from npm (external dependency). Treat install/runtime as a supply-chain boundary.

```bash
npm install @drip-sdk/node@<pinned-version>
```

- Use pinned versions in `package.json` and a committed lockfile.
- Verify package provenance before supplying credentials:
  - npm: https://www.npmjs.com/package/@drip-sdk/node
  - repo: https://github.com/MichaelLevin5908/drip
  - sdk repo (node): https://github.com/MichaelLevin5908/drip-sdk
  - sdk repo (python): https://github.com/MichaelLevin5908/drip-sdk-python
- Do not run ad-hoc remote package execution flows (`npx <package>`) for this skill.

## Registry Consistency

- `DRIP_API_KEY` is required for this skill.
- If a registry listing or generated metadata says no required env vars, treat that as stale metadata.
- Update registry metadata and/or deploy tooling so `DRIP_API_KEY` is always set.

## Runtime Trust Boundary

This skill file is instruction-only. It does not bundle the runtime SDK implementation.

- Documented sanitization controls are expected behavior.
- Actual enforcement depends on the installed `@drip-sdk/node` version.
- Re-verify sanitization behavior when upgrading SDK versions.

## Environment Setup

```bash
# Required
export DRIP_API_KEY=pk_live_...

# Optional
# export DRIP_BASE_URL=https://api.drippay.dev/v1
# export DRIP_WORKFLOW_ID=research-agent

# Only for trusted server-side admin operations:
# export DRIP_API_KEY=sk_live_...
```

## Key Scoping

- Prefer `pk_live_` / `pk_test_` for all skill and agent integrations.
- Use `sk_live_` / `sk_test_` only when admin endpoints are required (webhook CRUD, key management, feature flags).
- Treat `sk_` keys as high impact credentials with broad API authority.
- Validate `pk_` vs `sk_` action semantics with the provider for your workspace before enabling production billing writes.

## Core Usage Patterns

### Basic metering

```typescript
import { Drip } from '@drip-sdk/node';

const drip = new Drip({
  apiKey: process.env.DRIP_API_KEY,
  baseUrl: process.env.DRIP_BASE_URL,
});

await drip.trackUsage({
  customerId: 'customer_123',
  meter: 'llm_tokens',
  quantity: 1500,
  metadata: { modelFamily: 'gpt-4', latencyMs: 820 },
});
```

### Complete run summary

```typescript
await drip.recordRun({
  customerId: 'cus_123',
  workflow: process.env.DRIP_WORKFLOW_ID ?? 'research-agent',
  events: [
    { eventType: 'llm.call', model: 'gpt-4', quantity: 1700, units: 'tokens' },
    { eventType: 'tool.call', name: 'web-search', duration: 1500 },
  ],
  status: 'COMPLETED',
});
```

### Streaming run events

```typescript
const run = await drip.startRun({
  customerId: 'cus_123',
  workflowId: process.env.DRIP_WORKFLOW_ID ?? 'document-processor',
});

await drip.emitEvent({
  runId: run.id,
  eventType: 'llm.call',
  model: 'gpt-4',
  quantity: 1700,
  units: 'tokens',
});

await drip.endRun(run.id, { status: 'COMPLETED' });
```

## Auto-Tracking (Fail-Closed Configuration)

### LangChain callback handler

```typescript
import { DripCallbackHandler } from '@drip-sdk/node/langchain';

const handler = new DripCallbackHandler({
  apiKey: process.env.DRIP_API_KEY,
  baseUrl: process.env.DRIP_BASE_URL,
  customerId: 'cus_123',
  workflow: process.env.DRIP_WORKFLOW_ID ?? 'langchain',
  metadata: { integration: 'langchain' },
  metadataAllowlist: ['integration', 'model', 'latencyMs', 'promptCount', 'queryHash', 'statusCode'],
  redactMetadataKeys: ['prompt', 'input', 'output', 'response', 'authorization', 'token', 'apiKey'],
});
```

### Framework middleware

```typescript
import { withDrip } from '@drip-sdk/node/middleware';

export const POST = withDrip({
  meter: 'api_calls',
  quantity: 1,
  metadataAllowlist: ['integration', 'route', 'statusCode', 'latencyMs'],
  redactMetadataKeys: ['authorization', 'cookie', 'prompt', 'responseBody'],
}, handler);
```

## Verification Checklist (Before Production)

1. Verify installed SDK version and lockfile pinning.
2. Confirm metadata allowlist/redaction is explicitly configured in your integration code.
3. Inspect callback/middleware sanitization paths in the installed SDK release before enabling auto-tracking.
4. Confirm telemetry payloads do not include raw prompts/outputs/PII/secrets.
5. Confirm `sk_` keys are not exposed to untrusted runtimes.
6. Confirm provider-documented `pk_` capabilities for your account (do not assume charge/create semantics without validation).
7. If package provenance or `pk_`/`sk_` semantics cannot be validated, run only in isolated staging and do not provide any `sk_` keys.

## Reference

See [references/API.md](references/API.md) for SDK API details and integration examples.
