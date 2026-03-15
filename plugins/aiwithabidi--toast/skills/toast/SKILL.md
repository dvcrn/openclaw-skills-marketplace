---
name: toast
description: "Toast — restaurant POS, orders, menus, employees, revenue centers, and reporting."
homepage: https://www.agxntsix.ai
---

# 🍞 Toast

Toast — restaurant POS, orders, menus, employees, revenue centers, and reporting.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `TOAST_API_KEY` | ✅ | Toast API key |
| `TOAST_RESTAURANT_GUID` | ✅ | Restaurant GUID |


## Quick Start

```bash
# List orders
python3 {{baseDir}}/scripts/toast.py list-orders --start-date <value> --end-date <value> --page-size "25"

# Get order details
python3 {{baseDir}}/scripts/toast.py get-order <id>

# List menus
python3 {{baseDir}}/scripts/toast.py list-menus

# Get menu details
python3 {{baseDir}}/scripts/toast.py get-menu <id>

# List menu items
python3 {{baseDir}}/scripts/toast.py list-menu-items --page-size "100"

# List employees
python3 {{baseDir}}/scripts/toast.py list-employees

# Get employee details
python3 {{baseDir}}/scripts/toast.py get-employee <id>

# List revenue centers
python3 {{baseDir}}/scripts/toast.py list-revenue-centers

# List tables
python3 {{baseDir}}/scripts/toast.py list-tables

# List dining options
python3 {{baseDir}}/scripts/toast.py list-dining-options

# Get restaurant info
python3 {{baseDir}}/scripts/toast.py get-restaurant --guid <value>
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/toast.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
