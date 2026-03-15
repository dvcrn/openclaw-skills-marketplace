---
name: val
description: "Val"
---

> Generated note: shared plugin assets for this package live at the plugin root. Common local references were rewritten when they appeared in backticks or markdown links.

# Workspace Skill Entry

This file exists as a stable entry-point for agents that try to read `SKILL.md` from the workspace root.

## Where Skills Actually Live

- Root index: `../../skills/README.md`
- Calibre read-only: `../../skills/calibre-catalog-read/SKILL.md`
- Calibre metadata edit: `../../skills/calibre-metadata-apply/SKILL.md`

## Calibre Routing (Hard Rule)

- Read/search/list/id -> `calibre-catalog-read`
- Metadata edit/fix/update (title/authors/series/series_index/tags/publisher/pubdate/languages) -> `calibre-metadata-apply`
- Never start `calibre-server` from chat flow. Connect to an already-running Content server.

