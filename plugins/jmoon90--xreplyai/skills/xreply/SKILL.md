---
name: xreply
description: "Generate, schedule, and publish posts to X and LinkedIn in your voice using AI. Browse viral content, manage preferences, and track billing."
homepage: https://xreplyai.com
---

# XReply — AI Post Generator

Generate, schedule, and publish posts to X and LinkedIn in your voice using AI. Browse viral content for inspiration, manage your post queue, and track billing and quota.

## Authentication

All tools require an `XREPLY_TOKEN` environment variable — a JWT token from XreplyAI Settings. This is automatically injected by OpenClaw when set in your skill config.

## MCP Server

The XReply MCP server is published as `@xreplyai/mcp` on npm. You invoke tools via `mcporter`:

```
mcporter call 'npx @xreplyai/mcp' <tool_name> [param:value ...]
```

To discover all available tools and their parameters:

```
mcporter list 'npx @xreplyai/mcp' --all-parameters
```

## Tools

### Discovery

#### xreply_viral_library

Browse high-performing tweets (100+ likes) for inspiration. Filter by niche, keyword, and time range. Requires Pro or BYOK subscription.

```
mcporter call 'npx @xreplyai/mcp' xreply_viral_library
mcporter call 'npx @xreplyai/mcp' xreply_viral_library niche:ai sort:top_engaged
mcporter call 'npx @xreplyai/mcp' xreply_viral_library niche:saas query:pricing time_range:7d
mcporter call 'npx @xreplyai/mcp' xreply_viral_library niche:startups sort:recent page:2
```

Parameters:
- `niche` (optional): `ai` | `saas` | `marketing` | `productivity` | `startups` | `growth`
- `sort` (optional): `top_engaged` (default) | `recent`
- `query` (optional): keyword search within tweet text
- `time_range` (optional): `7d` | `30d`
- `page` (optional): page number, 20 results per page (default: 1)

---

### Generation

#### xreply_posts_generate

Generate a single AI post in the user's voice and auto-save it as a draft. Specify `platform` to control output length and style — X posts are capped at 280 chars, LinkedIn posts up to 3000 chars. Returns the generated body and saved post ID. Counts as 1 against the daily quota (5/day free, 100/day pro).

```
mcporter call 'npx @xreplyai/mcp' xreply_posts_generate
mcporter call 'npx @xreplyai/mcp' xreply_posts_generate topic:"my SaaS hit 1000 users"
mcporter call 'npx @xreplyai/mcp' xreply_posts_generate topic:"lessons from year 1" angle:story_arc
mcporter call 'npx @xreplyai/mcp' xreply_posts_generate platform:linkedin topic:"leadership lessons"
mcporter call 'npx @xreplyai/mcp' xreply_posts_generate angle:one_liner
```

Parameters:
- `topic` (optional): topic or prompt for the post (max 280 chars)
- `angle` (optional): `one_liner` | `list` | `question` | `story_arc` | `paragraph` | `my_voice`
- `platform` (optional): `x` (default) | `linkedin` — controls output length and style

#### xreply_posts_generate_batch

Generate multiple AI posts at once. Each post counts as 1 against the daily quota — check billing first if quota is a concern. A batch of 9 will exhaust a free account.

```
mcporter call 'npx @xreplyai/mcp' xreply_posts_generate_batch category:personalized count:5
mcporter call 'npx @xreplyai/mcp' xreply_posts_generate_batch category:trending count:3
mcporter call 'npx @xreplyai/mcp' xreply_posts_generate_batch category:viral count:9
```

Parameters:
- `category` (required): `personalized` | `trending` | `viral`
- `count` (required): number of posts to generate (1–9, must not exceed remaining daily quota)

---

### Post Management

#### xreply_posts_list

List all posts in the queue — drafts, scheduled, and recent posts. Returns post IDs, body text, status, scheduled times, and per-platform content.

```
mcporter call 'npx @xreplyai/mcp' xreply_posts_list
```

No parameters.

#### xreply_posts_create

Save a post draft. Use `body` for a simple X-only post. Use `post_contents` for LinkedIn posts or when posting different content to multiple platforms. The post is not published until you call `xreply_posts_publish`.

**X-only post (simple):**
```
mcporter call 'npx @xreplyai/mcp' xreply_posts_create body:"Your tweet text here"
```

**X post with auto-retweet:**
```
mcporter call 'npx @xreplyai/mcp' xreply_posts_create post_contents:'[{"platform":"x","body":"Tweet text","metadata":{"auto_rt_hours":24}}]'
```

**LinkedIn post:**
```
mcporter call 'npx @xreplyai/mcp' xreply_posts_create post_contents:'[{"platform":"linkedin","body":"Your long LinkedIn post here..."}]'
```

