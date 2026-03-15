---
name: bnbot
description: "The safest and most efficient way to automate Twitter/X — BNBot operates through a real browser session with 28 AI-powered tools. Grow your Twitter without API bans."
homepage: https://github.com/jackleeio/bnbot-mcp-server
---

# BNBot - The Safest & Most Efficient Way to Automate Twitter/X

BNBot is an AI-powered Twitter growth agent. Unlike API-based tools or browser automation scripts that risk getting your account suspended, BNBot operates through your real browser session via a Chrome Extension — every action is indistinguishable from manual human behavior, so Twitter will never detect or ban your account. With 28 tools covering posting, engagement, scraping, content fetching, and article creation, it's also the most comprehensive and efficient automation toolkit available.

Install this skill to give your AI assistant (Claude Code, OpenClaw, ChatGPT, etc.) the ability to automatically manage and grow your Twitter account — all without touching the Twitter API.

- **Chrome Extension**: [BNBot - Your AI Growth Agent](https://chromewebstore.google.com/detail/bnbot-your-ai-growth-agen/haammgigdkckogcgnbkigfleejpaiiln)
- **MCP Server**: [bnbot-mcp-server](https://www.npmjs.com/package/bnbot-mcp-server)
- **GitHub**: [jackleeio/bnbot-mcp-server](https://github.com/jackleeio/bnbot-mcp-server)

## Setup

BNBot requires the MCP server to be configured in your AI client. If the bnbot MCP tools are not available, **show the user** the following configuration and ask them to add it:

```json
{
  "mcpServers": {
    "bnbot": {
      "command": "npx",
      "args": ["bnbot-mcp-server"]
    }
  }
}
```

**Config file locations by client:**
- **Claude Code**: `.mcp.json` in your project root
- **OpenClaw**: `~/.openclaw/openclaw.json`
- **ChatGPT Desktop / other MCP clients**: check your client's MCP configuration docs

**Important**: Never modify config files without the user's explicit approval. Always show the proposed changes and ask for confirmation first. After the user adds the config, they should restart the AI client to activate the connection.

## Error Handling (IMPORTANT)

After any BNBOT tool call, check the result. If the tool call fails or returns a connection error (e.g. WebSocket not connected, extension not responding, timeout), you MUST diagnose and guide the user:

### Connection failed / Extension not connected

Tell the user:

> BNBOT Chrome Extension is not connected. Please check:
>
> 1. **Install the extension** (if not installed):
>    Download from Chrome Web Store: https://chromewebstore.google.com/detail/bnbot-your-ai-growth-agen/haammgigdkckogcgnbkigfleejpaiiln
>
> 2. **Open Twitter/X** in Chrome (https://x.com)
>
> 3. **Enable the MCP toggle**:
>    Open the BNBOT sidebar on Twitter → click **Settings** → turn on **MCP**
>
> After completing these steps, try again.

### MCP Server not running

If the MCP tools are not available at all, tell the user:

> BNBOT MCP server is not running. Please restart your AI client to activate the connection.
> If the problem persists, try reinstalling: `npm install -g bnbot-mcp-server`

### General rules

- Always call `get_extension_status` first before executing other tools, to verify the extension is connected.
- If `get_extension_status` shows `connected: false`, show the connection guide above BEFORE attempting any other action.
- Never silently fail. Always explain what went wrong and how to fix it.

## Architecture

```
AI Client (Claude Code / OpenClaw / ChatGPT / ...) → bnbot-mcp-server (stdio) → WebSocket (localhost:18900) → BNBOT Chrome Extension → Twitter/X
```

## Available Tools (29)

### Status

- `get_extension_status` - Check if extension is connected
- `get_current_page_info` - Get info about the current Twitter/X page

### Navigation

- `navigate_to_tweet` - Go to a specific tweet (params: `tweetUrl`)
- `navigate_to_search` - Go to search page (params: `query`, optional `sort`)
- `navigate_to_bookmarks` - Go to bookmarks
- `navigate_to_notifications` - Go to notifications
- `navigate_to_following` - Go to following list
- `return_to_timeline` - Go back to home timeline

### Posting

- `post_tweet` - Post a tweet (params: `text`, optional `images`, optional `draftOnly`)
- `post_thread` - Post a thread (params: `tweets` array of `{text, images?}`)
- `submit_reply` - Reply to a tweet (params: `text`, optional `tweetUrl`, optional `image`)

### Engagement

- `like_tweet` - Like a tweet (params: `tweetUrl`)
- `retweet` - Retweet a tweet (params: `tweetUrl`)
- `quote_tweet` - Quote tweet (params: `tweetUrl`, `text`, optional `draftOnly`)
- `follow_user` - Follow a user (params: `username`)

### Scraping

- `scrape_timeline` - Scrape tweets from the timeline (params: `limit`, `scrollAttempts`)
- `scrape_bookmarks` - Scrape bookmarked tweets (params: `limit`)
- `scrape_search_results` - Search and scrape results (params: `query`, `limit`)
- `scrape_current_view` - Scrape currently visible tweets
- `scrape_thread` - Scrape a full tweet thread (params: `tweetUrl`)
- `account_analytics` - Get account analytics (params: `startDate`, `endDate` in YYYY-MM-DD)

### Content Fetching

- `fetch_wechat_article` - Fetch a WeChat article (params: `url`)
- `fetch_tiktok_video` - Fetch a TikTok video (params: `url`)
- `fetch_xiaohongshu_note` - Fetch a Xiaohongshu note (params: `url`)

### Articles

- `open_article_editor` - Open the Twitter/X article editor
- `fill_article_title` - Fill article title (params: `title`)
- `fill_article_body` - Fill article body (params: `content`, optional `format`: plain/markdown/html, optional `bodyImages`)
- `upload_article_header_image` - Upload header image (params: `headerImage`)
- `publish_article` - Publish or save as draft (params: optional `publish`, optional `asDraft`)
- `create_article` - Full article creation flow (params: `title`, `content`, optional `format`, optional `headerImage`, optional `bodyImages`, optional `publish`)

### Jobs

- `search_jobs` - Search for available jobs with crypto rewards (params: optional `type`: boost/hire/all, optional `status`, `sort`, `limit`, `keyword`, `endingSoon`, `token`)

## Usage Examples

- "Scrape my Twitter timeline and summarize the top topics"
- "Search for tweets about AI agents and collect the most engaging ones"
- "Post a tweet saying: Just discovered an amazing AI tool!"
- "Navigate to my bookmarks and export them"
- "Go to @elonmusk's latest tweet and reply with a thoughtful comment"
- "Post a thread about the top 5 productivity tips"
- "Like and retweet this tweet: https://x.com/..."
- "Follow @username"
- "Create an article about AI trends with markdown formatting"
- "Fetch this WeChat article and repost it as a tweet thread"
