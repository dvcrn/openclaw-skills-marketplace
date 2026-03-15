---
name: searcher-os
description: "Manage deal pipeline, search on-market deals, track brokers, and review CIM analyses in Searcher OS"
homepage: https://searcheros.ai
---

# Searcher OS

Manage the user's M&A deal pipeline, search for businesses on the market, track broker relationships, review inbound emails, and analyze CIM documents via the Searcher OS REST API.

## Setup

The user must have a Searcher OS account on the Searcher ($90/mo) or Deal Team ($244/mo) plan. Get an API key from Settings > Agent in the Searcher OS web app.

## API

**Base URL:** `https://searcheros.ai/api/agent`

All tool calls use a single endpoint:

```
POST https://searcheros.ai/api/agent/invoke
Authorization: Bearer $SEARCHER_OS_API_KEY
Content-Type: application/json

{"tool": "<tool_name>", "params": {<params>}}
```

**Responses:**
- Success: `{"ok": true, "result": {...}}`
- Error: `{"ok": false, "error": {"code": "...", "message": "..."}}`
- Confirmation needed: `{"ok": true, "result": {"status": "pending_confirmation", "confirmationId": "...", "message": "...", "expiresAt": "..."}}`

## Tool Discovery

Call `GET https://searcheros.ai/api/agent/tools` with the same Authorization header to get the live list of all available tools with their descriptions and parameter schemas. Use this to stay current as new tools are added.

## Session Start

At the start of every conversation, call `get_context` first. It returns the user's name, buy boxes, pipeline stage counts, and feed stats in a single call. Use this to:
1. Greet the user by name
2. Give a brief pipeline status (e.g., "You have 12 active deals: 5 Interested, 3 NDA Signed, 2 CIM Review, 2 Conversations")
3. Highlight anything notable (e.g., "47 new deals came in this week")
4. Suggest 2-3 next actions:
   - "Want me to check your newest on-market deals?"
   - "Ready to update the stage on any deals?"
   - "Want to search for deals matching your buy box?"

## Available Tools

### Context
- **get_context** — Get session context: user profile, buy boxes, pipeline counts, feed stats. Call FIRST at start of every conversation.
- **ping** — Health check. No params.
- **buy_box_list** — Get user's acquisition criteria (buy boxes). No params.

### Pipeline (My Deals)
- **pipeline_list** — List tracked deals. Params: `stage?` (interested|nda_signed|cim_review|conversations|loi_sent|due_diligence|closed|dead), `search?` (string), `limit?` (default 20, max 100), `offset?`
- **pipeline_get_deal** — Get full deal details. Params: `opportunity_id` (uuid, required)
- **pipeline_stage_counts** — Count deals per stage. No params.
- **pipeline_move_stage** — Move deal to new stage. Needs confirmation. Params: `opportunity_id` (uuid), `new_stage` (enum)
- **pipeline_add_note** — Add note to deal. Params: `opportunity_id` (uuid), `notes` (string)
- **pipeline_kill_deal** — Kill a deal. Needs confirmation. Params: `opportunity_id` (uuid), `kill_reason` (string), `kill_notes?`

### Feed (On-Market Deals)
- **feed_search** — Search on-market deals. Params: `keyword?`, `industry?`, `states?` (string[]), `min_price?`, `max_price?`, `min_ebitda?`, `max_ebitda?`, `buy_box_id?`, `freshness_hours?`, `sort_by?` (first_seen|asking_price|sde_ebitda|gross_revenue), `sort_order?` (asc|desc), `limit?` (default 20, max 50), `offset?`
- **feed_count** — Count matching deals. Same filter params as feed_search minus pagination/sort.
- **feed_stats** — Feed statistics. No params.
- **feed_save_deal** — Save deal to pipeline. Needs confirmation. Params: `staging_listing_id` (uuid), `private_notes?`
- **feed_dismiss_deal** — Dismiss deal from feed. Needs confirmation. Params: `staging_listing_id` (uuid)

### Inbox (Inbound Emails)
- **inbox_list** — List emails. Params: `status?` (unmatched|matched|ignored), `limit?`, `offset?`
- **inbox_get_email** — Get full email. Params: `email_id` (uuid)
- **inbox_link_to_deal** — Link email to deal. Needs confirmation. Params: `email_id` (uuid), `opportunity_id` (uuid)
- **inbox_ignore** — Ignore email. Params: `email_id` (uuid)

### Brokers
- **broker_list** — List brokers. Params: `search?`, `sort_by?` (name|company|deal_count)
- **broker_get** — Get broker details. Params: `broker_id` (uuid)
- **broker_create** — Add broker. Needs confirmation. Params: `name` (required), `email?`, `phone?`, `company?`
- **broker_log_interaction** — Log interaction. Needs confirmation. Params: `broker_id` (uuid), `interaction_type` (call|email_sent|email_received|meeting|note), `subject?`, `notes?`, `opportunity_id?`

### CIM (Confidential Information Memorandums)
- **cim_list** — List CIM analyses for a deal. Params: `opportunity_id` (uuid)
- **cim_get_analysis** — Get CIM analysis details. Params: `cim_id` (uuid)
- **cim_search** — Search across CIM analyses. Params: `query?`

### Confirmations
Write operations may return `"status": "pending_confirmation"`. Use these tools to manage:
- **confirmation_list_pending** — List pending confirmations. No params.
- **confirmation_check_status** — Check status. Params: `confirmation_id` (uuid)
- **confirmation_resolve** — Approve or deny. Params: `confirmation_id` (uuid), `decision` (approved|denied)
- **confirmation_get_auto_approve** — Get auto-approve settings. No params.

## Confirmation Flow

Some tools (marked "Needs confirmation") require user approval before executing:

1. Call the write tool (e.g., `pipeline_move_stage`)
2. If result has `"status": "pending_confirmation"` — tell the user it needs their approval
3. The user can approve in the Searcher OS web app OR tell you "yes, approve it"
4. If user says approve: call `confirmation_resolve` with `{"confirmation_id": "<id>", "decision": "approved"}`
5. The action executes and returns the result
6. Confirmations expire after 30 minutes if not resolved

## Rate Limits

100 requests per minute per API key. On 429 responses, check the `Retry-After` header.
