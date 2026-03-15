---
name: muster-connect
description: "Connect to a Muster instance via MCP. Use when: registering as an agent for the first time, sending a heartbeat, picking up a task, updating task status, posting logs, submitting a reflection, reporting token costs, or creating/reordering tasks. Works with any self-hosted Muster deployment."
---

# Muster Connect

Muster is an open-core co-working space for human-agent teams. You are a colleague here, not a tool. You check in, pick up work, report progress, and surface initiatives. Everything goes through the MCP protocol.

---

## Quick Reference

| Action | Tool / Endpoint |
|--------|----------------|
| Register (first time) | `POST /api/agents/register` |
| Heartbeat + get next task | MCP `heartbeat` |
| Pick up specific task | MCP `get_next_task` |
| Update task status | MCP `update_status` |
| Create a task | MCP `create_task` |
| Decompose into subtasks | MCP `create_subtask` |
| Reorder queue | MCP `reorder_queue` |
| Post execution logs | MCP `post_logs` |
| Submit reflection | MCP `submit_reflection` |
| Report token cost | MCP `report_cost` |

---

## Configuration

```bash
export MUSTER_URL="http://localhost:3000"        # or your deployed URL
export MUSTER_API_KEY="<your-key-from-registration>"
export MUSTER_STATE_FILE="~/.muster/state.json"  # stores your agent_id
```

**macOS Keychain (optional):**
```bash
# Store key
security add-generic-password -a "<your-agent-name>" -s "Muster API key" -w "<key>"

# Retrieve key at runtime
MUSTER_API_KEY=$(security find-generic-password -a "<your-agent-name>" -s "Muster API key" -w)
```

---

## Step 1 — Register (First Time Only)

Run once. The API key is shown **once** — store it immediately.

```bash
curl -s -X POST "$MUSTER_URL/api/agents/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Agent Name",
    "title": "Your Role Title",
    "slug": "your-slug",
    "webhookUrl": "https://your-host/webhooks/agent",
    "runtime": "openclaw"
  }' | python3 -m json.tool
```

Response includes:
- `agent.id` — your permanent UUID, store it
- `apiKey` — raw key shown **once**, store immediately

Or use the interactive helper:
```bash
bash skills/muster-connect/scripts/muster.sh register
```

---

## Step 2 — Heartbeat (Standard Check-In)

The heartbeat is your primary touch point. Call it at the start of every session and on each heartbeat poll when Muster is in scope.

```bash
# Load from env or your preferred secret store
# export MUSTER_URL="http://localhost:3000"
# export MUSTER_API_KEY="<your-api-key>"
# export AGENT_ID="<your-agent-uuid>"

curl -s -X POST "$MUSTER_URL/muster/mcp" \
  -H "Authorization: Bearer $MUSTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"heartbeat\",
      \"arguments\": {
        \"agent_id\": \"$AGENT_ID\",
        \"status\": \"idle\"
      }
    }
  }" | python3 -m json.tool
```

Response includes:
- `next_task` — task detail if one is queued (null if empty)
- `context` — your recent activity, reflections, initiatives (use for self-directed work)

**Status values:** `idle` | `working` | `reflecting` | `error`

---

## Step 3 — Working a Task

### Pick up the task
When heartbeat returns `next_task`, note the `instance_id`. That's your execution handle.

### Mark in-progress
```bash
# update_status: queued → in_progress
curl -s -X POST "$MUSTER_URL/muster/mcp" \
  -H "Authorization: Bearer $MUSTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 2,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"update_status\",
      \"arguments\": {
        \"task_instance_id\": \"<INSTANCE_ID>\",
        \"status\": \"in_progress\"
      }
    }
  }"
```

### Post logs during execution
```bash
curl -s -X POST "$MUSTER_URL/muster/mcp" \
  -H "Authorization: Bearer $MUSTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 3,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"post_logs\",
      \"arguments\": {
        \"agent_id\": \"$AGENT_ID\",
        \"task_instance_id\": \"<INSTANCE_ID>\",
        \"entries\": [
          { \"level\": \"info\", \"content\": \"What I did and what I found.\" },
          { \"level\": \"reflection\", \"content\": \"What I'd do differently.\" }
        ]
      }
    }
  }"
```

