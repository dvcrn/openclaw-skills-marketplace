# Agent Injection Rules — Local Free Web Search v2.0

## When to use this skill

Activate this skill when:
- The user asks about current events, latest news, recent releases, or real-time information
- The built-in `web_search` tool is unavailable or not configured
- The user explicitly asks to search the web
- The task requires verifying facts with up-to-date sources

## Step 1 — Search

Run the search script with the appropriate intent:

```bash
python3 ~/.openclaw/workspace/skills/local-web-search/scripts/search_local_web.py \
  --query "<user query>" \
  --intent <factual|news|research|tutorial|comparison|privacy|general> \
  --limit 5
```

Choose intent based on query type:
- Current events / news → `--intent news --freshness day`
- Technical docs / facts → `--intent factual`
- Academic / GitHub → `--intent research`
- How-to / examples → `--intent tutorial`
- A vs B questions → `--intent comparison`
- Sensitive queries → `--intent privacy`

## Step 2 — Browse top results

For each result with Score > 50 or marked `[cross-validated]`:

```bash
python3 ~/.openclaw/workspace/skills/local-web-search/scripts/browse_page.py \
  --url "<result URL>" \
  --max-words 600
```

## Step 3 — Answer rules

- **HIGH confidence** → safe to answer from this page
- **MEDIUM confidence** → answer with caveat, suggest checking another source
- **LOW confidence** → do NOT use this page; try next URL
- **NEVER** fabricate content when all sources fail — tell the user the search returned no usable results
- **ALWAYS** cite the URL and published date when answering factual questions
- **PREFER** `[cross-validated]` results over single-engine results for factual claims

## Fallback behaviour

If local SearXNG is unavailable, both scripts automatically fall back to `searx.be`.
If all sources fail, output:

```
Search unavailable. To start local SearXNG:
cd "$(cat ~/.openclaw/workspace/skills/local-web-search/.project_root)" && ./start_local_search.sh
```
