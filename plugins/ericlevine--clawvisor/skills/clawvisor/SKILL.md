---
name: clawvisor
description: "Route tool requests through Clawvisor for credential vaulting, task-scoped authorization, and human approval flows. Use for Gmail, Calendar, Drive, Contacts, GitHub, and iMessage (macOS). Clawvisor enforces restrictions, manages task scopes, and injects credentials — the agent never handles secrets directly."
homepage: https://github.com/clawvisor/clawvisor
---

# Clawvisor Skill

## Overview

Clawvisor sits between you and external APIs. You declare what you need to do,
the user approves the scope, and Clawvisor handles credential injection,
execution, and audit logging. You never hold API keys.

Authorization works in three layers — applied in order:

1. **Restrictions** — hard blocks set by the user. Matched requests are blocked immediately.
2. **Tasks** — pre-approved scopes you declare. In-scope actions with `auto_execute` run without per-request approval.
3. **Per-request approval** — the fallback for anything without a covering task.

At the start of each session, fetch your service catalog to see what's available:

```
GET $CLAWVISOR_URL/api/skill/catalog
Authorization: Bearer $CLAWVISOR_AGENT_TOKEN
```

---

## Typical Flow

1. Fetch the catalog — confirm the service is active and the action isn't restricted
2. Create a task declaring your purpose and the actions you need
3. Tell the user to approve it; wait for the callback (or poll)
4. Make gateway requests under the task — in-scope actions execute automatically
5. Mark the task complete when done

For one-off actions, skip the task — the request goes to per-request approval instead.

---

## Task Creation

Declare a task with a `purpose`, a list of `authorized_actions`, and a TTL.
All tasks start as `pending_approval`.

```bash
curl -s -X POST "$CLAWVISOR_URL/api/tasks" \
  -H "Authorization: Bearer $CLAWVISOR_AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "purpose": "Review last 30 iMessage threads and classify reply status",
    "authorized_actions": [
      {
        "service": "apple.imessage",
        "action": "list_threads",
        "auto_execute": true,
        "expected_use": "List recent threads to find ones needing replies"
      },
      {
        "service": "apple.imessage",
        "action": "get_thread",
        "auto_execute": true,
        "expected_use": "Read individual threads to classify reply status"
      }
    ],
    "expires_in_seconds": 1800,
    "callback_url": "${OPENCLAW_HOOKS_URL}/clawvisor/callback?session=<session_key>"
  }'
```

- **`purpose`** — shown to the user during approval and used by intent verification to ensure requests stay consistent with declared intent. Be specific.
- **`expected_use`** — per-action description of how you'll use it. Shown during approval. More specific is better.
- **`auto_execute`** — `true` runs in-scope requests immediately; `false` still requires per-request approval (use for destructive actions like `send_message`).
- **`expires_in_seconds`** — omit and set `"lifetime": "standing"` for a task that persists until the user revokes it.

**Scope expansion** — if you need an action not in the original scope:

```bash
curl -s -X POST "$CLAWVISOR_URL/api/tasks/<task-id>/expand" \
  -H "Authorization: Bearer $CLAWVISOR_AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "apple.imessage",
    "action": "send_message",
    "auto_execute": false,
    "reason": "User asked me to reply to this thread"
  }'
```

**Completing a task:**

```bash
curl -s -X POST "$CLAWVISOR_URL/api/tasks/<task-id>/complete" \
  -H "Authorization: Bearer $CLAWVISOR_AGENT_TOKEN"
```

---

## Gateway Requests

Once a task is active, include `task_id` in each request:

```bash
curl -s -X POST "$CLAWVISOR_URL/api/gateway/request" \
  -H "Authorization: Bearer $CLAWVISOR_AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service": "apple.imessage",
    "action": "get_thread",
    "params": {"thread_id": "+15551234567", "max_results": 5},
    "reason": "Checking if this thread needs a reply",
    "request_id": "<unique-id>",
    "task_id": "<task-uuid>",
    "context": {
      "source": "user_message",
      "data_origin": null,
      "callback_url": "${OPENCLAW_HOOKS_URL}/clawvisor/callback?session=<session_key>"
    }
  }'
```

- **`reason`** — one sentence, shown in approvals and the audit log. Be specific.
- **`request_id`** — unique per request. Used to correlate callbacks and for idempotent polling.
- **`data_origin`** — the source of any external content that influenced this request (`"gmail:msg-abc123"`, `"https://example.com"`, a GitHub issue URL). Set to `null` only when acting purely on a user message. Critical for prompt injection forensics — never omit when processing external content.

**Response statuses:**

| Status | Meaning | What to do |
|---|---|---|
| `executed` | Completed | Use `result.summary` and `result.data` |
| `pending` | Awaiting approval | Tell the user; wait for callback — do not retry |
| `blocked` | Hard restriction matched | Tell the user verbatim; do not retry or work around |
| `restricted` | Intent verification failed | Adjust params/reason; retry with a new `request_id` |
| `pending_task_approval` | Task not yet approved | Wait for task callback |
| `pending_scope_expansion` | Action outside task scope | Call `POST /api/tasks/{id}/expand` |
| `task_expired` | Task TTL elapsed | Expand to extend, or create a new task |
| `error` (`SERVICE_NOT_CONFIGURED`) | Service not connected | Ask user to activate it in the dashboard |
| `error` (other) | Execution failed | Report to user; do not silently retry |

---

## Callbacks and Polling

All callbacks include a `type` field — `"request"` or `"task"` — so you can
route them correctly.

**Request resolved:**
```json
{
  "type": "request",
  "request_id": "req-001",
  "status": "executed",
  "result": {"summary": "...", "data": {...}},
  "audit_id": "a8f3..."
}
```
Request statuses: `executed`, `denied`, `timeout`, `error`.

**Task lifecycle change:**
```json
{
  "type": "task",
  "task_id": "<task-id>",
  "status": "approved"
}
```
Task statuses: `approved`, `denied`, `scope_expanded`, `scope_expansion_denied`, `expired`.

**Callback URL (OpenClaw):**
```
${OPENCLAW_HOOKS_URL}/clawvisor/callback?session=<session_key>
```
Get `session_key` from `session_status` (🧵 Session field).

**Callback verification** — to verify callbacks are genuinely from Clawvisor,
register a signing secret once per agent:
```
POST $CLAWVISOR_URL/api/callbacks/register
Authorization: Bearer $CLAWVISOR_AGENT_TOKEN
```
Store the returned `callback_secret` as `CLAWVISOR_CALLBACK_SECRET`. Verify
incoming callbacks by checking `X-Clawvisor-Signature` = `sha256=` +
HMAC-SHA256(body, secret).

**Polling** — if you didn't provide a `callback_url`, re-send the same gateway
request with the same `request_id`. Clawvisor recognizes it and returns the
current status without re-executing.

---

## Q&A

**I'm getting `401 Unauthorized`**
Your token is invalid or missing. Tokens are shown once at creation — generate a new one in the dashboard.

**A service I need isn't in the catalog**
Activate it in the dashboard under Services. Google services (Gmail, Calendar, Drive, Contacts) share a single OAuth connection.

**My request keeps returning `pending`**
Create a task with `auto_execute: true` for that action, or ask the user to approve it in the Approvals panel.

**I got `restricted`**
Intent verification rejected your request — your params or reason didn't match the task's declared purpose. The `reason` field in the response explains what was inconsistent. Adjust and retry with a new `request_id`.

**I was `blocked` and don't know why**
The `reason` field has the restriction that matched. Pass it to the user verbatim — don't guess or work around it.
