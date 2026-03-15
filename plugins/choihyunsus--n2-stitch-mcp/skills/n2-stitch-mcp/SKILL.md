---
name: n2-stitch-mcp
description: "Resilient MCP proxy for Google Stitch — 3-layer safety (auto-retry, token refresh, TCP drop recovery)."
homepage: https://nton2.com
---

# 🛡️ N2 Stitch MCP — Resilient Proxy Skill

Never lose a screen generation again. The only Stitch MCP proxy with **TCP drop recovery**.

## The Problem

Google Stitch's `generate_screen_from_text` takes **2–10 minutes**, but the API **drops TCP after ~60 seconds**.

```
Other MCP servers:  Request → 60s → TCP drop → ❌ LOST!
N2 Stitch MCP:      Request → 60s → TCP drop → 🛡️ Auto-recovery → ✅ Delivered!
```

## Why This One?

| Feature | Others | **N2 Stitch MCP** |
|---------|:---:|:---:|
| TCP Drop Recovery | ❌ | ✅ Auto-polling |
| Generation Tracking | ❌ | ✅ `generation_status` |
| Exponential Backoff | ❌ | ✅ 3x retry + jitter |
| Auto Token Refresh | ⚠️ | ✅ Background refresh |
| Test Suite | ❌ | ✅ 35 tests |

## Quick Setup

### 1. Authenticate (one-time)
```bash
# Option A: gcloud (recommended)
gcloud auth application-default login

# Option B: API Key
export STITCH_API_KEY="your-key"
```

### 2. Add to MCP Config
```json
{
  "mcpServers": {
    "n2-stitch": {
      "command": "npx",
      "args": ["-y", "n2-stitch-mcp"]
    }
  }
}
```

## Available Tools

### Stitch API (auto-discovered)
- **create_project** — Create a Stitch project
- **list_projects** — List all projects
- **get_project** — Get project details
- **list_screens** — List screens in a project
- **get_screen** — Get screen HTML/CSS
- **generate_screen_from_text** — ✨ Generate UI from text (Resilient!)
- **edit_screens** — Edit existing screens
- **generate_variants** — Generate design variants

### Virtual Tools (N2 Exclusive)
- **generation_status** — Check generation progress in real-time
- **list_generations** — List all tracked generations

## Links
- NPM: https://www.npmjs.com/package/n2-stitch-mcp
- GitHub: https://github.com/choihyunsus/n2-stitch-mcp
- Website: https://nton2.com

---
*Part of the N2 AI Body series — Building the Body for AI*
