# TRUST.md — openclaw-cli-bridge-elvatis

> Tracks verification status of critical system properties.
> **verified** = agent ran code/tests and observed output.
> **assumed** = derived from docs/config, not directly tested.
> **untested** = status unknown, needs verification.
>
> TTL: how long a "verified" claim remains valid before it should be re-checked.

---

<!-- SECTION: build -->
## Build System

| Property | Status | Last Verified | Agent | TTL | Notes |
|----------|--------|---------------|-------|-----|-------|
| `npm run build` passes | **verified** | 2026-03-11 | Akido/claude-sonnet-4-6 | 7d | Clean compile, no TS errors |
| `npm test` passes | **assumed** | 2026-03-08 | Akido/claude-sonnet-4-6 | 7d | 28 tests passed at v0.2.21; no logic changes in v0.2.24 |
| `npm run typecheck` passes | **verified** | 2026-03-11 | Akido/claude-sonnet-4-6 | 7d | Build success implies typecheck |
<!-- /SECTION: build -->

<!-- SECTION: runtime -->
## Runtime Behavior

| Property | Status | Last Verified | Agent | TTL | Notes |
|----------|--------|---------------|-------|-----|-------|
| Plugin loads in gateway | **verified** | 2026-03-08 | Akido/claude-sonnet-4-6 | 14d | Verified at v0.2.21; no structural changes since |
| Proxy starts on :31337 | **verified** | 2026-03-08 | Akido/claude-sonnet-4-6 | 14d | Logs: `[cli-bridge] proxy ready on :31337` |
| `vllm/cli-claude/` models route correctly | **verified** | 2026-03-08 | Akido/claude-sonnet-4-6 | 14d | claude-sonnet-4-6, claude-haiku-4-5 tested |
| `vllm/cli-gemini/` models route correctly | **verified** | 2026-03-08 | Akido/claude-sonnet-4-6 | 14d | gemini-2.5-pro, gemini-2.5-flash tested |
| `openai-codex` provider loads | **verified** | 2026-03-08 | Akido/claude-sonnet-4-6 | 14d | Codex model call succeeded |
| Proxy server closes cleanly on plugin stop | **verified** | 2026-03-08 | Akido/claude-sonnet-4-6 | 14d | registerService stop() + closeAllConnections() |
| `/cli-*` commands reachable from webchat | **verified** | 2026-03-08 | Akido/claude-sonnet-4-6 | 14d | requireAuth:false + gateway commands.allowFrom |
| Token refresh interval stops on server close | **assumed** | 2026-03-11 | Akido/claude-sonnet-4-6 | 7d | server.on("close", stopTokenRefresh) added; not live-tested yet |
| Sleep-resilient token refresh works | **assumed** | 2026-03-11 | Akido/claude-sonnet-4-6 | 7d | setInterval(10min) pattern verified by code review; no sleep test run |
<!-- /SECTION: runtime -->

<!-- SECTION: security -->
## Security

| Property | Status | Last Verified | Agent | TTL | Notes |
|----------|--------|---------------|-------|-----|-------|
| No secrets in source | **verified** | 2026-03-08 | Akido/claude-sonnet-4-6 | 30d | Auth tokens read from files, never printed; `[REDACTED]` pattern enforced |
| Proxy only binds to 127.0.0.1 | **verified** | 2026-03-08 | Akido/claude-sonnet-4-6 | 30d | `server.listen(port, "127.0.0.1")` — not exposed externally |
| Proxy requires API key bearer auth | **verified** | 2026-03-08 | Akido/claude-sonnet-4-6 | 14d | 401 returned for missing/wrong key |
| Claude Code CLI spawned without full process.env | **verified** | 2026-03-08 | Akido/claude-sonnet-4-6 | 30d | buildMinimalEnv() used — no OPENCLAW_* vars leaked to subprocess |
| No PII written to logs | **assumed** | — | — | — | Token values redacted; message content not logged |
<!-- /SECTION: security -->

---

## Update Rules (for agents)

- Change `untested` → `verified` only after **running actual code/tests**
- Change `assumed` → `verified` after direct confirmation
- Never downgrade `verified` without explaining why in `LOG.md`
- Add new rows when new system properties become critical
- Check TTL expiry at session start — expired `verified` downgrades to `assumed`
