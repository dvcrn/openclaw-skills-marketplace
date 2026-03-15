---
name: second-brain-ai
description: "Read, capture, search, relate, and assemble context from a user-specified local Markdown knowledge base (Obsidian/Logseq style). Supports controlled write operations with explicit approval and attribution. Use when the user wants a Second Brain / note-vault memory layer for Markdown notes, including saving ideas, searching past notes, finding related notes or backlinks, building context packs, appending to existing notes (with attribution), or getting smart link suggestions."
---

# Second Brain AI Skill v2.0 (Repair Build)

A lightweight skill for working with a user-chosen Markdown knowledge base with controlled write operations and attribution requirements.

## Requirements

- Node.js >= 16.0.0
- Environment variable `SECOND_BRAIN_VAULT` must be set explicitly
- Optional: Frontmatter support (YAML)
- Optional: WikiLinks support `[[Note Title]]`

## Configuration

```bash
export SECOND_BRAIN_VAULT="/absolute/path/to/your/vault"
```

## Safety Boundaries

- Only operates within the configured vault path
- Write operations require `allow_write: true`
- Append operations require `appended_by` attribution

## Tools

### 1. init_vault
Initialize a new vault with standard folder structure.

**Input:** `{ "allow_write": true }`

### 2. capture_note
Create a new note.

**Input:**
```json
{
  "allow_write": true,
  "title": "Note Title",
  "content": "Body content",
  "type": "idea",
  "tags": ["tag1", "tag2"],
  "links": ["Related Note"]
}
```

### 3. append_note
Append content to an existing note with attribution.

**Input:**
```json
{
  "allow_write": true,
  "title": "Note Title",
  "content": "Additional content",
  "section": "Updates",
  "appended_by": "Agent Name"
}
```

**Required:** `appended_by` must identify who is appending.

### 4. search_notes
Search notes by keywords.

**Input:** `{ "query": "search terms", "limit": 5 }`

### 5. find_related
Find notes related to a topic.

**Input:** `{ "topic": "Topic Name", "limit": 5 }`

### 6. get_backlinks
Get notes that link to a specific note.

**Input:** `{ "note_title": "Target Note" }`

### 7. build_context_pack
Build a context pack for agent consumption.

**Input:** `{ "topic": "Topic", "limit": 10 }`

### 8. suggest_links
Get smart link suggestions for a note.

**Input:** `{ "title": "Note Title", "limit": 5 }`

### 9. rebuild_index
Refresh index (currently returns skip status as SQLite is not implemented).

**Input:** `{}`

## Note Format

Standard frontmatter:
```yaml
---
id: 20260313
title: Note Title
type: idea
tags: [tag1, tag2]
created: 2026-03-13
updated: 2026-03-13
status: active
---
```

## Append Attribution Format

When appending, the skill adds:
```markdown
> Append Record
> Added by: {appended_by}
> Added at: {timestamp}

{content}
```

## Limitations (Repair Build)

- SQLite indexing is not implemented; uses file-based scanning
- No semantic/vector search
- No automatic link insertion
- No conflict detection
- Single vault only

## Testing

```bash
npm test
```
