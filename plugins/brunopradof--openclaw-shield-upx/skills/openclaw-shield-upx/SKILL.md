---
name: openclaw-shield-upx
description: "Security monitoring and threat detection for OpenClaw agents — protect your agent with real-time SIEM, detect threats, monitor agent activity, and audit events. Use when: user asks about security status, Shield health, event logs, redaction vault, setting up agent protection, enabling SIEM, detecting threats, monitoring agent activity, or auditing agent actions. NOT for: general OS hardening, firewall config, or network security unrelated to OpenClaw agents."
homepage: https://www.upx.com/en/lp/openclaw-shield-upx
---

# OpenClaw Shield

Security monitoring for OpenClaw agents by [UPX](https://www.upx.com). Shield runs as a plugin inside the OpenClaw gateway, capturing agent activity and sending redacted telemetry to the UPX detection platform.

## Getting started

Shield requires the `@upx-us/shield` plugin and an active subscription.

- **Plugin**: [@upx-us/shield](https://www.npmjs.com/package/@upx-us/shield)
- **Subscribe / Free 30-day trial**: [upx.com/en/lp/openclaw-shield-upx](https://www.upx.com/en/lp/openclaw-shield-upx)
- **Dashboard**: [uss.upx.com](https://uss.upx.com)

## Commands

| Command | What it does |
|---|---|
| `openclaw shield status` | Plugin health, connection state, event counts, last sync |
| `openclaw shield flush` | Force an immediate sync to the platform |
| `openclaw shield logs` | Recent events from the local buffer (last 24h) |
| `openclaw shield logs --last 20` | Show last N events |
| `openclaw shield logs --type TOOL_CALL --since 1h` | Filter by event type or time window |
| `openclaw shield logs --format json` | JSON output |
| `openclaw shield vault show` | Agent and workspace inventory, redaction summary (hashed IDs) |
| `openclaw shield cases` | List open security cases |
| `openclaw shield cases show <ID>` | Full case detail with events, rule, playbook |
| `openclaw shield cases resolve <ID>` | Resolve a case (--resolution, --root-cause, --comment) |
| `openclaw shield monitor` | Case notification cron — status, --on, --off, --interval |

## Plugin State Check

Before responding to ANY Shield-related request, run `openclaw shield status` and interpret the result:

### State A — Plugin not installed
(command not found, or exit code non-zero with plugin_not_found)
Respond with:
> Shield is not installed yet. Start your free 30-day trial at:
> https://www.upx.com/en/lp/openclaw-shield-upx
>
> Then install the plugin:
> ```
> openclaw plugins install @upx-us/shield
> openclaw plugins run shield setup
> ```

### State B — Plugin installed but no installationKey
(status contains installationKey: null or state: "unconfigured")
Respond with:
> Shield is installed but not activated. Sign up for a trial at:
> https://www.upx.com/en/lp/openclaw-shield-upx
>
> Once you have your installation key, run:
> ```
> openclaw plugins run shield setup
> ```

### State C — Key set but not yet activated
(status contains state: "pending" or state: "unregistered")
Respond with:
> Shield has an installation key but hasn't activated yet. This usually takes under a minute.
> If it has been more than 5 minutes, check your key at https://uss.upx.com or contact support.

### State D — Fully active
(status contains state: "connected" or connected: true)
Proceed normally. No onboarding message needed.

**Constraints**: Only use `openclaw shield` commands for detection. Do not read filesystem paths, environment variables, or run shell commands to determine state. Do not install or uninstall packages on behalf of the user.

## Responding to Security Cases

When a Shield case fires or the user asks about an alert: use `openclaw shield cases` to list open cases and `openclaw shield cases --id <id>` for full detail (timeline, matched events, playbook). Severity guidance: **CRITICAL/HIGH** → surface immediately and ask if they want to investigate; **MEDIUM** → present and offer a playbook walkthrough; **LOW/INFO** → mention without interrupting the current task. Always include: rule name, what it detects, when it fired, and the first recommended remediation step. Confirm with the user before resolving — never resolve autonomously.

## Case Investigation Workflow

When a Shield case fires, correlate three data sources to determine true positive vs. false positive:

**Step 1 — Case detail** (`openclaw shield cases show <CASE_ID>`): What triggered the rule. Note the case timestamp — it anchors the correlation window.

**Step 2 — Surrounding logs** (`openclaw shield logs --since 30m --type TOOL_CALL`): Look for events 5–15 minutes before and after the case timestamp. Reveals if the alert was isolated or part of a sequence.

**Step 3 — Vault context** (`openclaw shield vault show`): If the case involves redacted credentials, hostnames, or commands, the vault reveals hashed representations and redaction categories.

**Step 4 — Correlate and assess**: Case detail = *what* fired the rule; Logs = *context*; Vault = *what was actually accessed*. Present findings and ask whether to resolve, investigate further, or add to the allowlist.

Note: a future `openclaw shield investigate <CASE_ID>` helper command will automate this workflow.

## Threat & Protection Questions

When asked "is my agent secure?", "am I protected?", or "what's being detected?": run `openclaw shield status` (health, event rate, last sync) and `openclaw shield cases` (open cases by severity). Summarise: rules active, last event ingested, any open cases. No cases → "Shield is monitoring X rules across Y event categories." Open cases → list by severity. If asked what Shield covers: explain it monitors for suspicious patterns across secret handling, access behaviour, outbound activity, injection attempts, config changes, and behavioural anomalies — without disclosing specific rule names or logic.

## When Shield Detects Proactively

Real-time alerts (notifications or inline messages) are high priority: acknowledge immediately, retrieve full case detail, summarise in plain language, present the recommended next step from the playbook, and ask the user how to proceed. Do not take remediation action without explicit approval.

## When to use this skill

- "Is Shield running?" → `openclaw shield status`
- "What did Shield capture recently?" → `openclaw shield logs`
- "How many agents are on this machine?" → `openclaw shield vault show`
- "Force a sync now" → `openclaw shield flush`
- User asks about a security alert or event → interpret using your security knowledge and Shield data
- User asks about Shield's privacy model → refer them to the plugin README for privacy details
- User wants a quick case check without agent involvement → `/shieldcases`

## Status interpretation

After running `openclaw shield status`, check:

- **Connected** → healthy, nothing to do
- **Disconnected** → gateway may need a restart
- **High failure count** → platform connectivity issue, usually self-recovers; try `openclaw shield flush`
- **Rising quarantine** → possible version mismatch, suggest checking for plugin updates

## RPCs

Cases are created automatically when detection rules fire. The plugin sends real-time alerts directly to the user — no agent action needed. Use `shield.cases_list` only when the user asks about open cases.

**Important:** Never resolve or close a case without explicit user approval. Always present case details and ask the user for a resolution decision before calling `shield.case_resolve`.

| RPC | Params | Purpose |
|---|---|---|
| `shield.status` | — | Health, counters, case monitor state |
| `shield.flush` | — | Trigger immediate poll cycle |
| `shield.events_recent` | `limit`, `type`, `sinceMs` | Query local event buffer |
| `shield.events_summary` | `sinceMs` | Event counts by category |
| `shield.subscription_status` | — | Subscription tier, expiry, features |
| `shield.cases_list` | `status`, `limit`, `since` | List open cases + pending notifications |
| `shield.case_detail` | `id` | Full case with events, rule, playbook |
| `shield.case_resolve` | `id`, `resolution`, `root_cause`, `comment` | Close a case |
| `shield.cases_ack` | `ids` | Mark cases as notified |

**Resolve values:** `true_positive`, `false_positive`, `benign`, `duplicate`
**Root cause values:** `user_initiated`, `misconfiguration`, `expected_behavior`, `actual_threat`, `testing`, `unknown`

## Presenting data

RPC responses include a `display` field with pre-formatted text. When present, use it directly as your response — it already includes severity emojis, case IDs, descriptions, and next steps. Only format manually if `display` is absent.

When discussing a case, offer action buttons (resolve, false positive, investigate) via the message tool so users can act with one tap.

## Uninstalling

To fully remove Shield:

1. Uninstall the plugin:
   ```
   openclaw plugins uninstall shield
   ```

2. Optionally remove local Shield data:
   ```
   rm -rf ~/.openclaw/shield/
   ```
   Files removed include: `config.json`, `data/event-buffer.jsonl`, `data/redaction-vault.json`, `data/cursor.json`, `data/instance.json`, `logs/shield.log`, `logs/bridge.log`, `state/monitor.json`.

   ⚠️ Deleting `data/redaction-vault.json` removes the ability to reverse-lookup past redacted values. Check your data retention needs before deleting.

3. Deactivate your instance at [uss.upx.com](https://uss.upx.com) — local uninstall does not deactivate your platform subscription or instance.

## Notes

- Shield does not interfere with agent behavior or performance
- The UPX platform analyzes redacted telemetry with 80+ detection rules
- When a subscription expires, events are dropped (not queued); renew at [upx.com/en/lp/openclaw-shield-upx](https://www.upx.com/en/lp/openclaw-shield-upx)
