---
name: knods
description: "Build and modify Knods visual AI workflows using the OpenClaw Gateway polling protocol. Use when Knods sends polling payloads with fields like messageId/message/history and responses must be streamed back as delta chunks with optional [KNODS_ACTION] JSON blocks in assistant text. Includes a packaged bridge runtime and installer for persistent polling."
---

# Knods

## Overview

Handle Knods chat turns that request new flows or edits on a visual canvas. Parse Knods polling payload messages, generate assistant text, and include `[KNODS_ACTION]...[/KNODS_ACTION]` blocks when the canvas should change.

## Workflow

1. Parse incoming payload fields.
- Treat `message` as the primary request.
- Use `history` for continuity.
- On first turn in a conversation, expect prepended context in `message` describing node types and action rules.
- Use `messageId` to map all response chunks to the correct message.

2. Choose whether to emit a canvas action block.
- Use `addNode` for single-node additions.
- Use `addFlow` for multi-node workflows or any request requiring edges.
- If the user only asks a question, respond with normal text and no action block.

3. Build strict action JSON.
- Wrap each action exactly as:
  - `[KNODS_ACTION]{"action":"addNode",...}[/KNODS_ACTION]`
  - `[KNODS_ACTION]{"action":"addFlow",...}[/KNODS_ACTION]`
- For `addFlow`, ensure every edge `source` and `target` references an existing node id.
- Always end flows with an `Output` node.
- Never connect two generator nodes directly; route through `Output` or through appropriate input/output structure.
- Use stable node IDs (for example `input_1`, `image_1`, `output_1`) so follow-up edits are easy.
- Avoid unknown keys in action JSON.

4. Stream response back to Knods.
- Send assistant text as delta chunks to `/respond` for the same `messageId`.
- Send `{"messageId":"...","done":true}` when complete.
- Keep first chunk quick to avoid timeout perception.

## Output Rules

- Return normal assistant text; do not wrap the full reply in a custom envelope.
- Include `[KNODS_ACTION]...[/KNODS_ACTION]` inline only when a canvas mutation is intended.
- Do not mention internal polling URLs/tokens in user-facing text.
- Keep action JSON valid and compact.

## Flow Design Heuristics

- Build the smallest flow that satisfies the request.
- Prefer node types listed in the first-message context when provided.
- Default catalog (when context is absent): `ChatGPT`, `Claude`, `Gemini`, `GPTImage`, `FluxImage`, `FalAIImage`, `Veo31Video`, `WanAnimate`, `TextInput`, `ImagePanel`, `Dictation`, `Output`.
- Add `initialData` only when user intent clearly implies parameters.
- If one generator must feed another, route through `Output`.
- When node catalog is unknown, make a best-effort choice and clearly state assumptions.

## Gateway Behavior Constraints

- Poll interval target: about 1-2 seconds.
- Message claim timeout: about 2 minutes.
- Always preserve `messageId` across all chunk posts for a turn.
- Gateway auth uses `gw_...` token via query parameter `token`; never require Supabase JWT in this flow.

## Runtime Operations

When running a persistent poller service/process:

- Support either configuration style:
  - `KNODS_BASE_URL` already includes `/updates?token=...`
  - or `KNODS_BASE_URL` points to connection base and token is supplied separately (`KNODS_GATEWAY_TOKEN`)
- Derive `/respond` from the same connection root as `/updates`.
- Log handled `messageId` values and transport errors for debugging.

### Packaged Runtime (required)

This skill ships the runtime bridge and installer:

- `scripts/knods_iris_bridge.py`
- `scripts/install_local.sh`

Install/deploy from the skill folder:

```bash
bash /home/rolf/.openclaw/skills/knods/scripts/install_local.sh
```

The installer deploys:

- `~/.openclaw/scripts/knods_iris_bridge.py`
- `~/.config/systemd/user/knods-iris-bridge.service`

Then runs:

- `systemctl --user daemon-reload`
- `systemctl --user enable --now knods-iris-bridge.service`

### Environment Variables

Set these in `~/.openclaw/.env`:

- Required:
  - `KNODS_BASE_URL`
- Required when `KNODS_BASE_URL` does not already include `?token=...`:
  - `KNODS_GATEWAY_TOKEN`
- Optional:
  - `OPENCLAW_AGENT_ID` (default: `iris`)
  - `OPENCLAW_BIN` (default: `openclaw` on `PATH`)

### Service Operations

- Status:
  - `systemctl --user status knods-iris-bridge.service`
- Restart:
  - `systemctl --user restart knods-iris-bridge.service`
- Logs:
  - `journalctl --user -u knods-iris-bridge.service -f`

### Config Change Lifecycle (required)

After changing gateway URL/token env values, restart the running bridge process so it reloads config.

- Generic service form:
  - `systemctl --user restart <knods-bridge-service>`
- Generic process form:
  - stop old process
  - start poller again with updated env

Do not assume env changes are picked up live without restart.

## Reference

Read `references/protocol.md` for canonical polling endpoints, payload schemas, and action examples.
