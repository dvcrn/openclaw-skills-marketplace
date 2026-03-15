---
name: discord-bot
description: "Discord Bot API integration — manage servers, channels, messages, roles, members, and webhooks via the Discord REST API. Send messages, manage server settings, moderate users, create channels, and handle role assignments. Built for AI agents — Python stdlib only, zero dependencies. Use for Discord server management, bot automation, community management, message sending, moderation, and webhook integrations."
homepage: https://www.agxntsix.ai
---

# 🤖 Discord Bot

Discord Bot API integration — manage servers, channels, messages, roles, members, and webhooks via the Discord REST API.

## Features

- **Send messages** — text, embeds, files to any channel
- **Channel management** — create, update, delete channels
- **Server info** — guild details, settings, and statistics
- **Member management** — list, kick, ban, role assignment
- **Role management** — create, update, assign roles
- **Message operations** — send, edit, delete, react, pin
- **Webhook management** — create and send via webhooks
- **Thread management** — create and manage threads
- **Emoji management** — list and manage custom emojis
- **Audit log** — view server audit events

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `DISCORD_BOT_TOKEN` | ✅ | API key/token for Discord Bot |

## Quick Start

```bash
# List bot's servers
python3 {baseDir}/scripts/discord-bot.py guilds
```

```bash
# Get server details
python3 {baseDir}/scripts/discord-bot.py guild-get 123456789
```

```bash
# List server channels
python3 {baseDir}/scripts/discord-bot.py channels --guild 123456789
```

```bash
# Create a channel
python3 {baseDir}/scripts/discord-bot.py channel-create --guild 123456789 "general-chat" --type text
```



## Commands

### `guilds`
List bot's servers.
```bash
python3 {baseDir}/scripts/discord-bot.py guilds
```

### `guild-get`
Get server details.
```bash
python3 {baseDir}/scripts/discord-bot.py guild-get 123456789
```

### `channels`
List server channels.
```bash
python3 {baseDir}/scripts/discord-bot.py channels --guild 123456789
```

### `channel-create`
Create a channel.
```bash
python3 {baseDir}/scripts/discord-bot.py channel-create --guild 123456789 "general-chat" --type text
```

### `channel-update`
Update channel.
```bash
python3 {baseDir}/scripts/discord-bot.py channel-update 987654321 '{"name":"announcements","topic":"Important updates"}'
```

### `send`
Send a message.
```bash
python3 {baseDir}/scripts/discord-bot.py send --channel 987654321 "Hello from the bot!"
```

### `send-embed`
Send embed message.
```bash
python3 {baseDir}/scripts/discord-bot.py send-embed --channel 987654321 '{"title":"Update","description":"New feature released","color":5814783}'
```

### `messages`
List channel messages.
```bash
python3 {baseDir}/scripts/discord-bot.py messages --channel 987654321 --limit 20
```

### `message-edit`
Edit a message.
```bash
python3 {baseDir}/scripts/discord-bot.py message-edit --channel 987654321 --message 111222333 "Updated text"
```

### `message-delete`
Delete a message.
```bash
python3 {baseDir}/scripts/discord-bot.py message-delete --channel 987654321 --message 111222333
```

### `react`
Add reaction to message.
```bash
python3 {baseDir}/scripts/discord-bot.py react --channel 987654321 --message 111222333 --emoji 👍
```

### `members`
List server members.
```bash
python3 {baseDir}/scripts/discord-bot.py members --guild 123456789 --limit 50
```

### `roles`
List server roles.
```bash
python3 {baseDir}/scripts/discord-bot.py roles --guild 123456789
```

### `role-assign`
Assign role to member.
```bash
python3 {baseDir}/scripts/discord-bot.py role-assign --guild 123456789 --user 444555666 --role 777888999
```

### `webhooks`
List channel webhooks.
```bash
python3 {baseDir}/scripts/discord-bot.py webhooks --channel 987654321
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/discord-bot.py guilds --limit 5

# Human-readable
python3 {baseDir}/scripts/discord-bot.py guilds --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/discord-bot.py` | Main CLI — all Discord Bot operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the Discord Bot API and results are returned to stdout. Your data stays on Discord Bot servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