**Cross-post to X and LinkedIn with different text:**
```
mcporter call 'npx @xreplyai/mcp' xreply_posts_create post_contents:'[{"platform":"x","body":"Short tweet"},{"platform":"linkedin","body":"Expanded LinkedIn version..."}]'
```

**LinkedIn post with image:**
```
mcporter call 'npx @xreplyai/mcp' xreply_posts_create post_contents:'[{"platform":"linkedin","body":"Caption here","content_type":"single_image","metadata":{"asset_urn":"urn:li:digitalmediaAsset:..."}}]'
```

Parameters:
- `body` (optional): X post body text (max 280 chars). Use `post_contents` for LinkedIn or cross-posting.
- `post_contents` (optional): array of per-platform content objects. Takes precedence over `body`.
  - `platform` (required): `x` | `linkedin`
  - `body` (required): post body (max 280 for X, max 3000 for LinkedIn)
  - `content_type` (optional): `text` (default) | `single_image` | `multi_image`
  - `metadata` (optional): `{ asset_urn: "..." }` for single_image, `{ asset_urns: ["...","..."] }` for multi_image, `{ auto_rt_hours: 24 }` for X auto-retweet
- `account_id` / `account_ids` (optional): social account(s) to post from

#### xreply_posts_edit

Edit a post's content, scheduled time, or auto-retweet setting. Use `body` to update X-only text, or `post_contents` to update per-platform content. Cannot edit posts that are processing or already published.

```
mcporter call 'npx @xreplyai/mcp' xreply_posts_edit id:123 body:"Updated tweet text"
mcporter call 'npx @xreplyai/mcp' xreply_posts_edit id:123 'scheduled_at:2026-03-15T09:00:00Z'
mcporter call 'npx @xreplyai/mcp' xreply_posts_edit id:123 post_contents:'[{"platform":"linkedin","body":"Updated LinkedIn text"}]'
```

Parameters:
- `id` (required): post ID (integer)
- `body` (optional): new X body text (max 280 chars)
- `post_contents` (optional): per-platform content to update — replaces content for submitted platforms only. `metadata.auto_rt_hours` sets X auto-retweet hours; pass `null` to disable.
- `scheduled_at` (optional): ISO 8601 datetime string — omit to leave unchanged; pass `null` to unschedule

#### xreply_posts_delete

Delete a post. Cannot delete posts that are processing or already published.

```
mcporter call 'npx @xreplyai/mcp' xreply_posts_delete id:123
```

Parameters:
- `id` (required): post ID (integer)

---

### Publishing

#### xreply_posts_publish

Publish or schedule a post. Requires `account_id` or `account_ids` — if neither is provided and no accounts were attached when the post was created, returns `NO_ACCOUNT_SPECIFIED`. If `scheduled_at` is provided (ISO 8601), the post will be queued for that time (scheduling horizon depends on your plan). If omitted, the post is published immediately. Each platform (X, LinkedIn) requires the corresponding social account to be connected.

```
mcporter call 'npx @xreplyai/mcp' xreply_posts_publish id:123 account_id:1
mcporter call 'npx @xreplyai/mcp' xreply_posts_publish id:123 account_id:1 'scheduled_at:2026-03-15T09:00:00Z'
mcporter call 'npx @xreplyai/mcp' xreply_posts_publish id:123 'account_ids:[1,2]'
```

Parameters:
- `id` (required): post ID (integer)
- `account_id` (required if no accounts attached): social account ID to publish from
- `account_ids` (optional): array of social account IDs — takes precedence over `account_id`
- `scheduled_at` (optional): ISO 8601 datetime to schedule; omit to publish immediately

---

### Context

#### xreply_billing_status

Get subscription tier (free/byok/pro), quota usage, daily limits, and subscription details.

```
mcporter call 'npx @xreplyai/mcp' xreply_billing_status
```

No parameters.

#### xreply_voice_status

Get voice profile status — whether it has been analyzed, tweet count, AI provider configured, and writing style summary.

```
mcporter call 'npx @xreplyai/mcp' xreply_voice_status
```

No parameters.

#### xreply_preferences_get

Get current post generation preferences — tone, emoji usage, and default structure.

```
mcporter call 'npx @xreplyai/mcp' xreply_preferences_get
```

No parameters.

#### xreply_preferences_set

Update post generation preferences. Provide only the fields you want to change.

```
mcporter call 'npx @xreplyai/mcp' xreply_preferences_set tone:witty
mcporter call 'npx @xreplyai/mcp' xreply_preferences_set tone:professional include_emoji:false
mcporter call 'npx @xreplyai/mcp' xreply_preferences_set structure:story_arc
```

Parameters:
- `tone` (optional): `auto` | `casual` | `professional` | `witty` | `empathetic`
- `include_emoji` (optional): `true` | `false`
- `structure` (optional): `one_liner` | `paragraph` | `question` | `list` | `story_arc`

