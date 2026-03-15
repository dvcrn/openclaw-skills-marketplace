# openclaw-cli-bridge-elvatis

> OpenClaw plugin that bridges locally installed AI CLIs (Codex, Gemini, Claude Code) as model providers — with slash commands for instant model switching, restore, health testing, and model listing.

**Current version:** `1.8.2`

---

## What it does

### Phase 1 — Auth bridge (`openai-codex`)
Registers the `openai-codex` provider by reading OAuth tokens already stored by the Codex CLI (`~/.codex/auth.json`). No re-login needed.

### Phase 2 — Request bridge (local proxy)
Starts a local OpenAI-compatible HTTP proxy on `127.0.0.1:31337` and configures OpenClaw's `vllm` provider to route calls through `gemini` and `claude` CLI subprocesses.

**Prompt delivery:** always via **stdin** (never CLI args or `@file`) — avoids `E2BIG` for long sessions and Gemini agentic mode. Each message batch is truncated to the last 20 messages + system message (`MAX_MESSAGES`/`MAX_MSG_CHARS` in `src/cli-runner.ts`).

| Model reference | CLI invoked | Latency |
|---|---|---|
| `vllm/cli-gemini/gemini-2.5-pro` | `gemini -m gemini-2.5-pro -p ""` (stdin, cwd=/tmp) | ~8–10s |
| `vllm/cli-gemini/gemini-2.5-flash` | `gemini -m gemini-2.5-flash -p ""` (stdin, cwd=/tmp) | ~4–6s |
| `vllm/cli-gemini/gemini-3-pro-preview` | `gemini -m gemini-3-pro-preview -p ""` (stdin, cwd=/tmp) | ~8–10s |
| `vllm/cli-gemini/gemini-3-flash-preview` | `gemini -m gemini-3-flash-preview -p ""` (stdin, cwd=/tmp) | ~4–6s |
| `vllm/cli-claude/claude-sonnet-4-6` | `claude -p --output-format text --model claude-sonnet-4-6` (stdin) | ~2–4s |
| `vllm/cli-claude/claude-opus-4-6` | `claude -p --output-format text --model claude-opus-4-6` (stdin) | ~3–5s |
| `vllm/cli-claude/claude-haiku-4-5` | `claude -p --output-format text --model claude-haiku-4-5` (stdin) | ~1–3s |

### Phase 3 — Slash commands

All commands use gateway-level `commands.allowFrom` for authorization (`requireAuth: false` at plugin level).

**Claude Code CLI** (routed via local proxy on `:31337`):

| Command | Model |
|---|---|
| `/cli-sonnet` | `vllm/cli-claude/claude-sonnet-4-6` |
| `/cli-opus` | `vllm/cli-claude/claude-opus-4-6` |
| `/cli-haiku` | `vllm/cli-claude/claude-haiku-4-5` |

**Gemini CLI** (routed via local proxy on `:31337`, stdin + `cwd=/tmp`):

| Command | Model |
|---|---|
| `/cli-gemini` | `vllm/cli-gemini/gemini-2.5-pro` |
| `/cli-gemini-flash` | `vllm/cli-gemini/gemini-2.5-flash` |
| `/cli-gemini3` | `vllm/cli-gemini/gemini-3-pro-preview` |
| `/cli-gemini3-flash` | `vllm/cli-gemini/gemini-3-flash-preview` |

**Codex CLI** (via `openai-codex` provider — OAuth auth, calls OpenAI API directly, **not** through the local proxy):

| Command | Model | Notes |
|---|---|---|
| `/cli-codex` | `openai-codex/gpt-5.3-codex` | ✅ Tested |
| `/cli-codex-spark` | `openai-codex/gpt-5.3-codex-spark` | |
| `/cli-codex52` | `openai-codex/gpt-5.2-codex` | |
| `/cli-codex54` | `openai-codex/gpt-5.4` | May require upgraded OAuth scope |
| `/cli-codex-mini` | `openai-codex/gpt-5.1-codex-mini` | ✅ Tested |

**BitNet local inference** (via local proxy → llama-server on 127.0.0.1:8082, no API key):

| Command | Model |
|---|---|
| `/cli-bitnet` | `vllm/local-bitnet/bitnet-2b` |

**Utility:**

| Command | What it does |
|---|---|
| `/cli-back` | Restore the model active **before** the last `/cli-*` switch |
| `/cli-test [model]` | One-shot proxy health check — **does NOT switch your active model** |
| `/cli-list` | Show all registered CLI bridge models with commands |

**`/cli-back` details:**
- Before every `/cli-*` switch the current model is saved to `~/.openclaw/cli-bridge-state.json`
- `/cli-back` reads it, calls `openclaw models set <previous>`, then clears the file
- State survives gateway restarts — safe to use any time

