---
name: pinecone
description: "Pinecone vector database — manage indexes, upsert vectors, query similarity search, manage namespaces, and track collections via the Pinecone API. Build semantic search, recommendation systems, and RAG pipelines with high-performance vector storage. Built for AI agents — Python stdlib only, zero dependencies. Use for vector search, semantic similarity, RAG applications, recommendation engines, and AI memory systems."
homepage: https://www.agxntsix.ai
---

# 🌲 Pinecone

Pinecone vector database — manage indexes, upsert vectors, query similarity search, manage namespaces, and track collections via the Pinecone API.

## Features

- **Index management** — create, configure, delete indexes
- **Vector upsert** — insert and update vectors with metadata
- **Similarity search** — query nearest neighbors
- **Namespace management** — organize vectors by namespace
- **Metadata filtering** — filter queries by metadata fields
- **Collection management** — create snapshots of indexes
- **Batch operations** — bulk upsert and delete
- **Index stats** — vector counts, dimensions, usage
- **Sparse-dense** — hybrid search with sparse vectors
- **Serverless** — auto-scaling serverless indexes

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `PINECONE_API_KEY` | ✅ | API key/token for Pinecone |

## Quick Start

```bash
# List indexes
python3 {baseDir}/scripts/pinecone.py indexes
```

```bash
# Get index details
python3 {baseDir}/scripts/pinecone.py index-get my-index
```

```bash
# Create an index
python3 {baseDir}/scripts/pinecone.py index-create '{"name":"my-index","dimension":1536,"metric":"cosine","spec":{"serverless":{"cloud":"aws","region":"us-east-1"}}}'
```

```bash
# Delete an index
python3 {baseDir}/scripts/pinecone.py index-delete my-index
```



## Commands

### `indexes`
List indexes.
```bash
python3 {baseDir}/scripts/pinecone.py indexes
```

### `index-get`
Get index details.
```bash
python3 {baseDir}/scripts/pinecone.py index-get my-index
```

### `index-create`
Create an index.
```bash
python3 {baseDir}/scripts/pinecone.py index-create '{"name":"my-index","dimension":1536,"metric":"cosine","spec":{"serverless":{"cloud":"aws","region":"us-east-1"}}}'
```

### `index-delete`
Delete an index.
```bash
python3 {baseDir}/scripts/pinecone.py index-delete my-index
```

### `upsert`
Upsert vectors.
```bash
python3 {baseDir}/scripts/pinecone.py upsert --index my-index '{"vectors":[{"id":"vec1","values":[0.1,0.2,...],"metadata":{"text":"hello"}}]}'
```

### `query`
Query similar vectors.
```bash
python3 {baseDir}/scripts/pinecone.py query --index my-index '{"vector":[0.1,0.2,...],"topK":10,"includeMetadata":true}'
```

### `fetch`
Fetch vectors by ID.
```bash
python3 {baseDir}/scripts/pinecone.py fetch --index my-index --ids vec1,vec2,vec3
```

### `delete`
Delete vectors.
```bash
python3 {baseDir}/scripts/pinecone.py delete --index my-index --ids vec1,vec2
```

### `delete-namespace`
Delete all vectors in namespace.
```bash
python3 {baseDir}/scripts/pinecone.py delete-namespace --index my-index --namespace docs
```

### `stats`
Get index statistics.
```bash
python3 {baseDir}/scripts/pinecone.py stats --index my-index
```

### `collections`
List collections.
```bash
python3 {baseDir}/scripts/pinecone.py collections
```

### `collection-create`
Create collection from index.
```bash
python3 {baseDir}/scripts/pinecone.py collection-create '{"name":"backup","source":"my-index"}'
```

### `namespaces`
List namespaces in index.
```bash
python3 {baseDir}/scripts/pinecone.py namespaces --index my-index
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/pinecone.py indexes --limit 5

# Human-readable
python3 {baseDir}/scripts/pinecone.py indexes --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/pinecone.py` | Main CLI — all Pinecone operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the Pinecone API and results are returned to stdout. Your data stays on Pinecone servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
