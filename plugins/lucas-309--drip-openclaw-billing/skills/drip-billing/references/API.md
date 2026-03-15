# Drip SDK API Reference

## Security & Key Scoping

Drip issues two key types. **Always use the least-privileged key that meets your needs.**

| Key Type | Prefix | Access | Recommended For |
|----------|--------|--------|-----------------|
| **Public Key** | `pk_live_` / `pk_test_` | Provider-defined least-privilege integration access (validate exact actions per account/workspace) | **Default for skill and agent integrations** |
| **Secret Key** | `sk_live_` / `sk_test_` | Full API access including webhooks, API key management, feature flags | Server-side admin only |

> **Use `pk_` keys by default.** Use least-privilege keys for agent integrations and reserve `sk_` keys for trusted server-side admin operations.
> Never provide `sk_` keys to untrusted agents, browser/mobile clients, or third-party runtimes.
> Validate `pk_` vs `sk_` action semantics with the provider for your workspace before enabling production writes.

**Metadata safety:** Send only sanitized, non-sensitive metadata. Never include PII, secrets, raw prompts, model outputs, or environment variables. Use metadata only for operational context (model family, tool name, status code, latency, hashed IDs).

---

## Provenance & Execution Policy

- Package: https://www.npmjs.com/package/@drip-sdk/node
- Source: https://github.com/MichaelLevin5908/drip
- This skill is instruction-only and does not bundle `@drip-sdk/node` source code.
- Use pinned dependency versions in `package.json` + lockfile.
- Treat SDK installation as an external npm supply-chain dependency and verify provenance before installation.
- This skill does not recommend running remote package executors (for example `npx <package>`) before credentials are configured.
- Prefer direct SDK integration in your codebase rather than ad-hoc runtime package execution.

---

## SDK Quick Setup

```bash
# Recommended: public key (pk_) — default least-privilege key for agent integrations
export DRIP_API_KEY=pk_live_...

# Optional: trusted API base URL override
# export DRIP_BASE_URL=https://api.drippay.dev/v1

# Optional: workflow grouping default for run telemetry
# export DRIP_WORKFLOW_ID=research-agent

# Only for admin operations (webhooks, key management, feature flags):
# export DRIP_API_KEY=sk_live_...
```

> **Key scoping:** Treat `pk_` keys as default least-privilege integration credentials and `sk_` keys as broad admin credentials. Confirm exact permissions with vendor documentation/support for your account before assuming which write operations are allowed.

**Node.js:**
```typescript
import { drip } from '@drip-sdk/node';

// Reads DRIP_API_KEY from environment automatically (pk_live_... recommended)
await drip.trackUsage({ customerId: 'cust_123', meter: 'api_calls', quantity: 1 });
```

**Python:**
```python
from drip import drip

# Reads DRIP_API_KEY from environment automatically (pk_live_... recommended)
drip.track_usage(customer_id="cust_123", meter="api_calls", quantity=1)
```

The `drip` singleton reads from `DRIP_API_KEY` automatically.
Only `DRIP_API_KEY` is required. `DRIP_BASE_URL` and `DRIP_WORKFLOW_ID` are optional.

## Metadata Policy Controls

Use these controls to enforce least-privilege telemetry at runtime:

```typescript
import { DripCallbackHandler } from '@drip-sdk/node/langchain';

const handler = new DripCallbackHandler({
  customerId: 'cus_123',
  metadata: { integration: 'langchain', tenant: 'acme' },
  metadataAllowlist: ['integration', 'tenant', 'model', 'latencyMs', 'promptCount', 'queryHash'],
  redactMetadataKeys: ['tenantEmail', 'userEmail', 'apiKey', 'token'],
});
```

Before enabling auto-tracking in production, verify the installed SDK version still sanitizes metadata in callback/middleware paths (allowlist filtering, explicit redact keys, non-primitive drop, and string truncation).
This reference file documents expected controls, but runtime enforcement depends on the installed SDK package and version.
If package provenance or key semantics cannot be validated, run integrations only in isolated/staging environments and do not provide any `sk_` keys.

For framework middleware wrappers (`withDrip`, `dripMiddleware`), pass the same keys:

```typescript
withDrip({
  meter: 'api_calls',
  quantity: 1,
  metadata: { integration: 'api', route: '/v1/search' },
  metadataAllowlist: ['integration', 'route', 'latencyMs', 'statusCode'],
  redactMetadataKeys: ['authorization', 'cookie', 'prompt', 'responseBody'],
}, handler);
```

---

## Core Methods

### `ping()`

Verify API connection.

```typescript
await drip.ping();
// Returns: { status: 'ok' }
```

### `trackUsage(params)`

Record metered usage.

```typescript
await drip.trackUsage({
  customerId: string;      // Required: Customer identifier
  meter: string;           // Required: Meter name (e.g., 'llm_tokens')
  quantity: number;        // Required: Usage quantity
  metadata?: object;       // Optional: operational context only (model name, tool name) — never PII or secrets
});
```

### `recordRun(params)`

Log a complete agent run (simplified, single call).

```typescript
await drip.recordRun({
  customerId: string;      // Required: Customer identifier
  workflow: string;        // Required: Workflow/agent name
  events: Event[];         // Required: Array of events
  status: 'COMPLETED' | 'FAILED';
});
```

