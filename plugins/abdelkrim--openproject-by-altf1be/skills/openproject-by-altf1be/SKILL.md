---
name: openproject-by-altf1be
description: "OpenProject CRUD skill — manage work packages, projects, time entries, comments, attachments, statuses, and more via OpenProject API v3 with API token auth. Supports cloud and self-hosted instances."
homepage: https://github.com/ALT-F1-OpenClaw/openclaw-skill-openproject
---

# OpenProject by @altf1be

Manage OpenProject work packages, projects, time entries, comments, attachments, and workflow transitions via the API v3. Works with both cloud and self-hosted instances.

## Setup

1. Log in to your OpenProject instance
2. Go to **My Account → Access Tokens → + Add**
3. Create an API token and copy it
4. Set environment variables (or create `.env` in `{baseDir}`):

```
OP_HOST=https://projects.xflowdata.com
OP_API_TOKEN=your-api-token
OP_DEFAULT_PROJECT=my-project
```

5. Install dependencies: `cd {baseDir} && npm install`

## Commands

### Work Packages

```bash
# List work packages (with optional filters)
node {baseDir}/scripts/openproject.mjs wp-list --project my-project --status open --assignee me

# Create a work package
node {baseDir}/scripts/openproject.mjs wp-create --project my-project --type Task --subject "Fix login bug" --description "Users can't log in"

# Read work package details
node {baseDir}/scripts/openproject.mjs wp-read --id 42

# Update a work package
node {baseDir}/scripts/openproject.mjs wp-update --id 42 --subject "New title" --priority High

# Delete a work package (requires --confirm)
node {baseDir}/scripts/openproject.mjs wp-delete --id 42 --confirm
```

### Projects

```bash
# List all projects
node {baseDir}/scripts/openproject.mjs project-list

# Read project details
node {baseDir}/scripts/openproject.mjs project-read --id my-project

# Create a project
node {baseDir}/scripts/openproject.mjs project-create --name "My Project" --identifier my-project
```

### Comments (Activities)

```bash
# List comments on a work package
node {baseDir}/scripts/openproject.mjs comment-list --wp-id 42

# Add a comment
node {baseDir}/scripts/openproject.mjs comment-add --wp-id 42 --body "Ready for review"
```

### Attachments

```bash
# List attachments on a work package
node {baseDir}/scripts/openproject.mjs attachment-list --wp-id 42

# Upload an attachment
node {baseDir}/scripts/openproject.mjs attachment-add --wp-id 42 --file ./screenshot.png

# Delete an attachment (requires --confirm)
node {baseDir}/scripts/openproject.mjs attachment-delete --id 10 --confirm
```

### Time Entries

```bash
# List time entries
node {baseDir}/scripts/openproject.mjs time-list --project my-project

# Log time
node {baseDir}/scripts/openproject.mjs time-create --wp-id 42 --hours 2.5 --comment "Code review" --activity-id 1

# Update time entry
node {baseDir}/scripts/openproject.mjs time-update --id 5 --hours 3 --comment "Updated"

# Delete time entry (requires --confirm)
node {baseDir}/scripts/openproject.mjs time-delete --id 5 --confirm
```

### Statuses & Transitions

```bash
# List all statuses
node {baseDir}/scripts/openproject.mjs status-list

# Update work package status
node {baseDir}/scripts/openproject.mjs wp-update --id 42 --status "In progress"
```

### Reference Data

```bash
# List work package types
node {baseDir}/scripts/openproject.mjs type-list

# List priorities
node {baseDir}/scripts/openproject.mjs priority-list

# List project members
node {baseDir}/scripts/openproject.mjs member-list --project my-project

# List versions/milestones
node {baseDir}/scripts/openproject.mjs version-list --project my-project

# List categories
node {baseDir}/scripts/openproject.mjs category-list --project my-project
```

## Security

- API token auth (Basic auth with `apikey` as username)
- No secrets or tokens printed to stdout
- All delete operations require explicit `--confirm` flag
- Path traversal prevention for file uploads
- Built-in rate limiting with exponential backoff retry
- Lazy config validation (only checked when a command runs)

## Dependencies

- `commander` — CLI framework
- `dotenv` — environment variable loading
- Node.js built-in `fetch` (requires Node >= 18)

## Author

Abdelkrim BOUJRAF — [ALT-F1 SRL](https://www.alt-f1.be), Brussels 🇧🇪 🇲🇦
X: [@altf1be](https://x.com/altf1be)
