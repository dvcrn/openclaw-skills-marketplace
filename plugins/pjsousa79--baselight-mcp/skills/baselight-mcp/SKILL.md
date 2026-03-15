---
name: baselight-mcp
description: "Connects to the Baselight MCP (Model Context Protocol)"
homepage: https://baselight.ai/docs/connecting-to-the-baselight-mcp-server/
---

# Baselight MCP

Use Baselight via MCP to browse, discover, and query Baselight datasets
directly from your AI tool or IDE.

MCP Server URL: https://api.baselight.app/mcp

## When to Use This Skill

-   User wants datasets for a topic
-   User wants structured tables
-   User wants SQL analysis
-   User wants verifiable results

## Quick Start

Connect using OAuth or API key depending on client.

### OAuth Clients

-   ChatGPT connectors
-   Claude Web/Desktop

### API Key Clients

-   VS Code
-   Gemini CLI
-   LibreChat

------------------------------------------------------------------------

## Workflow

1.  Understand question
2.  Discover datasets
3.  Inspect schema
4.  Query data
5.  Return results + SQL

------------------------------------------------------------------------

## Query Format

Tables use:

@username.dataset.table

Example:

SELECT \* FROM @user.soccer.matches LIMIT 10;

------------------------------------------------------------------------

## Best Practices

-   Discover first
-   Inspect schema
-   Query iteratively
-   Include SQL
-   Explain assumptions

------------------------------------------------------------------------

## Limitations

-   Requires Baselight account or API key
-   Query limits may apply
-   Dataset freshness varies

------------------------------------------------------------------------

## Troubleshooting

Connection fails: - Verify MCP URL - Reauthenticate or regenerate key

Unauthorized: - Invalid key or expired OAuth

Slow query: - Reduce scope - Add LIMIT

------------------------------------------------------------------------

## Support

Docs: https://baselight.ai/docs/connecting-to-the-baselight-mcp-server/

App: https://baselight.app
