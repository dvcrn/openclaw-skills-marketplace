---
name: wechat-article-to-markdown
description: "Fetch WeChat Official Account articles and convert to Markdown with Camoufox anti-detection browser"
---

# WeChat Article to Markdown

Fetch a WeChat Official Account article and convert it to a clean Markdown file.

## When to use

Use this skill when you need to save WeChat articles as Markdown for:
- Personal archive
- AI summarization input
- Knowledge base ingestion

## Prerequisites

- Python 3.8+
- `uv` installed (recommended), or install from PyPI:

```bash
pipx install wechat-article-to-markdown
```

## Install into Claude Code user directory

```bash
mkdir -p ~/.claude/skills/wechat-article-to-markdown
curl -o ~/.claude/skills/wechat-article-to-markdown/SKILL.md \
  https://raw.githubusercontent.com/jackwener/wechat-article-to-markdown/main/SKILL.md
```

## Usage

```bash
wechat-article-to-markdown "<WECHAT_ARTICLE_URL>"
```

If running from source repository:

```bash
cd /Users/jakevin/kabi-reader/wechat-article-to-markdown
uv run wechat-article-to-markdown "<WECHAT_ARTICLE_URL>"
```

Input URL format:
- `https://mp.weixin.qq.com/s/...`

Output files:
- `<current-working-directory>/output/<article-title>/<article-title>.md`
- `<current-working-directory>/output/<article-title>/images/*`

## Features

1. Anti-detection fetch with Camoufox
2. Metadata extraction (title, account name, publish time, source URL)
3. Image localization to local files
4. WeChat code-snippet extraction and fenced code block output
5. HTML to Markdown conversion via markdownify
6. Concurrent image downloading

## Limitations

- Some code snippets are image/SVG rendered and cannot be extracted as source code
- Public `mp.weixin.qq.com` URL is required
