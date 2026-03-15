# STATUS.md — openclaw-cli-bridge-elvatis

<!-- SECTION: summary -->
v0.2.25 built + tested (51/51). Staged model switching + token refresh stability. Ready to publish.
<!-- /SECTION: summary -->

<!-- SECTION: version -->
## Current Version: 0.2.25 — STABLE (unpublished)

_Last session: 2026-03-11 — Akido (claude-sonnet-4-6)_

| Platform | Version | Status |
|----------|---------|--------|
| GitHub | v0.2.25 | ✅ Tagged + Release |
| npm | 0.2.25 | ✅ Published |
| ClawHub | 0.2.25 | ✅ Published (direct API — clawhub CLI v0.7.0 bug: missing acceptLicenseTerms) |
| Local | 0.2.25 | ✅ Up to date |
<!-- /SECTION: version -->

<!-- SECTION: build_health -->
## Build Health

| Check | Result | Notes |
|-------|--------|-------|
| `npm run build` | ✅ | TypeScript compiles clean, no errors |
| `npm test` | ✅ 51/51 | All tests pass |
| `npm run typecheck` | ✅ | Implied by build |
| Plugin loads in gateway | ✅ | Verified at v0.2.21; no structural changes |
<!-- /SECTION: build_health -->

<!-- SECTION: what_is_done -->
## What Is Done

### Session-Safety: Staged Model Switching (v0.2.25)
- ✅ **`/cli-*` stages by default** — switch saved to `~/.openclaw/cli-bridge-pending.json`, NOT applied. Shows warning + instructions.
- ✅ **`/cli-* --now`** — immediate switch (user's explicit choice; only use between sessions)
- ✅ **`/cli-apply`** — apply staged switch after finishing current task
- ✅ **`/cli-pending`** — show staged switch state
- ✅ **`/cli-back`** — restore previous model + clear any staged switch
- ✅ **`/cli-list`** — updated to show pending state + switching instructions

### Token Refresh Stability (v0.2.25 — merged from v0.2.24)
- ✅ Sleep-resilient: `setInterval(10min)` polling instead of long `setTimeout`
- ✅ No timer-leak: `stopTokenRefresh()` called at top of `scheduleTokenRefresh()`
- ✅ `stopTokenRefresh()` exported; called via `server.on("close")`

### Previously Validated (v0.2.23 and below)
- ✅ Phase 1: `openai-codex` provider via `~/.codex/auth.json`
- ✅ Phase 2: Local proxy on `127.0.0.1:31337` (Gemini + Claude CLI)
- ✅ Phase 3: 15 slash commands (all `/cli-*`)
- ✅ Model allowlist, vllm prefix stripping, buildMinimalEnv XDG vars
- ✅ End-to-end tested: claude-sonnet-4-6 ✅ claude-haiku-4-5 ✅ gemini-2.5-flash ✅ gemini-2.5-pro ✅ codex ✅
<!-- /SECTION: what_is_done -->

<!-- SECTION: what_is_missing -->
## What Is Missing / Open

- ✅ **v0.2.25 published** — GitHub, npm, ClawHub alle auf 0.2.25
- ℹ️ **Claude CLI auth expires ~90 days** — when `/cli-test` returns 401, run `claude auth login`
- ℹ️ **Config patcher writes `openclaw.json` directly** — triggers one gateway restart on first install
- ℹ️ **ClawHub publish ignores `.clawhubignore`** — use rsync workaround (see CONVENTIONS.md)
<!-- /SECTION: what_is_missing -->

<!-- SECTION: bugs_fixed -->
## Bug History

| Version | Bug | Fix |
|---------|-----|-----|
| 0.2.25 | `/cli-*` mid-session breaks active agent (silent tool-call failures) | Staged switch by default; --now for explicit immediate |
| 0.2.25 | Timer-leak in scheduleTokenRefresh | stopTokenRefresh() clears interval on every call |
| 0.2.25 | Long setTimeout missed after system sleep/resume | setInterval(10min) polling |
| 0.2.25 | Token refresh interval leaked on proxy close | server.on("close", stopTokenRefresh) |
| 0.2.21 | Claude Code OAuth 401 on Gnome Keyring | buildMinimalEnv forwards XDG_RUNTIME_DIR |
| 0.2.14 | vllm/ prefix not stripped → unknown model | Strip prefix before routing |
| 0.2.13 | requireAuth:true blocked webchat commands | requireAuth:false |
| 0.2.9 | fuser -k SIGKILL'd gateway process | Safe health probe |
| 0.2.7–8 | EADDRINUSE on hot-reload | closeAllConnections() + registerService |
<!-- /SECTION: bugs_fixed -->
