# Proactive Automations — Server-Side Push Notifications

Wayve automations are server-side scheduled notifications that run independently of any client. They work on every platform: OpenClaw, Claude Code with Dobby, or Claude Code standalone.

## How It Works

```
User configures automation via wayve_manage_automations
    → Stored in wayve.automations (DB)
    → Azure timer function checks every 5 minutes
    → Builds message from template + live data
    → Delivers via configured channel (Telegram, Discord, Slack, email, or pull)
```

No VPS, no bash scripts, no cron jobs needed. Everything runs server-side.

## App Deep Links

Always include the relevant link when directing the user to take action in the Wayve app. Base URL: `https://gowayve.com`

| Action | URL |
|--------|-----|
| Dashboard | https://gowayve.com/dashboard |
| Weekly Planning | https://gowayve.com/week |
| Calendar | https://gowayve.com/calendar |
| Life Buckets | https://gowayve.com/buckets |
| Projects | https://gowayve.com/projects |
| Time Locks | https://gowayve.com/time-locks |
| Review Hub | https://gowayve.com/review |
| Wrap Up Ritual | https://gowayve.com/wrap-up |
| Fresh Start Ritual | https://gowayve.com/fresh-start |
| Account Settings | https://gowayve.com/account |

## Available Types

| Type | Default Schedule | What it sends |
|------|-----------------|---------------|
| `morning_brief` | `30 7 * * *` | Today's activity count + dashboard link |
| `evening_winddown` | `0 21 * * *` | Completed/total activities today |
| `wrap_up_reminder` | `0 19 * * 0` | Sunday wrap-up nudge |
| `fresh_start_reminder` | `30 8 * * 1` | Monday planning nudge with carryover count |
| `mid_week_pulse` | `30 12 * * 3` | Mid-week progress summary |
| `friday_check` | `0 15 * * 5` | Uncompleted activities count |
| `frequency_tracker` | `0 20 * * *` | Bucket frequency alert (silent when on track) |
| `monthly_audit` | `0 11 1 * *` | Monthly review prompt |
| `time_audit_checkin` | `0 */2 * * *` | Time audit check-in (per audit config) |

## Delivery Channels

| Channel | What you need | How it works |
|---------|---------------|--------------|
| `telegram` | Bot token + chat ID | Direct Telegram Bot API call |
| `discord` | Webhook URL | POST to Discord webhook |
| `slack` | Incoming webhook URL | POST to Slack webhook |
| `email` | Email address | Via Azure Communication Services |
| `openclaw` | Gateway URL + hook token | POST to /hooks/wake + direct channel delivery |
| `openclaw_whatsapp` | Gateway URL + hook token | POST to /hooks/agent with WhatsApp delivery |
| `pull` | Nothing | Messages stored in DB, retrieved via SessionStart hook |

### Channel Setup Details

**Telegram:**
1. Create a bot via @BotFather, get the bot token
2. Start a chat with your bot, send a message
3. Get your chat_id via `https://api.telegram.org/bot<TOKEN>/getUpdates`
4. delivery_config: `{"bot_token": "...", "chat_id": "..."}`

**Discord:**
1. In your Discord server: Server Settings > Integrations > Webhooks > New Webhook
2. Copy the webhook URL
3. delivery_config: `{"webhook_url": "https://discord.com/api/webhooks/..."}`

**Slack:**
1. Create an Incoming Webhook at api.slack.com/apps
2. Copy the webhook URL
3. delivery_config: `{"webhook_url": "https://hooks.slack.com/services/..."}`

**Email:**
1. delivery_config: `{"email": "you@example.com"}`

**Pull (no setup needed):**
Messages are stored server-side and automatically presented when you start a new Claude Code session (via the SessionStart hook).

## Setup Flow

When offering automations to the user:

1. **Ask what they want**: "I can set up proactive notifications. Want the Starter Bundle (morning brief + weekly rituals) or the Full Bundle?"
2. **Ask timezone**: "What's your timezone? (e.g., Europe/Amsterdam)"
3. **Ask delivery channel**: "Where should I send notifications — Telegram, Discord, Slack, email, or just show them when you start a session?"
4. **Collect channel credentials** if needed (bot token, webhook URL, etc.)
5. **Create the bundle or individual automations** via `wayve_manage_automations`
6. **Confirm**: Show what was created with schedules

### Example: Create a starter bundle
```
wayve_manage_automations(
  action: 'create_bundle',
  bundle: 'starter',
  timezone: 'Europe/Amsterdam',
  delivery_channel: 'telegram',
  delivery_config: { bot_token: '...', chat_id: '...' }
)
```

## Bundles

### Starter Bundle
- Morning Brief (7:30 daily)
- Wrap Up Reminder (Sunday 19:00)
- Fresh Start Reminder (Monday 8:30)

### Full Bundle
Everything in Starter, plus:
- Evening Wind Down (21:00 daily)
- Mid-Week Pulse (Wednesday 12:30)
- Friday Check (Friday 15:00)
- Frequency Tracker (20:00 daily)
- Monthly Audit (1st of month 11:00)

## Managing Automations

| User says | Action |
|-----------|--------|
| "List my automations" | `wayve_manage_automations(action: 'list')` |
| "Pause my morning briefs" | `wayve_manage_automations(action: 'update', id: '...', enabled: false)` |
| "Resume morning briefs" | `wayve_manage_automations(action: 'update', id: '...', enabled: true)` |
| "Change morning brief to 8:00" | `wayve_manage_automations(action: 'update', id: '...', schedule_cron: '0 8 * * *')` |
| "Delete all automations" | List, then delete each |
| "Switch to Discord" | Update each automation with new delivery_channel + delivery_config |

Always update the knowledge base when automations change.

## When to Suggest Automations

| Moment | Suggested Automations |
|--------|----------------------|
| After **onboarding** completes | Starter bundle |
| After first **Wrap Up** | wrap_up_reminder if not set |
| After first **Fresh Start** | fresh_start_reminder if not set |
| User starts a **Time Audit** | time_audit_checkin for audit duration |
| User says "remind me" | Suggest creating an automation |

Frame it naturally: "Want me to send you a morning brief at 7:30 every day? I can also nudge you Sunday evening for your Wrap Up."

## Security Constraints

- **User approval required** — every automation must be explicitly approved
- **Predefined types only** — only the 9 types listed above are accepted
- **No arbitrary code execution** — messages are fixed templates filled with live data
- **Delivery credentials encrypted** — AES-256-GCM at rest, never returned via API
- **User can stop at any time** — "stop all reminders" must be respected immediately