#### xreply_rules_list

List custom writing rules applied during generation — e.g. "never use hashtags", "always end with a question". Requires Pro or BYOK subscription.

```
mcporter call 'npx @xreplyai/mcp' xreply_rules_list
```

No parameters.

---

## Workflow Examples

### Generate and schedule an X post

```
1. mcporter call 'npx @xreplyai/mcp' xreply_posts_generate topic:"ship fast, learn faster" angle:story_arc
   → returns { body: "...", post: { id: 42, ... } }
2. mcporter call 'npx @xreplyai/mcp' xreply_posts_publish id:42 account_id:1 'scheduled_at:2026-03-12T09:00:00Z'
```

### Generate and schedule a LinkedIn post

```
1. mcporter call 'npx @xreplyai/mcp' xreply_posts_generate platform:linkedin topic:"leadership lessons from year 1" angle:story_arc
   → returns { body: "...", post: { id: 43, ... } }
2. mcporter call 'npx @xreplyai/mcp' xreply_posts_publish id:43 account_id:2 'scheduled_at:2026-03-12T09:00:00Z'
```

### Cross-post to X and LinkedIn with different text

```
1. mcporter call 'npx @xreplyai/mcp' xreply_posts_generate topic:"motivation" platform:x
   → { body: "Short tweet...", post: { id: 44 } }
2. mcporter call 'npx @xreplyai/mcp' xreply_posts_generate topic:"motivation" platform:linkedin
   → { body: "Long LinkedIn article...", post: { id: 45 } }

   Or create as a single post with both platforms:
3. mcporter call 'npx @xreplyai/mcp' xreply_posts_create post_contents:'[{"platform":"x","body":"Short tweet..."},{"platform":"linkedin","body":"Long LinkedIn article..."}]'
4. mcporter call 'npx @xreplyai/mcp' xreply_posts_publish id:46 'account_ids:[1,2]' 'scheduled_at:2026-03-13T09:00:00Z'
```

### Browse viral content for inspiration, then generate

```
1. mcporter call 'npx @xreplyai/mcp' xreply_viral_library niche:saas sort:top_engaged
   → review viral tweet formats
2. mcporter call 'npx @xreplyai/mcp' xreply_posts_generate topic:"inspired by those formats" angle:list
```

### Plan posts for the week

```
1. mcporter call 'npx @xreplyai/mcp' xreply_billing_status
   → check remaining quota before a large batch
2. mcporter call 'npx @xreplyai/mcp' xreply_posts_generate_batch category:personalized count:7
   → generates 7 drafts
3. mcporter call 'npx @xreplyai/mcp' xreply_posts_list
   → review the queue
4. mcporter call 'npx @xreplyai/mcp' xreply_posts_edit id:101 'scheduled_at:2026-03-11T09:00:00Z'
   mcporter call 'npx @xreplyai/mcp' xreply_posts_edit id:102 'scheduled_at:2026-03-12T09:00:00Z'
   → schedule each post
```

### Edit and publish an existing draft

```
1. mcporter call 'npx @xreplyai/mcp' xreply_posts_list
   → find the draft ID
2. mcporter call 'npx @xreplyai/mcp' xreply_posts_edit id:55 body:"Revised tweet text"
3. mcporter call 'npx @xreplyai/mcp' xreply_posts_publish id:55 account_id:1
```

---

## Error Handling

**Token expired:** If tools return a 401 error, the `XREPLY_TOKEN` has expired (tokens last 30 days). Ask the user to get a fresh token from XreplyAI Settings and update it in their OpenClaw config.

**Quota exhausted:** If generation returns a quota error (e.g. "Daily generation quota exhausted"), call `xreply_billing_status` to check limits and inform the user. Quota resets at midnight.

**Quota insufficient for batch:** If `xreply_posts_generate_batch` returns `quota_insufficient: true`, reduce `count` to the `available` value shown in the response, or ask the user to confirm.

**Schedule out of range:** If scheduling returns a validation error, the requested time exceeds the plan's scheduling horizon. Call `xreply_billing_status` to check `max_schedule_days` and suggest an earlier time.

**Cannot edit/delete:** Posts with status `processing` or `posted` cannot be edited or deleted. Call `xreply_posts_list` to check the current status.

**Viral library requires Pro:** If `xreply_viral_library` or `xreply_rules_list` returns a 403, inform the user these features require a Pro or BYOK subscription.

**No account specified:** If publish returns `NO_ACCOUNT_SPECIFIED`, you must pass `account_id` or `account_ids`. Call `xreply_posts_list` to see which accounts are already attached to the post, or ask the user which account to publish from.

**LinkedIn account not connected:** If publishing to LinkedIn returns a 422, the user has not connected their LinkedIn account. Direct them to XreplyAI Settings to connect it.