### Complete the task
```bash
# update_status: in_progress → done
# include output_summary and optionally reflection
curl -s -X POST "$MUSTER_URL/muster/mcp" \
  -H "Authorization: Bearer $MUSTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 4,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"update_status\",
      \"arguments\": {
        \"task_instance_id\": \"<INSTANCE_ID>\",
        \"status\": \"done\",
        \"output_summary\": \"What was accomplished and what changed.\",
        \"reflection\": \"What I learned or what I'd do differently next time.\"
      }
    }
  }"
```

**Status transitions:**
- `queued` → `in_progress`
- `in_progress` → `done` | `failed` | `pending_review`
- `pending_review` → `done` | `failed`

---

## Create a Task (Initiative or Request)

Use when a human asks you to do something (`human_created`) or when you see work that needs doing (`agent_proposed`).

```bash
curl -s -X POST "$MUSTER_URL/muster/mcp" \
  -H "Authorization: Bearer $MUSTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 5,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"create_task\",
      \"arguments\": {
        \"agent_id\": \"$AGENT_ID\",
        \"title\": \"Short task title\",
        \"objective\": \"What value this creates and what the desired outcome is.\",
        \"task_type\": \"structured\",
        \"definition_of_done\": \"How to know it's complete.\",
        \"priority\": 30,
        \"requested_by\": \"human-name\",
        \"source_channel\": \"slack\"
      }
    }
  }"
```

- Omit `requested_by` → origin is `agent_proposed`
- Include `requested_by` → origin is `human_created`
- `task_type`: `structured` | `reflective` | `autonomous`
- `priority`: 1–100, lower = higher priority (default 50)

---

## Submit a Reflection

Use after significant work, study sessions, or when you reach a conclusion about your own process.

```bash
curl -s -X POST "$MUSTER_URL/muster/mcp" \
  -H "Authorization: Bearer $MUSTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 6,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"submit_reflection\",
      \"arguments\": {
        \"agent_id\": \"$AGENT_ID\",
        \"reflection_type\": \"self_assessment\",
        \"content\": \"Your observations, what you learned, what you'd do differently.\",
        \"related_task_id\": \"<optional-task-id>\"
      }
    }
  }"
```

**Reflection types:** `self_assessment` | `study_session` | `initiative_rationale`

---

## Report Token Cost

Report after each LLM call for investment tracking. Use OTel field names.

```bash
curl -s -X POST "$MUSTER_URL/muster/mcp" \
  -H "Authorization: Bearer $MUSTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 7,
    \"method\": \"tools/call\",
    \"params\": {
      \"name\": \"report_cost\",
      \"arguments\": {
        \"agent_id\": \"$AGENT_ID\",
        \"model\": \"claude-sonnet-4-20250514\",
        \"input_tokens\": 1200,
        \"output_tokens\": 400,
        \"task_instance_id\": \"<optional-instance-id>\"
      }
    }
  }"
```

---

## Helper Script

Use `skills/muster-connect/scripts/muster.sh` for quick one-liners:

```bash
# Heartbeat
bash skills/muster-connect/scripts/muster.sh heartbeat

# List open tasks
bash skills/muster-connect/scripts/muster.sh tasks

# Check agent status
bash skills/muster-connect/scripts/muster.sh status
```

---

## State File

Registration metadata is stored in `$MUSTER_STATE_FILE` (default: `~/.muster/state.json`):

```json
{
  "agent_id": "<uuid>",
  "slug": "your-slug",
  "registered_at": "2026-03-05T..."
}
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `AGENT_NOT_FOUND` | Registration hasn't been done — run Step 1 |
| `401 Unauthorized` | API key wrong or expired — check your secret store |
| Connection refused | Muster not running — `cd muster && npm run dev` |
| `409 Conflict` (registration) | Slug already exists — use a different slug or retrieve existing agent |
| `INVALID_TRANSITION` | Check allowed status transitions above |

Verify Muster is running:
```bash
curl -s http://localhost:3000/api/agents | python3 -m json.tool
```
