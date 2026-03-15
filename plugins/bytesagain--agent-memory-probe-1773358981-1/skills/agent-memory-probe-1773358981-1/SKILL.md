---
name: agent-memory-probe-1773358981-1
description: "Agent Memory Pro"
---

# Agent Memory Pro

- **name**: Agent Memory Pro
- **description**: Production-grade structured memory for AI agents with category-based storage, hash deduplication, consolidation, and portable export. Organizes learnings into typed categories, detects duplicates via MD5, and exports Markdown/JSON for cross-agent portability. Commands: init, save, recall, review, consolidate, export, stats, forget.

## FAQ

**Q: How is this different from basic agent memory?**
A: Structured categories, MD5 deduplication, and full export — not flat file storage.

**Q: Where are memories stored?**
A: `~/agent-memory/` with typed subdirs: learnings, facts, decisions, archive, exports.

**Q: Can I migrate memories between agents?**
A: Yes — `export` creates portable Markdown any agent can ingest.

**Q: How does consolidation work?**
A: MD5 hashing detects exact duplicates and reports them for cleanup.

## Commands

| Command | Purpose |
|---------|---------|
| `init` | Setup structured memory dirs |
| `save` | Store categorized learning |
| `recall` | Keyword search with ranking |
| `review` | Show recent 72h memories |
| `consolidate` | Hash-based deduplication |
| `export` | Portable Markdown export |
| `stats` | Per-category statistics |
| `forget` | Selective pruning |
