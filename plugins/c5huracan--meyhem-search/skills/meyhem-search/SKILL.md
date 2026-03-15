---
name: meyhem-search
description: "Web search client that queries api.rhdxm.com and returns ranked results. Optionally retrieve page content. No API key."
homepage: https://github.com/c5huracan/meyhem
---

# Meyhem Search

Web search client for AI agents. Sends queries to api.rhdxm.com, which searches across multiple engines and returns ranked results. Optionally retrieve page content for a selected result.

No API key. No signup. No rate limits.

## Why Meyhem?

- **Simple interface**: send a query, get ranked results from multiple engines
- **Optional content retrieval**: use `--content` to fetch page text for the top result

## Quick Start

```bash
python3 search.py "transformer attention mechanism"
python3 search.py "async python best practices" -n 3
python3 search.py "react server components" --content
python3 search.py "kubernetes debugging" --agent my-agent
```

## Quick Start (REST)

Full API docs: https://api.rhdxm.com/docs

```bash
curl -s -X POST https://api.rhdxm.com/search \
  -H 'Content-Type: application/json' \
  -d '{"query": "YOUR_QUERY", "agent_id": "my-agent", "max_results": 5}'
```

## MCP

You can also connect via MCP at `https://api.rhdxm.com/mcp/` for richer integration.

## Data Transparency

This skill sends your search query, an agent identifier, and any selected URLs to `api.rhdxm.com`. The skill does not access local files, environment variables, or credentials on its own, but anything you include in the query or agent_id will be transmitted. Avoid sending sensitive or proprietary content.

Source code: https://github.com/c5huracan/meyhem
