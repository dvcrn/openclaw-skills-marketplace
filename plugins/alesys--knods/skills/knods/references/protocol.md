# OpenClaw Gateway Protocol (Knods)

## Setup

1. Open Iris panel in Knods and click the gear icon.
2. Click `Add Connection`, set name/icon.
3. Copy `Gateway Token` and `Polling URL`.

## Polling Loop

Implement two HTTP calls in a loop.

### 1) Poll for messages

```http
GET {knods_url}/api/agent-gateway/{connectionId}/updates?token={gateway_token}
```

Response:

```json
{
  "messages": [
    {
      "messageId": "uuid",
      "message": "User message (first message includes context)",
      "history": [
        { "role": "user", "content": "..." },
        { "role": "assistant", "content": "..." }
      ]
    }
  ]
}
```

- Empty `messages` array means no work.
- Poll every 1-2 seconds.

### 2) Send streamed response

```http
POST {knods_url}/api/agent-gateway/{connectionId}/respond?token={gateway_token}
Content-Type: application/json
```

Send one or more chunk payloads:

```json
{ "messageId": "uuid", "delta": "Hello " }
{ "messageId": "uuid", "delta": "world!" }
```

Then completion payload:

```json
{ "messageId": "uuid", "done": true }
```

## Canvas Actions in Assistant Text

Knods parses action blocks embedded in assistant text:

### Single node

```text
[KNODS_ACTION]{"action":"addNode","nodeType":"FluxImage"}[/KNODS_ACTION]
```

### Multi-node flow

```text
[KNODS_ACTION]{"action":"addFlow","nodes":[{"id":"n1","nodeType":"TextInput"},{"id":"n2","nodeType":"FluxImage"},{"id":"n3","nodeType":"Output"}],"edges":[{"source":"n1","target":"n2"},{"source":"n2","target":"n3"}]}[/KNODS_ACTION]
```

Rules:

- Include action blocks only when mutating canvas.
- Keep JSON valid and compact.
- End each flow with `Output`.
- Ensure every edge references an existing node id.

## Available Node Types (Default Catalog)

- Text generators: `ChatGPT`, `Claude`, `Gemini`
- Image generators: `GPTImage`, `FluxImage`, `FalAIImage`
- Video generators: `Veo31Video`, `WanAnimate`
- Inputs: `TextInput`, `ImagePanel`, `Dictation`
- Output: `Output`

When first-message context provides a node catalog, prefer that list over defaults.

## Timeouts

- Unclaimed messages time out after about 2 minutes.
- Keep first response chunk fast.

## Authentication

- Use `gateway_token` query parameter (`token=...`) for gateway endpoints.
- Token format: `gw_` prefix, fixed-length token string.
- Regeneration invalidates previous token.

## Environment Configuration Patterns

Support both deployment patterns:

1. Full polling URL in env:
- `KNODS_BASE_URL=https://.../api/agent-gateway/<connectionId>/updates?token=<gateway_token>`

2. Base connection URL + separate token:
- `KNODS_BASE_URL=https://.../api/agent-gateway/<connectionId>`
- `KNODS_GATEWAY_TOKEN=<gateway_token>`

In both cases, use the same connection root for `/respond`.

## Restart Requirement After Env Changes

Bridge processes usually read env only at startup. After changing URL/token values, restart the bridge.

Example (systemd user service):

```bash
systemctl --user restart knods-iris-bridge.service
systemctl --user status knods-iris-bridge.service
```
