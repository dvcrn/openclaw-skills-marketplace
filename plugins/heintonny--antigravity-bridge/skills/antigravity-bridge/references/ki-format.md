# Knowledge Item (KI) Format Reference

## Directory Structure

Each KI lives in its own topic directory:

```
knowledge/<topic_snake_case>/
├── metadata.json
├── timestamps.json
└── artifacts/
    ├── overview.md
    ├── <artifact_name>.md
    └── <subdirectory>/
        └── <artifact_name>.md
```

## metadata.json

```json
{
    "title": "Human-Readable Topic Title",
    "summary": "Comprehensive summary of what this knowledge covers. Should be detailed enough for the agent to decide whether to load full artifacts. 2-4 sentences.",
    "references": [
        {
            "type": "conversation_id",
            "value": "uuid-of-antigravity-session"
        },
        {
            "type": "file",
            "value": "/absolute/path/to/relevant/file"
        }
    ]
}
```

## timestamps.json

```json
{
    "created": "2026-01-15T10:30:00Z",
    "updated": "2026-03-06T22:00:00Z"
}
```

## Artifact Files

Markdown documents with detailed knowledge. No required format, but common patterns:

- `overview.md` — high-level summary of the topic
- `patterns.md` — implementation patterns and examples
- `hazards/*.md` — known pitfalls and warnings
- `lifecycle/*.md` — process documentation
- `implementation/*.md` — technical details

## Topic Naming

Use `snake_case` for topic directory names:
- ✅ `authentication_and_identity`
- ✅ `frontend_design_and_standards`
- ❌ `auth` (too vague)
- ❌ `Frontend-Design` (wrong case)

## Writing Guidelines

1. **Summaries power discovery.** The agent reads summaries to decide which KIs to load. Make them descriptive.
2. **Artifacts are self-contained.** Each artifact should be understandable without reading others.
3. **Reference, don't duplicate.** Link to other KIs or memory files instead of copying content.
4. **Date your updates.** Include "Updated: YYYY-MM-DD" in artifacts that change frequently.
5. **Respect knowledge.lock.** Check for the lock file before writing. Remove after writing.
