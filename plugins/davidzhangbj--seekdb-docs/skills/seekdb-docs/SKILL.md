---
name: seekdb-docs
description: "seekdb database documentation lookup. Use when users ask about seekdb features, SQL syntax, vector search, hybrid search, integrations, deployment, or any seekdb-related topics. Automatically locates relevant docs via catalog-based semantic search."
---

# seekdb Documentation

Provides access to ~1000 seekdb documentation entries through a catalog-based search system. **Remote-only mode**: this skill ships only the catalog; doc content is always loaded from public documentation URLs (no local `seekdb-docs/`).

## Scope and behavior

This skill is **documentation-only**. It does not execute code or run scripts. The agent reads the local catalog (one JSONL file) and fetches doc content from public read-only URLs. No credentials, no installs, no subprocess calls.

## Version Info

<!-- AUTO-UPDATED — do not edit manually -->
- **Documentation versions covered**: V1.0.0, V1.1.0 (merged, latest takes priority)
- **Latest version**: V1.1.0
<!-- END AUTO-UPDATED -->
- The `branch` field in catalog entries indicates which Git branch hosts the file (used for remote fallback URLs only). It does NOT indicate which seekdb version the content applies to — many docs apply to all versions.
- If the user asks about a specific seekdb version, note that this documentation set reflects the latest available content and may not distinguish version-specific differences.

## Path Resolution (Do First)

1. Read this SKILL.md to get its absolute path and extract the parent directory as `<skill_dir>`
2. Catalog (required): `<skill_dir>references/seekdb-docs-catalog.jsonl`  
   If missing locally, load from: `https://raw.githubusercontent.com/oceanbase/seekdb-ecology-plugins/main/agent-skills/skills/seekdb/references/seekdb-docs-catalog.jsonl`

## Workflow

### Step 1: Search Catalog

**Keyword search (preferred for most queries)**  
Search the catalog file for lines containing the query keywords. File: `<skill_dir>references/seekdb-docs-catalog.jsonl`. Each line is one JSON object with `path`, `description`, and `branch`. Match by keyword or meaning.

**Full catalog** (when needed): same file as above, or fetch `https://raw.githubusercontent.com/oceanbase/seekdb-ecology-plugins/main/agent-skills/skills/seekdb/references/seekdb-docs-catalog.jsonl`. Format: JSONL — one `{"path": "...", "description": "...", "branch": "..."}` per line (~1000 entries).

### Step 2: Match Query

- Extract `path`, `description`, and `branch` from search results
- Select entries whose descriptions best match the query semantically (match by meaning, not just keywords)
- Consider multiple matches for comprehensive answers

### Step 3: Read Document (remote)

Fetch the document from the public docs URL (no local doc files in this package):

- URL: `https://raw.githubusercontent.com/oceanbase/seekdb-doc/[branch]/en-US/[path]`
- `[branch]` and `[path]` come from the catalog entry (e.g. `V1.0.0`, `V1.1.0`). Some files exist only on a specific branch.

## Example

```
Query: "How to integrate with Claude Code?"

1. Search catalog: look for lines containing "claude code" in <skill_dir>references/seekdb-docs-catalog.jsonl
2. Match: {"path": "300.integrations/300.developer-tools/700.claude-code.md",
           "description": "This guide explains how to use the seekdb plugin with Claude Code...",
           "branch": "V1.0.0"}
3. Fetch doc: https://raw.githubusercontent.com/oceanbase/seekdb-doc/V1.0.0/en-US/300.integrations/300.developer-tools/700.claude-code.md
```

See [examples.md](references/examples.md) for more complete workflow examples.

## Notes

- **Multi-version**: Each catalog entry's `branch` field is used in the doc URL; some files exist only on a specific branch.

## Category Overview

- **Get Started**: Quick start, basic operations, overview
- **Development**: Vector search, hybrid search, AI functions, MCP, multi-model
- **Integrations**: Frameworks, model platforms, developer tools, workflows
- **Guides**: Deployment, management, security, OBShell, performance
- **Reference**: SQL syntax, PL, error codes, SDK APIs
- **Tutorials**: Step-by-step scenarios
