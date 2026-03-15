---
name: agent-mineru
description: "MinerU document parsing CLI with layout.json post-processing and S3 integration. Parse PDF/Word/PPT/images to structured Markdown with formula, table, and code extraction."
---

# Document Parsing with agent-mineru

## Installation

```bash
npm install -g agent-mineru
```

## Authentication

```bash
export MINERU_TOKEN="your_api_token"
```

Get your token at: https://mineru.net/apiManage/docs

## Quick start

```bash
agent-mineru parse https://arxiv.org/pdf/2410.17247   # Parse PDF
agent-mineru extract ./task_id/layout.json             # Extract formulas/tables
agent-mineru convert ./task_id/layout.json -o custom.md # Custom Markdown
```

## Important: HTML vs PDF output difference

- **PDF/Doc/PPT/Image** → ZIP with `layout.json` + `full.md` + `images/` → supports fine-grained post-processing
- **HTML** → only `full.md` → no layout.json, no post-processing available

## Commands

### Parse (single file)

```bash
agent-mineru parse <url|file>              # Auto-detect type, parse & download
agent-mineru parse ./paper.pdf             # Local file
agent-mineru parse https://example.com/doc.pdf --model pipeline
agent-mineru parse https://example.com/page.html  # Auto-selects MinerU-HTML
agent-mineru parse ./paper.pdf --no-wait   # Submit only, don't wait
agent-mineru parse ./paper.pdf --json      # JSON output for piping
agent-mineru parse ./paper.pdf --s3        # Auto-upload to S3 after download
```

### Parse batch (multiple URLs)

```bash
agent-mineru parse-batch url1.pdf url2.pdf
agent-mineru parse-batch --file urls.txt         # URLs from file
agent-mineru parse-batch --file urls.txt --model vlm
```

### Upload (local files)

```bash
agent-mineru upload ./paper1.pdf ./paper2.pdf
agent-mineru upload ./docs/*.pdf --model pipeline
```

### Check status

```bash
agent-mineru status <task_id>              # Single task status
agent-mineru status <task_id> --json       # JSON output
agent-mineru status-batch <batch_id>       # Batch task status
```

### Extract elements (PDF only, needs layout.json)

```bash
agent-mineru extract <json_file>                           # All elements as JSON
agent-mineru extract layout.json --types formula           # Formulas only
agent-mineru extract layout.json --types table             # Tables only
agent-mineru extract layout.json --types formula,table     # Both
agent-mineru extract layout.json --formula-filter interline # Display formulas only
agent-mineru extract layout.json --pages 1-5               # Page range (1-based)
agent-mineru extract layout.json -f markdown               # Markdown output
agent-mineru extract layout.json -f plain                  # Plain text output
agent-mineru extract layout.json -o result.json            # Output to file
```

### Convert to Markdown (PDF only, needs layout.json)

```bash
agent-mineru convert <json_file>                  # Custom Markdown to stdout
agent-mineru convert layout.json -o custom.md     # Output to file
agent-mineru convert layout.json --no-discard     # Keep headers/footers/page numbers
```

### S3 storage (optional)

```bash
agent-mineru s3 upload <task_id>           # Upload task results to S3
agent-mineru s3 upload ./output/ --prefix papers/
agent-mineru s3 ls                         # List all objects
agent-mineru s3 ls papers/2025/            # List with prefix
agent-mineru s3 get <key> [output]         # Download object
agent-mineru s3 rm <key>                   # Delete object
agent-mineru s3 rm <prefix> -r             # Delete recursively
```

## Parse options

```bash
--model <model>           # vlm | pipeline | MinerU-HTML (default: auto-detect)
--ocr                     # Enable OCR (pipeline only)
--formula / --no-formula  # Formula recognition (default: on)
--table / --no-table      # Table recognition (default: on)
--language <lang>         # Document language (default: ch)
--pages <range>           # Page range (e.g. "2,4-6")
--extra-formats <fmts>    # Extra export: docx,html,latex
--wait / --no-wait        # Wait for completion (default: on)
--poll-interval <ms>      # Poll interval (default: 3000)
--timeout <ms>            # Max wait time (default: 600000)
-o, --output <dir>        # Output directory
--no-download             # Submit only, don't download
--s3                      # Auto-upload to S3 after download
--json                    # JSON output for piping
```

## File type auto-detection

The CLI uses a 3-layer detection to select the correct model:
1. URL path extension check (fastest, no network)
2. HEAD request Content-Type check (covers 99% cases)
3. Magic bytes fallback (PDF starts with `%PDF`)

## S3 configuration (optional)

```bash
export MINERU_S3_ENDPOINT="s3.amazonaws.com"
export MINERU_S3_BUCKET="my-bucket"
export MINERU_S3_ACCESS_KEY="your_key"
export MINERU_S3_SECRET_KEY="your_secret"
export MINERU_S3_REGION="us-east-1"       # optional, default: us-east-1
export MINERU_S3_USE_SSL="true"            # optional, default: true
```

Compatible with AWS S3, MinIO, Alibaba Cloud OSS, and other S3-compatible storage.

## Example: Paper parsing workflow

```bash
# 1. Parse paper
agent-mineru parse https://arxiv.org/pdf/2410.17247 -o ./paper/

# 2. Extract all formulas
agent-mineru extract ./paper/layout.json --types formula -f markdown -o formulas.md

# 3. Extract tables
agent-mineru extract ./paper/layout.json --types table -o tables.json

# 4. Generate custom Markdown (with headers/footers)
agent-mineru convert ./paper/layout.json --no-discard -o full-with-headers.md

# 5. Upload to S3
agent-mineru s3 upload ./paper/
```

## Example: Batch processing

```bash
# Create URL list
echo "https://example.com/paper1.pdf" > urls.txt
echo "https://example.com/paper2.pdf" >> urls.txt

# Batch parse with auto S3 upload
agent-mineru parse-batch --file urls.txt --s3
```

## Limitations

- Single file: max 200MB, max 600 pages
- Batch: max 200 files per request
- Foreign URLs (GitHub, AWS) may timeout from China servers
- HTML parsing produces only Markdown, no structured JSON

## Troubleshooting

- If MINERU_TOKEN is not set, the CLI will show setup instructions
- If S3 commands fail, check that all S3 environment variables are set
- For HTML files, do not use `extract` or `convert` commands (no layout.json available)
- Use `--json` flag for machine-readable output in scripts

## Notes

- Model priority: vlm (highest accuracy) > pipeline (faster)
- The `extract` and `convert` commands work on layout.json from PDF/Doc/PPT/Image results only
- Post-processing supports both Pipeline and VLM model outputs with automatic detection
