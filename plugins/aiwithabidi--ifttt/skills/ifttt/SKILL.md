---
name: ifttt
description: "IFTTT (If This Then That) automation — trigger webhooks, manage applets, and fire events via the IFTTT Webhooks and API. Connect 800+ services with simple if-then logic, trigger custom events, and pass data between services. Built for AI agents — Python stdlib only, zero dependencies. Use for simple automation, webhook triggers, IoT integration, smart home control, and cross-service event firing."
homepage: https://www.agxntsix.ai
---

# 🔀 IFTTT

IFTTT (If This Then That) automation — trigger webhooks, manage applets, and fire events via the IFTTT Webhooks and API.

## Features

- **Webhook triggers** — fire custom events with data
- **Event data** — pass up to 3 values per trigger
- **Service queries** — check connection status
- **User info** — get authenticated user details
- **Applet management** — list and manage applets (Connect API)
- **Trigger history** — recent webhook activity
- **Multi-event** — fire multiple events in sequence
- **JSON payload** — send structured data via webhooks

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `IFTTT_WEBHOOK_KEY` | ✅ | API key/token for IFTTT |

## Quick Start

```bash
# Fire a webhook event
python3 {baseDir}/scripts/ifttt.py trigger my_event --value1 "Hello" --value2 "World"
```

```bash
# Fire with JSON payload
python3 {baseDir}/scripts/ifttt.py trigger-json my_event '{"value1":"data1","value2":"data2","value3":"data3"}'
```

```bash
# Check webhook connectivity
python3 {baseDir}/scripts/ifttt.py status
```

```bash
# Get user info (Connect API)
python3 {baseDir}/scripts/ifttt.py user
```



## Commands

### `trigger`
Fire a webhook event.
```bash
python3 {baseDir}/scripts/ifttt.py trigger my_event --value1 "Hello" --value2 "World"
```

### `trigger-json`
Fire with JSON payload.
```bash
python3 {baseDir}/scripts/ifttt.py trigger-json my_event '{"value1":"data1","value2":"data2","value3":"data3"}'
```

### `status`
Check webhook connectivity.
```bash
python3 {baseDir}/scripts/ifttt.py status
```

### `user`
Get user info (Connect API).
```bash
python3 {baseDir}/scripts/ifttt.py user
```

### `applets`
List applets (Connect API).
```bash
python3 {baseDir}/scripts/ifttt.py applets --limit 20
```

### `applet-enable`
Enable an applet.
```bash
python3 {baseDir}/scripts/ifttt.py applet-enable abc123
```

### `applet-disable`
Disable an applet.
```bash
python3 {baseDir}/scripts/ifttt.py applet-disable abc123
```

### `services`
List connected services.
```bash
python3 {baseDir}/scripts/ifttt.py services
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/ifttt.py trigger --limit 5

# Human-readable
python3 {baseDir}/scripts/ifttt.py trigger --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/ifttt.py` | Main CLI — all IFTTT operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the IFTTT API and results are returned to stdout. Your data stays on IFTTT servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
