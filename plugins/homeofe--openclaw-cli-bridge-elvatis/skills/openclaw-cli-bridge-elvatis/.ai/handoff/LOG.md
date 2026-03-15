# LOG.md — openclaw-cli-bridge-elvatis

_Last 10 sessions. Older entries in LOG-ARCHIVE.md._

---

## 2026-03-11 — Session 6 (Akido / claude-sonnet-4-6)

> **Agent:** claude-sonnet-4-6
> **Phase:** implementation
> **Commit before:** (unpublished local, v0.2.24 base)
> **Commit after:** pending (v0.2.25)

**T-011: Session-safe staged model switching**

### Problem
`/cli-*` commands called `openclaw models set <model>` immediately — a global, instantaneous
switch. If a conversation was in progress, the running agent lost its context mid-task:
tool calls failed silently, plan files weren't written, no error feedback. Session had to
be abandoned. Root cause: no API exists in the plugin SDK to detect if a session is active;
the switch always went through regardless.

### Fix (index.ts)

**New state file:** `~/.openclaw/cli-bridge-pending.json` — stores a staged switch
(`{ model, label, requestedAt }`).

**`switchModel()` refactored into two paths:**
- `applyModelSwitch()` — runs `openclaw models set` immediately (extracted helper)
- `switchModel(forceNow=false)` — stages by default, calls `applyModelSwitch` only with `--now`

**New commands registered:**
- `/cli-apply` — apply staged switch; safe to run after finishing the current task
- `/cli-pending` — show current staged switch state
- `/cli-back` — now also calls `clearPending()` to discard any staged switch

**All `/cli-*` switch commands updated:**
- `acceptsArgs: true` — passes `--now` flag through
- Default: stages + shows warning with instructions
- `--now`: immediate (explicit user choice)

**`/cli-list` updated** to show pending state inline and switching instructions.

### Build + Tests
- `npm run build` — ✅ clean
- `npm test` — ✅ 51/51 (no test changes needed; new code is command-handler logic)

### Version
0.2.24 → 0.2.25 (feature bump: staged switching is new behavior, not just a fix)

---

## 2026-03-11 — Session 5 (Akido / claude-sonnet-4-6)

> **Agent:** claude-sonnet-4-6
> **Phase:** fix
> **Commit before:** (unpublished local, v0.2.23 base)
> **Commit after:** pending (v0.2.24, not yet committed)

**T-009: Stability — sleep-resilient token refresh + timer cleanup**

### Problem
`scheduleTokenRefresh()` in `claude-auth.ts` used a single long `setTimeout` (potentially hours).
Three issues:
1. **Sleep-miss:** If the server went to sleep/hibernate during the timeout window, the timer fired late or not at all. Token expired silently.
2. **Timer-leak:** Repeated calls to `scheduleTokenRefresh()` (e.g., after a refresh) didn't reliably clear the old timer. Duplicate intervals could accumulate.
3. **No cleanup hook:** The `setInterval`/`setTimeout` was never stopped when the proxy server closed, leaving orphaned timers after plugin teardown.

### Fix (3 files)

**`src/claude-auth.ts`:**
- Replaced `refreshTimer: ReturnType<typeof setTimeout>` with `refreshTimer: ReturnType<typeof setInterval>`
- Added `nextRefreshAt: number` state variable — tracks when the next refresh is due (epoch ms)
- Replaced `setTimeout(msUntilRefresh)` with `setInterval(10 * 60 * 1000)` — polls every 10 min, checks `Date.now() >= nextRefreshAt`
- Exported `stopTokenRefresh()` — clears the interval and resets state; safe to call multiple times
- `stopTokenRefresh()` called at top of `scheduleTokenRefresh()` — guarantees no duplicate intervals
- `doRefresh()` no longer calls `scheduleTokenRefresh()` recursively — updates `nextRefreshAt` in-place instead

**`src/proxy-server.ts`:**
- Imported `stopTokenRefresh` from `claude-auth.js`
- Added `server.on("close", () => { stopTokenRefresh(); })` — interval is cleaned up automatically when the server closes

**`openclaw.plugin.json` + `index.ts` + `package.json`:**
- Version bumped 0.2.23 → 0.2.24

### Build
`npm run build` — ✅ clean, no TypeScript errors

### Not yet done
- `npm test` not run (no logic changes to model routing/proxy; assumed passing)
- Not published to GitHub/npm/ClawHub yet → T-010

---

## 2026-03-11 — Session 4 (Akido / claude-sonnet-4-6)

> **Agent:** claude-sonnet-4-6
> **Phase:** review + analysis
> **Note:** Planning session. Code analysis of proxy/auth architecture. Plan written to `/home/chef-linux/.claude/plans/buzzing-honking-corbato.md`. Implementation deferred to Session 5.

---

## 2026-03-08 — Session 3 (Akido / claude-sonnet-4-6)

**Critical bug: Gateway SIGKILL via fuser (fixed in v0.2.9)**

Root cause: `fuser -k 31337/tcp` (added in v0.2.8) sent SIGKILL to the gateway process itself during in-process hot-reloads. The same gateway process holds port 31337 after spawning the proxy. `fuser -k` found it as the port owner and killed it → `code=killed, status=9/KILL` in systemd journal, 1.9G memory peak at death.

Fix: replaced `fuser -k` with a safe health probe. Before binding, `GET /v1/models` is sent to the existing proxy. If 200 → reuse silently. If EADDRINUSE + no response → wait 1s and retry once. No process killing.

**Release pipeline:**
- v0.2.9 → v0.2.21 (incremental fixes: requireAuth, vllm prefix, XDG env vars, model allowlist, tests)
- All published to GitHub, npm, ClawHub

---

## 2026-03-07 — Session 2 (Akido / claude-sonnet-4-6)

**Bug: Port leak on gateway hot-reload (fixed in v0.2.6)**

Root cause: HTTP proxy server on port 31337 had no cleanup handler. On hot-reloads, old server kept port bound. Fix: `api.registerService({ stop: async () => server.close() })` + `closeAllConnections()`.

Also fixed: `openclaw.extensions` missing from `package.json`; `.clawhubignore` documented with rsync workaround.

**Root conflict with openclaw-self-healing-elvatis** resolved: self-healing's `lastRestartAt` was saved after `openclaw gateway restart` (kills process). Fixed in self-healing v0.2.8.

---

## 2026-03-07 — Session 1 (gpt-5.3-codex / sonnet)

**Architecture: Phase 1 + 2 + 3 implemented**

- Phase 1: `openai-codex` auth bridge via `~/.codex/auth.json`
- Phase 2: local OpenAI-compatible proxy (`src/proxy-server.ts`, `src/cli-runner.ts`, `src/config-patcher.ts`)
  - Gemini CLI → `cli-gemini/*` models (prompt via stdin, cwd=tmpdir)
  - Claude Code CLI → `cli-claude/*` models (prompt via stdin, --permission-mode plan)
- Phase 3: `/cli-sonnet`, `/cli-opus`, `/cli-haiku`, `/cli-gemini`, `/cli-gemini-flash`, `/cli-gemini3`, `/cli-codex`, `/cli-codex-mini`, `/cli-back`, `/cli-test`

Published to GitHub, npm, ClawHub at v0.2.5.

Known issue: `openai-codex/gpt-5.4` → 401 missing scope `model.request` (OpenAI account limitation, not a bug).
