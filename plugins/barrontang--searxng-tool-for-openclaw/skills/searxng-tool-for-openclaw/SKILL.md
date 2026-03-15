---
name: searxng-tool-for-openclaw
description: "Install an OpenClaw plugin that adds SearXNG-powered web search without paid search APIs."
---

# SearXNG Tool for OpenClaw

This skill bundle points users at the npm package for the actual OpenClaw plugin.

## What it installs

The published npm package contains:

- the OpenClaw plugin entry declared in `openclaw.extensions`
- the `openclaw.plugin.json` manifest used for validation
- an executable installer so `npx searxng-tool-for-openclaw install` works

## Recommended install paths

Install the plugin directly from npm through OpenClaw:

```bash
openclaw plugins install searxng-tool-for-openclaw
```

Or use the package's installer binary:

```bash
npx searxng-tool-for-openclaw install
```

## Required runtime

- OpenClaw installed and available on your machine
- A reachable SearXNG instance with JSON output enabled

## Minimal config

Add the plugin entry to your OpenClaw config and point it at your SearXNG base URL.

```json
{
  "plugins": {
    "entries": {
      "searxng-tool": {
        "enabled": true,
        "config": {
          "baseUrl": "http://127.0.0.1:8888"
        }
      }
    }
  }
}
```

After install or config changes, restart the gateway.