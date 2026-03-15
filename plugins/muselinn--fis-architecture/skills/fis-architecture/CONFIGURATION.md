# Configuration Guide - FIS 3.2.0-lite

> **Customize Your Shared Hub**

---

## Default Configuration

FIS 3.2 uses a simplified structure:

```
~/.openclaw/
├── fis-hub/             # Default Shared Hub
│   ├── tickets/                  # Task workflow
│   ├── knowledge/                # Shared knowledge (QMD-indexed)
│   ├── results/                  # Research outputs
│   └── .fis3.1/                  # Light configuration
└── workspace/                    # Your agent workspace
```

## Custom Shared Hub Name

### Method 1: Create Manually

```bash
# Create your custom hub
mkdir -p ~/.openclaw/my-project/{tickets/active,tickets/completed,knowledge,results,.fis3.1}

# Add a notification file
echo '{}' > ~/.openclaw/my-project/.fis3.1/notifications.json
```

### Method 2: Copy Template

```bash
# Copy existing structure
cp -r ~/.openclaw/fis-hub ~/.openclaw/my-project

# Clean up old data if needed
rm -rf ~/.openclaw/my-project/tickets/completed/*
```

---

## Multi-Project Support

Create independent hubs for different projects:

```
~/.openclaw/
├── fis-hub/             # GPR research project
├── product-dev/                  # Product development
└── team-collaboration/           # Team workspace
```

Each hub is completely independent with its own tickets and knowledge.

---

## Naming Conventions

| Scenario | Suggested Name |
|----------|---------------|
| Personal general | `fis-hub`, `personal-hub` |
| Research project | `research-lab`, `project-name` |
| Product development | `product-dev`, `app-name` |
| Team collaboration | `team-hub`, `org-name` |
| Temporary experiment | `experiment-2026` |

---

## Updating References

When you change hub names, update references in:

1. **Documentation** — Update any hardcoded paths
2. **Scripts** — Use relative paths or environment variables
3. **Memory files** — Update `MEMORY.md` references

---

## Environment Variable (Optional)

Set a default hub in your shell:

```bash
# Add to ~/.bashrc or ~/.zshrc
export FIS_SHARED_HUB="$HOME/.openclaw/fis-hub"
```

Then reference it in scripts:
```bash
TICKET_DIR="$FIS_SHARED_HUB/tickets/active"
```

---

## Simplified from 3.1

FIS 3.2 no longer requires:
- Initialization scripts
- Python path setup
- Registry files
- Complex directory structures

Just create tickets and knowledge files directly.

---

*FIS 3.2.0-lite — Minimal configuration 🐱⚡*
