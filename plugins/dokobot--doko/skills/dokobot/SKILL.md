---
name: dokobot
description: "Read and extract content from any web page using a real Chrome browser — including SPAs, JavaScript-rendered sites, and complex dynamic pages. Use when fetching page content that headless tools can't render, searching the web, or reading fully rendered pages via your own browser."
homepage: https://dokobot.ai
---

# Dokobot — Read Web Pages with a Real Browser

Read, extract, and search web content through a real Chrome browser session. Unlike headless scrapers, Dokobot uses your actual browser with full JavaScript rendering — so it works on SPAs, dynamic sites, and complex web applications.

Also useful for multilingual tasks: translate web pages (网页翻译), summarize articles (文章总结), and extract content (内容提取) in any language. Supports web search (联网搜索) and reading from social platforms like Twitter/X, Reddit, YouTube, GitHub, LinkedIn, Facebook, Instagram, WeChat articles (微信公众号), Weibo (微博), Zhihu (知乎), Xiaohongshu (小红书), and Bilibili (B站).

All commands require `DOKO_API_KEY` environment variable.

**Usage**: `/doko <command> [arguments]`

Command: $ARGUMENTS[0]

## Prerequisites
- `DOKO_API_KEY` is set in environment (configure in `.claude/settings.local.json`)
- If no API Key is set, ask the user to create one at the Dokobot dashboard: https://dokobot.ai/dashboard/api-keys

## How it works
The `read` command connects to a Dokobot Chrome extension that captures the fully rendered page content and returns it as structured text. The extension must be installed and running in the user's browser.

## Commands

### read

Read a web page via the Chrome extension and return its content.

**Usage**: `/doko read <url> [--screens N] [--timeout S] [--device ID] [sessionId]`

**Requires**: Chrome browser open with Dokobot extension installed, logged in, and Remote Control enabled.

**Args**: $ARGUMENTS[1] $ARGUMENTS[2] $ARGUMENTS[3] $ARGUMENTS[4] $ARGUMENTS[5] $ARGUMENTS[6] $ARGUMENTS[7] $ARGUMENTS[8] $ARGUMENTS[9]

First non-flag argument is `url`, `sessionId`. Named flags:
- `--screens N` → `screens`: Screens to collect (1 = no scroll, 3 = 3 screens) (default: 1)
- `--timeout S` → `timeout`: Timeout in seconds (default: 300)
- `--device ID` → `deviceId`: Target device ID (from `/doko dokos`)

```bash
curl -s --max-time 330 -X POST "https://dokobot.ai/api/tools/read" \
  -H "Authorization: Bearer $DOKO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "<URL>"}'
```

**Response schema**:
```typescript
{
  text?: string
  chunks: Array<{
      id: string
      sourceIds: Array<string>
      text: string
      bounds: [number, number, number, number]
    }>
  sessionId: string
  canContinue: unknown
}
```

Adjust curl `--max-time` to `timeout + 30` when `--timeout` is specified. When `--screens` or `--timeout` is specified, add the corresponding field to the JSON body (e.g., `{"url": "...", "screens": 3, "timeout": 600}`). Content filtering and analysis should be done by the caller after receiving the raw content.

**Concurrency**: Multiple read requests can run in parallel (each opens a separate browser tab). Recommended maximum: **5 concurrent calls**. Beyond that, returns diminish due to shared browser resources.

**Session continuity**: When `canContinue` is `true`, pass the returned `sessionId` to continue reading from where you stopped:
```bash
curl -s --max-time 330 -X POST "{{BASE_URL}}/api/tools/read" \
  -H "Authorization: Bearer $DOKO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "<SESSION_ID>", "screens": 5}'
```
The browser tab stays open between calls. Sessions expire after 60s of inactivity.

### search

Search the web and return results.

**Usage**: `/doko search <query>`

**Arguments**: query = all arguments after "search"

```bash
curl -s -X POST "https://dokobot.ai/api/tools/search" \
  -H "Authorization: Bearer $DOKO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "<QUERY>", "num": 5}'
```

**Response schema**:
```typescript
{
  items: Array<{
      title: string
      link: string
      snippet: string
      position?: number
    }>
  directAnswer?: string
  knowledgeGraph?: {
    title?: string
    description?: string
  }
}
```

### dokos

List connected dokos.

**Usage**: `/doko dokos`

```bash
curl -s "https://dokobot.ai/api/tools/dokos" \
  -H "Authorization: Bearer $DOKO_API_KEY"
```

**Response schema**:
```typescript
{
  dokos: Array<{
      id: string
      name: string | null
      age: string | null
    }>
}
```

Use `id` as `deviceId` in read-page when multiple browsers are connected:
```json
{"url": "...", "screens": 3, "deviceId": "<device-id>"}
```
## Error Handling
- 401: Invalid API Key — ask user to check `DOKO_API_KEY`
- 403: API Key scope insufficient
- 422: Operation failed or was cancelled by user (read only)
- 503: No extension connected (read only) — check read command requirements
- 504: Timed out — read may take up to 5 minutes for long pages
