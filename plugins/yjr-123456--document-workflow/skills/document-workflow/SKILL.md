---
name: document-workflow
description: "One-click academic paper research workflow. Use when: (1) searching papers by topic, (2) downloading PDFs from arXiv or journals, (3) extracting text in chunks, (4) summarizing papers by structured schema. Supports Tavily (default, ~100% PDF availability) and Semantic Scholar (fallback, richer metadata)."
---

# Document Workflow

Execute academic paper research: **Search → Download → Extract → Summarize**

---

## Quick Start

### One-Click Workflow

```bash
python -m skills.document-workflow.scripts.research \
  --query "world model autonomous driving" \
  --output "./papers" \
  --max_papers 3 \
  --year_from 2024 \
  --download \
  --extract
```

**Output:**
```
papers/
├── search_results.json
├── paper_1/
│   ├── metadata.json
│   ├── pdf/paper.pdf
│   └── chunk_1_10.json
└── paper_2/
```

---

## Scripts

### search_papers

Search papers with Tavily priority:

```bash
python -m skills.document-workflow.scripts.search_papers \
  --query "world model" \
  --max_results 5 \
  --year_from 2024
```

**Parameters:**
- `--query` (required): Search keyword
- `--max_results`: Number of results (default: 5)
- `--year_from/--year_to`: Year filter
- `--use_semantic_scholar`: Force Semantic Scholar instead of Tavily

**Returns:** JSON array with `title`, `authors`, `pdf_url`, `citationCount`, `venue`

**Search behavior:**
- Default: Tavily searches arXiv (~100% PDF availability)
- Fallback: Semantic Scholar (richer metadata, lower PDF availability)

---

### download_paper

Download PDF from URL or search output:

```bash
# From search output (pipeline)
python -m skills.document-workflow.scripts.search_papers --query "..." --max_results 1 | \
  python -m skills.document-workflow.scripts.download_paper \
    --json_input - \
    --papers_dir "./papers" \
    --theme "World_Models"

# Direct URL
python -m skills.document-workflow.scripts.download_paper \
  --url "https://arxiv.org/pdf/2503.20523.pdf" \
  --theme "World_Models"
```

**Parameters:**
- `--json_input`: Accept search_papers JSON (`-` for stdin)
- `--url`: Direct PDF URL
- `--papers_dir`: Base directory (default: `C:\Users\Lenovo\Desktop\papers`)
- `--theme`: Theme subdirectory
- `--timeout`: Download timeout seconds (default: 120)

**Behavior:**
- Save PDF to `{papers_dir}/{theme}/{title}_{year}.pdf`
- Auto-save `metadata.json` alongside PDF

---

### pdf_reader

Extract text from PDF in chunks:

```bash
python -m skills.document-workflow.scripts.pdf_reader \
  "paper.pdf" \
  --start 1 --end 10 \
  --output "chunk1.json"
```

**Parameters:**
- `pdf_file`: PDF file path
- `--start/--end`: Page range (1-indexed, default: 1-10)
- `--output`: Output JSON file

**Why chunked extraction:**
- Large papers (50+ pages) exceed context window
- Extract 5-10 pages per chunk
- JSON output is reusable across sessions

---

### summarize

Summarize extracted chunks by schema:

```bash
python -m skills.document-workflow.scripts.summarize \
  --chunks "chunk_*.json" \
  --output "summary.json"
```

**Output schema:**

```json
{
  "paper_title": "Paper Title",
  "authors": ["Author List"],
  "source": "Journal/Conference",
  "task_definition": {
    "domain": "Research Domain",
    "task": "Specific Task",
    "problem_statement": "Problem Being Solved",
    "key_contributions": ["Contribution 1", "Contribution 2"]
  },
  "experiments": {
    "datasets": ["Datasets"],
    "baselines": ["Baseline Methods"],
    "metrics": [{"name": "Metric", "description": "Description"}],
    "results": [{"setting": "Setting", "metric": "Metric", "proposed_method": "Ours", "best_baseline": "Best Baseline"}],
    "key_findings": ["Key Findings"]
  }
}
```

---

### research

Execute complete workflow:

```bash
python -m skills.document-workflow.scripts.research \
  --query "world model" \
  --output "./papers" \
  --max_papers 3 \
  --year_from 2024 \
  --download \
  --extract
```

**Parameters:**
- `--query` (required): Search query
- `--output`: Output directory
- `--max_papers`: Max papers to process (default: 3)
- `--year_from`: Filter from year (default: 2024)
- `--download`: Download PDFs
- `--extract`: Extract text in chunks
- `--chunk_size`: Pages per chunk (default: 10)

---

## Configuration

### Environment Variables

```bash
export SEMANTIC_SCHOLAR_API_KEY="your-api-key"
```

If not set, uses built-in key.

### Default Paths

- Download directory: `C:\Users\Lenovo\Desktop\papers`
- Modify via `--papers_dir` parameter

---

## Best Practices

1. **Specify year**: Use `--year_from 2024` to avoid outdated papers
2. **Chunked extraction**: 5-10 pages per chunk avoids context overflow
3. **Reuse extracted JSON**: Extracted chunks are reusable across sessions
4. **Check citation count**: Use Semantic Scholar for high-citation papers
5. **Save metadata**: Download auto-saves `metadata.json`

---

## Troubleshooting

**Download failed:**
- Verify PDF URL is valid
- Increase `--timeout` for large files

**Extraction garbled:**
- Ensure UTF-8 encoding
- Windows: run `chcp 65001` first

**No search results:**
- Try broader keywords
- Expand year range

---

## References

- **Output schema**: See `references/output_schema.json` for detailed schema definition
- **Search comparison**: Tavily (~100% PDF) vs Semantic Scholar (rich metadata, ~30% PDF)

---

## Scripts Directory

```
scripts/
├── research.py          # One-click workflow
├── search_papers.py     # Tavily + Semantic Scholar search
├── search_tavily.py     # Standalone Tavily search
├── download_paper.py    # PDF download
├── pdf_reader.py        # Chunked text extraction
├── summarize.py         # Schema-based summarization
└── auto_research.py     # Automated workflow
```
