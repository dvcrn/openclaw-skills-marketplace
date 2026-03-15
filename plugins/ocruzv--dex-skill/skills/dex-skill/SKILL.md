---
name: dex-skill
description: "Manage your Dex personal CRM — search, create, and update contacts, log interaction notes, set follow-up reminders, organize contacts with tags and groups, and manage custom fields. Use this skill when the user wants to: (1) Find or look up a contact, (2) Add or edit contact details, (3) Log a meeting, call, or interaction note, (4) Set a reminder or follow-up task, (5) Organize contacts into groups or apply tags, (6) Track custom data with custom fields, (7) Merge duplicate contacts, (8) Review their relationship history or prepare for a meeting, or any other personal CRM task involving their professional network."
---

# Dex Personal CRM

Dex is a personal CRM that helps users maintain and nurture their professional relationships. It tracks contacts, interaction history, reminders, and organizational structures (groups, tags, custom fields).

## Setup — Detect Access Method

Check which access method is available, in this order:

1. **MCP tools available?** If `dex_search_contacts` and other `dex_*` tools are in the tool list, use MCP tools directly. This is the preferred method — skip CLI setup entirely.
2. **CLI installed?** Check if `~/.dex/bin/dex` exists and run `~/.dex/bin/dex auth status`. If authenticated, use CLI commands.
3. **Neither?** Run the setup script to install the CLI, then authenticate.

### First-Time Setup

Run the bundled setup script. It automatically picks the best path based on what's installed:

```bash
bash scripts/setup.sh
```

**Path A — Go installed:** Generates a `dex` CLI binary at `~/.dex/bin/dex` via CLIHub. Opens browser for OAuth during generation. CLI credentials persist in `~/.clihub/credentials.json`.

```bash
~/.dex/bin/dex auth status  # Verify authentication
```

**Path B — No Go (requires Node.js):** Uses `npx add-mcp` to configure the hosted Dex MCP server (`https://mcp.getdex.com/mcp`) across all detected AI clients automatically. User authenticates via browser on first MCP connection.

Supported clients (auto-detected by `add-mcp`): Claude Code, Claude Desktop, Cursor, VS Code (Copilot), Gemini CLI, Codex, Goose, OpenCode, Zed, and more.

**Path C — Neither Go nor Node.js:** Prints the MCP config snippet for the user to add manually.

The setup script is idempotent — safe to run multiple times.

### Headless / Server Setup

For headless environments (SSH servers, CI, containers) where no browser is available, the setup script picks the best method automatically:

**Interactive headless (has TTY, no browser) — Device Code Flow:**

```bash
bash scripts/setup.sh
```

The script detects the environment and starts a device code flow:
1. Downloads the pre-built CLI binary for your platform
2. Requests a one-time code from the Dex server
3. Displays a short code (e.g., `ABCD-1234`) and a URL
4. You open the URL on any device with a browser, log in to Dex, and enter the code
5. The CLI automatically receives an API key and completes setup

This is the recommended path for SSH servers and headless desktops where a human is present.

**Non-interactive / CI — API Key Flow:**

For CI pipelines, containers, or automation where no human is present:

