---
name: ampersend
description: "Ampersend CLI for agent payments"
---

# Ampersend CLI

CLI for Ampersend smart account wallets. Enables agents to make payments.

## Setup

```bash
npm install -g @ampersend_ai/ampersend-sdk@beta
```

If not configured, commands return setup instructions. To configure:

```bash
ampersend config init
# {"ok": true, "data": {"sessionKeyAddress": "0x...", "status": "pending_agent"}}

# Register sessionKeyAddress in Ampersend dashboard, then:
ampersend config set-agent <SMART_ACCOUNT_ADDRESS>
# {"ok": true, "data": {"status": "ready", ...}}

ampersend config status
# {"ok": true, "data": {"status": "ready", "source": "file", ...}}
# source: "env" | "file" | "none"
```

## Commands

### fetch

Make HTTP requests with automatic x402 payment handling.

```bash
ampersend fetch <url>
ampersend fetch -X POST -H "Content-Type: application/json" -d '{"key":"value"}' <url>
```

| Option        | Description                                  |
| ------------- | -------------------------------------------- |
| `-X <method>` | HTTP method (default: GET)                   |
| `-H <header>` | Header as "Key: Value" (repeat for multiple) |
| `-d <data>`   | Request body                                 |

## Output

All commands return JSON. Check `ok` first.

```json
{ "ok": true, "data": { ... } }
```

```json
{ "ok": false, "error": { "code": "...", "message": "..." } }
```

For `fetch`, success includes `data.status`, `data.body`, and `data.payment` (when payment made).
