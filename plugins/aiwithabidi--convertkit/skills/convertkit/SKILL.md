---
name: convertkit
description: "ConvertKit (Kit) creator marketing — manage subscribers, forms, sequences, broadcasts, tags, and automations via the ConvertKit API. Build email lists, create automated sequences, send broadcasts, and track subscriber engagement. Built for AI agents — Python stdlib only, zero dependencies. Use for creator email marketing, newsletter management, subscriber growth, email sequences, and audience building."
homepage: https://www.agxntsix.ai
---

# ✉️ ConvertKit

ConvertKit (Kit) creator marketing — manage subscribers, forms, sequences, broadcasts, tags, and automations via the ConvertKit API.

## Features

- **Subscriber management** — add, tag, search, and segment
- **Form management** — list forms and their subscribers
- **Email sequences** — create and manage drip campaigns
- **Broadcasts** — create and send one-time emails
- **Tag operations** — create, apply, remove subscriber tags
- **Automation rules** — view automation workflows
- **Custom fields** — manage subscriber custom fields
- **Subscriber search** — find by email or custom attributes
- **Analytics** — subscriber growth, form conversions, sequence stats
- **Bulk operations** — tag/untag multiple subscribers

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `CONVERTKIT_API_KEY` | ✅ | API key/token for ConvertKit |

## Quick Start

```bash
# List subscribers
python3 {baseDir}/scripts/convertkit.py subscribers --limit 50 --sort created_at
```

```bash
# Get subscriber details
python3 {baseDir}/scripts/convertkit.py subscriber-get 12345
```

```bash
# Add a subscriber
python3 {baseDir}/scripts/convertkit.py subscriber-add --email "user@example.com" --first-name "Jane"
```

```bash
# Search by email
python3 {baseDir}/scripts/convertkit.py subscriber-search "user@example.com"
```



## Commands

### `subscribers`
List subscribers.
```bash
python3 {baseDir}/scripts/convertkit.py subscribers --limit 50 --sort created_at
```

### `subscriber-get`
Get subscriber details.
```bash
python3 {baseDir}/scripts/convertkit.py subscriber-get 12345
```

### `subscriber-add`
Add a subscriber.
```bash
python3 {baseDir}/scripts/convertkit.py subscriber-add --email "user@example.com" --first-name "Jane"
```

### `subscriber-search`
Search by email.
```bash
python3 {baseDir}/scripts/convertkit.py subscriber-search "user@example.com"
```

### `tags`
List all tags.
```bash
python3 {baseDir}/scripts/convertkit.py tags
```

### `tag-create`
Create a tag.
```bash
python3 {baseDir}/scripts/convertkit.py tag-create "VIP Customer"
```

### `tag-apply`
Tag a subscriber.
```bash
python3 {baseDir}/scripts/convertkit.py tag-apply --tag 123 --email user@example.com
```

### `tag-remove`
Remove tag.
```bash
python3 {baseDir}/scripts/convertkit.py tag-remove --tag 123 --email user@example.com
```

### `forms`
List forms.
```bash
python3 {baseDir}/scripts/convertkit.py forms
```

### `form-subscribers`
List form subscribers.
```bash
python3 {baseDir}/scripts/convertkit.py form-subscribers 456
```

### `sequences`
List sequences.
```bash
python3 {baseDir}/scripts/convertkit.py sequences
```

### `sequence-subscribers`
List sequence subscribers.
```bash
python3 {baseDir}/scripts/convertkit.py sequence-subscribers 789
```

### `broadcasts`
List broadcasts.
```bash
python3 {baseDir}/scripts/convertkit.py broadcasts --limit 20
```

### `broadcast-create`
Create a broadcast.
```bash
python3 {baseDir}/scripts/convertkit.py broadcast-create '{"subject":"Weekly Update","content":"<p>Hello!</p>"}'
```

### `broadcast-send`
Send a broadcast.
```bash
python3 {baseDir}/scripts/convertkit.py broadcast-send 12345
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/convertkit.py subscribers --limit 5

# Human-readable
python3 {baseDir}/scripts/convertkit.py subscribers --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/convertkit.py` | Main CLI — all ConvertKit operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the ConvertKit API and results are returned to stdout. Your data stays on ConvertKit servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
