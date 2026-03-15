---
name: html-to-markdown
description: "Convert HTML to Markdown or Markdown to HTML, including file, URL, and batch modes with readability cleanup, metadata frontmatter, reports, and themed HTML output."
---

# html-to-markdown

Use this skill when the user wants to:
- convert HTML files, raw HTML, or web pages into Markdown
- convert Markdown into standalone HTML documents
- batch-convert directories or URL lists
- preserve article content with readability-style cleanup
- emit metadata/frontmatter or quality reports

## What it provides

This skill includes two scripts:
- `scripts/html_to_markdown.mjs` — HTML → Markdown
- `scripts/markdown_to_html.mjs` — Markdown → HTML

Read `references/profiles.md` when you need the preset cleanup profiles (`article`, `docs`, `forum`, `custom`) or want a quick capability map.

## HTML → Markdown

### Supported inputs
- `--file <path>`
- `--html <string>`
- `--url <https://...>`
- `--input-dir <dir>`
- `--url-list <file.txt>`

### Common outputs/options
- `--out <file.md>` / `--output-dir <dir>`
- `--profile <article|docs|forum|custom>`
- `--content-mode <readable|full>`
- `--engine <auto|best|turndown|pandoc>`
- `--meta-frontmatter <true|false>`
- `--report <file.json>`
- `--base-url <url>`
- `--image-style <inline|ref>`

### Examples

```bash
node scripts/html_to_markdown.mjs \
  --url "https://example.com/article" \
  --out ./article.md \
  --profile article \
  --engine best \
  --meta-frontmatter true \
  --report ./article.report.json
```

```bash
node scripts/html_to_markdown.mjs \
  --input-dir ./html \
  --output-dir ./md \
  --profile docs
```

## Markdown → HTML

### Supported inputs
- `--file <path.md>`
- `--markdown "# text"`
- `--input-dir <dir>`

### Common outputs/options
- `--out <file.html>` / `--output-dir <dir>`
- `--theme <light|github|minimal>`
- `--title <text>`
- `--standalone <true|false>`
- `--embed-css <true|false>`

### Examples

```bash
node scripts/markdown_to_html.mjs \
  --file ./README.md \
  --out ./README.html \
  --theme github
```

```bash
node scripts/markdown_to_html.mjs \
  --input-dir ./md \
  --output-dir ./html \
  --theme light
```

## Notes
- Prefer targeted conversions; do not rewrite unrelated content.
- For article/web content, start with `--profile article`.
- For docs sites, start with `--profile docs`.
- Use `--engine best` when output quality matters more than speed.
