# Wayve MCP — Setup Guide

## 1. Install the Skill

Find Wayve on [ClawHub.ai](https://clawhub.ai) and click **Install**, or run:

```bash
clawhub install wayve
```

## 2. Create a Wayve Account

1. Go to [gowayve.com](https://gowayve.com) and sign up
2. Verify your email via the OTP code you receive
3. Go to [gowayve.com/account](https://gowayve.com/account) → **API Keys** section
4. Generate a new key and copy it — it starts with `wk_live_`

## 3. Add Your API Key (recommended: SecretRefs)

Use OpenClaw's secrets workflow instead of storing plaintext keys in `openclaw.json`.

1. Run:

```bash
openclaw secrets configure
openclaw secrets audit --check
openclaw secrets reload
```

2. Store `WAYVE_API_KEY` in your configured secret provider (for example file-backed secrets), and map the Wayve skill `apiKey` to that SecretRef.

3. Keep your OpenClaw config referencing the secret (not the raw key), for example:

```json
{
  "skills": {
    "entries": {
      "wayve": {
        "enabled": true,
        "apiKey": { "source": "file", "provider": "filemain", "id": "/WAYVE_API_KEY" }
      }
    }
  }
}
```

This keeps credentials out of plaintext config and supports safe reload/rotation via `openclaw secrets reload`.

## 4. Verify

Type `/wayve help` to see all available commands. If the assistant responds with a list of commands and calls `wayve_get_planning_context`, you're all set.

## 5. Get Started

- `/wayve setup` — first-time onboarding (create life buckets, set preferences)
- `/wayve plan` — plan your week
- `/wayve brief` — today's schedule
- `/wayve wrapup` — end-of-week reflection
- `/wayve time audit` — track where your time goes
- `/wayve life audit` — deep life review

## 6. Automations (Optional)

Set up server-side push notifications for proactive check-ins:
- Morning daily briefs
- Sunday wrap-up reminders
- Monday fresh start nudges
- Mid-week pulse checks
- Frequency alerts

Delivery via Telegram, Discord, Slack, email, or pull (shown at session start).

Say "set up automations" and Wayve will walk you through choosing a delivery channel and creating a bundle. See `references/automations.md` for full details.

## Troubleshooting

**No wayve tools showing up:** Make sure Node.js 18+ is installed (`node --version`) and restart your client. If the MCP server still doesn't connect, you can add it manually in Claude Code:

```
/mcp add wayve -- npx -y @gowayve/wayve@^1.2.5
```

**"Invalid API key":** Keys must start with `wk_live_`. Generate a new one at [gowayve.com/account](https://gowayve.com/account).

**Key not being picked up:** Make sure `WAYVE_API_KEY` is stored in your secret provider and that `~/.openclaw/openclaw.json` has the SecretRef under `skills.entries.wayve.apiKey`. Run `openclaw secrets audit --check` to verify, then `openclaw secrets reload`.
