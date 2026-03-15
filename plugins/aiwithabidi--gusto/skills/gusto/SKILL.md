---
name: gusto
description: "Gusto payroll & HR — manage employees, payroll, benefits, and tax forms via REST API"
homepage: https://www.agxntsix.ai
---

# 💰 Gusto

Gusto payroll & HR — manage employees, payroll, benefits, and tax forms via REST API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `GUSTO_ACCESS_TOKEN` | ✅ | OAuth access token |
| `GUSTO_COMPANY_ID` | ✅ | Company UUID |

## Quick Start

```bash
# Get company info
python3 {{baseDir}}/scripts/gusto.py company

# List locations
python3 {{baseDir}}/scripts/gusto.py locations

# List employees
python3 {{baseDir}}/scripts/gusto.py employees

# Get employee
python3 {{baseDir}}/scripts/gusto.py employee-get id <value>

# Create employee
python3 {{baseDir}}/scripts/gusto.py employee-create --first_name <value> --last_name <value> --email <value>

# List payrolls
python3 {{baseDir}}/scripts/gusto.py payrolls --start_date <value> --end_date <value>

# Get payroll
python3 {{baseDir}}/scripts/gusto.py payroll-get id <value>

# List pay schedules
python3 {{baseDir}}/scripts/gusto.py pay-schedules
```

## All Commands

| Command | Description |
|---------|-------------|
| `company` | Get company info |
| `locations` | List locations |
| `employees` | List employees |
| `employee-get` | Get employee |
| `employee-create` | Create employee |
| `payrolls` | List payrolls |
| `payroll-get` | Get payroll |
| `pay-schedules` | List pay schedules |
| `compensations` | List compensations |
| `benefits` | List benefits |
| `employee-benefits` | List employee benefits |
| `contractors` | List contractors |
| `contractor-payments` | List contractor payments |
| `tax-forms` | List tax forms |
| `garnishments` | List garnishments |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/gusto.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/gusto.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
