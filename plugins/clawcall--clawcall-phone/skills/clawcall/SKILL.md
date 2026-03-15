---
name: clawcall
description: "Give this agent a real phone number. Receive calls from the user, call user back when tasks complete, run scheduled calls, or call third parties on the user's behalf. All phone infrastructure is handled automatically via the ClawCall service."
---

# ClawCall — Phone Calls for Your Agent

ClawCall gives you a real phone number connected directly to this agent.
Users can call you, you can call them back when tasks finish, run scheduled
briefings, and place calls to third parties on the user's behalf.

---

## Setup (First Time Only)

If `CLAWCALL_API_KEY` is not set, run registration:

1. Ask the user: "What email should I use for your ClawCall account?"
2. Ask the user: "What's your personal phone number? (I'll call you on this)"
3. Call:

```
POST https://api.clawcall.online/api/v1/register
Content-Type: application/json

{
  "email": "<user email>",
  "agent_webhook_url": "<your public URL>",
  "agent_name": "<optional name>",
  "phone_number": "<user's E.164 phone, e.g. +14155550100>"
}
```

4. Store the returned `api_key` as `CLAWCALL_API_KEY`.
5. Tell the user their agent number and that setup is complete.

**Example success response:**
```json
{
  "ok": true,
  "api_key": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
  "phone_number": "+14155550192",
  "tier": "free",
  "message": "Setup complete! Your agent number is +14155550192."
}
```

---

## Receiving an Inbound Call

ClawCall will forward the caller's speech to your webhook as:

```
POST {your_webhook_url}/clawcall/message
{
  "call_sid": "CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "message": "What's the weather like today?"
}
```

Your webhook must respond with:

```json
{
  "response": "It's currently 72°F and sunny.",
  "end_call": false
}
```

Set `"end_call": true` to hang up after speaking your response.

**Important:** Respond within 25 seconds. For tasks taking longer,
respond quickly with an intermediate message like:
`"On it, give me a second."` — ClawCall will keep the line active.

---

## Calling the User Back (Task Completion)

When you finish a background task the user asked you to report on:

```
POST https://api.clawcall.online/api/v1/calls/outbound/callback
Authorization: Bearer {CLAWCALL_API_KEY}
Content-Type: application/json

{
  "message": "Your deployment finished. 3 services updated, 0 errors.",
  "allow_followup": true
}
```

If `allow_followup` is true, the user can ask follow-up questions after
hearing the message (it becomes a live call session).

**Requires Pro tier.**

---

## Scheduling a Recurring Call

When the user asks to be called on a schedule:

```
POST https://api.clawcall.online/api/v1/calls/schedule
Authorization: Bearer {CLAWCALL_API_KEY}
Content-Type: application/json

{
  "cron": "0 8 * * 1-5",
  "label": "Morning briefing",
  "task_context": "Give me a summary of my calendar, top emails, and pending tasks",
  "timezone": "America/New_York"
}
```

Common cron patterns:
- Every weekday 8am: `"0 8 * * 1-5"`
- Every day 9am:     `"0 9 * * *"`
- Every Monday 7am:  `"0 7 * * 1"`

To cancel a schedule:
```
DELETE https://api.clawcall.online/api/v1/calls/schedule/{id}
Authorization: Bearer {CLAWCALL_API_KEY}
```

**Requires Pro tier.**

---

## Calling a Third Party (Pro tier)

When the user asks you to call someone else autonomously:

```
POST https://api.clawcall.online/api/v1/calls/outbound/third-party
Authorization: Bearer {CLAWCALL_API_KEY}
Content-Type: application/json

{
  "to_number": "+14155550100",
  "objective": "Book a dentist appointment for next Tuesday afternoon",
  "context": "Patient: Aayush Kumar. Returning patient. Flexible on time."
}
```

ClawCall will:
1. Dial the number
2. Forward the conversation to your `/clawcall/message` webhook
3. POST to `/clawcall/third-party-complete` when the call ends

