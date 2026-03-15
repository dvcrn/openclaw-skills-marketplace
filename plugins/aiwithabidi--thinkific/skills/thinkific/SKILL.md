---
name: thinkific
description: "Thinkific — manage courses, students, enrollments, coupons, and products via REST API"
homepage: https://www.agxntsix.ai
---

# 🎓 Thinkific

Thinkific — manage courses, students, enrollments, coupons, and products via REST API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `THINKIFIC_API_KEY` | ✅ | API key |
| `THINKIFIC_SUBDOMAIN` | ✅ | School subdomain |

## Quick Start

```bash
# List courses
python3 {{baseDir}}/scripts/thinkific.py courses --page <value>

# Get course
python3 {{baseDir}}/scripts/thinkific.py course-get id <value>

# Create course
python3 {{baseDir}}/scripts/thinkific.py course-create --name <value> --slug <value>

# Update course
python3 {{baseDir}}/scripts/thinkific.py course-update id <value> --name <value>

# Delete course
python3 {{baseDir}}/scripts/thinkific.py course-delete id <value>

# List chapters
python3 {{baseDir}}/scripts/thinkific.py chapters id <value>

# List users
python3 {{baseDir}}/scripts/thinkific.py users --page <value> --query <value>

# Get user
python3 {{baseDir}}/scripts/thinkific.py user-get id <value>
```

## All Commands

| Command | Description |
|---------|-------------|
| `courses` | List courses |
| `course-get` | Get course |
| `course-create` | Create course |
| `course-update` | Update course |
| `course-delete` | Delete course |
| `chapters` | List chapters |
| `users` | List users |
| `user-get` | Get user |
| `user-create` | Create user |
| `enrollments` | List enrollments |
| `enroll` | Create enrollment |
| `coupons` | List coupons |
| `coupon-create` | Create coupon |
| `products` | List products |
| `orders` | List orders |
| `groups` | List groups |
| `instructors` | List instructors |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/thinkific.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/thinkific.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
