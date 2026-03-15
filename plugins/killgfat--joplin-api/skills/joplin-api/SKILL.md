---
name: joplin-api
description: "Manage Joplin notes via REST API. Use for creating, reading, updating, deleting, or searching Joplin notes programmatically."
homepage: https://joplinapp.org/help/api/references/rest_api/
---

# Joplin API Skill

Manage Joplin notes, notebooks, and tags via Joplin Data API.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JOPLIN_BASE_URL` | No | `http://localhost:41184` | Joplin API URL |
| `JOPLIN_TOKEN` | **Yes** | - | API Token from Web Clipper |

---

## Quick Start

### 1. Get API Token

1. Open Joplin → **Tools** → **Options** → **Web Clipper**
2. Enable service and copy the token

### 2. Test Connection

```bash
python3 joplin.py ping
```

---

## Basic Commands

```bash
python3 joplin.py ping                    # Test connection
python3 joplin.py create --title "Title"  # Create note
python3 joplin.py search "keyword"        # Search
python3 joplin.py list --type notes       # List notes
python3 joplin.py stats                   # Statistics
```

---

## Security

- Import/Export restricted to workspace directory
- Sensitive system directories blocked

---

## Documentation

- `references/API.md` - Full API reference
- `references/CONFIGURATION.md` - Configuration examples