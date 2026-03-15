---
name: mem9
description: "Persistent cloud memory for OpenClaw agents.\n\n Use when users say:\n - \"install mem9\"\n - \"setup memory\"\n - \"add memory plugin\"\n - \"openclaw memory\"\n - \"mem9 onboarding\"\n - \"memory not working\"\n - \"import memories\"\n - \"upload sessions\""
---

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   ███╗   ███╗███████╗███╗   ███╗ █████╗                      │
│   ████╗ ████║██╔════╝████╗ ████║██╔══██╗                     │
│   ██╔████╔██║█████╗  ██╔████╔██║╚██████║                     │
│   ██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║ ╚═══██║                     │
│   ██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║ █████╔╝                     │
│   ╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ ╚════╝                      │
│                                                              │
│   persistent memory for ai agents                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

# mem9

Your agent forgets nothing. Stateless plugin → REST API → DB.

Persistent memory for AI agents.

No authentication. Tenant ID in URL path is the only identifier.

---

## What You Get

| Tool | When |
|------|------|
| `memory_store` | Persist facts, decisions, context |
| `memory_search` | Hybrid vector + keyword search |
| `memory_get` | Retrieve by ID |
| `memory_update` | Modify existing memory |
| `memory_delete` | Remove |

Lifecycle hooks (automatic — no agent action needed):

| Hook | Trigger | What happens |
|------|---------|-------------|
| `before_prompt_build` | Every LLM call | Relevant memories injected as context |
| `before_reset` | Before `/reset` | Session summary saved |
| `agent_end` | Agent finishes | Last response captured |

---

## Onboarding

### Step 1 — Provision tenant

`[AGENT]`

```bash
curl -sX POST https://api.mem9.ai/v1alpha1/mem9s | jq .
```

Response:
```json
{
  "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

Save `id` as `TENANT_ID`.

### Step 2 — Install plugin

`[AGENT]`

```bash
openclaw plugins install @mem9/mem9
```

### Step 3 — Configure openclaw.json

#### OpenClaw ≥2.2.0

`[AGENT]` Patch existing config (merge-safe, preserves other keys):

```bash
jq --arg tid "$TENANT_ID" '
  .plugins.slots.memory = "mem9" |
  .plugins.entries.mem9 = {
    enabled: true,
    config: { apiUrl: "https://api.mem9.ai", tenantID: $tid }
  } |
  .plugins.allow = ((.plugins.allow // []) + ["mem9"] | unique)
' openclaw.json > tmp.json && mv tmp.json openclaw.json
```

**Note:** The `allow` array is additive—existing entries are preserved, `mem9` is appended (deduplicated).

Or if no `openclaw.json` exists, create:

```json
{
  "plugins": {
    "slots": { "memory": "mem9" },
    "entries": {
      "mem9": {
        "enabled": true,
        "config": {
          "apiUrl": "https://api.mem9.ai",
          "tenantID": "<your-tenant-id>"
        }
      }
    },
    "allow": ["mem9"]
  }
}
```

#### OpenClaw <2.2.0

`[AGENT]` No `allow` array needed:

```bash
jq --arg tid "$TENANT_ID" '
  .plugins.slots.memory = "mem9" |
  .plugins.entries.mem9 = {
    enabled: true,
    config: { apiUrl: "https://api.mem9.ai", tenantID: $tid }
  }
' openclaw.json > tmp.json && mv tmp.json openclaw.json
```

If result returns stored memory → setup successful.

### Step 4 — What's Next

`[AGENT]` Print the following to the user:

```
✅ mem9 installed!

📤 UPLOAD HISTORY (optional)
   Upload your local memory files for complete cloud backup:
   
   Say "import memories to mem9" and I'll scan and upload automatically.
   Supported: memory.json, memories/*.json, sessions/*.json

💾 YOUR RECOVERY KEY (save this!)
   
   TENANT_ID: <your-tenant-id>
   
   Lost your OpenClaw? New machine? Just configure this ID in Step 3.
   All memories instant restore. Zero re-upload.
```

---

## API Reference

Base: `https://api.mem9.ai`  
Routes: `/v1alpha1/mem9s/{tenantID}/...`  
Header: `X-Mnemo-Agent-Id: <name>` (optional)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1alpha1/mem9s` | Provision tenant |
| GET | `/healthz` | Health check |
| POST | `/{tid}/memories` | Create memory |
| GET | `/{tid}/memories` | Search (`?q=`, `?tags=`, `?source=`, `?limit=`) |
| GET | `/{tid}/memories/{id}` | Get by ID |
| PUT | `/{tid}/memories/{id}` | Update |
| DELETE | `/{tid}/memories/{id}` | Delete |
| POST | `/{tid}/imports` | Upload file (multipart) |
| GET | `/{tid}/imports` | List import tasks |
| GET | `/{tid}/imports/{id}` | Task status |

---

## Examples

```bash
export TENANT_ID="your-tenant-id"
export API="https://api.mem9.ai/v1alpha1/mem9s/$TENANT_ID"
```

**Store:**
```bash
curl -sX POST "$API/memories" -H "Content-Type: application/json" \
  -d '{"content":"Project uses PostgreSQL 15","tags":["tech"],"source":"agent-1"}'
```

**Search:**
```bash
curl -s "$API/memories?q=postgres&limit=5"
curl -s "$API/memories?tags=tech&source=agent-1"
```

**Get/Update/Delete:**
```bash
curl -s "$API/memories/{id}"
curl -sX PUT "$API/memories/{id}" -H "Content-Type: application/json" -d '{"content":"updated"}'
curl -sX DELETE "$API/memories/{id}"
```

**Import files:**
```bash
# Memory file
curl -sX POST "$API/imports" -F "file=@memory.json" -F "agent_id=agent-1" -F "file_type=memory"

# Session file
curl -sX POST "$API/imports" -F "file=@session.json" -F "agent_id=agent-1" -F "file_type=session" -F "session_id=ses-001"

# Check status
curl -s "$API/imports"
```

---

## Default Import Behavior

When user says "import memories to mem9" without specifying files:

1. Scan agent workspace for memory/session files
2. Upload **15 most recent** (by mtime)
3. **Upload in parallel** for speed
   **Paths to scan:**
```
./memory.json         → file_type=memory
./memories.json       → file_type=memory
./memories/*.json     → file_type=memory
./sessions/*.json     → file_type=session (session_id = filename)
./session/*.json      → file_type=session (session_id = filename)
```

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Plugin not loading | Check `slots.memory = "mem9"` and `entries.mem9.enabled = true` |
| `404` on API call | Verify tenantID; run `curl https://api.mem9.ai/healthz` |
---

## Next Steps

After first read, do this immediately:

1. **Print** — Tell the user:
   > mem9 ready. I can `memory_store`, `memory_search`, `memory_get`, `memory_update`, `memory_delete`. Memories auto-recall on every prompt and auto-capture on session end.
2. **Test** — Ask the user to tell you something to remember. Store it. Start a new session. Verify recall.
3. **Explore** — `curl -s "https://api.mem9.ai/v1alpha1/mem9s/$TENANT_ID/memories?limit=10" | jq .`

---

## Update

Check daily (add to heartbeat or cron at 00:00):

```bash
curl -s https://raw.githubusercontent.com/qiffang/mnemos/main/clawhub-skill/mem9/SKILL.md \
  -o ~/.openclaw/skills/mem9/SKILL.md
```

---

```
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
░  stateless agents · cloud memory · zero amnesia              ░
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```