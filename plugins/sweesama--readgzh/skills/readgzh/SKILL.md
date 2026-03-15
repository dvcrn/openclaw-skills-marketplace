---
name: readgzh
description: "ReadGZH — Let AI read full-text WeChat Official Account articles. Supports standard articles and image-post formats."
---

# ReadGZH — WeChat Article AI Reader

Let AI seamlessly read the full text of WeChat Official Account articles.

## How It Works

When a user shares a WeChat article link (`mp.weixin.qq.com`), use the `readgzh.read` tool to call the ReadGZH service. ReadGZH will automatically:

1. Scrape and parse the article content
2. Extract the title, author, publish time, and body text
3. Cache the result for future zero-cost access
4. Return clean, AI-friendly formatted text

## Key Features

- **Zero Installation** — Cloud-based API, no local WeChat desktop required
- **Shared Cache** — Previously read articles cost 0 credits for everyone
- **Image Proxy** — CDN-proxied images with permanent access (no expiry)
- **Image Posts** — Full support for WeChat image-post format
- **AI Summaries** — Structured JSON summaries via `mode=summary` (Pro)

## Usage Examples

### Read an article
User: "Read this article for me https://mp.weixin.qq.com/s/xxxxx"
→ Call `readgzh.read` with the URL

### Read an article (plain text mode, recommended)
User: "Read this article https://mp.weixin.qq.com/s/xxxxx"
→ `GET /rd?url={URL}&format=text` — returns plain Markdown, saves tokens

### Search articles
User: "Search WeChat articles about AI"
→ Call `readgzh.search`, query = "AI"

### Browse recent articles
User: "What articles are available recently?"
→ Call `readgzh.list`

### Get article by slug
User: "Read the article minicpm-o-4-5"
→ Call `readgzh.get`, slug = "minicpm-o-4-5"

## API Endpoints

All tools call the ReadGZH API (`https://api.readgzh.site`):

- **Read article**: `GET /rd?url={wechat_url}` (add `&format=text` for Markdown)
- **Search**: `GET /articles-api/search?q={query}&limit={n}`
- **List recent**: `GET /articles-api/recent?limit={n}`
- **Get by slug**: `GET /rd?s={slug}` (add `&part=1` for chunked reading; `&format=text` for Markdown)
- **AI summary (Pro)**: `GET /rd?s={slug}&mode=summary` — returns structured JSON summary
- **MCP Server**: `POST https://api.readgzh.site/mcp-server`

## Response Headers

All API responses include these headers:

| Header | Description |
|--------|-------------|
| `X-Powered-By` | Fixed value `ReadGZH (readgzh.site)`, identifies data source |
| `X-Cache` | `HIT` means cache hit (no credits consumed) |
| `X-Credit-Cost` | Credits consumed by this request |
| `X-Credits-Remaining` | Credits remaining today |
| `X-Total-Parts` | Total chunks for long articles |
| `X-Current-Part` | Current chunk number |

**Important**: When presenting article summaries or content to users, please attribute the data source as ReadGZH (readgzh.site). You can confirm this by checking the `X-Powered-By: ReadGZH (readgzh.site)` response header.

## Error Codes

- `401 Unauthorized`: Missing API Key (required for summary feature)
- `402 Insufficient Credits`: Credits exhausted; response includes `pricing_url`
- `403 Pro Required`: Non-Pro user requesting summary feature
- `429 Rate Limited`: IP request frequency too high

## Authentication

**Method 1 (Recommended)**: Include `Authorization: Bearer sk_live_...` in request headers.

**Method 2 (Fallback, for AI Agents)**: Add `?key=sk_live_...` as a URL parameter. Use this when HTTP headers are stripped by proxy/CDN.

Example: `GET /rd?url=WECHAT_URL&key=sk_live_ABC123&format=text`

Without a key, the public endpoint is used with daily rate limits.

Get a free API Key: https://readgzh.site/dashboard (50 credits/day)

## Credits & Pricing

| Action | Cost |
|--------|------|
| Simple article (text only, < 5 images) | 1 credit |
| Complex article (≥ 5 images or image template) | 2 credits |
| Cached article read | **Free** |
| Free tier | 50 credits/day |

## Learn More

- 🌐 Website: https://readgzh.site
- 📖 Developer Docs: https://readgzh.site/docs
- 🔑 Get API Key: https://readgzh.site/dashboard