**`/cli-test` details:**
- Accepts short form (`cli-sonnet`) or full path (`vllm/cli-claude/claude-sonnet-4-6`)
- Default when no arg given: `cli-claude/claude-sonnet-4-6`
- Reports response content, latency, and confirms your active model is unchanged

**`/cli-list` details:**
- Lists all registered models grouped by provider (Claude CLI, Gemini CLI, Codex)
- No arguments required

---

### Phase 4 — Web Browser Providers (headless, no API key needed)

Routes requests through real browser sessions on the provider's web UI. Requires a valid login session (free or paid tier). Uses persistent Chromium profiles — sessions survive gateway restarts.

**Grok** (grok.com — SuperGrok subscription):

| Model | Notes |
|---|---|
| `web-grok/grok-3` | Full model |
| `web-grok/grok-3-fast` | Faster variant |
| `web-grok/grok-3-mini` | Lightweight |
| `web-grok/grok-3-mini-fast` | Fastest |

| Command | What it does |
|---|---|
| `/grok-login` | Authenticate via X.com OAuth, save session to `~/.openclaw/grok-profile/` |
| `/grok-status` | Show session validity + cookie expiry |
| `/grok-logout` | Clear session |

**Gemini** (gemini.google.com):

| Model | Notes |
|---|---|
| `web-gemini/gemini-2-5-pro` | Gemini 2.5 Pro |
| `web-gemini/gemini-2-5-flash` | Gemini 2.5 Flash |
| `web-gemini/gemini-3-pro` | Gemini 3 Pro |
| `web-gemini/gemini-3-flash` | Gemini 3 Flash |

| Command | What it does |
|---|---|
| `/gemini-login` | Authenticate, save cookies to `~/.openclaw/gemini-profile/` |
| `/gemini-status` | Show session validity + cookie expiry |
| `/gemini-logout` | Clear session |

**Claude.ai** (claude.ai — Pro/Team subscription):

| Model | Notes |
|---|---|
| `web-claude/claude-sonnet` | Claude Sonnet (web) |
| `web-claude/claude-opus` | Claude Opus (web) |
| `web-claude/claude-haiku` | Claude Haiku (web) |

| Command | What it does |
|---|---|
| `/claude-login` | Authenticate, save cookies to `~/.openclaw/claude-profile/` |
| `/claude-status` | Show session validity + cookie expiry |
| `/claude-logout` | Clear session |

**ChatGPT** (chatgpt.com — Plus/Pro subscription):

| Model | Notes |
|---|---|
| `web-chatgpt/gpt-4o` | GPT-4o |
| `web-chatgpt/gpt-4o-mini` | GPT-4o Mini |
| `web-chatgpt/gpt-4.1` | GPT-4.1 |
| `web-chatgpt/o3` | o3 |
| `web-chatgpt/o4-mini` | o4-mini |
| `web-chatgpt/gpt-5` | GPT-5 |
| `web-chatgpt/gpt-5-mini` | GPT-5 Mini |

| Command | What it does |
|---|---|
| `/chatgpt-login` | Authenticate, save cookies to `~/.openclaw/chatgpt-profile/` |
| `/chatgpt-status` | Show session validity + cookie expiry |
| `/chatgpt-logout` | Clear session |

**Session lifecycle:**
- First use: run `/xxx-login` once — authenticates and saves cookies to persistent Chromium profile
- **No CDP required:** `/xxx-login` no longer depends on the OpenClaw browser (CDP port 18800). If CDP is available, cookies are imported from it; otherwise a standalone persistent Chromium is launched automatically.
- If headless login fails, a **headed browser** opens for manual login (5 min timeout)
- After gateway restart: sessions are **automatically restored** from saved profiles on startup (sequential, ~25s after start)
- `/bridge-status` — shows all 4 providers at a glance with login state + expiry info

---

## Requirements

