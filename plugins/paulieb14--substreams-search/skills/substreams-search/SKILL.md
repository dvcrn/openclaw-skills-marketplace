---
name: substreams-search
description: "Substreams Search"
---

# Substreams Search

Search, inspect, and analyze Substreams packages from the substreams.dev registry — from discovery to sink deployment.

## Tools

- **search_substreams** — Search the substreams.dev package registry by keyword, sort order, and blockchain network
- **inspect_package** — Inspect a .spkg file to see its module graph (DAG), protobuf output types, dependencies, and a Mermaid diagram
- **list_package_modules** — Lightweight module listing with types and inputs/outputs
- **get_sink_config** — Analyze sink configuration, extract SQL schemas, and generate ready-to-run CLI commands

## Install

```bash
npx substreams-search-mcp
```

## Use Cases

- Find Substreams packages for any blockchain (Ethereum, Solana, Arbitrum, Base, etc.)
- Inspect module graphs and understand data flow before deploying
- Get sink setup commands for PostgreSQL, ClickHouse, or subgraph entity sinks
- Discover sink-compatible modules in packages without embedded sink configs
