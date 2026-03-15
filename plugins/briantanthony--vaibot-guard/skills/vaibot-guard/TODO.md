# VAIBot-Guard — TODO / Notes

## Gateway plugin + installer direction (2026-03-03)

We want VAIBot-Guard enforcement to be **guaranteed** via an in-process **OpenClaw Gateway plugin** (using plugin hooks like `before_tool_call` / `after_tool_call`), not merely encouraged via a skill prompt.

### v1 packaging decision (no npm yet)

OpenClaw supports `openclaw plugins install <npmSpec>`, but for v1 we are **not** requiring npm publishing.

Instead, the installer CLI should:
- drop the plugin into OpenClaw’s discovery path, e.g.
  - `~/.openclaw/extensions/<plugin-id>/index.ts`
  - `~/.openclaw/extensions/<plugin-id>/openclaw.plugin.json`
- enable it via config (`plugins.entries.<plugin-id>.enabled = true`)
- restart the Gateway if needed

Plan for v2:
- publish the plugin to npm (so `openclaw plugins install …` works cleanly)
- keep the same plugin id + config schema for smooth migration

### Modes / posture

- Support `observe` (monitor/log-only) and `enforce` modes.
- Default: `enforce`.
- Missing guard service / outage default posture: **fail-closed** (deny tool execution unless explicitly configured otherwise).
