# Session Management with AgentGo

## What is a session

A session groups related browser interactions under a single ID. Using a `_sessionId` lets you:

- **Reconnect** to the same cloud browser after a disconnect
- **Share state** (cookies, localStorage) across multiple connections
- **Track** and identify your automation runs

If no `_sessionId` is provided, the server auto-generates one. For most automations you should generate your own.

## Generating a session ID

Session IDs use the format `xxxxxxxx_xxxxxxxxxxxxx` (8 hex chars + underscore + 13 hex chars):

```typescript
import crypto from "crypto";

function generateSessionId(): string {
  const a = crypto.randomBytes(4).toString("hex");       // 8 hex chars
  const b = crypto.randomBytes(7).toString("hex").slice(0, 13); // 13 hex chars
  return `${a}_${b}`;
}

// Example: "562d8e02_641ba8ac71b57"
```

## Connecting with a session ID

```typescript
import { chromium } from "playwright";

const sessionId = generateSessionId();

const options = {
  _apikey: process.env.AGENTGO_API_KEY,
  _sessionId: sessionId,
  _region: "us",
};

const serverUrl = `wss://app.browsers.live?launch-options=${encodeURIComponent(JSON.stringify(options))}`;
const browser = await chromium.connect(serverUrl);
```

## Connection options

| Option       | Description                        | Required | Default        |
| ------------ | ---------------------------------- | -------- | -------------- |
| `_apikey`    | Your AgentGo API key               | Yes      | —              |
| `_sessionId` | Session ID (`xxxxxxxx_xxxxxxxxxxxxx`) | No    | Auto-generated |
| `_region`    | Geographic region code (lowercase) | No       | `"us"`         |

## Reconnecting to an existing session

Use the same session ID to reconnect after a disconnect or from a different script:

```typescript
const existingSessionId = "562d8e02_641ba8ac71b57";

const options = {
  _apikey: process.env.AGENTGO_API_KEY,
  _sessionId: existingSessionId,
  _region: "us",
};

const serverUrl = `wss://app.browsers.live?launch-options=${encodeURIComponent(JSON.stringify(options))}`;
const browser = await chromium.connect(serverUrl);
```

## Complete example

```typescript
import crypto from "crypto";
import { chromium } from "playwright";

function generateSessionId(): string {
  const a = crypto.randomBytes(4).toString("hex");
  const b = crypto.randomBytes(7).toString("hex").slice(0, 13);
  return `${a}_${b}`;
}

async function main() {
  const sessionId = generateSessionId();
  console.log("Session:", sessionId);

  const options = {
    _apikey: process.env.AGENTGO_API_KEY,
    _sessionId: sessionId,
    _region: "us",
  };
  const serverUrl = `wss://app.browsers.live?launch-options=${encodeURIComponent(JSON.stringify(options))}`;
  const browser = await chromium.connect(serverUrl);

  try {
    const page = await browser.newPage();
    await page.goto("https://example.com");
    await page.screenshot({ path: "example.png" });
  } finally {
    await browser.close();
  }
}

main().catch(console.error);
```

## Multiple isolated contexts

Share a single session across independent browsing contexts:

```typescript
const browser = await chromium.connect(serverUrl);
const ctxA = await browser.newContext();
const ctxB = await browser.newContext();

const pageA = await ctxA.newPage();
const pageB = await ctxB.newPage();
// pageA and pageB share no cookies or storage

await ctxA.close();
await ctxB.close();
await browser.close();
```

## Save and restore auth state

Persist login state across sessions:

```typescript
// Save after login
await context.storageState({ path: "auth.json" });

// Restore in a new session
const context = await browser.newContext({ storageState: "auth.json" });
```

## Region selection

Pass `_region` to connect to a cloud browser in a specific geography:

```typescript
// North America
{ _region: "us" }  { _region: "ca" }

// Europe
{ _region: "uk" }  { _region: "de" }  { _region: "fr" }

// Asia
{ _region: "jp" }  { _region: "sg" }  { _region: "in" }

// Oceania
{ _region: "au" }
```

Choose regions close to your target websites for better performance.

## Error handling

```typescript
try {
  const browser = await chromium.connect(serverUrl);
  const page = await browser.newPage();
  await page.goto("https://example.com");
} catch (error) {
  console.error("Connection or automation failed:", error);
}
```

## Always close in finally

Cloud browsers consume AgentGo credits while open:

```typescript
const browser = await chromium.connect(serverUrl);
try {
  const page = await browser.newPage();
  await doWork(page);
} finally {
  await browser.close();
}
```

## Session limitations

- Maximum **4 concurrent pages** per browser session
- File upload/download operations are **not supported**
- Sessions timeout after **120 seconds** of inactivity
- Use appropriate waiting strategies instead of fixed timeouts