### `startRun(params)`

Start an execution trace for streaming events.

```typescript
const run = await drip.startRun({
  customerId: string;      // Required: Customer identifier
  workflowId: string;      // Required: Workflow ID or slug
  correlationId?: string;  // Optional: Trace ID for distributed tracing
  externalRunId?: string;   // Optional: Your external run ID
  metadata?: object;        // Optional: Run metadata (operational context only — never PII or secrets)
});
// Returns: { id: string, ... }
```

### `emitEvent(params)`

Log an event within an active run.

```typescript
await drip.emitEvent({
  runId: string;           // Required: Run ID from startRun
  eventType: string;       // Required: Event type
  // Event-specific fields:
  model?: string;          // For LLM events
  inputTokens?: number;    // For LLM events
  outputTokens?: number;   // For LLM events
  name?: string;           // For tool events
  duration?: number;       // Duration in ms
  status?: string;         // 'success' | 'error'
  description?: string;    // Human-readable description
  metadata?: object;       // Optional: operational context only — never include PII, secrets, or raw user content
});
```

### `emitEventsBatch(params)`

Batch log multiple events.

```typescript
await drip.emitEventsBatch({
  runId: string;
  events: Event[];
});
```

### `endRun(runId, params)`

Complete an execution trace.

```typescript
await drip.endRun(runId, {
  status: 'COMPLETED' | 'FAILED';
  errorMessage?: string;   // If status is 'FAILED' — use a short message, never include stack traces with env vars
  metadata?: object;       // Optional: operational context only
});
```

### `getRunTimeline(runId)`

Get execution timeline for a run.

```typescript
const timeline = await drip.getRunTimeline(runId);
// Returns: { events: Event[], summary: string }
```

## Customer Management

### `createCustomer(params)`

At least one of `externalCustomerId` or `onchainAddress` is required.

```typescript
await drip.createCustomer({
  externalCustomerId?: string;  // Your internal user/account ID
  onchainAddress?: string;      // Customer's Ethereum address (for on-chain billing)
  isInternal?: boolean;         // Mark as internal (non-billing). Default: false
  metadata?: object;            // Optional: operational context only — never include PII or secrets
});
```

### `getCustomer(customerId)`

```typescript
const customer = await drip.getCustomer('customer_123');
```

### `listCustomers(options)`

```typescript
const customers = await drip.listCustomers({
  limit?: number;
  offset?: number;
});
```

## Error Handling

```typescript
import { Drip, DripError } from '@drip-sdk/node';

try {
  await drip.trackUsage({ ... });
} catch (error) {
  if (error instanceof DripError) {
    console.error(`Error: ${error.message} (${error.code})`);
    // error.code: 'INVALID_API_KEY' | 'RATE_LIMITED' | 'VALIDATION_ERROR' | ...
  }
}
```

## Status Values

| Status | Description |
|--------|-------------|
| `PENDING` | Run created but not started |
| `RUNNING` | Run in progress |
| `COMPLETED` | Run finished successfully |
| `FAILED` | Run failed with error |

---

## Auto-Tracking Integrations

### LangChain (Auto-Track LLM Usage)

**Node.js:**
```typescript
import { DripCallbackHandler } from '@drip-sdk/node/langchain';
const handler = new DripCallbackHandler({
  customerId: 'cus_123',
  workflow: process.env.DRIP_WORKFLOW_ID ?? 'langchain',
  metadata: { integration: 'langchain' },
  metadataAllowlist: ['integration', 'model', 'latencyMs', 'promptCount', 'queryHash', 'statusCode'],
  redactMetadataKeys: ['prompt', 'input', 'output', 'response', 'apiKey', 'token', 'authorization'],
});
const llm = new ChatOpenAI({ callbacks: [handler] });
// LLM calls are auto-tracked with explicit metadata policy controls.
```

**Python:**
```python
from drip.integrations import DripCallbackHandler
handler = DripCallbackHandler(customer_id="cus_123")
llm = ChatOpenAI(callbacks=[handler])
```

### Framework Middleware

**Next.js:**
```typescript
import { withDrip } from '@drip-sdk/node/middleware';
export const POST = withDrip({
  meter: 'api_calls',
  quantity: 1,
  metadataAllowlist: ['integration', 'route', 'statusCode', 'latencyMs'],
  redactMetadataKeys: ['authorization', 'cookie', 'prompt', 'responseBody'],
}, handler);
```

**Express:**
```typescript
import { dripMiddleware } from '@drip-sdk/node/middleware';
app.use('/api', dripMiddleware({
  meter: 'api_calls',
  quantity: 1,
  metadataAllowlist: ['integration', 'route', 'statusCode', 'latencyMs'],
  redactMetadataKeys: ['authorization', 'cookie', 'prompt', 'responseBody'],
}));
```

**FastAPI:**
```python
from drip.middleware.fastapi import DripMiddleware
app.add_middleware(DripMiddleware, meter="api_calls", quantity=1)
```

**Flask:**
```python
from drip.middleware.flask import drip_middleware
@app.route("/api/generate", methods=["POST"])
@drip_middleware(meter="api_calls", quantity=1)
def generate():
    return {"success": True}
```
