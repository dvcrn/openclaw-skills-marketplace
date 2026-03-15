---
name: md-to-gdoc
description: "Convert markdown files to properly formatted Google Docs. Use when asked to create a Google Doc from markdown, upload markdown to Google Docs, put a .md file into Google Docs, or convert research/notes/documents to Google Docs format."
---

# Markdown to Google Doc

Convert `.md` files into Google Docs with proper heading styles, bold, code blocks, lists, links, and blockquotes.

## Requirements

- **[gog](https://github.com/tychohq/gog)** — Google Workspace CLI (must be authenticated: `gog auth add <email>`)
- **python3** — used for JSON parsing in the script

## Quick Start

```bash
scripts/md-to-gdoc.sh <file.md> [--title "Title"] [--parent <folder-id>] [--account <email>]
```

Resolve `scripts/` relative to this skill's directory.

## Critical Rules

1. **Use `gog docs update --format=markdown`** — never `write --markdown`, never `create --file`. The `update` path is the only one that correctly applies Google Docs heading styles via the API.
2. **Markdown must have proper `#` headings.** If the source has "heading-looking" plain text without `#` markers, add them before conversion. The script warns but proceeds.
3. **Two-step process**: create empty doc → populate with `update`. This is deterministic and reliable.
4. **Always verify heading syntax** in the markdown before running. No `#` = no formatted headings in the output.

## What Works

- `#`–`######` headings → Google Docs Heading 1–6
- `**bold**` → bold text
- `` `inline code` `` → Courier New
- Fenced code blocks → Courier New + gray background
- `> blockquotes` → indented paragraphs
- `- bullets` → bullet-prefixed text
- `1. numbered` → number-prefixed text
- `[text](url)` → hyperlinks
- Markdown tables → native Google Docs tables

## Known Limitations

- `*italic*` may not render (gog CLI bug in inline formatting parser — italic detection fails in certain contexts)
- Bullet/numbered lists use text prefixes (`•`, `1.`), not native Google Docs list objects
- Horizontal rules render as 40 dashes

## Options

- `--title` — Doc title. Defaults to filename with hyphens→spaces.
- `--parent` — Google Drive folder ID to place the doc in.
- `--account` — Google account email. Defaults to gog's default (first authenticated account).

## Troubleshooting

- **All body text, no headings**: The markdown file lacks `#` heading markers. Add them.
- **gog auth errors**: Run `gog auth list` to verify auth. May need `gog auth add <email>`.
- **Empty doc created**: The `update` step failed. Check gog output for API errors.
