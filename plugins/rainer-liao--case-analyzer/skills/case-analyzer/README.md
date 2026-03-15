# Case Analyzer

End-to-end workflow for analyzing Pexo video creation sessions: fetch Langfuse traces → identify issues → generate QA dashboard → upload to admin backend.

## Features

- **Trace Fetching** — Pull all traces for a conversation from Langfuse
- **Asset Extraction** — Extract media assets (images, videos, audio) with prompts and model info
- **QA Dashboard** — Self-contained HTML dashboard with embedded media, problem analysis, and skill modification tracking
- **Auto Upload** — Package and upload to admin.pexo.ai strategy-optimizer
- **MCP Server** — Works with any MCP-compatible agent (Cursor, Claude Desktop, etc.)

## Install

### Option 1: ClaWHub

```bash
clawhub install case-analyzer
```

### Option 2: Git Clone

```bash
git clone https://github.com/pexo-ai/case-analyzer.git
cd case-analyzer
bash install.sh
```

### Option 3: Manual Copy

Copy this directory to `~/.cursor/skills/case-analyzer/` and run `bash install.sh`.

## Prerequisites

| Dependency | Required | Purpose |
|-----------|----------|---------|
| `uv` | Yes | Python version & dependency management |
| `python3` | Yes | Scripts execution |
| `curl` | Yes | Media download & API calls |
| `zip` | Yes | Dashboard packaging |
| `ffmpeg` | No | Video compression for large packages |

### Environment Variables

```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."
export LANGFUSE_HOST="https://cloud.langfuse.com"
export PEXO_ADMIN_TOKEN="eyJhbG..."  # from admin.pexo.ai DevTools
```

## Usage

### As Cursor Skill

Say "分析 case 31574785111" in Cursor — the skill triggers automatically.

### As MCP Server

Add to your MCP client config (`~/.cursor/mcp.json`, Claude Desktop, etc.):

```json
{
  "case-analyzer": {
    "command": "uv",
    "args": ["run", "--script", "~/.cursor/skills/case-analyzer/mcp-server.py"]
  }
}
```

**Exposed tools:**

| Tool | Args | Description |
|------|------|-------------|
| `fetch_traces` | `conversation_id` | Fetch Langfuse traces for a case |
| `extract_assets` | `case_dir` | Extract media metadata + download files |
| `upload_package` | `conversation_id`, `dashboard_dir` | Package & upload to admin backend |
| `list_cases` | — | List all analyzed cases with status |

### CLI Scripts

```bash
# Fetch traces
python3 ~/.cursor/skills/case-analyzer/scripts/fetch-case.py \
  --conversation-id 31574785111 --output-dir analysis/langfuse-data

# Extract assets
python3 ~/.cursor/skills/case-analyzer/scripts/extract-assets.py \
  --case-dir analysis/langfuse-data/cases/31574785111

# Upload
bash ~/.cursor/skills/case-analyzer/scripts/upload-package.sh \
  31574785111 analysis/langfuse-data/cases/31574785111
```

## Workflow

```
Phase A (auto)     Phase B (review)     Phase C (auto)
┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
│ Fetch traces │──→│ User reviews │──→│ Apply skill mods  │
│ Analyze      │   │ proposed     │   │ Generate dashboard│
│ Extract media│   │ skill changes│   │ Upload to admin   │
└──────────────┘   └──────────────┘   └──────────────────┘
```

## License

MIT