1. **Generate an API key** at [Dex Settings > Integrations](https://getdex.com/settings/integrations) (requires Professional plan)
2. **Set the key** as an environment variable:
   ```bash
   export DEX_API_KEY=dex_your_key_here
   ```
3. **Run setup**:
   ```bash
   bash scripts/setup.sh
   ```

The script will:
- Download the pre-built CLI binary for your platform from [GitHub Releases](https://github.com/getdex/agent-skills/releases)
- Authenticate using your API key
- Save the key to `~/.dex/api-key` (chmod 600) so you only need to provide it once

Subsequent runs reuse the saved key — no need to export `DEX_API_KEY` again.

**Headless detection triggers:** `$DEX_API_KEY` is set, `~/.dex/api-key` exists, SSH session without `$DISPLAY`, or Linux without any display server.

## Data Model

```
Contact
├── Emails, Phone Numbers, Social Profiles
├── Company, Job Title, Birthday, Website
├── Description (rich text notes about the person)
├── Tags (flat labels: "Investor", "College Friend")
├── Groups (collections with emoji + description: "🏢 Acme Team")
├── Custom Fields (user-defined: input, dropdown, datepicker)
├── Notes/Timeline (interaction log: meetings, calls, coffees)
├── Reminders (follow-up tasks with optional recurrence)
└── Starred / Archived status
```

## Using Tools

### MCP Mode

Call `dex_*` tools directly. All tools accept and return JSON.

### CLI Mode

Use the CLI at `~/.dex/bin/dex`. Every MCP tool maps to a CLI subcommand:

| MCP Tool | CLI Command |
|----------|------------|
| `dex_search_contacts` | `dex dex-search-contacts --query "..."` |
| `dex_get_contact` | `dex dex-get-contact --id "..."` |
| `dex_create_contact` | `dex dex-create-contact --first-name "..." --last-name "..."` |
| `dex_update_contact` | `dex dex-update-contact --id "..." --company "..."` |
| `dex_delete_contacts` | `dex dex-delete-contacts --from-json '{"contact_ids":["..."]}'` |
| `dex_merge_contacts` | `dex dex-merge-contacts --from-json '{"contact_id_groups":[["id1","id2"]]}'` |
| `dex_manage_tags` | `dex dex-manage-tags --action list` |
| `dex_manage_groups` | `dex dex-manage-groups --action list` |
| `dex_manage_notes` | `dex dex-manage-notes --action list --contact-id "..."` |
| `dex_manage_reminders` | `dex dex-manage-reminders --action list` |
| `dex_manage_custom_fields` | `dex dex-manage-custom-fields --action list` |

For complex inputs, use `--from-json`:
```bash
dex dex-manage-tags --from-json '{"action":"add_to_contacts","tag_ids":["id1"],"contact_ids":["c1","c2"]}'
```

Use `--output json` for machine-readable output, `--output text` (default) for human-readable.

Run `dex [command] --help` for full flag documentation on any subcommand.

## Core Workflows

### 1. Find a Contact

```
search → get details (with notes if needed)
```

- Search by name, email, company, or any keyword
- Use `*` or empty query to browse recent contacts (sorted by last interaction)
- Include `include_notes: true` when user needs interaction history

### 2. Add a New Contact

```
create contact → (optionally) add to groups → apply tags → set reminder
```

- Create with whatever info is available (no fields are strictly required)
- Immediately organize: add relevant tags and groups
- Set a follow-up reminder if the user just met this person

### 3. Log an Interaction

```
(optional) list note types → create note on contact timeline
```

- Discover note types first with `list_note_types` action to pick the right one (Meeting, Call, Coffee, Note, etc.)
- Set `event_time` to when the interaction happened, not when logging it
- Keep notes concise but capture key details, action items, and personal context

### 4. Set a Reminder

```
create reminder → (link to contact if applicable)
```

- Always require `due_at_date` (ISO format: "2026-03-15")
- Use `text` for the reminder description — there is no separate title field
- Recurrence options: `weekly`, `biweekly`, `monthly`, `quarterly`, `biannually`, `yearly`

### 5. Organize Contacts

**Tags** — flat labels for cross-cutting categories:
```
create tag → add to contacts (bulk)
```

**Groups** — named collections with emoji and description:
```
create group → add contacts (bulk)
```

Best practice: Use tags for attributes ("Investor", "Engineer", "Met at Conference X") and groups for relationship clusters ("Startup Advisors", "Book Club", "Acme Corp Team").

### 6. Manage Custom Fields

```
list fields → create field definition → batch update contacts
```

- Three field types: `input` (free text), `autocomplete` (dropdown with options), `datepicker`
- Use `batch_update_contacts` to set values on multiple contacts at once
- For autocomplete fields, provide `categories` array with the allowed options

### 7. Meeting Prep

When a user says "I have a meeting with X":

1. Search for the contact
2. Get full details with `include_notes: true`
3. Check recent reminders for pending items
4. Summarize: last interaction, key notes, pending follow-ups, shared context
5. See [CRM Workflows](references/crm-workflows.md) for detailed meeting prep guidance

### 8. Merge Duplicates

```
search for potential duplicates → confirm with user → merge
```

- First ID in each group becomes the primary — all other data merges into it
- Always confirm with the user before merging (destructive operation)
- Can merge multiple groups in a single call

## Important Patterns

### Pagination

All list operations support cursor-based pagination:
- Pass `limit` to control page size (default: 10)
- Check `has_more` in response
- Pass `next_cursor` from previous response to get next page
- Iterate until `has_more: false` to get all results

### Destructive Operations

Always confirm with the user before:
- Deleting contacts (`dex_delete_contacts`)
- Merging contacts (`dex_merge_contacts`)
- Deleting tags, groups, notes, reminders, or custom fields

### Response Truncation

Responses are capped at 25,000 characters. If truncated, use pagination to fetch remaining results.

### Date Formats

- All dates: ISO 8601 strings (e.g., `"2026-03-15"`, `"2026-03-15T14:30:00Z"`)
- Birthdays: `YYYY-MM-DD`
- Reminder due dates: `YYYY-MM-DD`

## Detailed References

- **[Tool Reference](references/tools-reference.md)** — Complete parameter documentation for every tool, with examples
- **[CRM Workflows](references/crm-workflows.md)** — Relationship management best practices, follow-up cadences, and strategies for being an effective CRM assistant
