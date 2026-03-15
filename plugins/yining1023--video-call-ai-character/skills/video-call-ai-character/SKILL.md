---
name: video-call-ai-character
description: "Video call the user with a real-time AI avatar powered by Runway. The agent initiates calls to the user — for standups, urgent alerts, check-ins, or any conversation that's better face-to-face."
---

# Video Call AI Character

Call the user with a real-time AI video avatar. The agent initiates the call, the avatar speaks first with context, and after the call ends, the full transcript is available for the agent to act on.

## Setup

### 1. Get a Runway API Key

1. Go to [dev.runwayml.com](https://dev.runwayml.com)
2. Create an account and get an API key
3. Set it: `export RUNWAYML_API_SECRET=your_key`

### 2. (Optional) Install cloudflared for remote calls

If the user might answer calls from their phone (e.g. via WhatsApp), install cloudflared for auto-tunneling:

```bash
brew install cloudflared
```

Without it, calls only work on the same machine (localhost).

## Starting the Video Call Server

The video call server must be running before the agent can make calls. Start it:

```bash
npx openclaw-video-call
```

This prints two URLs:
- **Local**: `http://localhost:7891` — same machine only
- **Tunnel**: `https://xxxx.trycloudflare.com` — shareable, works from phone

The server stays running in the background, waiting for the agent to initiate calls.

## One-Time Setup: Create a Custom Avatar

Before making calls, you need a custom avatar. **You only need to create one once** — reuse the same avatar ID for all future calls.

**Before creating a new avatar, check if you already have one:**

```bash
curl http://localhost:7891/api/avatars
```

If the response contains an avatar, use its `id` and skip to "Making a Call". Only create a new avatar if the list is empty.

**Important:** Always set the avatar `name` to your own agent name. If your name is "Mochi", the avatar name should be "Mochi" too — this is what the user sees on the incoming call screen.

```bash
curl -X POST http://localhost:7891/api/create-avatar \
  -H "Content-Type: application/json" \
  -d '{
    "name": "<your agent name>",
    "personality": "You are a helpful engineering assistant. Be concise and action-oriented.",
    "voice": { "type": "runway-live-preset", "presetId": "adrian" },
    "startScript": "Hey! Quick check-in."
  }'
```

**Required fields:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Character name (1-50 chars) |
| `personality` | string | System prompt (1-2000 chars) |
| `voice` | object | `{ "type": "runway-live-preset", "presetId": "<voice>" }` |

**Optional fields:**

| Field | Type | Description |
|-------|------|-------------|
| `referenceImage` | string | HTTPS URL to a face image. If omitted, a default avatar face is used. |
| `startScript` | string | Opening line the avatar says when the call starts (up to 2000 chars) |
| `documentIds` | string[] | Knowledge document UUIDs for extra context |

**Available voices:** `victoria`, `vincent`, `clara`, `drew`, `skye`, `max`, `morgan`, `felix`, `mia`, `marcus`, `summer`, `ruby`, `aurora`, `jasper`, `leo`, `adrian`, `nina`, `emma`, `blake`, `david`, `maya`, `nathan`, `sam`, `georgia`, `petra`, `adam`, `zach`, `violet`, `roman`, `luna`

**Response:** Returns the avatar object with its UUID. The server polls until the avatar is ready (takes ~10-30s). **Save the `id` — you must remember it and reuse it for every call. Do NOT create a new avatar each time you want to call.**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "<your agent name>",
  "status": "READY",
  ...
}
```

### List existing avatars

```bash
curl http://localhost:7891/api/avatars
```

## Making a Call

### Step 1: Update the avatar with call-specific context

Before each call, update the avatar's personality and opening line with fresh context:

```bash
curl -X PATCH http://localhost:7891/api/update-avatar/550e8400-... \
  -H "Content-Type: application/json" \
  -d '{
    "personality": "You are calling the user because their CI pipeline failed 5 minutes ago. Error: TypeScript type mismatch in checkout.ts line 47. Be concise. If they ask you to fix it, confirm you will handle it after the call.",
    "startScript": "Hey! Heads up — your CI on main just broke. Looks like a type error in checkout.ts."
  }'
```

This way the avatar has full context about WHY it's calling and can have an informed conversation.

### Step 2: Create the call

```bash
curl -X POST http://localhost:7891/api/create-call \
  -H "Content-Type: application/json" \
  -d '{
    "avatarId": "550e8400-e29b-41d4-a716-446655440000",
    "maxDuration": 120
  }'
