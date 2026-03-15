---
name: infinite-memory
description: "High-precision memory with 100% recall accuracy for long contexts."
---

# Infinite Memory 🦞

High-precision RAG engine for deep context retrieval (Phase 16 Architecture).

## Tools

### recall_facts
- **Cmd:** `python scripts/recall.py "{{query}}"`
- **Goal:** Search for facts in the historical database.

### memorize_data
- **Cmd:** `python scripts/ingest.py "{{filename}}" "{{text}}"`
- **Goal:** Store new data into the long-term memory.
