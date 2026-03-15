# Dex Tools Reference

Complete parameter documentation for all Dex MCP tools. Each tool is documented with its parameters, return format, and usage examples.

## Table of Contents

- [Contacts](#contacts)
  - [dex_search_contacts](#dex_search_contacts)
  - [dex_get_contact](#dex_get_contact)
  - [dex_create_contact](#dex_create_contact)
  - [dex_update_contact](#dex_update_contact)
  - [dex_delete_contacts](#dex_delete_contacts)
  - [dex_merge_contacts](#dex_merge_contacts)
- [Tags](#tags) — dex_manage_tags
- [Groups](#groups) — dex_manage_groups
- [Notes](#notes) — dex_manage_notes
- [Reminders](#reminders) — dex_manage_reminders
- [Custom Fields](#custom-fields) — dex_manage_custom_fields

---

## Contacts

### dex_search_contacts

Search contacts by name, email, or any keyword with paginated results.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | Search query. Use `*` or empty for all contacts sorted by last interaction |
| `cursor` | string | No | Pagination cursor from previous response |
| `limit` | number | No | Results per page (default: 10) |

**Returns:** `{ items: Contact[], has_more: boolean, next_cursor?: string, count?: number }`

**Examples:**

```json
// Search by name
{ "query": "John Smith" }

// Search by company
{ "query": "Acme Corp" }

// Browse all contacts (most recently interacted first)
{ "query": "*", "limit": 20 }

// Paginate
{ "query": "engineer", "cursor": "abc123", "limit": 10 }
```

---

### dex_get_contact

Get full contact details by ID, including emails, phones, tags, groups, custom fields, and optionally recent notes.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | string | Yes | Contact ID |
| `include_notes` | boolean | No | Include up to 10 recent timeline items (default: false) |

**Returns:** Full contact object with nested relationships.

**When to use `include_notes: true`:**
- User wants to review interaction history
- Preparing for a meeting
- Checking when they last spoke to someone
- Looking for context about a relationship

---

### dex_create_contact

Create a new contact. No fields are strictly required, but at least one should be provided.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `first_name` | string | No | First name |
| `last_name` | string | No | Last name |
| `company` | string | No | Company name |
| `job_title` | string | No | Job title |
| `email` | string | No | Primary email address |
| `phone` | string | No | Primary phone number |
| `linkedin` | string | No | LinkedIn profile URL |
| `twitter` | string | No | Twitter/X handle |
| `birthday` | string | No | Birthday (YYYY-MM-DD) |
| `description` | string | No | Notes about the contact |
| `website` | string | No | Website URL |

**Returns:** Created contact object.

**Example:**

```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "company": "Acme Corp",
  "job_title": "VP Engineering",
  "email": "jane@acme.com",
  "linkedin": "https://linkedin.com/in/janedoe"
}
```

---

### dex_update_contact

Partial update — only provided fields are changed.

**Parameters:**

All fields from `dex_create_contact` plus:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | string | Yes | Contact ID to update |
| `starred` | boolean | No | Star/unstar contact |
| `is_archived` | boolean | No | Archive/unarchive contact |

**Note:** Setting `email` or `phone` replaces the existing value, not appends.

---

### dex_delete_contacts

Bulk delete contacts. Irreversible — always confirm with user first.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `contact_ids` | string[] | Yes | Array of contact IDs to delete |

**Returns:** `{ deleted: string[] }`

---

### dex_merge_contacts

Merge duplicate contacts. The first ID in each group becomes the primary.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `contact_id_groups` | string[][] | Yes | Groups of IDs to merge. Each group: minimum 2 IDs |

**Example:**

```json
{
  "contact_id_groups": [
    ["primary-id-1", "duplicate-id-1a", "duplicate-id-1b"],
    ["primary-id-2", "duplicate-id-2a"]
  ]
}
```

---

## Tags

### dex_manage_tags

Multi-action tool for tag management.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `action` | enum | Yes | `list`, `get`, `create`, `update`, `delete`, `add_to_contacts`, `remove_from_contacts` |
| `tag_id` | string | Conditional | Required for: `get`, `update`, `delete` |
| `name` | string | Conditional | Required for: `create`, `update` |
| `tag_ids` | string[] | Conditional | Required for: `add_to_contacts`, `remove_from_contacts` |
| `contact_ids` | string[] | Conditional | Required for: `add_to_contacts`, `remove_from_contacts` |
| `cursor` | string | No | Pagination cursor (for `list`) |
| `limit` | number | No | Results per page (default: 10, for `list`) |

**Action examples:**

```json
// List all tags
{ "action": "list" }

// Create a tag
{ "action": "create", "name": "Investor" }

// Tag multiple contacts
{ "action": "add_to_contacts", "tag_ids": ["tag1"], "contact_ids": ["c1", "c2", "c3"] }

// Remove tags from contacts
{ "action": "remove_from_contacts", "tag_ids": ["tag1"], "contact_ids": ["c1"] }
```

---

## Groups

### dex_manage_groups

Multi-action tool for group management.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `action` | enum | Yes | `list`, `get`, `create`, `update`, `delete`, `add_contacts`, `remove_contacts`, `list_contacts` |
| `group_id` | string | Conditional | Required for: `get`, `update`, `delete`, `add_contacts`, `remove_contacts`, `list_contacts` |
| `name` | string | Conditional | Required for: `create` |
| `emoji` | string | No | Emoji icon (create/update) |
| `description` | string | No | Group description (create/update) |
| `contact_ids` | string[] | Conditional | Required for: `add_contacts`, `remove_contacts` |
| `cursor` | string | No | Pagination cursor (for `list_contacts`) |
| `limit` | number | No | Results per page (default: 10, for `list_contacts`) |

**Note:** `list` returns ALL groups (no pagination). `list_contacts` within a group IS paginated.

**Action examples:**

```json
// Create a group
{ "action": "create", "name": "Startup Advisors", "emoji": "🚀", "description": "Advisory board members" }

// Add contacts to group
{ "action": "add_contacts", "group_id": "g1", "contact_ids": ["c1", "c2"] }

// List contacts in group
{ "action": "list_contacts", "group_id": "g1", "limit": 20 }
```

---

## Notes

### dex_manage_notes

Multi-action tool for timeline notes.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `action` | enum | Yes | `list`, `get`, `create`, `update`, `delete`, `list_note_types` |
| `note_id` | string | Conditional | Required for: `get`, `update`, `delete` |
| `contact_id` | string | Conditional | Required for: `list` (filter), `create` (associate) |
| `content` | string | Conditional | Note body. Required for: `create` |
| `event_time` | string | No | ISO datetime of when the event happened. Defaults to now. |
| `note_type_id` | string | No | Type ID from `list_note_types`. Falls back to "Note" if omitted. |
| `cursor` | string | No | Pagination cursor (for `list`) |
| `limit` | number | No | Results per page (default: 10, for `list`) |

**Important:** Always call `list_note_types` first to discover available types before creating notes. The type IDs are user-specific.

**Action examples:**

```json
// Discover note types
{ "action": "list_note_types" }

// Log a meeting
{
  "action": "create",
  "contact_id": "c1",
  "content": "Discussed Series A fundraising timeline. They're targeting Q3. Action: send intro to our LP contacts.",
  "event_time": "2026-03-01T14:00:00Z",
  "note_type_id": "meeting-type-id"
}

// List contact's timeline
{ "action": "list", "contact_id": "c1", "limit": 20 }
```

---

## Reminders

### dex_manage_reminders

Multi-action tool for reminders/tasks.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `action` | enum | Yes | `list`, `get`, `create`, `update`, `delete` |
| `reminder_id` | string | Conditional | Required for: `get`, `update`, `delete` |
| `text` | string | Conditional | Reminder description. Required for: `create`. No separate title field. |
| `due_at_date` | string | Conditional | Due date (YYYY-MM-DD). Required for: `create` |
| `contact_id` | string | No | Link to a contact (create) |
| `recurrence` | enum | No | `weekly`, `biweekly`, `monthly`, `quarterly`, `biannually`, `yearly` |
| `is_complete` | boolean | No | Mark complete/incomplete (update) |
| `cursor` | string | No | Pagination cursor (for `list`) |
| `limit` | number | No | Results per page (default: 10, for `list`) |

**Action examples:**

```json
// Create a follow-up reminder
{
  "action": "create",
  "text": "Follow up with Jane about the partnership proposal",
  "due_at_date": "2026-03-15",
  "contact_id": "c1"
}

// Create a recurring check-in
{
  "action": "create",
  "text": "Monthly check-in with mentor",
  "due_at_date": "2026-04-01",
  "contact_id": "c2",
  "recurrence": "monthly"
}

// Complete a reminder
{ "action": "update", "reminder_id": "r1", "is_complete": true }
```

---

## Custom Fields

### dex_manage_custom_fields

Multi-action tool for custom field definitions and values.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `action` | enum | Yes | `list`, `create`, `update`, `delete`, `batch_update_contacts` |
| `custom_field_id` | string | Conditional | Required for: `update`, `delete` |
| `name` | string | Conditional | Field name. Required for: `create` |
| `field_type` | enum | Conditional | `input` (free text), `autocomplete` (dropdown), `datepicker`. Required for: `create` |
| `categories` | string[] | No | Dropdown options for `autocomplete` type |
| `updates` | object[] | Conditional | Batch updates. Required for: `batch_update_contacts` |

**Batch update format:**

```json
{
  "action": "batch_update_contacts",
  "updates": [
    { "contact_id": "c1", "custom_field_id": "cf1", "text_value": "Enterprise" },
    { "contact_id": "c2", "custom_field_id": "cf1", "text_value": "Startup" },
    { "contact_id": "c3", "custom_field_id": "cf2", "date_value": "2026-01-15" }
  ]
}
```

**Action examples:**

```json
// List all custom fields
{ "action": "list" }

// Create a dropdown field
{
  "action": "create",
  "name": "Deal Stage",
  "field_type": "autocomplete",
  "categories": ["Prospect", "Qualified", "Negotiation", "Closed Won", "Closed Lost"]
}

// Create a date field
{ "action": "create", "name": "Last Contract Date", "field_type": "datepicker" }
```

---

## Error Handling

Common error patterns:

- **Professional subscription required**: 403 response. Inform user they need a Dex Professional plan and provide upgrade URL.
- **Not found**: Contact/tag/group/note/reminder ID doesn't exist. Ask user to search again.
- **Invalid date**: Date string couldn't be parsed. Ensure ISO 8601 format.
- **Truncated response**: Response exceeded 25,000 chars. Use pagination with smaller `limit`.
