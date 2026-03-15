---
name: pinboard-manager
description: "Pinboard bookmark management — tag audit, dead link detection, and timeliness check. Triggers on \"pinboard\", \"bookmark\", \"tag audit\", \"dead link\", \"timeliness\". 触发场景：用户说「pinboard 整理 tag」「pinboard 检查死链」「pinboard 检查时效」「pinboard audit」「pinboard cleanup」「pinboard timeliness check」「pinboard 过时检测」「整理书签」时触发。"
---

# Pinboard Manager

Interactive Pinboard bookmark management with tag auditing, dead link detection, and content timeliness checking.

## Prerequisites

| Tool | Type | Required | How to get |
|------|------|----------|------------|
| Pinboard account | service | Yes | [pinboard.in](https://pinboard.in/) |
| `PINBOARD_AUTH_TOKEN` | env var | Yes | See [user-config.md](references/user-config.md) |
| `curl` | cli | Yes | Built-in on macOS/Linux |

> Do NOT proactively verify these tools on skill load. If a command fails due to a missing tool or token, directly guide the user through setup step by step.

## First-Time Setup

If `references/tag-convention.md` does not exist in the skill directory, run the
**Tag Convention Generator** before any other mode:

1. Fetch all bookmarks via the Pinboard API
2. Analyze existing tags: frequency, patterns, languages, potential typos
3. Present findings to the user:
   - Top 30 tags by frequency
   - Tags that look like typos or duplicates
   - Chinese/non-English tags that may need English equivalents
   - Tags with inconsistent casing or separators
4. Ask the user about their preferred categories (tech, life, culture, etc.)
5. Generate `references/tag-convention.md` based on the analysis and user input,
   following the structure in `references/tag-convention.example.md`
6. Confirm with the user before saving

> An example convention is provided at `references/tag-convention.example.md` for
> reference. Users should customize it to match their own bookmarking habits.

## Mode Selection

| User Intent | Mode | Section |
|-------------|------|---------|
| 「pinboard 整理 tag」「pinboard audit」「整理书签」 | Tag Audit | [Tag Audit Mode](#tag-audit-mode) |
| 「pinboard 检查死链」「pinboard check links」 | Dead Link Detection | [Dead Link Detection Mode](#dead-link-detection-mode) |
| 「pinboard 检查时效」「pinboard timeliness check」「pinboard 过时检测」 | Timeliness Check | [Timeliness Check Mode](#timeliness-check-mode) |

## API Helpers

All Pinboard API calls use these patterns:

### Fetch bookmarks

```bash
# Fetch all bookmarks
curl -s "https://api.pinboard.in/v1/posts/all?auth_token=$PINBOARD_AUTH_TOKEN&format=json"

# Fetch bookmarks with toread=yes
curl -s "https://api.pinboard.in/v1/posts/all?auth_token=$PINBOARD_AUTH_TOKEN&format=json&toread=yes"

# Fetch a specific bookmark by URL
curl -s "https://api.pinboard.in/v1/posts/get?auth_token=$PINBOARD_AUTH_TOKEN&format=json&url=ENCODED_URL"
```

### Update a bookmark (overwrite mode)

**CRITICAL**: Always pass ALL fields to avoid data loss. The `/posts/add` endpoint overwrites the entire bookmark.

```bash
curl -s "https://api.pinboard.in/v1/posts/add?auth_token=$PINBOARD_AUTH_TOKEN&format=json&url=ENCODED_URL&description=ENCODED_TITLE&extended=ENCODED_NOTES&tags=ENCODED_TAGS&shared=ORIGINAL_SHARED&toread=ORIGINAL_TOREAD&replace=yes"
```

Required fields to preserve:

- `url` — the bookmark URL (identifier)
- `description` — title
- `extended` — notes/description
- `tags` — space-separated tag list
- `shared` — `yes` or `no`
- `toread` — `yes` or `no`
- `replace` — MUST be `yes` to update existing

### Delete a bookmark

```bash
curl -s "https://api.pinboard.in/v1/posts/delete?auth_token=$PINBOARD_AUTH_TOKEN&format=json&url=ENCODED_URL"
```

### Rate limiting

Pinboard recommends at most 1 API call per 3 seconds. When making multiple calls (batch updates, link checks), add `sleep 3` between calls.

> **`posts/all` special limit**: This endpoint is rate-limited to **once every 5 minutes**. Cache the result in `/tmp/pinboard_all.json` and reuse it within the same session. If both Tag Audit and Dead Link Detection are run consecutively, reuse the cached file.

## Tag Audit Mode

### Overview

Audit all bookmarks against the tag convention, present issues in batches, and apply fixes with user confirmation.

Reference: [tag-convention.md](references/tag-convention.md) (generated during first-time setup)

### Step 1: Fetch all bookmarks

```bash
curl -s "https://api.pinboard.in/v1/posts/all?auth_token=$PINBOARD_AUTH_TOKEN&format=json" > /tmp/pinboard_all.json
```

Parse the JSON and count total bookmarks.

### Step 2: Analyze tag issues

Load the tag convention from [tag-convention.md](references/tag-convention.md) and scan all bookmarks. Categorize issues:

| Priority | Category | Example |
|----------|----------|---------|
| 1 | Typos | `ainme` → `anime` |
| 2 | Missing tags | Bookmarks with empty `tags` field |
| 3 | Case issues | `Health` → `health` |
| 4 | Chinese tags | `终极文档` → `reference` |
| 5 | Concept overlap | `ai` + `llm` on same bookmark |
| 6 | Deprecated tags | `TODO`, year tags like `2025` |

### Step 3: Present issues in batches

For each category (in priority order), present **5-10 bookmarks per batch**:

```text
### Batch 1: Typos (3 items)

1. 「Some anime article」
   URL: https://example.com/anime
   Current tags: `ainme game`
   Suggested: `anime game`

2. 「Editor comparison」
   URL: https://example.com/editor
   Current tags: `editer tool`
   Suggested: `programming tool`

3. ...

Options: [confirm all] [modify] [skip all] [skip individual]
```

### Step 4: Apply confirmed changes

For each confirmed change, update via `/posts/add` with `replace=yes`:

```bash
# URL-encode all parameters
curl -s "https://api.pinboard.in/v1/posts/add?auth_token=$PINBOARD_AUTH_TOKEN&format=json&url=ENCODED_URL&description=ENCODED_TITLE&extended=ENCODED_NOTES&tags=NEW_TAGS&shared=ORIGINAL_SHARED&toread=ORIGINAL_TOREAD&replace=yes"
sleep 3  # Rate limit
```

**IMPORTANT**: Preserve ALL original fields. Only modify `tags`.

### Step 5: Summary

After all batches are processed, show:

```text
Tag Audit Complete
- Bookmarks scanned: 200
- Issues found: 45
- Fixed: 38
- Skipped: 7
```

## Dead Link Detection Mode

### Overview

Check all bookmarks for broken URLs and report results for user action.

### Step 1: Fetch all bookmarks

Same as Tag Audit Step 1.

### Step 2: Check links in batches

Process 10 URLs per batch using HTTP HEAD requests:

```bash
# HEAD request with 10 second timeout
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L --max-redirs 5 -I -m 10 "URL")
```

Classification (based on final status after following redirects):

| Status | Meaning | Action |
|--------|---------|--------|
| 2xx | Working | No action |
| 403, 405 | HEAD rejected | Retry with GET |
| 4xx (other) | Broken | Report to user |
| 5xx | Server error | Report to user |
| 000 | Timeout/unreachable | Report to user |

For HEAD-rejected URLs, retry once with GET:

```bash
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L --max-redirs 5 -m 10 "URL")
```

### Step 3: Present results

Show broken links grouped by status:

```text
### Dead Links Found (12 items)

#### 404 Not Found (5)
1. 「Article title」 — https://example.com/gone
   Tags: programming
   → [delete] [keep] [skip]

2. ...

#### Timeout (4)
1. 「Slow site article」 — https://slow-site.com/article
   Tags: reference
   → [delete] [keep] [skip]

#### Server Error 5xx (3)
1. ...
```

### Step 4: Apply user decisions

For deletions:

```bash
curl -s "https://api.pinboard.in/v1/posts/delete?auth_token=$PINBOARD_AUTH_TOKEN&format=json&url=ENCODED_URL"
sleep 3  # Rate limit
```

### Step 5: Summary

```text
Dead Link Check Complete
- Links checked: 200
- Working: 188
- Broken: 8 (deleted: 5, kept: 3)
- Timeout: 4 (deleted: 1, kept: 3)
```

## Timeliness Check Mode

### Overview

Identify tech bookmarks whose content may be outdated using a two-stage approach: heuristic pre-filtering to narrow candidates, then AI content analysis via Jina Reader + current Claude session.

This mode does NOT auto-delete anything — all actions require user confirmation.

### Step 1: Fetch all bookmarks

Reuse the cached file if available from a previous mode in this session:

```bash
# Only fetch if cache doesn't exist or is stale
if [ ! -f /tmp/pinboard_all.json ]; then
  curl -s "https://api.pinboard.in/v1/posts/all?auth_token=$PINBOARD_AUTH_TOKEN&format=json" > /tmp/pinboard_all.json
fi
```

Parse the JSON and count total bookmarks.

### Step 2: Heuristic pre-filtering

Apply three filters in order to identify candidates for AI analysis:

#### Filter 1: Tag filter (tech only)

Include bookmarks with ANY of these tech-related tags:

`llm`, `claude`, `programming`, `python`, `javascript`, `typescript`, `web`, `devops`, `cloudflare`, `shell`, `github`, `database`, `security`, `home_assistant`, `iot`, `zigbee`

Exclude bookmarks with ANY of these meta tags (even if they have tech tags):

`evergreen`, `reference`, `collection`

#### Filter 2: Age filter

Include bookmarks saved more than **2 years ago** (based on the Pinboard `time` field).

#### Filter 3: Version detection

Include bookmarks whose **title** or **URL** contains version number patterns, regardless of age:

- Named versions: `React 16`, `Python 3.8`, `Vue 2`, `Angular 1.x`
- Version prefixes: `v2.0`, `v1.x`, `v3`
- ECMAScript versions: `ES5`, `ES6`, `ES2015`
- Framework-specific: `Rails 4`, `Django 1.x`, `Node 12`

#### Candidate condition

A bookmark is a candidate if it matches: **Filter 1 AND (Filter 2 OR Filter 3)**

Report the number of candidates found before proceeding:

```text
Heuristic pre-filtering complete:
- Total bookmarks: 376
- Tech bookmarks (after tag filter): 120
- Candidates (age > 2y OR version detected): 35
```

### Step 3: Content fetching via Jina Reader

For each candidate, fetch content using Jina Reader:

```bash
CONTENT=$(curl -s "https://r.jina.ai/BOOKMARK_URL" | head -c 5000)
sleep 2  # Rate limiting between requests
```

**Error handling**:

- If Jina Reader returns an error or empty response → mark as "unable to fetch", skip this bookmark
- If the URL is unreachable → skip and continue with next candidate
- Always wait 2 seconds between Jina Reader requests

### Step 4: AI timeliness analysis

For each successfully fetched candidate, analyze the content and determine timeliness. Output for each:

| Field | Values | Description |
|-------|--------|-------------|
| Status | `outdated` / `possibly_outdated` / `still_valid` | Timeliness assessment |
| Reason | Free text | One sentence explaining the assessment |
| Suggestion | `delete` / `mark_evergreen` / `keep` | Recommended action |

**Assessment guidelines**:

- **`outdated`**: Content discusses deprecated APIs, removed features, old framework versions with no relevance today, or superseded best practices. Suggest `delete`.
- **`possibly_outdated`**: Content references specific versions but core concepts may still apply, or the technology has evolved significantly. Suggest `keep`.
- **`still_valid`**: Content discusses timeless concepts, patterns, or approaches that remain current. Suggest `mark_evergreen`.

### Step 5: Batch presentation

Present results in batches of **5 candidates**:

```text
### Batch 1: Timeliness Analysis (5 items)

1. 「Introduction to React 16 Lifecycle Methods」
   URL: https://example.com/react-16-lifecycle
   Tags: javascript web
   Status: 🔴 outdated
   Reason: Article covers React 16 class component lifecycle methods; React 18+ recommends functional components with hooks
   Suggestion: delete

2. 「Understanding Python Type Hints」
   URL: https://example.com/python-types
   Tags: python programming
   Status: 🟢 still_valid
   Reason: Python type hints syntax and concepts remain current in Python 3.12+
   Suggestion: mark_evergreen

3. 「Setting up Webpack 3 for React」
   URL: https://example.com/webpack-3
   Tags: javascript web
   Status: 🔴 outdated
   Reason: Webpack 3 is deprecated; most projects use Webpack 5 or Vite
   Suggestion: delete

4. 「Git Branching Strategies」
   URL: https://example.com/git-branching
   Tags: programming github
   Status: 🟢 still_valid
   Reason: Git branching concepts are fundamental and haven't changed
   Suggestion: mark_evergreen

5. 「Django 1.11 Migration Guide」
   URL: https://example.com/django-1.11
   Tags: python web
   Status: 🟡 possibly_outdated
   Reason: Django 1.11 is EOL but some migration concepts may apply to newer versions
   Suggestion: keep

Options: [confirm suggestions] [modify individual] [skip all]
```

Use the **AskUserQuestion tool** to let the user choose their action for each batch.

### Step 6: Apply user actions

For each bookmark based on user decision:

**Delete** (for `outdated` bookmarks user confirms):

```bash
curl -s "https://api.pinboard.in/v1/posts/delete?auth_token=$PINBOARD_AUTH_TOKEN&format=json&url=ENCODED_URL"
sleep 3  # Rate limit
```

**Mark evergreen** (for `still_valid` bookmarks user confirms):

```bash
# Add 'evergreen' to existing tags, preserve ALL other fields
curl -s "https://api.pinboard.in/v1/posts/add?auth_token=$PINBOARD_AUTH_TOKEN&format=json&url=ENCODED_URL&description=ENCODED_TITLE&extended=ENCODED_NOTES&tags=EXISTING_TAGS%20evergreen&shared=ORIGINAL_SHARED&toread=ORIGINAL_TOREAD&replace=yes"
sleep 3  # Rate limit
```

**CRITICAL**: When adding `evergreen` tag, preserve ALL original fields (description, extended, shared, toread). Only append `evergreen` to the tags list.

**Skip**: No API call, move to next item.

### Step 7: Summary

After all batches are processed:

```text
Timeliness Check Complete
- Total bookmarks: 376
- Candidates (after heuristic filter): 35
- Unable to fetch: 3
- Analyzed: 32
  - Outdated: 12 (deleted: 10, kept: 2)
  - Possibly outdated: 8 (all kept)
  - Still valid: 12 (marked evergreen: 10, kept: 2)
- Skipped: 5
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `PINBOARD_AUTH_TOKEN not set` | Env var missing | See [user-config.md](references/user-config.md) |
| `403 Forbidden` on API calls | Invalid or expired token | Re-check token at Pinboard settings |
| `429 Too Many Requests` | Rate limit exceeded | Increase sleep between calls; `posts/all` is limited to once per 5 min |
| Partial update lost data | Missing fields in `/posts/add` | Always pass ALL original fields with `replace=yes` |
| Jina Reader empty response | Site blocks Jina Reader or URL is broken | Skip this bookmark, mark as "unable to fetch" |
| Jina Reader timeout | Slow site or network issue | Skip and continue with next candidate |
