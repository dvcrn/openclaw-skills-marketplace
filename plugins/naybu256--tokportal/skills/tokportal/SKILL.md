---
name: tokportal
description: "Automate social media at scale — create TikTok/Instagram accounts, distribute videos, upload content, and track analytics with 30 AI-native MCP tools via the TokPortal API."
homepage: https://developers.tokportal.com
---

# TokPortal

Manage mass social media account creation, video distribution, and analytics via the TokPortal platform. This skill exposes 30 tools through a dedicated MCP server, giving your AI agent full control over TikTok and Instagram operations at scale.

## Setup

### 1. Get your API key

Sign up at [tokportal.com](https://tokportal.com) and generate an API key at [app.tokportal.com/developer/api-keys](https://app.tokportal.com/developer/api-keys).

### 2. Install the MCP server

The recommended way to use TokPortal with OpenClaw is via the MCP server:

```bash
npm install -g tokportal-mcp
```

### 3. Configure OpenClaw

Add to your `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "tokportal": {
        "enabled": true,
        "apiKey": "tok_live_your_key_here"
      }
    }
  }
}
```

Or set the environment variable:

```bash
export TOKPORTAL_API_KEY="tok_live_your_key_here"
```

### 4. Add MCP server config

Add to your MCP configuration (Cursor `.cursor/mcp.json` or Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "tokportal": {
      "command": "npx",
      "args": ["-y", "tokportal-mcp"],
      "env": {
        "TOKPORTAL_API_KEY": "tok_live_your_key_here"
      }
    }
  }
}
```

## Available Tools (30)

### Info (6 tools)
- `get_me` — Your profile, credit balance, and API key info
- `get_credit_balance` — Detailed balance with expiration dates
- `get_credit_history` — Transaction history (paginated)
- `get_countries` — Available countries for account creation
- `get_platforms` — Supported platforms (TikTok, Instagram) with features
- `get_credit_costs` — Full credit cost grid for all actions

### Bundles (8 tools)
- `create_bundle` — Create a bundle (account only, account + videos, or videos only)
- `create_bulk_bundles` — Performance Max: create multiple bundles at once
- `list_bundles` — List bundles with status/platform filters
- `get_bundle` — Full bundle state including account config and videos
- `publish_bundle` — Publish a configured bundle (goes live to account managers)
- `unpublish_bundle` — Pull a bundle back to draft
- `add_video_slots` — Add video slots to an existing bundle (2 credits/slot)
- `add_edit_slots` — Add editing slots (3 credits/slot)

### Account Configuration (4 tools)
- `get_account_config` — View current account setup
- `configure_account` — Set username, display name, bio, profile picture
- `finalize_account` — Approve an account that is in review
- `request_account_corrections` — Request fixes on specific fields

### Videos (6 tools)
- `list_videos` — List all videos in a bundle
- `configure_video` — Set up a single video (caption, publish date, media URL, sound settings)
- `batch_configure_videos` — Configure multiple videos at once
- `finalize_video` — Approve a video in review
- `request_video_corrections` — Request fixes on a video
- `unschedule_video` — Cancel a scheduled video

### Delivered Accounts (3 tools)
- `list_accounts` — List your delivered accounts with filters
- `get_account_detail` — Full credentials + TokMail email for an account
- `get_verification_code` — Retrieve the latest 6-digit verification code

### Analytics (4 tools)
- `get_analytics` — Followers, views, engagement rate, and more
- `refresh_analytics` — Trigger an analytics refresh (48h cooldown, 500/month quota)
- `can_refresh_analytics` — Check if a refresh is available
- `get_video_analytics` — Per-video analytics (views, likes, engagement)

### Uploads (2 tools — MCP only)
- `upload_video` — Upload a local video file, returns a public URL
- `upload_image` — Upload a local image file (for carousels or profile pictures)

## Example Workflows

### Create a TikTok account with 5 videos

> "Create a TikTok bundle in the US with 5 videos and niche warming for fitness content"

The agent will call `create_bundle` with the right params, then guide you through account and video configuration.

### Check your account analytics

> "Show me the analytics for all my delivered accounts"

The agent will call `list_accounts`, then `get_analytics` for each.

### Bulk video distribution

> "Create 10 TikTok accounts in France with 3 videos each"

Uses `create_bulk_bundles` (Performance Max) to create all bundles in one call.

## API Reference

- **Base URL:** `https://app.tokportal.com/api/ext`
- **Auth:** `X-API-Key` header
- **Rate limit:** 120 requests/minute per API key
- **Full docs:** [developers.tokportal.com](https://developers.tokportal.com)

## Credit System

TokPortal uses a credit-based model (1 credit = $1):
- Account creation: 5-8 credits depending on country
- Video upload: 2 credits per video
- Niche warming: 7 credits
- Deep warming (Instagram): 40 credits
- Comment moderation: 25 credits
- Video editing: 3 credits per edit slot

## Support

- Documentation: [developers.tokportal.com](https://developers.tokportal.com)
- Support: team@tokportal.com
- npm package: [tokportal-mcp](https://www.npmjs.com/package/tokportal-mcp)
