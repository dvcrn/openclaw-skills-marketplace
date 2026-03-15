---
name: pagerduty
description: "PagerDuty incident management — manage incidents, services, schedules, escalation policies, and on-call via REST API"
homepage: https://www.agxntsix.ai
---

# 🚨 PagerDuty

PagerDuty incident management — manage incidents, services, schedules, escalation policies, and on-call via REST API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `PAGERDUTY_API_KEY` | ✅ | API token from pagerduty.com |

## Quick Start

```bash
# List incidents
python3 {{baseDir}}/scripts/pagerduty.py incidents --statuses[] <value> --since <value> --until <value>

# Get incident
python3 {{baseDir}}/scripts/pagerduty.py incident-get id <value>

# Create incident
python3 {{baseDir}}/scripts/pagerduty.py incident-create --title <value> --service_id <value> --urgency <value>

# Update incident
python3 {{baseDir}}/scripts/pagerduty.py incident-update id <value> --status <value>

# List incident notes
python3 {{baseDir}}/scripts/pagerduty.py incident-notes id <value>

# Add note
python3 {{baseDir}}/scripts/pagerduty.py incident-note-add id <value> --content <value>

# List services
python3 {{baseDir}}/scripts/pagerduty.py services --query <value>

# Get service
python3 {{baseDir}}/scripts/pagerduty.py service-get id <value>
```

## All Commands

| Command | Description |
|---------|-------------|
| `incidents` | List incidents |
| `incident-get` | Get incident |
| `incident-create` | Create incident |
| `incident-update` | Update incident |
| `incident-notes` | List incident notes |
| `incident-note-add` | Add note |
| `services` | List services |
| `service-get` | Get service |
| `service-create` | Create service |
| `oncalls` | List on-calls |
| `schedules` | List schedules |
| `schedule-get` | Get schedule |
| `escalation-policies` | List escalation policies |
| `users` | List users |
| `user-get` | Get user |
| `teams` | List teams |
| `vendors` | List vendors |
| `notifications` | List notifications |
| `abilities` | List abilities |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/pagerduty.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/pagerduty.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
