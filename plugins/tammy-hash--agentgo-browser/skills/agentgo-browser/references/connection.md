# AgentGo Connection Reference

## How it works

AgentGo exposes a Playwright-compatible WebSocket server. Connect with `chromium.connect(wss://...)` using `playwright@1.51.0` — no local browser binary needed.

> **Important:** Use `playwright@1.51.0` exactly. Newer versions have protocol incompatibilities with AgentGo's server.

## Connection URL format

```
wss://app.browsers.live?launch-options=<url-encoded-json>
```

## Minimal connection

```typescript
import { chromium } from "playwright";

const opts = encodeURIComponent(JSON.stringify({ _apikey: process.env.AGENTGO_API_KEY }));
const browser = await chromium.connect(`wss://app.browsers.live?launch-options=${opts}`);
```

## With timeout

```typescript
const browser = await chromium.connect(serverUrl, { timeout: 30000 });
```

## Authentication

`_apikey` is the only required field. Always read from env:

```typescript
if (!process.env.AGENTGO_API_KEY)
  throw new Error("AGENTGO_API_KEY is not set");
```

Get your API key at **https://app.agentgo.live/** — free credits, no credit card required.
