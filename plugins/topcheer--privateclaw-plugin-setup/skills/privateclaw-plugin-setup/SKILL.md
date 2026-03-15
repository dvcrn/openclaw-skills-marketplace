---
name: privateclaw-plugin-setup
description: "Install, enable, verify, and pair the PrivateClaw OpenClaw plugin, preferably returning the invite QR to the current Telegram, Discord, or QQ conversation via /privateclaw."
---

# PrivateClaw plugin setup

Use this skill when the user wants to install, enable, verify, configure, or pair the **PrivateClaw** OpenClaw plugin.

This skill is especially relevant for requests like:

- install PrivateClaw
- enable the PrivateClaw plugin
- set up private encrypted chat for OpenClaw
- start QR pairing
- return the pairing QR to the current Telegram, Discord, or QQ chat
- configure a custom PrivateClaw relay
- use `/privateclaw`, `/privateclaw group`, `/session-qr`, or `openclaw privateclaw pair`
- renew or re-share an existing PrivateClaw session
- 安装 PrivateClaw 插件
- 启用 PrivateClaw
- 配置 PrivateClaw relay
- 启动二维码配对
- 把配对二维码发回当前 Telegram / Discord / QQ 对话

## Core facts

- The production plugin package is `@privateclaw/privateclaw`.
- The production install path is `openclaw plugins install @privateclaw/privateclaw@latest`.
- The plugin id is `privateclaw`.
- The default public relay is `https://relay.privateclaw.us`.
- If the user is happy with the default public relay, do **not** set `relayBaseUrl`.
- PrivateClaw is an **OpenClaw plugin**, not an OpenClaw channel. Do **not** run `openclaw channels add privateclaw`.
- After `openclaw plugins install`, `openclaw plugins enable`, or any `openclaw config set plugins.entries.privateclaw.config...` change, the running OpenClaw gateway or service must be restarted before testing.

## Preferred behavior

Default to the production npm install path unless the user explicitly asks for:

- a local checkout / linked development install
- a custom relay
- a pinned package version

If the user wants the pairing QR or invite to be sent back to the **current existing OpenClaw chat conversation**, prefer the registered plugin command flow:

- `/privateclaw` for a normal one-to-one encrypted session
- `/privateclaw group` for a multi-participant encrypted room

That flow is preferred because the plugin command returns the invite URI and QR image back to the original Telegram, Discord, or QQ conversation through OpenClaw's normal reply payload path.

If the current environment can directly invoke the registered `privateclaw` plugin command in the active conversation, prefer that over local CLI pairing.

If there is no suitable active OpenClaw chat channel available, fall back to the local CLI pairing flow:

- `openclaw privateclaw pair`
- `openclaw privateclaw pair --group`
- `openclaw privateclaw pair --open`

## Recommended execution flow

### 1. Preflight

First confirm that the `openclaw` CLI is available:

```bash
openclaw --version
```

If `openclaw` is missing, stop and tell the user that OpenClaw itself must be installed first.

### 2. Install and enable the plugin

Use the production npm package by default:

```bash
openclaw plugins install @privateclaw/privateclaw@latest
openclaw plugins enable privateclaw
```

### 3. Optional relay override

Only do this when the user explicitly wants to point PrivateClaw at a self-hosted or custom relay:

```bash
openclaw config set plugins.entries.privateclaw.config.relayBaseUrl https://your-relay.example.com
```

If the user is using the default public relay at `https://relay.privateclaw.us`, skip this step.

### 4. Restart the running OpenClaw gateway or service

Do not claim setup is complete until the running OpenClaw process has reloaded the plugin and config.

That usually means restarting the active `openclaw start` process or whichever service unit hosts the gateway.

### 5. Verify command registration

Check that the `privateclaw` command is now registered:

```bash
openclaw commands list
```

Confirm that `privateclaw` appears in the command list before moving on.

## Pairing flows

### Flow A: return the QR to the current Telegram / Discord / QQ conversation

Use this flow when:

- the user is already using an OpenClaw-backed channel conversation
- the user wants the pairing QR returned to that same chat

Preferred next step:

- have the user send `/privateclaw` in that same conversation
- use `/privateclaw group` when the user wants a shared encrypted room for multiple app participants

Expected result:

- OpenClaw replies in the original channel conversation
- the reply contains the invite URI and QR image
- the user scans that QR with the PrivateClaw mobile app

If the runtime can execute the registered plugin command directly for the current channel conversation, do that instead of asking the user to repeat the command manually.

### Flow B: local CLI fallback

Use this flow when there is no active OpenClaw chat channel available, or when the user explicitly wants local terminal pairing:

```bash
openclaw privateclaw pair
```

Useful variants:

```bash
openclaw privateclaw pair --group
openclaw privateclaw pair --open
```

`--group` creates a multi-participant room.

`--open` opens a local browser preview page for the QR, which is useful when terminal rendering alone is inconvenient.

### Flow C: re-share an active session QR from inside PrivateClaw

Once a PrivateClaw session is already active, the participant can request the current pairing QR again from inside that encrypted session:

```text
/session-qr
```

Use this when the user wants to re-share the existing active session instead of creating a new one.

If the user needs to extend the session lifetime without replacing the whole setup, use:

```text
/renew-session
```

## Local checkout / development flow

Only use this when the user explicitly wants to install from a local repository checkout instead of npm:

```bash
openclaw plugins install --link ./packages/privateclaw-provider
openclaw plugins enable privateclaw
openclaw config set plugins.entries.privateclaw.config.relayBaseUrl ws://127.0.0.1:8787
```

Then restart the running OpenClaw gateway or service before testing.

## Guardrails

- Do not use `openclaw channels add privateclaw`; PrivateClaw is not a channel transport.
- Do not set `relayBaseUrl` unless the user asks for a custom relay.
- Do not default to the `--link` development install unless the user is working from a local checkout.
- Do not say setup succeeded until the gateway or service has been restarted and `openclaw commands list` shows `privateclaw`.
- If the user's goal is to receive the QR in the current Telegram, Discord, or QQ conversation, prefer `/privateclaw` over `openclaw privateclaw pair`.
- After a successful pairing flow, remind the user to scan the returned QR with the PrivateClaw app.

## Troubleshooting

### `privateclaw` does not appear in `openclaw commands list`

Likely causes:

- the plugin was installed but not enabled
- the gateway or service was not restarted after install or config change
- the user is looking at an older OpenClaw instance than the one they just modified

### The user wants `/privateclaw` in Telegram, Discord, or QQ but nothing happens there

PrivateClaw is only the plugin that creates the QR invite. The surrounding channel transport still has to exist separately in OpenClaw. If the user wants `/privateclaw` inside Telegram, Discord, or QQ, those channels must already be set up in OpenClaw.

### The user wants to use their own relay

Set:

```bash
openclaw config set plugins.entries.privateclaw.config.relayBaseUrl <relay-base-url>
```

Then restart the running OpenClaw gateway or service before testing again.

## Completion checklist

The setup should usually end with all of the following being true:

- the plugin is installed
- the plugin is enabled
- the running OpenClaw gateway or service has been restarted
- `openclaw commands list` shows `privateclaw`
- the user has either:
  - received a `/privateclaw` QR reply in the original channel conversation, or
  - received a local `openclaw privateclaw pair` QR and invite URI