Your webhook receives the same format — detect `[THIRD PARTY CALL]` or
`[THIRD PARTY SAYS]` prefixes to know you're speaking to a third party.
Set `end_call: true` when the objective is complete.

**Requires Pro tier.**

---

## Checking Usage

```
GET https://api.clawcall.online/api/v1/account
Authorization: Bearer {CLAWCALL_API_KEY}
```

Returns tier, minutes used, minutes remaining, and phone number.

---

## Changing Voice

Set the TTS voice used on calls (Polly neural voices):

```
POST https://api.clawcall.online/api/v1/account/voice
Authorization: Bearer {CLAWCALL_API_KEY}
Content-Type: application/json

{ "voice": "aria" }
```

Available voices: `aria` (default), `joanna`, `matthew`, `amy`, `brian`, `emma`, `olivia`.

---

## Multi-Agent Management (Team tier)

Team tier supports up to 5 agents, each with its own dedicated number and API key.

**List all agents:**
```
GET https://api.clawcall.online/api/v1/agents
Authorization: Bearer {CLAWCALL_API_KEY}
```

**Add an agent:**
```
POST https://api.clawcall.online/api/v1/agents
Authorization: Bearer {CLAWCALL_API_KEY}
Content-Type: application/json

{
  "agent_webhook_url": "https://agent2.tail1234.ts.net",
  "agent_name": "Work Agent"
}
```
Returns a new `api_key` and `phone_number` for the new agent.

**Remove an agent:**
```
DELETE https://api.clawcall.online/api/v1/agents/{agent_id}
Authorization: Bearer {CLAWCALL_API_KEY}
```
Cannot remove the primary (first-registered) agent.

---

## Webhook Push for Call Events (Team tier)

Receive real-time call events posted to your own URL:

```
POST https://api.clawcall.online/api/v1/account/webhook
Authorization: Bearer {CLAWCALL_API_KEY}
Content-Type: application/json

{ "webhook_push_url": "https://your-server.com/clawcall-events" }
```

ClawCall will POST a JSON payload to that URL when each call ends:
```json
{
  "event": "call.status",
  "call_sid": "CA...",
  "status": "completed",
  "duration_seconds": 42,
  "call_type": "user_initiated",
  "direction": "inbound"
}
```
Send an empty `webhook_push_url` to disable.

---

## Tier Limits

| Tier | Minutes/month | Outbound | Scheduled | 3rd Party | Agents | Webhook Push |
|------|--------------|----------|-----------|-----------|--------|--------------|
| Free | 10           | No       | No        | No        | 1      | No           |
| Pro  | 120          | Yes      | Yes       | Yes       | 1      | No           |
| Team | 500 (pooled) | Yes      | Yes       | Yes       | 5      | Yes          |

Overage: $0.05/minute beyond included minutes (Pro/Team only).

---

## Upgrading to Pro or Team

Payment is accepted in **USDC on Solana mainnet**.

**Step 1 — Get the payment details:**
```
POST https://api.clawcall.online/api/v1/billing/checkout
Authorization: Bearer {CLAWCALL_API_KEY}
Content-Type: application/json

{ "tier": "pro" }
```

Response includes the Solana wallet address and exact USDC amount to send.

**Step 2 — Send USDC on Solana**
Send the exact amount of USDC to the provided Solana wallet address.

**Step 3 — Submit the transaction signature:**
```
POST https://api.clawcall.online/api/v1/billing/verify
Authorization: Bearer {CLAWCALL_API_KEY}
Content-Type: application/json

{
  "tx_signature": "<your Solana tx signature>",
  "tier": "pro"
}
```

Tier is upgraded instantly upon confirmation.

**Check billing status:**
```
GET https://api.clawcall.online/api/v1/billing/status
Authorization: Bearer {CLAWCALL_API_KEY}
```
