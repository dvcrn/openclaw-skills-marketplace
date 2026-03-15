# OpenClaw ACP Agents Reference

## Table of Contents

- [Overview](#overview)
- [ACP vs Sub-Agents](#acp-vs-sub-agents)
- [Fast Operator Flow](#fast-operator-flow)
- [ACP Controls](#acp-controls)
- [ACP Command Cookbook](#acp-command-cookbook)
- [Thread-Bound Sessions](#thread-bound-sessions)
- [Session Target Resolution](#session-target-resolution)
- [Supported Harnesses](#supported-harnesses)
- [Required Config](#required-config)
- [Plugin Setup](#plugin-setup)
- [Permission Configuration](#permission-configuration)
- [Troubleshooting](#troubleshooting)

## Overview

ACP (Agent Communication Protocol) agents allow OpenClaw to spawn and manage external AI agent runtimes (Codex, Claude Code, Gemini CLI, OpenCode, etc.) as persistent or one-shot sessions, with thread-bound routing and live controls.

Natural-language triggers:
- "Start a persistent Codex session in a thread and keep it focused."
- "Run this as a one-shot Claude Code ACP session and summarize the result."
- "Use Gemini CLI for this task in a thread, then keep follow-ups in that same thread."

## ACP vs Sub-Agents

| Feature | ACP (`runtime: "acp"`) | Sub-agents (`runtime: "subagent"`) |
|---|---|---|
| Session key | `agent:<agentId>:acp:<uuid>` | `agent:<agentId>:subagent:<uuid>` |
| Slash commands | `/acp ...` | `/subagents ...` |
| Tool call | `sessions_spawn` with `runtime:"acp"` | `sessions_spawn` with `runtime:"subagent"` |
| External runtime | Yes (via acpx harness) | No (internal Pi) |
| Thread binding | Supported | Supported |
| Persistent sessions | Yes | One-shot or persistent |

## Fast Operator Flow

```
/acp spawn codex --mode persistent --thread auto   # 1. Spawn session
# Work in the bound thread...
/acp status                                          # 2. Check state
/acp model <provider/model>                          # 3. Tune model
/acp permissions <profile>                           # 4. Set permissions
/acp timeout <seconds>                               # 5. Set timeout
/acp steer tighten logging and continue              # 6. Nudge without replacing context
/acp cancel                                          # 7. Stop current turn
/acp close                                           # 8. Close session + remove bindings
```

## ACP Controls

| Command | Description |
|---|---|
| `/acp spawn` | Create new ACP session |
| `/acp cancel` | Stop current turn |
| `/acp steer` | Nudge active session without replacing context |
| `/acp close` | Close session + remove bindings |
| `/acp status` | Runtime state summary |
| `/acp set-mode` | Change execution mode (e.g., `plan`) |
| `/acp set <key> <value>` | Generic runtime option override |
| `/acp cwd <path>` | Update working directory |
| `/acp permissions <profile>` | Set permission profile |
| `/acp timeout <seconds>` | Set timeout |
| `/acp model <id>` | Change model |
| `/acp reset-options` | Clear all runtime overrides |
| `/acp sessions` | List active ACP sessions |
| `/acp doctor` | Diagnose ACP setup |
| `/acp install` | Install ACP dependencies |

### Runtime Options Mapping

| `/acp` Command | Runtime Config Key |
|---|---|
| `/acp model <id>` | `model` |
| `/acp permissions <profile>` | `approval_policy` |
| `/acp timeout <seconds>` | `timeout` |
| `/acp cwd <path>` | cwd override |
| `/acp set <key> <value>` | generic path (`key=cwd` uses cwd path) |

## ACP Command Cookbook

```
/acp spawn codex --mode persistent --thread auto --cwd /repo
/acp spawn codex --provenance meta          # v2026.3.8+: enable provenance tracking
/acp cancel agent:codex:acp:<uuid>
/acp steer --session support inbox prioritize failing tests
/acp close
/acp status
/acp set-mode plan
/acp set model openai/gpt-5.2
/acp cwd /Users/user/Projects/repo
/acp permissions strict
/acp timeout 120
/acp model anthropic/claude-opus-4-5
/acp reset-options
/acp sessions
/acp doctor
/acp install
```

## ACP Provenance Tracking (v2026.3.8+)

Optional ingress provenance metadata for session trace ID retention:

```bash
openclaw acp --provenance off              # No provenance (default)
openclaw acp --provenance meta             # Attach provenance metadata to session
openclaw acp --provenance meta+receipt     # Metadata + delivery receipt
```

Or via `/acp spawn`:

```
/acp spawn codex --provenance meta+receipt --thread auto
```

Provenance metadata includes session trace IDs, enabling end-to-end tracing across ACP sessions.

## Thread-Bound Sessions

Thread binding works across channels:

1. OpenClaw binds a thread to a target ACP session
2. Follow-up messages in that thread route to the bound ACP session
3. ACP output is delivered back to the same thread
4. Unfocus/close/archive/idle-timeout or max-age expiry removes the binding

**Spawn thread modes** (`--thread`):

| Mode | Behavior |
|---|---|
| `auto` | Create thread if channel supports it |
| `here` | Bind to current thread |
| `off` | No thread binding |

### Required Config for Thread Binding

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        spawnAcpSessions: true,
      },
    },
  },
}
```

## Session Target Resolution

When a `/acp` command refers to a target session, resolution order:

1. Explicit target argument (or `--session` for `/acp steer`)
   - tries key → UUID-shaped session id → label
2. Current thread binding (if thread is bound to ACP session)
3. Current requester session fallback

## Supported Harnesses

| Harness | Agent ID |
|---|---|
| Pi (OpenClaw internal) | `pi` |
| Claude Code | `claude` |
| Codex | `codex` |
| OpenCode | `opencode` |
| Gemini CLI | `gemini` |

Custom agents can be added with `--agent <command>`.

## Required Config

```json5
{
  acp: {
    enabled: true,
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "codex",
    allowedAgents: ["pi", "claude", "codex", "opencode", "gemini"],
    maxConcurrentSessions: 8,
    stream: {
      coalesceIdleMs: 300,
      maxChunkChars: 1200,
    },
    runtime: {
      ttlMinutes: 120,
    },
  },
}
```

## Plugin Setup

### Install acpx Backend

```bash
# From registry
openclaw plugins install @openclaw/acpx
openclaw config set plugins.entries.acpx.enabled true

# From source
openclaw plugins install ./extensions/acpx

# Verify
/acp doctor
```

## Permission Configuration

### permissionMode

| Mode | Behavior |
|---|---|
| `approve-all` | Auto-approve all permission prompts |
| `approve-reads` | Auto-approve read-only, prompt for writes |
| `deny-all` | Deny all permission prompts |

### nonInteractivePermissions

| Mode | Behavior |
|---|---|
| `fail` | Throw `AcpRuntimeError` on permission prompt |
| `deny` | Silently deny permission |

### Configure

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

**Recommended for non-interactive**: `permissionMode=approve-reads` + `nonInteractivePermissions=fail`.

## Troubleshooting

| Error | Fix |
|---|---|
| `ACP runtime backend is not configured` | Run `/acp doctor`, install acpx plugin |
| `ACP is disabled by policy (acp.enabled=false)` | Set `acp.enabled=true` |
| `ACP dispatch is disabled by policy` | Set `acp.dispatch.enabled=true` |
| `ACP agent "<id>" is not allowed by policy` | Add `agentId` to `acp.allowedAgents` |
| `Unable to resolve session target: ...` | Check `/acp sessions` for active sessions |
| `--thread here requires running inside an active thread` | Use `--thread auto` or `off` |
| `Only <user-id> can rebind this thread` | Original spawner must rebind |
| `Thread bindings are unavailable for <channel>` | Use `--thread off` or enable thread bindings |
| `AcpRuntimeError: Permission prompt unavailable` | Set `permissionMode` to `approve-all` |
