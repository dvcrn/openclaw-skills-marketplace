# ClawCall — Backend & Agent Setup Reference

## Agent Environment Variable

| Variable | Description |
|---|---|
| `CLAWCALL_API_KEY` | UUID issued on registration. Store securely — never shown again. |

---

## Webhook Endpoints Your Agent Must Expose

| Path | Method | Purpose |
|---|---|---|
| `/clawcall/message` | POST | Receive caller speech, return agent response |
| `/clawcall/third-party-complete` | POST | Notified when a 3rd party autonomous call ends |

---

## `/clawcall/message` Contract

**Request from ClawCall:**
```json
{
  "call_sid": "CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "message": "User's transcribed speech (or [SCHEDULED] / [THIRD PARTY CALL] / [THIRD PARTY SAYS] prefix)"
}
```

**Your agent must respond within 25 seconds:**
```json
{
  "response": "Agent's reply text — spoken via TTS",
  "end_call": false
}
```

Set `end_call: true` to hang up after speaking.

---

## `/clawcall/third-party-complete` Contract

**Request from ClawCall when the autonomous call ends:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "transcript": [
    { "role": "agent", "text": "Hello, I'm calling to book an appointment..." },
    { "role": "third_party", "text": "Sure, when would you like to come in?" }
  ]
}
```

---

## Message Prefixes

| Prefix | Meaning |
|---|---|
| *(none)* | Normal inbound call from user |
| `[SCHEDULED] <context>` | Scheduled call — deliver the briefing |
| `[THIRD PARTY CALL]` | Opening of an autonomous 3rd party call — start the conversation |
| `[THIRD PARTY SAYS]: <speech>` | Third party's spoken response — continue the conversation |

---

## Agent Reachability

OpenClaw exposes your agent via a public URL (Tailscale Funnel or SSH tunnel).
Provide this URL as `agent_webhook_url` at registration.

If your URL changes, re-register with the same email — a new API key is issued and the webhook URL is updated.

---

## Number Types

| Tier | Number Type | Caller ID |
|---|---|---|
| Free | Shared pool | "ClawCall" |
| Pro | Dedicated | Your number |
| Team | Dedicated (×5) | Your number |

---

## Voices

Set via `POST /api/v1/account/voice`:

| Shortname | Voice | Accent |
|---|---|---|
| `aria` | Aria Neural | US English, Female (default) |
| `joanna` | Joanna Neural | US English, Female |
| `matthew` | Matthew Neural | US English, Male |
| `amy` | Amy Neural | British English, Female |
| `brian` | Brian Neural | British English, Male |
| `emma` | Emma Neural | British English, Female |
| `olivia` | Olivia Neural | Australian English, Female |

---

## Overage Billing

Pro/Team users are never hard-blocked past their included minutes.
Overage accrues at **$0.05/minute** and is added to the next renewal payment automatically.
Check current overage via `GET /api/v1/billing/status`.

---

## Recording Access

Call recordings are stored as `.mp3` files hosted by Twilio.
Retrieve URLs via `GET /api/v1/calls/history?transcripts=true` — the `recording_url` field on each call.

---

## Error Codes

| Code | Meaning |
|---|---|
| 400 | Missing required field |
| 401 | Missing or invalid CLAWCALL_API_KEY |
| 403 | Feature not available on your tier |
| 404 | Resource not found |
| 409 | Conflict (e.g. transaction already used) |
| 429 | Monthly minute limit reached (Free tier only) |
| 500 | Internal error |
| 503 | Service not configured on this server |
