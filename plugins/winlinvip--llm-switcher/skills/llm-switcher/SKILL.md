---
name: llm-switcher
description: "Change OpenClaw's global default AI model in config, save the change, and restart the gateway after explicit confirmation. Before writing default config, first test model availability by applying a session-only override. Use when the user wants to switch the default model for future sessions and validate it safely first."
---

# Model Switcher

Change the global default LLM model in OpenClaw config, with a session-level availability check first.

## Workflow

### 1) Read config and show available models first

Run:

```bash
openclaw config get agents.defaults.models
openclaw config get agents.defaults.model.primary
```

Extract and show:
- model key (for example `openai-codex/gpt-5.3-codex`)
- alias (for example `codex`, `opus`) when present
- current default model

Do not switch anything before showing options.

### 2) Ask user to choose model

Ask for the model name they want to set as the global default. Accept:
- alias (preferred): `codex`, `opus`
- full provider/model id when configured

If the name is not in configured options, reject and ask again with the valid list.

### 3) Test selected model in current session first (availability/conflict check)

Before changing default config, apply a session-only override and run a live reply test.

In OpenClaw agent/tooling context:
- Use `session_status` with `model=<selected-model>`.
- Confirm the override succeeds (no error about unknown/unavailable model).
- Then send a short test prompt to the model and require an actual response, for example:
  - "What model/version are you currently running? Return provider/model id and a one-line status."
- Treat this as pass only if the model returns a normal reply.

If override or live reply test fails:
- Do not update default config.
- Report the error clearly.
- Explain that the model appears unavailable/misconfigured.
- Ask user to choose a different configured model.

If override and live reply test both succeed:
- Continue to update default config.

### 4) Apply default-config change

Update default model in config:

```bash
openclaw config set agents.defaults.model.primary '"<selected-model>"'
```

Then verify:

```bash
openclaw config get agents.defaults.model.primary
```

Never claim success without verification output.

### 5) Ask before restarting gateway

After updating config, explicitly ask:

- "Do you want me to restart the gateway now so the change takes effect?"

Only restart after a clear yes.

### 6) Restart gateway on confirmation

Run:

```bash
openclaw gateway restart
```

Then verify status:

```bash
openclaw gateway status
```

If restart fails, report the error and suggest:

```bash
openclaw gateway stop
openclaw gateway start
openclaw gateway status
```

## Response style

- Be short and direct.
- Always show current default and valid model choices before asking for selection.
- Do not ask scope questions (no session-only final path in this skill).
- Always run a session-level availability check before writing default config.
- Always require explicit confirmation before restarting gateway.
- Never claim success without verification output.
