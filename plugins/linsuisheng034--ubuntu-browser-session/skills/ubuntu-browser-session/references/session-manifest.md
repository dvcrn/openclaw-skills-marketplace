# Session Manifest

`session-manifest.sh` stores durable per-origin browser session records under `~/.agent-browser/` by default.

The runtime layer now derives browser state paths from both `origin` and `session-key`, so one manifest no longer implies one global browser process:

- runtime: `~/.agent-browser/run/<origin-key>/<session-key>/`
- assisted overlay: `~/.agent-browser/assist/<origin-key>/<session-key>/`
- profile: `~/.agent-browser/profiles/<origin-key>/<session-key>/`
- logs: `~/.agent-browser/logs/<origin-key>/<session-key>/`

Storage layout:

- `sessions/<origin-key>/<session-key>.json`
- `index/<origin-key>.json`

The helper intentionally fails ambiguous same-origin selection instead of choosing a session arbitrarily.

Current CLI surface:

```bash
scripts/session-manifest.sh list
scripts/session-manifest.sh write --origin 'https://example.com' --session-key acct-a-main --state ready --browser-pid 123
scripts/session-manifest.sh index-show --origin 'https://example.com'
scripts/session-manifest.sh select --origin 'https://example.com' --account-hint acct-a
scripts/session-manifest.sh mark-stale --origin 'https://example.com' --session-key acct-a-main --reason 'browser exited'
```

Manifest fields currently supported by the helper include:

- `origin`
- `session_key`
- `account_hint`
- `task_scope`
- `state`
- `browser_pid`
- `created_at`
- `last_verified_at`
- `block_reason`
- `cdp_port`
- `cdp_url`
- `websocket_debugger_url`
- `target_id`
- `profile_dir`
- `mode`
- `display`
- `xvfb_display`
- `xvfb_pid`
- `novnc_port`

Operational notes:

- Prefer reusing the same `session-key` across wrapper, runtime, and assisted commands so they resolve the same scoped paths.
- The manifest does not guarantee the browser process is still alive. Always follow selection with `browser-runtime.sh verify`.
- When multiple same-origin sessions exist, keep using `account_hint` or `task_scope` to avoid ambiguous reuse.

Selection rules:

- Return the exact session when `--account-hint` narrows the set to one candidate
- Return the exact session when `--task-scope` narrows the set to one candidate
- Fail with a non-zero exit code when multiple same-origin sessions remain ambiguous
- Never silently choose an arbitrary same-origin session
