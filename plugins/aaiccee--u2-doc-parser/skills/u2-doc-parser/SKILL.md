---
name: u2-doc-parser
description: "U2-doc-parser"
---

Name: u2-doc-parser
Description: Parse documents using UniDoc API for conversion to Markdown or JSON format. Supports both synchronous and asynchronous parsing with automatic status polling.

UniDoc Document Parser
======================

Overview
--------
Parse documents using UniDoc API for conversion to Markdown or JSON format. Supports both synchronous and asynchronous parsing with automatic status polling. Ideal for converting various document formats (PDF, DOC, DOCX, images) through a cloud-based API service.

Prereqs / when to read references
---------------------------------
If you encounter API errors, network issues, or need to understand the API endpoints, read:
* `references/unidoc-notes.md`

Quick start (single document)
-----------------------------
```bash
# Run from the skill directory
python scripts/unidoc_parse.py /path/to/file.pdf \
  --format md \
  --output ./unidoc-output \
  --mode sync
```

Options
-------
* `--format md|json` (default: `md`)
  - Output format: Markdown or JSON
* `--mode sync|async` (default: `sync`)
  - Synchronous mode: waits for conversion to complete
  - Asynchronous mode: polls status until completion
* `--func METHOD` (default: `unisound`)
  - Conversion method/algorithm to use
* `--output DIR` (default: `./unidoc-output`)
  - Output directory for converted files
- 
* `--uid UUID` (optional)
  - Custom user ID (auto-generated if not provided)

Output conventions
------------------
* Creates `./unidoc-output/<document_name>/` by default
* Markdown output: `output.md`
* JSON output: `output.json`
* Output filename preserves original document name

Notes
-----
* Requires network connectivity to UniDoc API (http://unidoc.uat.hivoice.cn)
* Supports multiple file formats: PDF, DOC, DOCX, PNG, JPG, etc.
* Async mode polls every 1 second until completion
* Max file size and rate limits depend on API service configuration
* For large files or batch processing, prefer async mode