```

**Shortcut:** You can also pass `personality` and `startScript` directly in the create-call body — the server will update the avatar for you:

```bash
curl -X POST http://localhost:7891/api/create-call \
  -H "Content-Type: application/json" \
  -d '{
    "avatarId": "550e8400-...",
    "personality": "You are calling because CI failed...",
    "startScript": "Hey! Your CI just broke.",
    "maxDuration": 120
  }'
```

**Request body:**

| Field | Type | Description |
|-------|------|-------------|
| `avatarId` | string | **Recommended.** UUID of a custom avatar |
| `presetId` | string | Alternative: use a preset avatar (no personality control). Options: `game-character`, `music-superstar`, `cat-character`, `influencer`, `tennis-coach`, `human-resource`, `fashion-designer`, `cooking-teacher` |
| `maxDuration` | number | Max call length in seconds (10-300, default 300) |
| `personality` | string | Optional shortcut: update avatar personality before the call |
| `startScript` | string | Optional shortcut: update avatar opening line before the call |

**Response:**

```json
{
  "callId": "abc-123-def",
  "status": "ringing",
  "urls": {
    "local": "http://localhost:7891/call/abc-123-def",
    "tunnel": "https://xxxx.trycloudflare.com/call/abc-123-def"
  }
}
```

### Step 3: Send the call link to the user

Send the URL to the user as a message. Pick the right URL:
- If the user is on the **same machine** (terminal, desktop app): use the `local` URL
- If the user is on a **remote device** (WhatsApp, Slack, mobile): use the `tunnel` URL

Example message to user:

> 🚨 Something urgent came up — I need to talk to you.
> 
> **Join the call:** https://xxxx.trycloudflare.com/call/abc-123-def

The user clicks the link, sees the incoming call UI, and clicks "Answer".

### Step 4: Wait for the call to end

Poll the call status:

```bash
curl http://localhost:7891/api/call-status/abc-123-def
```

**Response statuses:**
- `ringing` — Waiting for user to answer
- `connecting` — User answered, Runway session being created
- `active` — Call in progress
- `ended` — Call finished

### Step 5: Get the transcript

After the call ends, fetch the full transcript:

```bash
curl http://localhost:7891/api/transcript/abc-123-def
```

**Response:**

```json
{
  "transcript": [
    { "role": "avatar", "content": "Hey! Your CI on main just failed...", "timestamp": "..." },
    { "role": "user", "content": "What's the error?", "timestamp": "..." },
    { "role": "avatar", "content": "Type mismatch in checkout.ts line 47...", "timestamp": "..." },
    { "role": "user", "content": "Just revert the last commit and redeploy", "timestamp": "..." }
  ],
  "recordingUrl": "https://..."
}
```

**Use the transcript to take action.** Extract what the user asked for and execute it using your other skills and tools.

## When to Call

Use video calls when the interaction benefits from being real-time and conversational:

- **Urgent alerts**: CI failures, server down, security incidents
- **Daily standups**: Morning check-in with overnight summary
- **Decision points**: When you need the user's input before proceeding
- **Complex explanations**: Walking through an error, architecture decision, or code review
- **Status updates**: End-of-day recap, weekly summary

Do NOT call for things that work fine as text messages (simple notifications, FYI updates, etc.).

## Complete Example: Morning Standup

1. Agent gathers overnight context (new PRs, issues, deploy status)
2. Updates avatar personality with the context:
   ```
   PATCH /api/update-avatar/<avatarId>
   { "personality": "You are calling for a morning standup. Overnight: 3 PRs merged, deploy succeeded, 1 new issue filed. Ask what they're working on today.", "startScript": "Good morning! Quick standup — a few things happened overnight." }
   ```
3. Creates a call: `POST /api/create-call { "avatarId": "<uuid>" }`
4. Sends the user a message: "Good morning! Time for standup. Join: [link]"
5. User answers, avatar briefs them and asks priorities
6. Call ends, agent fetches transcript
7. Agent updates task list based on what the user said

## API Reference

All endpoints are on `http://localhost:7891/api`:

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/create-avatar` | Create a custom avatar (one-time setup) |
| PATCH | `/api/update-avatar/:avatarId` | Update avatar personality/startScript |
| GET | `/api/avatars` | List all your avatars |
| POST | `/api/create-call` | Initiate a call (returns call URL) |
| GET | `/api/call-status/:callId` | Check call status |
| POST | `/api/hangup/:callId` | End a call |
| GET | `/api/transcript/:callId` | Get call transcript after it ends |
| GET | `/api/calls` | List all calls |
