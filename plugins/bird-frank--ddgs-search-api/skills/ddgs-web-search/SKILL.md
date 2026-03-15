---
name: ddgs-web-search
description: "Use when needing to search the web in AI coding tools or OpenClaw. Uses DuckDuckGo API without API key."
---

# DuckDuckGo Web Search Skill

An Agent Skill for searching web content via DuckDuckGo.

## Overview

This Skill provides a command-line tool for web search using the `ddgs` Python package. Suitable for:

- Real-time web information needs in AI coding tools
- Fetching search results in OpenClaw workflows

## Core Features

- **Web Search**: General web search
- **News Search**: Dedicated news content search
- **Multiple Output Formats**: Text or JSON format
- **Flexible Configuration**: Region, time limits, and safe search level

## Installation

This project uses `uv` as the Python package manager.

### Option 1: Run with uv (Recommended)

```bash
# Run the script directly (uv will auto-install dependencies)
uv run scripts/ddgs_search.py "Python programming"

# Or navigate to the directory first
cd skills/ddgs-search
uv run scripts/ddgs_search.py "machine learning"
```

### Option 2: Manual Dependency Installation

```bash
# Install dependencies using uv
uv pip install ddgs

# Or use pip
pip install ddgs
```

## Quick Start

### Basic Usage

```bash
# Run with uv (recommended)
uv run scripts/ddgs_search.py "Python programming"

# Limit the number of results
uv run scripts/ddgs_search.py "machine learning" --max-results 5

# Search news
uv run scripts/ddgs_search.py "tech news" --news

# JSON output (for programmatic parsing)
uv run scripts/ddgs_search.py "API documentation" --json

# Time limit (today)
uv run scripts/ddgs_search.py "breaking news" --timelimit d
```

## Complete Parameter Reference

| Parameter | Short | Description | Default |
| --------- | ----- | ----------- | ------- |
| `query` | - | Search keywords | Required |
| `--max-results` | `-n` | Maximum number of results | 10 |
| `--region` | `-r` | Region code | `wt-wt` |
| `--safesearch` | `-s` | Safe search (on/moderate/off) | `moderate` |
| `--timelimit` | `-t` | Time limit (d/w/m/y) | - |
| `--backend` | `-b` | Search backend (auto/html/lite) | `auto` |
| `--news` | - | Search news | - |
| `--json` | `-j` | JSON format output | - |
| `--verbose` | `-v` | Show detailed information | - |

### Region Code Examples

- `wt-wt` - Worldwide (default)
- `us-en` - United States English
- `cn-zh` - China Chinese
- `jp-jp` - Japan
- `uk-en` - United Kingdom

### Time Limits

- `d` - Past day
- `w` - Past week
- `m` - Past month
- `y` - Past year

## Usage in OpenClaw

In OpenClaw workflows, you can invoke it via the `bash` tool:

```yaml
# Example workflow step
- name: search_web
  tool: bash
  command: cd skills/ddgs-search && uv run scripts/ddgs_search.py "{{ query }}" --json
```

Or using the Python tool:

```python
# Assuming the current directory is the project root
import subprocess
import json

result = subprocess.run(
    ["uv", "run", "skills/ddgs-search/scripts/ddgs_search.py", "Python tips", "--json"],
    capture_output=True,
    text=True
)
data = json.loads(result.stdout)
```

## Return Result Format

### Web Search Results

```json
[
  {
    "title": "Result Title",
    "href": "https://example.com/page",
    "body": "Page snippet/description..."
  }
]
```

### News Search Results

```json
[
  {
    "title": "News Headline",
    "href": "https://news.example.com/article",
    "body": "Article summary...",
    "date": "2024-01-15",
    "source": "News Source Name"
  }
]
```

## Usage Examples

### Example 1: Search Technical Documentation

```bash
uv run scripts/ddgs_search.py "FastAPI documentation" -n 5
```

### Example 2: Get Latest News

```bash
uv run scripts/ddgs_search.py "artificial intelligence" --news -t d -n 3
```

### Example 3: Chinese Search

```bash
uv run scripts/ddgs_search.py "机器学习教程" -r cn-zh -n 8
```

### Example 4: JSON Output Processing

```bash
uv run scripts/ddgs_search.py "python tips" --json | jq '.[0].href'
```

## FAQ

### uv Not Installed

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### ImportError: No module named 'ddgs'

```bash
# Install using uv
uv pip install ddgs

# Or run in the script directory (uv will auto-handle)
cd skills/ddgs-search
uv run scripts/ddgs_search.py "query"
```

### Empty Search Results

- Check network connection
- Try changing the `--backend` parameter (auto/html/lite)
- Some regions may require a proxy

### Rate Limiting

DuckDuckGo has implicit rate limiting. If frequent requests fail:

- Reduce request frequency
- Add delays between requests
- Use a different backend

## Dependencies

- Python 3.9+
- `uv` (package manager)
- `ddgs` >= 8.0.0
