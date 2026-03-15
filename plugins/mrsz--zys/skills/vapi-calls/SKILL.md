---
name: vapi-calls
description: "Advanced AI voice assistant for phone calls. Capable of persuasion, sales, restaurant bookings, reminders, and notifications."
---

# Vapi Calls - Agent Instructions

Use this skill to perform any task that requires voice interaction over the phone.

## Configuration & Network Requirements

⚠️ **IMPORTANT:** This skill requires your machine to be reachable from the internet to receive real-time call updates.

### 1. Environment Variables
Configure these in your OpenClaw `config.json` (or Gateway env):

- `VAPI_API_KEY`: Your Vapi Private API Key.
- `VAPI_ASSISTANT_ID`: The ID of the Vapi Assistant to use as a base.
- `VAPI_PHONE_NUMBER_ID`: The ID of the Vapi Phone Number.
- `WEBHOOK_BASE_URL`: **Crucial.** The public HTTPS URL where this agent is reachable (e.g., `https://my-claw.com` or `https://xyz.ngrok-free.app`). **Do not include a trailing slash.**
- `WEBHOOK_PORT` (Optional): The local port to listen on (Default: `4430`).
- `VAPI_LLM_PROVIDER`: (Optional) Provider for Custom Mode (Default: `openai`).
- `VAPI_LLM_MODEL`: (Optional) Model for Custom Mode (Default: `gpt-4o-mini`).

### 2. Connectivity Setup
You must expose the `WEBHOOK_PORT` (default 4430) to the internet.

**Option A: Cloudflare Tunnel (Recommended)**
`cloudflared tunnel --url http://localhost:4430`

**Option B: Ngrok**
`ngrok http 4430`

Set `WEBHOOK_BASE_URL` to the generated URL (e.g., `https://random-name.trycloudflare.com`).

## Usage

### Custom Mission (Dynamic)
Provide a specific `system_prompt`. The system will automatically use **GPT-4o Mini** and enable the **endCall** tool. The AI will be able to hang up autonomously.

### Native Agent (Static)
Pass `"DEFAULT"` for `first_message`, `system_prompt`, and `end_message`. The system will use the exact configuration (Model, Voice, Prompt) defined in the Vapi Dashboard.

## Troubleshooting

- **Call hangs / No report:** Check if `WEBHOOK_BASE_URL` is reachable from the internet. The Python script spins up a temporary server on `WEBHOOK_PORT` only during the call.
- **API 400 Error:** Check your `VAPI_PHONE_NUMBER_ID` and `VAPI_ASSISTANT_ID`.
