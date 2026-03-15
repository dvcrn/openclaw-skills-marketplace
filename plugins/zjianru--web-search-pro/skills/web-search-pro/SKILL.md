---
name: web-search-pro
description: "Multi-engine web search with full parameter control. Supports Tavily, Exa, Serper, and SerpAPI\n with domain filtering, date ranges, deep search, news mode, and content extraction.\n Auto-selects the best engine based on query type and available API keys.\n 多引擎精细化搜索：支持域名过滤、日期范围、深度搜索、新闻模式、内容提取。\n 根据查询类型和可用 API Key 自动选择最优引擎。"
homepage: https://github.com/Zjianru/web-search-pro
---

# Web Search Pro

Multi-engine web search with full parameter control for AI agents.
A precision supplement to OpenClaw's built-in `web_search` (Brave/Perplexity), providing
domain filtering, deep search, news mode, date ranges, and content extraction
that the built-in search does not support.

多引擎精细化网络搜索，为 AI Agent 设计。
作为 OpenClaw 内置 `web_search`（Brave/Perplexity）的精细化补充，提供域名过滤、
深度搜索、新闻模式、日期范围、内容提取等内置搜索不支持的能力。
配置一个或多个 API Key，自动选择最优引擎。

## Engines / 引擎

| Engine | Strengths | Free Tier | API Key Env |
|--------|-----------|-----------|-------------|
| **Tavily** | AI-optimized, best answer quality, full filters, extract | 1000/month | `TAVILY_API_KEY` |
| **Exa** | Semantic/neural search, deep research | $10 credit | `EXA_API_KEY` |
| **Serper** | Real Google SERP, best news coverage | 100/month | `SERPER_API_KEY` |
| **SerpAPI** | Multi-engine (Google/Bing/Baidu/Yandex/DuckDuckGo) | 250/month | `SERPAPI_API_KEY` |

## Auto-Select Priority / 自动选择优先级

When `--engine` is not specified, the skill picks the best available engine:

| Query Type | Priority | Reason |
|------------|----------|--------|
| Default | Tavily > Exa > Serper > SerpAPI | Tavily has best AI answer + full filters |
| `--deep` | Tavily > Exa | Both have dedicated deep search modes |
| `--news` | Serper > Tavily | Google News has widest coverage |
| `--news --days` | Tavily only | `--days` is Tavily news-specific parameter |
| `--include-domains` | Tavily > Exa > Serper > SerpAPI | Tavily/Exa have native domain filters |
| `--search-engine baidu` | SerpAPI | Only SerpAPI supports Baidu/Yandex |

## Search / 搜索

```bash
# Basic search (auto-select engine)
node {baseDir}/scripts/search.mjs "query"

# Force specific engine
node {baseDir}/scripts/search.mjs "query" --engine tavily

# Domain filtering (only search specific sites)
node {baseDir}/scripts/search.mjs "query" --include-domains "github.com,stackoverflow.com"

# Exclude domains
node {baseDir}/scripts/search.mjs "query" --exclude-domains "pinterest.com,quora.com"

# Date range (absolute)
node {baseDir}/scripts/search.mjs "query" --from 2026-01-01 --to 2026-02-09

# Time range (relative)
node {baseDir}/scripts/search.mjs "query" --time-range week

# Deep/advanced search
node {baseDir}/scripts/search.mjs "query" --deep

# News search
node {baseDir}/scripts/search.mjs "query" --news --days 7

# Multi-engine: Baidu search
node {baseDir}/scripts/search.mjs "query" --engine serpapi --search-engine baidu

# More results
node {baseDir}/scripts/search.mjs "query" -n 10

# JSON output (for programmatic use)
node {baseDir}/scripts/search.mjs "query" --json
```

## Extract / 内容提取

Extract readable content from URLs (Tavily Extract or Exa livecrawl):

```bash
node {baseDir}/scripts/extract.mjs "https://example.com/article"
node {baseDir}/scripts/extract.mjs "url1" "url2" "url3"
node {baseDir}/scripts/extract.mjs "url" --engine exa
node {baseDir}/scripts/extract.mjs "url" --json
```

## All Options / 全部参数

| Option | Description | Engines |
|--------|-------------|---------|
| `--engine <name>` | Force engine: tavily\|exa\|serper\|serpapi | all |
| `-n <count>` | Number of results (default: 5) | all |
| `--deep` | Deep/advanced search mode | tavily, exa |
| `--news` | News search mode | tavily, serper, serpapi |
| `--days <n>` | Limit news to last N days | tavily |
| `--include-domains <d,...>` | Only search these domains | all (native: tavily, exa) |
| `--exclude-domains <d,...>` | Exclude these domains | all (native: tavily, exa) |
| `--time-range <range>` | day\|week\|month\|year | all |
| `--from <YYYY-MM-DD>` | Results after this date | all |
| `--to <YYYY-MM-DD>` | Results before this date | all |
| `--search-engine <name>` | SerpAPI sub-engine: google\|bing\|baidu\|yandex\|duckduckgo | serpapi |
| `--country <code>` | Country code (us, cn, de...) | serper, serpapi |
| `--lang <code>` | Language code (en, zh, de...) | serper, serpapi |
| `--json` | Raw JSON output | all |

## Setup / 配置

Add API keys to your environment (e.g., `~/.openclaw/.env`):

```bash
# Configure at least one (recommended: Tavily)
TAVILY_API_KEY=tvly-xxxxx        # https://tavily.com (1000 free/month)
EXA_API_KEY=exa-xxxxx            # https://exa.ai ($10 free credit)
SERPER_API_KEY=xxxxx             # https://serper.dev (100 free/month)
SERPAPI_API_KEY=xxxxx            # https://serpapi.com (250 free/month)
```

## Notes / 说明

- At least one API key must be configured
- Skill metadata only declares the `node` runtime, because this skill supports multiple alternative provider keys and OpenClaw metadata does not currently support an `env_any` / one-of env requirement
- Provider key validation happens at command execution time, based on the selected engine and flags
- Any one of these keys can enable part of the skill: `TAVILY_API_KEY`, `EXA_API_KEY`, `SERPER_API_KEY`, `SERPAPI_API_KEY`
- `--search-engine <name>` always uses SerpAPI and requires `SERPAPI_API_KEY`
- `--deep` only works on Tavily/Exa; if both keys are missing, command exits with an error
- `--news` only works on Tavily/Serper/SerpAPI; if none are available, command exits with an error
- `--days` only works with Tavily news mode
- `--news --days <n>` auto-selects Tavily; if Tavily key is missing, command exits with an error
- Domain filtering via `--include-domains`/`--exclude-domains` works natively on Tavily and Exa; on Serper/SerpAPI it's implemented via `site:` query operators
- `--deep` mode uses more API credits (Tavily: 2x, Exa: varies)
- Extract only works with Tavily and Exa
- Missing/invalid option values fail fast with explicit CLI error messages (no silent fallback, no runtime TypeError)
- All output is Markdown-formatted for AI agent consumption; use `--json` for programmatic access
