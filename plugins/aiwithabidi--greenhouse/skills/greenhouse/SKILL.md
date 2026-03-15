---
name: greenhouse
description: "Greenhouse ATS — manage candidates, jobs, applications, offers, and interviews via Harvest API"
homepage: https://www.agxntsix.ai
---

# 🌱 Greenhouse

Greenhouse ATS — manage candidates, jobs, applications, offers, and interviews via Harvest API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `GREENHOUSE_API_KEY` | ✅ | Harvest API key |

## Quick Start

```bash
# List candidates
python3 {{baseDir}}/scripts/greenhouse.py candidates --per_page <value> --job_id <value>

# Get candidate
python3 {{baseDir}}/scripts/greenhouse.py candidate-get id <value>

# Create candidate
python3 {{baseDir}}/scripts/greenhouse.py candidate-create --first_name <value> --last_name <value> --email_addresses <value>

# List applications
python3 {{baseDir}}/scripts/greenhouse.py applications --status <value> --job_id <value>

# Get application
python3 {{baseDir}}/scripts/greenhouse.py application-get id <value>

# Advance application
python3 {{baseDir}}/scripts/greenhouse.py application-advance id <value>

# Reject application
python3 {{baseDir}}/scripts/greenhouse.py application-reject id <value> --rejection_reason_id <value>

# List jobs
python3 {{baseDir}}/scripts/greenhouse.py jobs --status <value>
```

## All Commands

| Command | Description |
|---------|-------------|
| `candidates` | List candidates |
| `candidate-get` | Get candidate |
| `candidate-create` | Create candidate |
| `applications` | List applications |
| `application-get` | Get application |
| `application-advance` | Advance application |
| `application-reject` | Reject application |
| `jobs` | List jobs |
| `job-get` | Get job |
| `job-stages` | List job stages |
| `offers` | List offers |
| `interviews` | List interviews |
| `scorecards` | List scorecards |
| `departments` | List departments |
| `offices` | List offices |
| `users` | List users |
| `sources` | List sources |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/greenhouse.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/greenhouse.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
