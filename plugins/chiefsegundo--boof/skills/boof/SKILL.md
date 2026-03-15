---
name: boof
description: "Convert PDFs and documents to markdown, index them locally for RAG retrieval, and analyze them token-efficiently. Use when asked to: read/analyze/summarize a PDF, process a document, boof a file, extract information from papers/decks/NOFOs, or when you need to work with large documents without filling the context window. Supports batch processing and cross-document queries."
---

# Boof 🍑

Local-first document processing: PDF → markdown → RAG index → token-efficient analysis.

Documents stay local. Only relevant chunks go to the LLM. Maximum knowledge absorption, minimum token burn.

## Quick Reference

### Convert + index a document
```bash
bash {SKILL_DIR}/scripts/boof.sh /path/to/document.pdf
```

### Convert with custom collection name
```bash
bash {SKILL_DIR}/scripts/boof.sh /path/to/document.pdf --collection my-project
```

### Query indexed content
```bash
qmd query "your question" -c collection-name
```

## Core Workflow

1. **Boof it:** Run `boof.sh` on a PDF. This converts it to markdown via Marker (local ML, no API) and indexes it into QMD for semantic search.

2. **Query it:** Use `qmd query` to retrieve only the relevant chunks. Send those chunks to the LLM — not the entire document.

3. **Analyze it:** The LLM sees focused, relevant excerpts. No wasted tokens, no lost-in-the-middle problems.

## When to Use Each Approach

**"Analyze this specific aspect of the paper"** → Boof + query (cheapest, most focused)

**"Summarize this entire document"** → Boof, then read the markdown section by section. Summarize each section individually, then merge summaries. See [advanced-usage.md](references/advanced-usage.md).

**"Compare findings across multiple papers"** → Boof all papers into one collection, then query across them.

**"Find where the paper discusses X"** → `qmd search "X" -c collection` for exact match, `qmd query "X" -c collection` for semantic match.

## Output Location

Converted markdown files are saved to `knowledge/boofed/` by default (override with `--output-dir`).

## Setup

If `boof.sh` reports missing dependencies, see [setup-guide.md](references/setup-guide.md) for installation instructions (Marker + QMD).

## Environment

- `MARKER_ENV` — Path to marker-pdf Python venv (default: `~/.openclaw/tools/marker-env`)
- `QMD_BIN` — Path to qmd binary (default: `~/.bun/bin/qmd`)
- `BOOF_OUTPUT_DIR` — Default output directory (default: `~/.openclaw/workspace/knowledge/boofed`)