- [OpenClaw](https://openclaw.ai) gateway (tested with `2026.3.x`)
- One or more of:
  - [`@openai/codex`](https://github.com/openai/codex) — `npm i -g @openai/codex` + `codex login`
  - [`@google/gemini-cli`](https://github.com/google-gemini/gemini-cli) — `npm i -g @google/gemini-cli` + `gemini auth`
  - [`@anthropic-ai/claude-code`](https://github.com/anthropic-ai/claude-code) — `npm i -g @anthropic-ai/claude-code` + `claude auth`

---

## Installation

```bash
# From ClawHub
clawhub install openclaw-cli-bridge-elvatis

# Or from workspace (development)
# Add to ~/.openclaw/openclaw.json:
# plugins.load.paths: ["~/.openclaw/workspace/openclaw-cli-bridge-elvatis"]
# plugins.entries.openclaw-cli-bridge-elvatis: { "enabled": true }
```

---

## Setup

### 1. Enable + restart

```json
// ~/.openclaw/openclaw.json → plugins.entries
"openclaw-cli-bridge-elvatis": { "enabled": true }
```

```bash
openclaw gateway restart
```

### 2. Verify (check gateway logs)

```
[cli-bridge] proxy ready on :31337
[cli-bridge] registered 14 commands: /cli-sonnet, /cli-opus, /cli-haiku,
             /cli-gemini, /cli-gemini-flash, /cli-gemini3, /cli-gemini3-flash,
             /cli-codex, /cli-codex-spark, /cli-codex52, /cli-codex54, /cli-codex-mini,
             /cli-back, /cli-test, /cli-list
```

### 3. Register Codex auth (optional — Phase 1 only)

```bash
openclaw models auth login --provider openai-codex
# Select: "Codex CLI (existing login)"
```

### 4. List available models

```
/cli-list
→ 🤖 CLI Bridge Models

  Claude Code CLI
    /cli-sonnet          claude-sonnet-4-6
    /cli-opus            claude-opus-4-6
    /cli-haiku           claude-haiku-4-5

  Gemini CLI
    /cli-gemini          gemini-2.5-pro
    /cli-gemini-flash    gemini-2.5-flash
    /cli-gemini3         gemini-3-pro-preview
    /cli-gemini3-flash   gemini-3-flash-preview

  Codex (OAuth)
    /cli-codex           gpt-5.3-codex
    /cli-codex-spark     gpt-5.3-codex-spark
    /cli-codex52         gpt-5.2-codex
    /cli-codex54         gpt-5.4
    /cli-codex-mini      gpt-5.1-codex-mini

  Utility
    /cli-back            Restore previous model
    /cli-test [model]    Health check (no model switch)
    /cli-list            This overview

  Proxy: 127.0.0.1:31337
```

### 5. Test without switching your model

```
/cli-test
→ 🧪 CLI Bridge Test
  Model: vllm/cli-claude/claude-sonnet-4-6
  Response: CLI bridge OK
  Latency: 2531ms
  Active model unchanged: anthropic/claude-sonnet-4-6

/cli-test cli-gemini
→ 🧪 CLI Bridge Test
  Model: vllm/cli-gemini/gemini-2.5-pro
  Response: CLI bridge OK
  Latency: 8586ms
  Active model unchanged: anthropic/claude-sonnet-4-6
```

### 6. Switch and restore

```
/cli-sonnet
→ ✅ Switched to Claude Sonnet 4.6 (CLI)
   `vllm/cli-claude/claude-sonnet-4-6`
   Use /cli-back to restore previous model.

... test things ...

/cli-back
→ ✅ Restored previous model
   `anthropic/claude-sonnet-4-6`
```

---

## Configuration

In `~/.openclaw/openclaw.json` → `plugins.entries.openclaw-cli-bridge-elvatis.config`:

```json5
{
  "enableCodex": true,         // register openai-codex from Codex CLI auth (default: true)
  "enableProxy": true,         // start local CLI proxy server (default: true)
  "proxyPort": 31337,          // proxy port (default: 31337)
  "proxyApiKey": "cli-bridge", // key between OpenClaw vllm provider and proxy (default: "cli-bridge")
  "proxyTimeoutMs": 120000     // CLI subprocess timeout in ms (default: 120s)
}
```

---

## Model Allowlist

`routeToCliRunner` enforces `DEFAULT_ALLOWED_CLI_MODELS` — only models registered in the plugin are accepted by the proxy. Unregistered models receive a clear error listing allowed options.

To disable the check (e.g. for custom vllm routing): pass `allowedModels: null` in `RouteOptions`.

---

## Architecture

```
OpenClaw agent
  │
  ├─ openai-codex/*  ──────────────────────────► OpenAI API (direct)
  │    auth: ~/.codex/auth.json OAuth tokens
  │    /cli-codex, /cli-codex-spark, /cli-codex52, /cli-codex54, /cli-codex-mini
  │
  └─ vllm/cli-gemini/*  ─┐
     vllm/cli-claude/*   ─┤─► localhost:31337  (openclaw-cli-bridge proxy)
                          │       ├─ cli-gemini/* → gemini -m <model> -p ""
                          │       │                 stdin=prompt, cwd=/tmp
                          │       │                 (neutral cwd prevents agentic mode)
                          │       └─ cli-claude/* → claude -p --model <model>
                          │                         stdin=prompt

Slash commands (requireAuth=false, gateway commands.allowFrom is the auth layer):
  /cli-sonnet|opus|haiku|gemini|gemini-flash|gemini3|gemini3-flash
  /cli-codex|codex-spark|codex52|codex54|codex-mini
     └─► saves current model → ~/.openclaw/cli-bridge-state.json
     └─► openclaw models set <model>

  /cli-back   → reads state file, restores previous model, clears state
  /cli-test   → HTTP POST → localhost:31337, no global model change
  /cli-list   → formatted table of all registered models
```

---

## Known Issues & Fixes

### `spawn E2BIG` (fixed in v0.2.1)
**Symptom:** `CLI error for cli-claude/…: spawn E2BIG` after ~500+ messages.
**Cause:** Gateway injects large values into `process.env` at runtime. Spreading it into `spawn()` exceeds Linux's `ARG_MAX` (~2MB).
**Fix:** `buildMinimalEnv()` — only passes `HOME`, `PATH`, `USER`, and auth keys.

### Claude Code 401 / timeout on OAuth login (fixed in v0.2.21)
**Symptom:** `/cli-test cli-claude/*` times out after 30s; logs show `401 Invalid authentication credentials`.
**Cause:** `buildMinimalEnv()` did not forward `XDG_RUNTIME_DIR` and `DBUS_SESSION_BUS_ADDRESS` to the spawned `claude` subprocess. Claude Code authenticated via `claude.ai` OAuth (Claude Max plan) stores its tokens in the system keyring (Gnome Keyring / libsecret) and needs these env vars to access it.
**Affects:** Only systems using `claude auth` OAuth login (Claude Max / Teams). API-key users (`ANTHROPIC_API_KEY`) are not affected.
**Fix:** Added `XDG_RUNTIME_DIR` and `DBUS_SESSION_BUS_ADDRESS` to the forwarded env keys in `buildMinimalEnv()`.

### Gemini agentic mode / hangs (fixed in v0.2.4)
**Symptom:** Gemini hangs, returns wrong answers, or says "directory does not exist".
**Cause:** `@file` syntax (`gemini -p @/tmp/xxx.txt`) triggers agentic mode — Gemini scans the working directory for project context and treats prompts as task instructions.
**Fix:** Stdin delivery (`gemini -p ""` with prompt via stdin) + `cwd=/tmp`.

---

## Development

```bash
npm run typecheck   # tsc --noEmit
npm test            # vitest run (83 tests)
```

---

## Changelog

### v1.8.2
- **fix:** `local-bitnet/*` exempt from tool-call rejection — llama-server ignores tool schemas silently. OpenClaw always sends tools with every request, so this was blocking all BitNet usage.

### v1.8.1
- **fix:** `--now` flag now works when followed by additional text (e.g. `/cli-bitnet --now hello`) — was using `===` instead of `startsWith`.

### v1.8.0
- **feat:** BitNet local inference — `local-bitnet/bitnet-2b` routes to llama-server on 127.0.0.1:8082. No API key, no internet, pure CPU inference (2.87 tok/s on i7-6700K). Use `/cli-bitnet` to switch.
- **feat:** `/bridge-status` shows BitNet server health as 5th provider.

### v1.7.5
- **chore:** Re-published to ClawHub with correct display name "OpenClaw CLI Bridge"

### v1.7.4
- **docs:** Handoff docs updated (DASHBOARD, LOG, STATUS, NEXT_ACTIONS)

### v1.7.3
- **fix:** Cookie expiry tracking for all 4 providers now uses the **longest-lived** auth cookie instead of the shortest. Previously, short-lived cookies caused false "session expired" alerts and unnecessary WhatsApp notifications on every gateway restart:
  - **Claude:** `__cf_bm` (Cloudflare, ~30 min) removed from scan list; now tracks `sessionKey` (~1 year)
  - **ChatGPT:** sort reversed; now prefers `__Secure-next-auth.session-token` over `_puid` (~7d)
  - **Gemini:** sort reversed; now uses longest of `__Secure-1PSID` / `__Secure-3PSID` / `SID`
  - **Grok:** sort reversed; now uses longest of `sso` / `sso-rw`

### v1.7.2
- **fix:** Startup restore now uses cookie expiry file as primary check — if cookies are still valid (>1h left), the persistent context is launched immediately without a fragile browser selector check. This eliminates false "not logged in" errors for Grok/Claude/ChatGPT caused by slow page loads or DOM selector changes.
- **fix:** Grok cookie file path corrected to `grok-cookie-expiry.json` (was `grok-session.json`).

### v1.7.1
- **feat:** `/status` HTML dashboard — browser-accessible health page at `http://127.0.0.1:31337/status`. Shows all 4 web providers with live status badge (Connected / Logged in / Expired / Never logged in), cookie expiry per provider, CLI and web model list. Auto-refreshes every 30s.

### v1.7.0
- **fix:** Startup restore timeout 3s → 6s with one retry, eliminates false "not logged in" for slow-loading pages (Grok)
- **feat:** Auto-relogin on startup — if cookies truly expired, attempt headless relogin before sending WhatsApp alert
- **feat:** Keep-alive (20h) now verifies session after touch and attempts auto-relogin if expired
- **feat:** Tests (vitest) — proxy tool rejection, models endpoint, auth, cookie expiry formatters

### v1.6.5
- **feat:** Automatic session keep-alive — every 20h, active browser sessions are silently refreshed by navigating to the provider home page. Prevents cookie expiry on providers like ChatGPT (7-day sessions) without storing credentials.

### v1.6.4
- **chore:** version bump (1.6.3 was already published on npm with partial changes)

### v1.6.3
- **fix:** CLI-proxy models (`cli-gemini/*`, `cli-claude/*`) now return HTTP 400 with `tools_not_supported` when a request includes tool/function call schemas — prevents agents from silently failing or hallucinating when assigned a CLI-proxy model
- **feat:** `/v1/models` response includes `capabilities.tools: false` for CLI-proxy models so OpenClaw can detect tool support upfront
- **fix:** EADDRINUSE on hot-reload: re-probe after 1.5s wait before retrying bind; probe timeout 800ms → 2000ms

### v1.6.2
- **docs:** Add missing changelog entries (v1.5.1, v1.6.0, v1.6.1), fix /cli-codex54 command name in SKILL.md, add startup re-login alert description to SKILL.md.

### v1.6.1
- **feat:** WhatsApp re-login alerts on startup. After each gateway restart, the session restore loop collects any providers that failed to restore (cookies expired) and sends a single batched WhatsApp notification with the exact `/xxx-login` commands needed. No credential storage — remains fully 2FA-safe.

### v1.6.0
- **feat:** Persistent Chromium profiles for all 4 web providers (Grok, Gemini, Claude.ai, ChatGPT). Browser sessions now survive gateway restarts — cookies are stored in `~/.openclaw/{grok,gemini,claude,chatgpt}-profile/` and restored automatically on startup.
- **feat:** Re-added `/claude-login`, `/claude-status`, `/claude-logout`, `/chatgpt-login`, `/chatgpt-status`, `/chatgpt-logout` commands with full persistent profile support.
- **feat:** `/bridge-status` now shows all 4 providers with session state and cookie expiry at a glance.
- **fix:** Startup restore guard (`_startupRestoreDone`) prevents duplicate browser launches on hot-reloads (SIGUSR1).

### v1.5.1
- **fix:** Hardcoded plugin version `1.3.1` in plugin object updated to `1.5.1`.
- **docs:** Added `CONTRIBUTING.md` with release checklist and smoketest workflow.

### v1.5.0
- **refactor:** Removed `/claude-login`, `/claude-logout`, `/claude-status`, `/chatgpt-login`, `/chatgpt-logout`, `/chatgpt-status` commands and all related browser automation code. Claude is fully covered by `cli-claude/*` via CLI proxy, ChatGPT by `openai-codex` + `copilot-proxy`.
- **refactor:** Removed `web-claude/*` and `web-chatgpt/*` proxy routes and model entries from proxy server.
- **refactor:** Removed `getOrLaunchClaudeContext()` and `getOrLaunchChatGPTContext()` functions, claude/chatgpt session state, cookie expiry tracking, and startup restore for these providers.
- **cleanup:** Deleted `test/claude-proxy.test.ts` and `test/chatgpt-proxy.test.ts`.
- **result:** Cleaner codebase, no browser timeout on startup for unused providers. Only Grok and Gemini browser providers remain.

### v1.4.3
- **fix:** Full stealth mode for all browser launches - `ignoreDefaultArgs: ['--enable-automation']` removes Playwright's automation flag, `--disable-blink-features=AutomationControlled` hides `navigator.webdriver`, and `--disable-infobars` suppresses the "Chrome is being controlled by automated software" banner. Combined with `channel: "chrome"` (v1.4.2), this bypasses Cloudflare human verification completely.
- **root cause:** Even with system Chrome (`channel: "chrome"`), Playwright injects `--enable-automation` by default, which sets `navigator.webdriver = true` and shows the automation infobar. Cloudflare checks both signals.

### v1.4.2
- **fix:** All browser launches now use `channel: "chrome"` (real system Chrome) instead of Playwright's bundled Chromium. Cloudflare human verification no longer blocks `/xxx-login` commands.
- **root cause:** Playwright's bundled Chromium is fingerprinted by Cloudflare as an automation browser, triggering CAPTCHA challenges that cannot be completed. System Chrome is not flagged.

### v1.4.1
- **fix:** `/claude-login`, `/gemini-login`, `/chatgpt-login` now fall back to a **headed** (visible) Chromium browser when headless login fails (no saved cookies in profile). The user can log in manually in the opened browser window (5 min timeout). After login, cookies are saved to the persistent profile for future headless use.
- **fix:** Added missing `claude-opus-4-6` and `claude-haiku-4-5` entries to the Claude browser MODEL_MAP
- **root cause:** Headless Chromium without saved cookies sees a login page, not the editor - the user cannot interact with a headless browser to log in

### v1.4.0
- **feat:** Persistent browser fallback for all providers - `/claude-login`, `/gemini-login`, `/chatgpt-login` no longer require the OpenClaw browser (CDP port 18800). If CDP is available, cookies are imported; otherwise a standalone persistent headless Chromium is launched automatically from the saved profile directory.
- **feat:** New helper functions `getOrLaunchClaudeContext()`, `getOrLaunchGeminiContext()`, `getOrLaunchChatGPTContext()` - same pattern as the existing `getOrLaunchGrokContext()` (try CDP, fall back to persistent Chromium, coalesce concurrent launches)
- **fix:** Proxy server `connectXxxContext` callbacks now use the persistent fallback too - no more "not logged in" errors when CDP is unavailable but a saved profile exists
- **fix:** `cleanupBrowsers()` now properly closes Claude, Gemini, and ChatGPT persistent contexts on plugin teardown (previously only cleaned up Grok + CDP)
- **root cause:** All 3 login commands (Claude, Gemini, ChatGPT) called `connectToOpenClawBrowser()` directly, which only tries CDP on 127.0.0.1:18800. If Chrome was not running with `--remote-debugging-port=18800`, login always failed. Grok already had the fallback pattern since v0.2.27 - now all 4 providers are consistent.

### v1.3.5
- **fix:** Startup session restore now runs only once per process lifetime — `_startupRestoreDone` module-level guard prevents re-running on every hot-reload (SIGUSR1), which was triggered every ~60s by the openclaw-control-ui dashboard poll
- **root cause:** Gateway `reload.mode=hybrid` + dashboard status polling caused plugin to reinitialize every 60s → each reload spawned a new Gemini Chromium instance → RAM/CPU OOM loop
- **behavior:** First load after gateway start: sequential profile restore runs once. All subsequent hot-reloads: skip restore, reuse existing in-memory contexts

### v1.3.4
- **feat:** Safe sequential session restore on startup — if a saved profile exists, providers are reconnected automatically after gateway restart (one at a time, 3s delay between each, headless)
- **fix:** No manual `/xxx-login` needed after reboot if profile is already saved
- **safety:** Profile-gated — only restores if `~/.openclaw/<provider>-profile/` or cookie file exists; never spawns a browser for an uninitialized provider

### v1.3.3
- **fix:** Removed auto-connect of all browser providers on plugin startup — caused OOM (load 195, 30GB RAM) by spawning 4+ persistent Chromium instances on every gateway start
- **fix:** Removed Grok session restore on startup — same root cause
- **behavior change:** Browsers are now started **on-demand only** via `/grok-login`, `/claude-login`, `/gemini-login`, `/chatgpt-login`

### v1.3.2
- **fix:** Singleton promise guard on `ensureAllProviderContexts()` — concurrent requests no longer each spawn their own Chromium; extra callers await the existing run
- **fix:** Removed recursive `ensureAllProviderContexts()` fallback from all `connect*Context` proxy callbacks — no more exponential browser spawn on CDP failure

### v1.3.1
- **fix:** /claude-login, /gemini-login, /chatgpt-login now bake cookies into persistent profile dirs
- **fix:** After gateway restart, providers auto-reconnect from saved profile (no browser tabs needed)
- **fix:** Better debug logging when persistent headless context fails (Cloudflare etc.)

### v1.3.0
- **fix:** Browser persistence after gateway restart — each provider launches its own persistent Chromium if OpenClaw browser is unavailable
- **feat:** `ensureAllProviderContexts()` — unified startup connect for all 4 providers
- **feat:** Lazy-connect fallback to persistent context when CDP unavailable

### v1.2.0
- **fix:** Fresh page per request — no more message accumulation across calls
- **feat:** ChatGPT model switching via URL param (?model=gpt-4o, o3, etc.)
- **chore:** Gemini model switching: TODO (requires UI interaction)

### v1.1.0
- **feat:** Auto-connect all providers on startup (no manual login after restart if browser is open)
- **feat:** `/bridge-status` — all 4 providers at a glance with expiry info
- **fix:** Removed obsolete CLI models: gpt-5.2-codex, gpt-5.3-codex-spark, gpt-5.1-codex-mini, gemini-3-flash-preview
- **fix:** Removed duplicate cli-gemini3-flash (was same as gemini-3-flash-preview)
- **chore:** Cleaned up CLI_MODEL_COMMANDS (8 models, down from 13)

## v1.0.0 — Full Headless Browser Bridge 🚀

All four major LLM providers are now available via browser automation.
No CLI binaries required — just authenticated browser sessions.

#### v1.1.0
- **feat:** Auto-connect all providers on startup (no manual login after restart if browser is open)
- **feat:** `/bridge-status` — all 4 providers at a glance with expiry info
- **fix:** Removed obsolete CLI models: gpt-5.2-codex, gpt-5.3-codex-spark, gpt-5.1-codex-mini, gemini-3-flash-preview
- **fix:** Removed duplicate cli-gemini3-flash (was same as gemini-3-flash-preview)
- **chore:** Cleaned up CLI_MODEL_COMMANDS (8 models, down from 13)

## v1.0.0
- **feat:** `chatgpt-browser.ts` — chatgpt.com DOM-automation (`#prompt-textarea` + `[data-message-author-role]`)
- **feat:** `web-chatgpt/*` models: gpt-4o, gpt-4o-mini, gpt-4.1, o3, o4-mini, gpt-5, gpt-5-mini (updated in v1.6.3)
- **feat:** `/chatgpt-login`, `/chatgpt-status`, `/chatgpt-logout` + cookie-expiry tracking
- **feat:** All 4 providers headless: Grok ✅ Claude ✅ Gemini ✅ ChatGPT ✅
- **test:** 96/83 tests green (8 test files)
- **fix:** Singleton CDP connection, cleanupBrowsers() on plugin stop

### v0.2.30
- **feat:** `gemini-browser.ts` — gemini.google.com DOM-automation (Quill editor + message-content polling)
- **feat:** `web-gemini/*` models in proxy (gemini-2-5-pro, gemini-2-5-flash, gemini-3-pro, gemini-3-flash)
- **feat:** `/gemini-login`, `/gemini-status`, `/gemini-logout` commands + cookie-expiry tracking
- **fix:** Singleton CDP connection — no more zombie Chromium processes
- **fix:** `cleanupBrowsers()` called on plugin stop — all browser resources released
- **test:** 90/90 tests green (+6 gemini-proxy tests)

### v0.2.29
- **feat:** `claude-browser.ts` — claude.ai DOM-automation (ProseMirror + `[data-test-render-count]` polling)
- **feat:** `web-claude/*` models in proxy (web-claude/claude-sonnet, claude-opus, claude-haiku)
- **feat:** `/claude-login`, `/claude-status`, `/claude-logout` commands
- **feat:** Claude cookie-expiry tracking (`~/.openclaw/claude-cookie-expiry.json`)
- **test:** 84/84 tests green (+7 claude-proxy tests, +8 claude-browser unit tests)

### v0.2.28
- **feat:** `/grok-login` scans auth cookie expiry (sso cookie) and saves to `~/.openclaw/grok-cookie-expiry.json`
- **feat:** `/grok-status` shows cookie expiry with color-coded warnings (🚨 <7d, ⚠️ <14d, ✅ otherwise)
- **feat:** Startup log shows cookie expiry and refreshes the expiry file on session restore
- **fix:** Flaky cli-runner test improved (was pre-existing)

### v0.2.27
- **feat:** Grok persistent Chromium profile (`~/.openclaw/grok-profile/`) — cookies survive gateway restarts
- **feat:** `/grok-login` imports cookies from OpenClaw browser into persistent profile automatically
- **fix:** `verifySession` reuses existing grok.com page instead of opening a new one (avoids Cloudflare 403)
- **fix:** DOM-polling strategy instead of direct fetch API — bypasses `x-statsig-id` anti-bot check completely
- **fix:** Lazy-connect: `connectGrokContext` callback auto-reconnects on first request after restart

### v0.2.26
- **feat:** Grok web-session bridge integrated into cli-bridge proxy — routes `web-grok/*` models through grok.com browser session (SuperGrok subscription, no API credits needed)
- **feat:** `/grok-login` — opens Chromium for X.com OAuth login, saves session to `~/.openclaw/grok-session.json`
- **feat:** `/grok-status` — check session validity
- **feat:** `/grok-logout` — clear session
- **fix:** Grok web-session plugin removed as separate plugin — consolidated into cli-bridge (fewer running processes, single proxy port)

### v0.2.25
- **feat:** Staged model switching — `/cli-*` now stages the switch instead of applying it immediately. Prevents silent session corruption when switching models mid-conversation.
  - `/cli-sonnet` → stages switch, shows warning, does NOT apply
  - `/cli-sonnet --now` → immediate switch (use only between sessions!)
  - `/cli-apply` → apply staged switch after finishing current task
  - `/cli-pending` → show staged switch (if any)
  - `/cli-back` → restore previous model + clear staged switch
- **fix:** Sleep-resilient OAuth token refresh — replaced single long `setTimeout` with `setInterval(10min)` polling. Token refresh no longer misses its window after system sleep/resume.
- **fix:** Timer leak in `scheduleTokenRefresh()` — old interval now reliably cleared via `stopTokenRefresh()` before scheduling a new one.
- **fix:** `stopTokenRefresh()` exported from `claude-auth.ts`; called automatically via `server.on("close")` when the proxy server closes.

### v0.2.23
- **feat:** Proactive OAuth token management (`src/claude-auth.ts`) — the proxy now reads `~/.claude/.credentials.json` at startup, schedules a refresh 30 minutes before expiry, and calls `ensureClaudeToken()` before every `claude` subprocess invocation. On 401 responses, automatically retries once after refreshing. Eliminates the need for manual re-login after token expiry in headless/systemd deployments.

### v0.2.22
- **fix:** `runClaude()` now detects expired/invalid OAuth tokens immediately (401 in stderr) and throws a clear actionable error instead of waiting for the 30s proxy timeout. Error message includes the exact re-login command.

### v0.2.21
- **fix:** `buildMinimalEnv()` now forwards `XDG_RUNTIME_DIR` and `DBUS_SESSION_BUS_ADDRESS` to Claude Code subprocesses — required for Gnome Keyring / libsecret access when Claude Code is authenticated via `claude.ai` OAuth (Claude Max). Without these, the spawned `claude` process cannot read its OAuth token from the system keyring, resulting in `401 Invalid authentication credentials` and a 30-second timeout on `/cli-test` and all `/cli-claude/*` requests.

### v0.2.20
- **fix:** `formatPrompt` now defensively coerces `content` to string via `contentToString()` — prevents `[object Object]` reaching the CLI when WhatsApp group messages contain structured content objects instead of plain strings
- **feat:** `ChatMessage.content` now accepts `string | ContentPart[] | unknown` (OpenAI multimodal content arrays supported)
- **feat:** New `contentToString()` helper: handles string, OpenAI ContentPart arrays, arbitrary objects (JSON.stringify), null/undefined

### v0.2.19
- **feat:** `/cli-list` command — formatted overview of all registered models grouped by provider
- **docs:** Rewrite README to reflect current state (correct model names, command count, requireAuth, test count, /cli-list docs)

### v0.2.18
- **feat:** Add `/cli-gemini3-flash` → `gemini-3-flash-preview`
- **feat:** Add `/cli-codex-spark` → `gpt-5.3-codex-spark`, `/cli-codex52` → `gpt-5.2-codex`, `/cli-codex54` → `gpt-5.4`
- **fix:** Update `DEFAULT_ALLOWED_CLI_MODELS` with `gemini-3-flash-preview`

### v0.2.17
- **fix:** `/cli-gemini3` model corrected to `gemini-3-pro-preview` (was `gemini-3-pro`, returns 404 from Gemini API)

### v0.2.16
- **feat(T-101):** Expand test suite to 45 tests — new cases for `formatPrompt` (mixed roles, boundary values, system messages) and `routeToCliRunner` (gemini paths, edge cases)
- **feat(T-103):** Add `DEFAULT_ALLOWED_CLI_MODELS` allowlist; `routeToCliRunner` now rejects unregistered models by default; pass `allowedModels: null` to opt out

### v0.2.15
- **docs:** Rewrite changelog (entries for v0.2.12–v0.2.14 were corrupted); all providers verified working end-to-end

### v0.2.14
- **fix:** Strip `vllm/` prefix in `routeToCliRunner` — OpenClaw sends full provider path (`vllm/cli-claude/...`) but proxy router expected bare `cli-claude/...`
- **test:** Add 4 routing tests (9 total)

### v0.2.13
- **fix:** Set `requireAuth: false` on all `/cli-*` commands — plugin-level auth uses different resolution path than `commands.allowFrom`; gateway allowlist is the correct security layer
- **fix:** Hardcoded `version: "0.2.5"` in plugin object now tracks `package.json`

### v0.2.9
- **fix:** Critical — replace `fuser -k 31337/tcp` with safe health probe to prevent gateway SIGKILL on hot-reloads

### v0.2.7–v0.2.8
- **fix:** Port leak on hot-reload — `registerService` stop() hook + `closeAllConnections()`

### v0.2.6
- **fix:** `openclaw.extensions` added to `package.json`; config patcher auto-adds vllm provider

### v0.2.5
- **feat:** `/cli-codex` + `/cli-codex-mini` (Codex OAuth provider, direct API)

### v0.2.4
- **fix:** Gemini agentic mode — stdin delivery + `cwd=/tmp`

### v0.2.3
- **feat:** `/cli-back` + `/cli-test`

### v0.2.2
- **feat:** Phase 3 — `/cli-*` slash commands

### v0.2.1
- **fix:** `spawn E2BIG` + unit tests

### v0.2.0
- **feat:** Phase 2 — local OpenAI-compatible proxy, stdin delivery, prompt truncation

### v0.1.x
- Phase 1: Codex CLI OAuth auth bridge

---

## License

MIT
