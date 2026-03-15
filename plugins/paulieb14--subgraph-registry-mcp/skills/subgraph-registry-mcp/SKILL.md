---
name: subgraph-registry-mcp
description: "Discover and filter 15,500+ The Graph subgraphs by domain, network, protocol type, or natural language goal with reliability scores and query URLs."
---

# Subgraph Registry

Agent-friendly discovery of 15,500+ classified subgraphs on The Graph Network. Search by domain, network, protocol type, or natural language goal — get reliability-scored results with query URLs.

## Tools

- **search_subgraphs** — Filter by domain (defi, nfts, dao, gaming), network (ethereum, arbitrum, base), protocol type (dex, lending, bridge), entity type, or keyword
- **recommend_subgraph** — Natural language goal like "find DEX trades on Arbitrum" returns the best matching subgraphs
- **get_subgraph_detail** — Full classification, entities, reliability score, and query instructions for a specific subgraph
- **list_registry_stats** — Registry overview with available domains, networks, and protocol types

## Requirements

- **Runtime:** Node.js >= 18 (runs via `npx`)
- **Environment variables:** None required. The registry is pre-built and bundled — no API key needed for read-only use.

## Install

```bash
npx subgraph-registry-mcp
```

## Network & Data Behavior

- On first run, the server downloads a pre-built `registry.db` (SQLite) from the [GitHub repository](https://github.com/PaulieB14/subgraph-registry) (~5 MB). This is cached locally and reused on subsequent runs.
- All tool queries run against this local database — no external API calls are made at query time.
- The SSE transport (`--http` / `--http-only`) starts a local HTTP server on port 3848 (configurable via `MCP_HTTP_PORT` env var).

## Use Cases

- Discover the right subgraph before querying The Graph
- Find high-reliability DeFi, NFT, DAO, or governance subgraphs by chain
- Get query URLs and entity schemas without manual exploration
- Compare subgraphs by reliability score (query fees, curation signal, indexer stake)
